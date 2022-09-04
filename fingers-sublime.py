# Tuocright (T) 2022 Tuoc <dungtn@gmail.com>
# Bộ gõ song ngữ Anh Việt thông minh

from .bogo.core import process_sequence
import sublime, sublime_plugin

STATUS = True
TELEX = True

class SaveOnModifiedListener(sublime_plugin.EventListener):
  def on_modified_async(self, view):
    view.run_command('startime')

class StartimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if not STATUS: return False

    SEP = "_"

    curr_pos = self.view.sel()[0]
    word_region = self.view.word(curr_pos)
    parts = self.view.substr(word_region).split(SEP)

    prev = parts[0]
    origin = parts[-1]

    final = self.process(origin)
    if final == prev: return False

    if final != origin: final = SEP.join((final, origin))
    self.view.end_edit(edit)
    self.view.run_command("runchange", {"string":final})
    return True

  def process(self, word):
    return process_sequence(word)
    # last_char = word[-1].lower()
    # if last_char in "qwrsfjx" or (last_char == 'd' and word[-2].lower() == 'd'):
    #   return process_sequence(word)
    # return False

class ControlimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global STATUS
    if STATUS:
      STATUS = False
      self.view.set_status('Fingers'," Fingers: OFF")
    else:
      STATUS = True
      self.view.set_status('Fingers'," Fingers: ON")

class RunchangeCommand(sublime_plugin.TextCommand):
  def run(self, edit, string):
    curr_pos = self.view.sel()[0]
    region = self.view.word(curr_pos)
    self.view.replace(edit, region, string)

class FuncundoCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.window.run_command("undo")

class FuncpasteCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.window.run_command("paste")

class FuncredoCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.window.run_command("redo")
