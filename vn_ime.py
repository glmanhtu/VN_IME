from .bogo.core import get_vni_definition, process_sequence
import sublime, sublime_plugin

STATUS = False
TELEX = False

class SaveOnModifiedListener(sublime_plugin.EventListener):
  def on_modified(self, view):
    view.run_command('startime')

class StartimeCommand(sublime_plugin.TextCommand):
  current_size = 0

  def run(self, edit):
    if not STATUS:
      return False

    if self.view.size() <= self.current_size:
      self.current_size = self.view.size()
      return True

    current_position = self.view.sel()[0]
    word_region = self.view.word(current_position)
    word = self.view.substr(word_region)

    final = self.process(word)
    
    if not final:
      return False
      
    self.view.run_command("runchange", {"string":final})
    self.current_size = self.view.size()
    return True

  def process(self, word):
    global TELEX

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

    settings = sublime.load_settings("Preferences.sublime-settings")
    if settings.get("telex"):
      TELEX = True
    else:
      TELEX = False
    sublime.error_message(str(TELEX))

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
