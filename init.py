# Bộ gõ song ngữ Anh Việt thông minh

from .telexify.core import process_sequence
import sublime, sublime_plugin
import os, webbrowser, urllib.parse

TELEXIFY = True
CURR_REGION = False
FINAL = ""

class SaveOnModifiedListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        view.run_command('key_pressed')

class FinishWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = self.view.sel()[0]
        region = sublime.Region(CURR_REGION.begin(), region.end())
        self.view.replace(edit, region, FINAL)


class KeyPressedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Bỏ qua nếu chế độ gõ Telex đang tắt
        if not TELEXIFY: return False
        self.view.hide_popup()

        curr_cursor = self.view.sel()[0]
        # Bỏ qua nếu có selected text
        if curr_cursor.begin() != curr_cursor.end(): return False
            
        global CURR_REGION
        global FINAL

        curr_pos = curr_cursor.begin()
        last_char = self.view.substr(sublime.Region(curr_pos - 1, curr_pos))
        # print(curr_pos, "/"+last_char+"/")
        if CURR_REGION and last_char == " ": # space pressed
            self.view.end_edit(edit)
            self.view.run_command("finish_word")

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
        region = self.view.sel()[0]
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
