# Bộ gõ song ngữ Anh Việt thông minh

from .telexify.core import process_sequence
import sublime, sublime_plugin
import os, webbrowser, urllib.parse

TELEXIFY = True

class SaveOnModifiedListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        view.run_command('key_pressed')


class TelexKeyPressedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        curr_cursor = self.view.sel()[0]
        word_region = self.view.word(curr_cursor)
        origin = self.view.substr(word_region) + kargs["keystroke"]
        self.view.run_command("replace_current", {"string":origin})
        # self.view.insert(edit, curr_cursor.end(), origin)
        # self.run_command("insert", {"point": curr_point, "text": origin})
        return True


class InsertCharCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        curr_cursor = self.view.sel()[0]


class KeyPressedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not TELEXIFY: return False
        curr_cursor = self.view.sel()[0]
        word_region = self.view.word(curr_cursor)
        origin = self.view.substr(word_region)

        last_char = origin[-1].lower()
        if last_char not in "qwrsfjxd": return False
        final = process_sequence(origin)
        if final == origin: return False
        self.view.end_edit(edit)
        self.view.run_command("replace_current", {"string":final})
        return True


class ReplaceCurrentCommand(sublime_plugin.TextCommand):
    def run(self, edit, string):
        curr_pos = self.view.sel()[0]
        region = self.view.word(curr_pos)
        self.view.replace(edit, region, string)


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
        url = "https://translate.google.com/?hl=vi&sl=auto&tl=vi&text="
        # url = "https://translate.google.com/?sl=en&tl=vi&text="
        url = url + urllib.parse.quote(selection)
        webbrowser.open(url)
