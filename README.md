# Vietnamese IME - Bộ gõ tiếng Việt

Gõ tiếng Việt trên Sublime Text 3

Phiên bản 2 sử dụng engine BoGoEngine của ibus-bogo

Phiên bản 1 với 2 nhánh riêng biệt cho kiểu gõ VNI và TELEX được lưu tại Repo [VN_IME](https://github.com/88d52bdba0366127fffca9dfặ99/VN_IME) và tại nhánh [TELEX](https://github.com/yehnkay/VN_IME/tree/TELEX)

## Cài đặt

Package Control: Install Package -> `vn ime`

Cài đặt bằng tay:

```
git clone https://github.com/yehnkay/VN_IME
```

## Hướng dẫn sử dụng

Nhấn phím F2 để bật gõ tiếng Việt, mặc định là kiểu gõ VNI. Nhấn tiếp phím F2 để tắt

Khi thanh status hiện chữ `VN IME : ON` là đang bật, `VN IME : OFF` là đã tắt

Để dùng kiểu gõ TELEX, thêm giá trị `telex` trong tập tin cấu hình `Preferences.sublime-settings` tại `Preferences` -> `Settings - User` với giá trị `true`. Ví dụ như sau:

```
{
  "telex": true
}
```