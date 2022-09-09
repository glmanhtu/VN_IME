# Bộ gõ song ngữ Anh Việt thông minh

from .telexify.core import process_sequence
import sublime, sublime_plugin
import os, webbrowser, urllib.parse

class State:
    TELEXIFY = True
    CURR_REGION = False
    FINAL = ""
    EV_DICT = {}

def first_cursor(view):
    return view.sel()[0]

class SaveOnModifiedListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        view.run_command('key_pressed')

class TabPressedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = first_cursor(self.view)
        if State.TELEXIFY and State.CURR_REGION:
            self.view.insert(edit, region.begin(), " ")
            State.CURR_REGION = False
        else:
            self.view.insert(edit, region.begin(), "\t")

class FinishWordCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        if State.TELEXIFY and State.CURR_REGION:
            region = first_cursor(self.view)
            region = sublime.Region(State.CURR_REGION.begin(), region.end())
            self.view.replace(edit, region, State.FINAL + key)
            State.CURR_REGION = False
        else:
            region = first_cursor(self.view)
            self.view.insert(edit, region.begin(), key)


class KeyPressedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Bỏ qua nếu chế độ gõ Telex đang tắt
        if not State.TELEXIFY: return False
        self.view.hide_popup()

        curr_cursor = first_cursor(self.view)
        # Bỏ qua nếu có selected text
        if curr_cursor.begin() != curr_cursor.end(): return False
            
        word_region = self.view.word(curr_cursor)
        curr_region = sublime.Region(word_region.begin(), curr_cursor.begin())

        origin = self.view.substr(curr_region)
        final = process_sequence(origin); #print(final)

        if final == origin:
            State.CURR_REGION = False
            self.view.hide_popup()
        else:
            State.CURR_REGION = curr_region
            State.FINAL = final
            loc = curr_region.end() - len(final)
            self.view.show_popup(final, location=loc)


class ToggleTelexModeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if State.TELEXIFY is True:
            State.TELEXIFY = False
            self.view.set_status('Fingers'," Gõ tiếng Việt: Tắt")
        else:
            State.TELEXIFY = True
            self.view.set_status('Fingers'," Gõ tiếng Việt: Bật")


class GoogleTranslateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = first_cursor(self.view)
        if region.begin() == region.end():  # No selection
            selection = self.view.substr(self.view.word(region)) # Text under cursor
        else:
            selection = self.view.substr(region)  # Text selected
        if not selection: return
        webbrowser.open("https://translate.google.com/?hl=vi&sl=auto&tl=vi&text=" + \
            urllib.parse.quote(selection))


class UndoFunctionCommand(sublime_plugin.WindowCommand):
    def run(self):
        State.TELEXIFY = False
        self.window.run_command("undo")
        State.TELEXIFY = True

import os, re
def plugin_loaded():
    # Nạp từ điển Anh Việt
    # Dict data https://github.com/catusf/tudien/blob/master/dict
    # cd /Applications/Sublime\ Text.app/Contents/MacOS
    # ln -s ~/repos/fingers-sublime/TudienAnhVietBeta.tab
    # cd ~/Library/Application\ Support/Sublime\ Text/Packages
    # ln -s ~/repos/fingers-sublime/TudienAnhVietBeta.tab
    t = open(os.getcwd() + "/TudienAnhVietBeta.tab", mode="r", encoding="utf-8").read()
    for w in t.split("\n"):
        ev = w.split("\t")
        if len(ev) >= 2: State.EV_DICT[ev[0]] = ev[1]
    print("TEST EV_DICT: visually => " + State.EV_DICT["visually"])


class DictionaryEventListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        word = view.substr(view.word(point))
        if not word: return

        try: word = re.compile(r"[a-zA-Z]+").search(word.lower()).group()
        except AttributeError: return # No match in text

        content = State.EV_DICT[word]
        if not content: return
        view.show_popup(
            "<b>" + word + "</b><br> " + content,
            location=point,
            max_width=800,
            max_height=400,
        )
