# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import partial
import codecs

from .bogo.core import _Action, _get_action, get_vni_definition, process_sequence
from .bogo.mark import Mark

import os
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

    position = self.view.sel()[0]

    if self.view.size() > self.current_size:
      a = self.view.sel()[0].begin()-1
      b = self.view.sel()[0].end()
      word_position = sublime.Region(a, b)
      word_region = self.view.word(word_position)
      word = self.view.substr(word_region)

      final = self.process(word)
      
      if not final:
        return False
        
      self.view.run_command("runchange", {"a":a, "b":b, "string":final})

      self.current_size = self.view.size();
    elif self.view.size() < self.current_size:
      self.current_size = self.view.size();
    
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

    settings = sublime.load_settings("vn_ime.sublime-settings")
    if settings.get("telex"):
      TELEX = True
    else:
      TELEX = False

    if STATUS:
      STATUS = False
      sublime.status_message("VN IME Stoped")
      self.view.set_status('VN IME'," VN IME: OFF")
    else:
      STATUS = True
      sublime.status_message("VN IME Started")
      self.view.set_status('VN IME'," VN IME: ON")

class RunchangeCommand(sublime_plugin.TextCommand):
  def run(self, edit, a, b, string):
    region = self.view.word(sublime.Region(a,b))
    self.view.replace(edit,region,string)