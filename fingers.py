# Bộ gõ song ngữ Anh Việt thông minh

from .telexify.core import process_sequence
import sublime, sublime_plugin

class State:
    TELEXIFY = True
    ORIGIN = False
    FINAL = False
    SKIP_RESET = True
    EV_DICT = False
    def reset():
        State.ORIGIN = False
        State.SKIP_RESET = True

''' Trả lại con trỏ đầu tiên trong multi-currsors '''
def first_cursor(view):
    return view.sel()[0]

''' Trả lại vị trí của con trỏ đầu tiên '''
def first_cursor_pos(view):
    return view.sel()[0].begin()

''' Mô phỏng lại động tác vùng text bôi đen bị xóa khi ấn 1 phím key bất kỳ '''
def replace_selected_region(view, edit, region, key):
    view.replace(edit, region, key)
    sel = view.sel()
    sel.clear()
    sel.add(region.begin() + len(key))

''' Mô phỏng việc bấm 1 phím key bất kỳ '''
def mimic_original_key_press(view, edit, key):
    region = first_cursor(view)
    if region.empty():
        view.insert(edit, region.begin(), key)
    else:
        replace_selected_region(view, edit, region, key)


''' TextCommand để hiện chuỗi ký tự gốc được gõ chứ ko chuyển hóa thành TV '''
class KeepOriginCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        if State.TELEXIFY and State.ORIGIN:
            self.view.end_edit(edit)
            self.view.run_command("replace_current", { "string" : State.ORIGIN + " " })
            State.reset()
            self.view.hide_popup()
        else:
            mimic_original_key_press(self.view, edit, key)


''' Nghe sự kiện on_modified để xóa kịp thời ORIGIN khi người dùng chuyển
từ việc gõ phím alphabet liên tục sang một theo tác khác => kết thúc chuỗi ký tự '''
class EventListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        if not State.SKIP_RESET:
            State.reset()
            view.hide_popup()
        # Đảm bảo gọi State.reset() cho lần thứ 2 liên tiếp on_modified được gọi
        State.SKIP_RESET = False


''' TextCommand sẽ chạy khi phím a-zA-Z hoặc backspace được bấm.
Các từ được cấu thành bởi alphabet key và backspace cho trường hợp viết sai xóa đi
viết lại. Đây là hàm quan trọng nhất của bộ gõ. '''
class AzPressCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        # Bỏ qua State.reset() cho lần đầu on_modified được gọi
        State.SKIP_RESET = True

        region = first_cursor(self.view)
        if region.empty(): # ko có selected text
            if key == "backspace":
                # Nếu ORIGIN chỉ còn 1 ký tự thì xóa ký tự thật tại vị trí con trỏ
                 if not State.ORIGIN or len(State.ORIGIN) == 1:
                    region = sublime.Region(region.end() - 1, region.end())
                    deleted = self.view.substr(region)
                    self.view.replace(edit, region, "")
                    # Chỉ thực hiện các xử lý tiếp nếu ký tự vừa xóa là a-zA-Z
                    if not deleted.isalpha(): return
            else:
                self.view.insert(edit, region.begin(), key)
        else: # xử lý selected text (đoạn text dc bôi đen)
            if key == "backspace": key = ""
            replace_selected_region(self.view, edit, region, key)
            return

        # Bỏ qua nếu chế độ gõ Telex đang tắt
        if not State.TELEXIFY: return False
        self.view.hide_popup()

        curr_cursor = first_cursor(self.view)
        # Bỏ qua nếu có selected text
        if curr_cursor.begin() != curr_cursor.end(): return False
            
        word_region = self.view.word(curr_cursor)
        curr_region = sublime.Region(word_region.begin(), curr_cursor.begin())
        current = self.view.substr(curr_region)

        # `current` là đoạn ký tự đang hiển thị trên màn hình từ phần đầu của
        # từ cho tới vị trí con trỏ
        # `ORIGIN` là chuỗi ký tự gốc được gõ (chưa chuyển hóa)
        # `FINAL` là chuỗi ký tự đã được telexify sang tiếng Việt (đã chuyển hóa)
        if State.ORIGIN:
            if key == "backspace":
                # Kiểm tra sự liền mạch của thao tác gõ
                if (State.ORIGIN == current or State.FINAL == current):
                    State.ORIGIN = State.ORIGIN[:-1] # xóa ký tự cuối của ORIGIN
                else: # thao tác gõ ko còn liền mạch nữa
                    State.ORIGIN = current[:-1]
                    region = sublime.Region(region.end() - 1, region.end())
                    self.view.replace(edit, region, "")
            else:
                # Kiểm tra sự liền mạch của thao tác gõ telex
                if (State.ORIGIN == current[:-1] or State.FINAL == current[:-1]):
                    State.ORIGIN += current[-1] # thêm key vừa gõ vào ORIGIN
                else: # thao tác gõ ko còn liền mạch nữa
                    State.ORIGIN = current
        else: # ORIGIN chưa được khởi tạo
            State.ORIGIN = current

        # Chuyển hóa ORIGIN (chuỗi ký tự được gõ) thành FINAL (tiếng Việt)
        State.FINAL = process_sequence(State.ORIGIN); #print(final)

        # Nếu chuyển hóa thành công, FINAL có thể là 1 từ tiếng Việt có nghĩa
        if State.FINAL:
            self.view.end_edit(edit) # thì hiển thị FINAL
            self.view.run_command("replace_current", { "string" : State.FINAL })
            if State.FINAL != State.ORIGIN:
                # đồng thời show ORIGIN trong popup để người gõ xem đó có phải
                # từ tiếng Anh mình muốn gõ hay không
                self.view.show_popup(State.ORIGIN, location=curr_region.begin())
        else: # Nếu ko thì hiển thị ORIGIN
            self.view.end_edit(edit)
            self.view.run_command("replace_current", { "string" : State.ORIGIN })


''' TextCommand để thay chuỗi ký tự đang gõ bằng 1 đoạn text được chỉ định '''
class ReplaceCurrentCommand(sublime_plugin.TextCommand):
    def run(self, edit, string):
        State.SKIP_RESET = True
        curr_cursor = first_cursor(self.view)
        word_region = self.view.word(curr_cursor)
        curr_region = sublime.Region(word_region.begin(), curr_cursor.begin())
        self.view.replace(edit, curr_region, string)


''' Bật tắt chế độ gõ Telex '''
class ToggleTelexModeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if State.TELEXIFY is True:
            State.TELEXIFY = False
            self.view.set_status('Fingers'," Gõ tiếng Việt: Tắt")
        else:
            State.TELEXIFY = True
            self.view.set_status('Fingers'," Gõ tiếng Việt: Bật")


''' Tiện ích gửi đoạn text được chọn lên Google dịch '''
import os, webbrowser, urllib.parse
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


''' Tiện ích tra từ điển Anh - Việt khi di chuột lên 1 từ '''
import os, re
import os.path
from os import path
def plugin_loaded():
    # Nạp từ điển Anh Việt
    # cd /Applications/Sublime\ Text.app/Contents/MacOS
    # ln -s ~/repos/fingers-sublime/TudienAnhVietBeta.tab
    # cd /Users/t/Library/Application\ Support/Sublime\ Text/Packages/
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

        while (len(word) > 0):
            try:
                content = State.EV_DICT[word]
                view.show_popup(
                    "<b>" + word + "</b><br> " + content,
                    location=point,
                    max_width=800,
                    max_height=400,
                )
                return
            except KeyError: word = word[:-1]