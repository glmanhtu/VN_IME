# Bộ gõ song ngữ Anh Việt thông minh

from .telexify.core import process_sequence
import sublime, sublime_plugin
import os, webbrowser, urllib.parse

class State:
    TELEXIFY = True
    REGION = False
    FINAL = False
    EV_DICT = False
    def reset():
        State.REGION = False

def first_cursor(view):
    return view.sel()[0]

def first_cursor_pos(view):
    return view.sel()[0].begin()

def replace_selected_region(view, edit, region, key):
    view.replace(edit, region, key)
    sel = view.sel()
    sel.clear()
    sel.add(region.begin() + len(key))

def mimic_original_key_press(view, edit, key):
    region = first_cursor(view)
    if region.empty():
        view.insert(edit, region.begin(), key)
    else:
        replace_selected_region(view, edit, region, key)


# class SaveOnModifiedListener(sublime_plugin.EventListener):
#     def on_modified(self, view):
#         view.run_command('finish_word')

class KeepOriginCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        if State.TELEXIFY and State.REGION:
            self.view.insert(edit, first_cursor_pos(self.view), " ")
            State.reset()
            self.view.hide_popup()
        else:
            mimic_original_key_press(self.view, edit, key)


class FinishWordCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        if State.TELEXIFY and State.REGION:
            if first_cursor_pos(self.view) == State.REGION.end(): 
                # quan trọng: ký tự dứt điểm phải dc gõ ở cuối từ đang chuyển hóa
                self.view.replace(edit, State.REGION, State.FINAL)
            State.reset()
            self.view.hide_popup()
        mimic_original_key_press(self.view, edit, key)


class AzPressCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        region = first_cursor(self.view)
        if region.empty():
            if key == "backspace":
                region=sublime.Region(region.end()-1, region.end())
                self.view.replace(edit, region, "")
            else:
                self.view.insert(edit, region.begin(), key)
        else: # đoạn text dc bôi đen
            if key == "backspace": key = ""
            replace_selected_region(self.view, edit, region, key)

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
            State.reset()
            self.view.hide_popup()
        else:
            State.REGION = curr_region
            State.FINAL = final
            loc = curr_region.end() - len(final)
            self.view.show_popup(
                final,
                location=loc,
                on_hide=State.reset
            )


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

import os, re
import os.path
from os import path
def plugin_loaded():
    # Nạp từ điển Anh Việt
    # cd /Applications/Sublime\ Text.app/Contents/MacOS
    # ln -s ~/repos/fingers-sublime/TudienAnhVietBeta.tab
    f = os.getcwd() + "/TudienAnhVietBeta.tab"; print(f)
    if not path.exists(f): return

    State.EV_DICT = {}
    t = open(f, mode="r", encoding="utf-8").read()
    for w in t.split("\n"):
        ev = w.split("\t")
        if len(ev) >= 2: State.EV_DICT[ev[0]] = ev[1]
    print("TEST EV_DICT: visually => " + State.EV_DICT["visually"])


class DictionaryEventListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        if not State.EV_DICT: return

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
