# Tuocright (T) 2022 Tuoc <dungtn@gmail.com>
# Bộ gõ song ngữ Anh Việt thông minh

from .bogo.core import process_sequence
import sublime, sublime_plugin
import os

STATUS = True
TELEX = True

# https://github.com/futureprogrammer360/Dictionary/blob/master/dictionary.py
class GoogleTranslateCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    region = self.view.sel()[0]
    if region.begin() == region.end():  # No selection
      selection = self.view.substr(self.view.word(region)) # Text under cursor
    else:
      selection = self.view.substr(region)  # Text selected
    if not selection:
      return

    cmd = "open https://translate.google.com/?hl=vi&sl=auto&tl=vi&text="
    cmd = cmd + selection
    self.view.run_command("runchange", {"string":cmd})
    # os.system(cmd)


class FingersPlugin(sublime_plugin.EventListener):
  def on_modified_async(self, view):
    view.run_command('startime')

class StartimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if not STATUS: return False

    curr_pos = self.view.sel()[0]
    word_region = self.view.word(curr_pos)
    origin = self.view.substr(word_region).split(SEP)
    # SEP = "_"
    # parts = self.view.substr(word_region).split(SEP)
    # prev = parts[0]
    # origin = parts[-1]

    final = self.to_vi_utf8(origin)
    if not final or final == origin: return False
    # if not final or final == prev: return False
    # if final != origin: final = SEP.join((final, origin))
    self.view.end_edit(edit)
    self.view.run_command("runchange", {"string":final})
    return True

  def to_vi_utf8(self, word):
    last_char = word[-1].lower()
    if last_char in "qwrsfjx" or (last_char == 'd' and word[-2].lower() == 'd'):
      return process_sequence(word)
    return False

class RunchangeCommand(sublime_plugin.TextCommand):
  def run(self, edit, string):
    curr_pos = self.view.sel()[0]
    region = self.view.word(curr_pos)
    self.view.replace(edit, region, string)

class ControlimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global STATUS
    if STATUS:
      STATUS = False
      self.view.set_status('Fingers'," Fingers: OFF")
    else:
      STATUS = True
      self.view.set_status('Fingers'," Fingers: ON")
