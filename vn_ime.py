from .bogo.core import get_vni_definition, process_sequence
import sublime, sublime_plugin

MOD = False
STATUS = False
TELEX = False

class SaveOnModifiedListener(sublime_plugin.EventListener):
  def on_modified(self, view):
    global MOD

    if not MOD:
      view.run_command('startime')
    MOD = False

class StartimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global MOD

    if not STATUS:
      return False

    current_position = self.view.sel()[0]
    word_region = self.view.word(current_position)
    word = self.view.substr(word_region)
    final = self.process(word)

    if not final:
      return False

    self.view.run_command("runchange", {"string":final})
    MOD = True
    return True

  def process(self, word):
    if TELEX:
      final_word = process_sequence(word)
    else:
      final_word = process_sequence(word, rules=get_vni_definition())

    if final_word != word:
      return final_word
    return False

class ControlimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global STATUS
    global TELEX
    global SKIP_NON_VIETNAMESE

    settings = sublime.load_settings("Preferences.sublime-settings")
    if settings.get("telex"):
      TELEX = True
    else:
      TELEX = False

    if STATUS:
      STATUS = False
      self.view.set_status('VN IME'," VN IME: OFF")
    else:
      STATUS = True
      self.view.set_status('VN IME'," VN IME: ON")

class RunchangeCommand(sublime_plugin.TextCommand):
  def run(self, edit, string):
    current_position = self.view.sel()[0]
    region = self.view.word(current_position)
    self.view.replace(edit, region, string)

class FuncundoCommand(sublime_plugin.WindowCommand):
  def run(self):
    global MOD
    
    tmp_MOD = MOD
    MOD = True
    self.window.run_command("undo")
    MOD = tmp_MOD

class FuncpasteCommand(sublime_plugin.WindowCommand):
  def run(self):
    global MOD
    
    tmp_MOD = MOD
    MOD = True
    self.window.run_command("paste")
    MOD = tmp_MOD

class FuncredoCommand(sublime_plugin.WindowCommand):
  def run(self):
    global MOD

    tmp_MOD = MOD
    MOD = True
    self.window.run_command("redo")
    MOD = tmp_MOD