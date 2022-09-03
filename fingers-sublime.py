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
    curr_pos = self.view.sel()[0]
    word_region = self.view.word(curr_pos)
    word = self.view.substr(word_region)
    final = self.process(word)
    #
    if not final: return False
    self.view.end_edit(edit)
    self.view.run_command("runchange", {"string":final})
    return True

  def process(self, word):
    final_word = process_sequence(word)
    if final_word != word:
      return final_word
    return False

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
