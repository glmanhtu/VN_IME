# Bộ gõ song ngữ Anh Việt thông minh

from .telexify.core import process_sequence
import sublime, sublime_plugin
import os, webbrowser, urllib.parse

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
        global CURR_REGION
        region = first_cursor(self.view)
        if TELEXIFY and CURR_REGION:
            self.view.insert(edit, region.begin(), " ")
            CURR_REGION = False
        else:
            self.view.insert(edit, region.begin(), "\t")

class FinishWordCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        global CURR_REGION
        if TELEXIFY and CURR_REGION:
            region = first_cursor(self.view)
            region = sublime.Region(CURR_REGION.begin(), region.end())
            self.view.replace(edit, region, FINAL + key)
            CURR_REGION = False
        else:
            region = first_cursor(self.view)
            self.view.insert(edit, region.begin(), key)


class KeyPressedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Bỏ qua nếu chế độ gõ Telex đang tắt
        if not TELEXIFY: return False
        self.view.hide_popup()

        curr_cursor = first_cursor(self.view)
        # Bỏ qua nếu có selected text
        if curr_cursor.begin() != curr_cursor.end(): return False
            
        global CURR_REGION
        global FINAL

        word_region = self.view.word(curr_cursor)
        curr_region = sublime.Region(word_region.begin(), curr_cursor.begin())

        origin = self.view.substr(curr_region)
        final = process_sequence(origin); #print(final)

        if final == origin:
            CURR_REGION = False
            self.view.hide_popup()
        else:
            CURR_REGION = curr_region
            FINAL = final
            loc = curr_region.end() - len(final)
            self.view.show_popup(FINAL, location=loc)


class ToggleTelexModeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global TELEXIFY
        if TELEXIFY is True:
            TELEXIFY = False
            self.view.set_status('Fingers'," Gõ tiếng Việt: Tắt")
        else:
            TELEXIFY = True
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
        global TELEXIFY
        TELEXIFY = False
        self.window.run_command("undo")

import os, re
def plugin_loaded():
    # Nạp từ điển Anh Việt
    # Dict data https://github.com/catusf/tudien/blob/master/dict
    # cd /Applications/Sublime\ Text.app/Contents/MacOS
    # ln -s ~/repos/fingers-sublime/TudienAnhVietBeta.tab
    # cd ~/Library/Application\ Support/Sublime\ Text/Packages
    # ln -s ~/repos/fingers-sublime/TudienAnhVietBeta.tab
    global EV_DICT
    t = open(os.getcwd() + "/TudienAnhVietBeta.tab", mode="r", encoding="utf-8").read()
    for w in t.split("\n"):
        ev = w.split("\t")
        if len(ev) >= 2: EV_DICT[ev[0]] = ev[1]
    print("TEST EV_DICT: visually => " + EV_DICT["visually"])


class DictionaryEventListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        word = view.substr(view.word(point))
        if not word: return

        word = clean_text(word.lower())
        content = EV_DICT[word]
        if not content: return

        word = "<b>" + word + "</b><br>"
        view.show_popup(
            word+content,
            location=point,
            max_width=800,
            max_height=400,
        )

def clean_text(text: str) -> str:
    try:
        text = re.compile(r"[a-zA-Z]+").search(text).group()
        # text = re.compile(r"[a-zA-Z0-9]+").search(text).group()
    except AttributeError:  # No match in text
        return ""
    return text
