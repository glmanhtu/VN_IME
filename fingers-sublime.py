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
        curr_point = curr_cursor.end()
        self.view.insert(edit, curr_point, 'z')
        # self.run_command("insert_char", {"text": kargs["keystroke"]})
        # self.view.run_command('key_pressed')

class InsertCharCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        curr_cursor = self.view.sel()[0]
        curr_point = curr_cursor.end()
        self.view.insert(edit, curr_point, text)
        # self.run_command("insert", {"point": curr_point, "text": text})

class KeyPressedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not TELEXIFY: return False

        curr_cursor = self.view.sel()[0]
        word_region = self.view.word(curr_cursor)
        origin = self.view.substr(word_region)
        # SEP = "_"
        # parts = self.view.substr(word_region).split(SEP)
        # prev = parts[0]
        # origin = parts[-1]

        final = self.to_vi_utf8(origin)
        if not final or final == origin: return False
        # if not final or final == prev: return False
        # if final != origin: final = SEP.join((final, origin))
        self.view.end_edit(edit)
        self.view.run_command("replace_current", {"string":final})
        return True

    def to_vi_utf8(self, word):
        last_char = word[-1].lower()
        if last_char in "qwrsfjxd": return process_sequence(word)
        return False


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
        url = url + urllib.parse.quote(selection)
        webbrowser.open(url)
