# 📦 Hệ Thống Quản Lý Kho

Ứng dụng web quản lý kho hàng được xây dựng bằng Streamlit, hỗ trợ quản lý sản phẩm, nhập/xuất hàng, cảnh báo tồn kho và dashboard báo cáo.

## 📋 Mục Lục

- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt](#cài-đặt)
- [Cấu Hình](#cấu-hình)
- [Chạy Ứng Dụng](#chạy-ứng-dụng)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Tính Năng](#tính-năng)
- [Lưu Ý Bảo Mật](#lưu-ý-bảo-mật)

## 🖥️ Yêu Cầu Hệ Thống

- **Python**: 3.8 trở lên
- **Hệ điều hành**: Windows, macOS, hoặc Linux
- **Trình duyệt**: Chrome, Firefox, Edge (phiên bản mới nhất)

## 📥 Cài Đặt

### Bước 1: Clone hoặc tải dự án

Nếu bạn đã có mã nguồn, bỏ qua bước này. Nếu chưa, hãy tải hoặc clone dự án về máy.

### Bước 2: Tạo Virtual Environment (venv)

Mở Terminal/Command Prompt và di chuyển đến thư mục dự án:

```bash
cd D:\Downloads\QTDA\pythonProject1
```

**Trên Windows:**
```bash
python -m venv venv
```

**Trên macOS/Linux:**
```bash
python3 -m venv venv
```

### Bước 3: Kích hoạt Virtual Environment

**Trên Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Trên Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Trên macOS/Linux:**
```bash
source venv/bin/activate
```

Sau khi kích hoạt thành công, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

### Bước 4: Cài đặt các thư viện cần thiết

Đảm bảo bạn đang trong virtual environment (có `(venv)` ở đầu dòng), sau đó chạy:

```bash
pip install -r requirements.txt
```

Lệnh này sẽ cài đặt tất cả các thư viện cần thiết:
- `pandas` - Xử lý dữ liệu
- `streamlit` - Framework web
- `openpyxl` - Đọc file Excel (.xlsx)
- `xlrd` - Đọc file Excel (.xls)
- `plotly` - Vẽ biểu đồ
- `streamlit-aggrid` - Bảng dữ liệu nâng cao

### Bước 5: Kiểm tra cài đặt

Chạy lệnh sau để kiểm tra Streamlit đã được cài đặt:

```bash
streamlit --version
```

## ⚙️ Cấu Hình

### Cấu hình Email (Tùy chọn)

Nếu bạn muốn sử dụng tính năng gửi email cảnh báo, cần cấu hình file `.streamlit/secrets.toml`:

1. Mở file `.streamlit/secrets.toml` (nếu chưa có, tạo mới)

2. Thêm cấu hình email của bạn:

```toml
email_sender = "your-email@gmail.com"        # Email người gửi
email_password = "your-app-password"         # Mật khẩu ứng dụng (App Password)
email_receiver = "receiver-email@gmail.com"  # Email người nhận
```

#### Cách lấy App Password từ Gmail:

1. Đăng nhập vào [Google Account](https://myaccount.google.com/)
2. Vào **Security** (Bảo mật)
3. Bật **2-Step Verification** (Xác minh 2 bước) nếu chưa bật
4. Vào **App passwords** (Mật khẩu ứng dụng)
5. Chọn **Mail** và **Other (Custom name)**
6. Nhập tên (ví dụ: "Streamlit App")
7. Nhấn **Generate** (Tạo)
8. Copy mật khẩu 16 ký tự (không có dấu cách) và dán vào `email_password`

**Lưu ý**: 
- Không sử dụng mật khẩu Gmail thông thường
- Chỉ sử dụng App Password (16 ký tự)
- Nếu không cấu hình email, tính năng cảnh báo vẫn hoạt động nhưng không gửi email

### Cấu hình Port (Tùy chọn)

File `.streamlit/config.toml` đã được cấu hình mặc định chạy trên port **8505**. Nếu muốn thay đổi, sửa dòng:

```toml
[server]
port = 8505  # Thay đổi số port nếu cần
```

## 🚀 Chạy Ứng Dụng

### Khởi động ứng dụng

Đảm bảo bạn đang trong virtual environment và thư mục dự án, sau đó chạy:

```bash
streamlit run Homepage.py
```

Hoặc nếu muốn chỉ định port:

```bash
streamlit run Homepage.py --server.port 8505
```

### Truy cập ứng dụng

Sau khi chạy lệnh, trình duyệt sẽ tự động mở. Nếu không, truy cập:

```
http://localhost:8505
```

### Thông tin đăng nhập mặc định

- **Email**: `admin@example.com`
- **Mật khẩu**: `123456`

⚠️ **Lưu ý bảo mật**: Hãy thay đổi thông tin đăng nhập trong file `app.py` trước khi triển khai lên môi trường production!

## 📁 Cấu Trúc Dự Án

```
pythonProject1/
│
├── Homepage.py                 # File chính - Trang đăng nhập và trang chủ
├── utils.py                    # Các hàm tiện ích (quản lý session, email)
├── login.html                  # Giao diện đăng nhập HTML
├── requirements.txt             # Danh sách thư viện cần thiết
├── README.md                   # File hướng dẫn này
│
├── .streamlit/                 # Thư mục cấu hình Streamlit
│   ├── config.toml            # Cấu hình theme và server
│   └── secrets.toml            # Thông tin bảo mật (email, etc.)
│
├── pages/                      # Các trang con của ứng dụng
│   ├── 1_Products.py          # Quản lý sản phẩm
│   ├── 2_Import.py            # Nhập hàng
│   ├── 3_Export.py            # Xuất hàng
│   ├── 4_Alert_Threshold.py  # Cảnh báo tồn kho
│   └── 5_Dashboard.py         # Dashboard báo cáo
│
├── database/                   # Thư mục lưu trữ dữ liệu
│   ├── sanpham.csv            # Danh sách sản phẩm
│   ├── phieu_nhap.csv         # Lịch sử phiếu nhập
│   └── phieu_xuat.csv         # Lịch sử phiếu xuất
│
├── session.json                # File lưu trạng thái đăng nhập
└── email_sent_history.json    # Lịch sử đã gửi email cảnh báo
```

## ✨ Tính Năng

### 1. 📦 Quản Lý Sản Phẩm (`/Products`)
- Thêm, sửa, xóa, xem chi tiết sản phẩm
- Tìm kiếm sản phẩm
- Xuất danh sách ra Excel
- Quản lý tồn kho, ROP, tồn kho an toàn

### 2. 📥 Nhập Hàng (`/Import`)
- Tạo phiếu nhập kho
- Import phiếu nhập từ Excel/CSV
- Tự động cập nhật tồn kho khi nhập hàng
- Xem lịch sử phiếu nhập

### 3. 📤 Xuất Hàng (`/Export`)
- Tạo phiếu xuất kho
- Import phiếu xuất từ Excel/CSV
- Tự động trừ tồn kho khi xuất hàng
- Kiểm tra tồn kho trước khi xuất
- Xem lịch sử phiếu xuất

### 4. 🚨 Cảnh Báo Tồn Kho (`/Alert_Threshold`)
- Hiển thị sản phẩm dưới ngưỡng ROP
- Tự động gửi email cảnh báo (nếu đã cấu hình)
- Chỉnh sửa ngưỡng ROP trực tiếp
- Quản lý lịch sử gửi email

### 5. 📊 Dashboard (`/Dashboard`)
- Tổng quan số lượng sản phẩm
- Biểu đồ tồn kho theo sản phẩm
- So sánh tồn kho và ROP
- Biểu đồ hệ số luân chuyển

## 🔒 Lưu Ý Bảo Mật

1. **File `.streamlit/secrets.toml`**:
   - ⚠️ **KHÔNG** commit file này lên Git
   - Đảm bảo file `.gitignore` có dòng: `.streamlit/secrets.toml`
   - Chỉ dùng cho môi trường local/development

2. **Thông tin đăng nhập**:
   - Thay đổi email và mật khẩu mặc định trong `app.py`
   - Sử dụng mật khẩu mạnh cho môi trường production

3. **App Password Gmail**:
   - Không chia sẻ App Password với người khác
   - Xóa App Password cũ nếu không còn sử dụng

4. **Dữ liệu CSV**:
   - File CSV chứa dữ liệu nhạy cảm, cần backup định kỳ
   - Không chia sẻ file database với người không có quyền

## 🐛 Xử Lý Lỗi Thường Gặp

### Lỗi: "ModuleNotFoundError"

**Nguyên nhân**: Chưa cài đặt thư viện hoặc chưa kích hoạt venv

**Giải pháp**:
```bash
# Kích hoạt venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Cài đặt lại thư viện
pip install -r requirements.txt
```

### Lỗi: "Port already in use"

**Nguyên nhân**: Port 8505 đang được sử dụng

**Giải pháp**:
- Đóng ứng dụng đang chạy trên port đó
- Hoặc thay đổi port trong `config.toml` hoặc dùng lệnh:
```bash
streamlit run app.py --server.port 8506
```

### Lỗi: "Email không gửi được"

**Nguyên nhân**: Cấu hình email sai hoặc chưa cấu hình

**Giải pháp**:
- Kiểm tra file `.streamlit/secrets.toml`
- Đảm bảo đã sử dụng App Password (không phải mật khẩu thường)
- Kiểm tra kết nối internet

### Lỗi: "FileNotFoundError: login.html"

**Nguyên nhân**: File `login.html` không tồn tại

**Giải pháp**: Đảm bảo file `login.html` nằm trong thư mục gốc của dự án

## 📝 Ghi Chú

- Dữ liệu được lưu dưới dạng CSV trong thư mục `database/`
- Trạng thái đăng nhập được lưu trong `session.json`
- Lịch sử email được lưu trong `email_sent_history.json`
- Ứng dụng tự động tạo file CSV nếu chưa tồn tại

## 📞 Hỗ Trợ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Đã cài đặt đầy đủ các thư viện trong `requirements.txt`
2. Đã kích hoạt virtual environment
3. Đã cấu hình đúng file `secrets.toml` (nếu dùng email)
4. Python version >= 3.8

## 📄 License

Dự án này được phát triển cho mục đích học tập và sử dụng nội bộ.

---

**Chúc bạn sử dụng ứng dụng thành công! 🎉**

