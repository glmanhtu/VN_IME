Gõ tiếng Việt thông minh trên Sublime Text. Nhấn phím `esc` để bật tắt chế độ gõ tiếng Việt.

https://user-images.githubusercontent.com/8133/189085556-2d5768fb-dda0-424d-9d41-1de51449a565.mp4

Cài đặt thông thường:

![](sublime-package-repo.jpg)

Add `https://github.com/telexyz/fingers-sublime.git`

Sau đó vào `Package Control: Install Package` và tìm `fingers-sublime` để cài đặt.

### Một số phím tắt cài sẵn:

- `command+shift` hoặc `windows+shift` để tắt / bật chế độ gõ.

- Lựa chọn đoạn text tiếng Anh rồi `command+esc` hoặc `windows+esc` để dịch google.

- - -

Cài đặt locally để phát triển:
```
git clone https://github.com/telexyz/fingers-sublime.git
ln -s ~/repos/fingers-sublime ~/Library/Application\ Support/Sublime\ Text/Packages/fingers-sublime
```

## DOING

- Khi viết code chỉ gõ dc TV trong comment và string.

- Lưu lại ORIGIN của các từ TV đã được chuyển hóa gần đây để tiện cho việc undo từ tiếng Việt trở lại thành tiếng Anh Việt (chuỗi ký tự gốc)

- Làm tính năng gợi ý từ đang gõ sử dụng bằng cách thống kê n-gram các văn bản có trong current folder. Note: với bộ gõ ta có thể giả sử các từ gõ trước luôn đúng (vì gõ sai người dùng thường sẽ sửa ngay trước khi gõ từ tiếp theo)

## DONE

- Hover để tra từ điển Anh - Việt | tham khảo https://github.com/futureprogrammer360/Dictionary

- Hiển thị nguyên gốc, TV hiển thị ở popup, nhấn `space` tự động chọn TV, `tab` bỏ qua

- Chọn đoạn text tiếng Anh, nhấn `command+esc` để google translate. Tiện ích cho việc dịch văn bản.

- Tìm cách bind zig code vào python
  https://github.com/gwenzek/fastBPE/blob/master/test/test_zig.py
