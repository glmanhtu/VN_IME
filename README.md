Gõ tiếng Việt thông minh trên Sublime Text

Cài đặt bằng tay:
```
ln -s ~/repos/fingers-sublime ~/Library/Application\ Support/Sublime\ Text/Packages/fingers-sublime
```


Nhấn phím F2 để bật gõ tiếng Việt, mặc định là kiểu gõ VNI. Nhấn tiếp phím F2 để tắt

Để dùng kiểu gõ TELEX, thêm giá trị `telex` trong tập tin cấu hình `Preferences.sublime-settings` tại `Preferences` -> `Settings - User` với giá trị `true`. Ví dụ như sau:

```
{
  "telex": true
}
```