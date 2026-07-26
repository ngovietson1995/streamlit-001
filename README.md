# Ứng dụng học thuộc lòng bằng Streamlit

Ứng dụng lấy ngẫu nhiên câu hỏi từ `kho_cau_hoi.xlsx`, hiển thị gợi ý, cho phép người học gõ lại đáp án, kiểm tra mức độ tương đồng và chủ động hiện/ẩn đáp án mẫu.

## 1. Cấu trúc thư mục

```text
hoc_thuoc_streamlit/
├── app.py
├── kho_cau_hoi.xlsx
├── requirements.txt
├── run_app.bat
└── .streamlit/
    └── config.toml
```

## 2. Chạy nhanh trên Windows

Cách đơn giản nhất: nhấp đúp vào `run_app.bat`. Lần đầu chương trình sẽ tạo môi trường ảo, cài thư viện và mở ứng dụng trong trình duyệt.

Hoặc chạy thủ công trong Terminal của VS Code:

```powershell
python -m venv venv
```

Trong PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Trong Command Prompt:

```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
streamlit run app.py
```

Sau khi chạy, trình duyệt thường mở tại `http://localhost:8501`.

## 3. Cách chuẩn bị file Excel

File `kho_cau_hoi.xlsx` cần có các cột:

| Cột | Bắt buộc | Nội dung |
|---|---:|---|
| `STT` | Không | Số thứ tự câu hỏi |
| `Câu hỏi` | Có | Nội dung câu hỏi |
| `Đáp án` | Có | Đáp án đầy đủ; có thể xuống dòng trong một ô |
| `Gợi ý` | Không | Các gợi ý ngăn cách bằng dấu `|` hoặc dấu `;` |

Ví dụ gợi ý:

```text
Sự cố|Không đóng lại|Được phép đóng lại|Lệnh điều độ
```

Khi cột `Gợi ý` bị bỏ trống, ứng dụng tự tạo gợi ý ngắn từ đáp án.

## 4. Các chức năng chính

- Xáo trộn thứ tự câu hỏi và hạn chế lặp lại trong một vòng học.
- Đáp án mẫu luôn bị ẩn khi mở ứng dụng hoặc chuyển sang câu mới.
- Nút `Hiện đáp án` và `Ẩn đáp án`.
- Ô nhập đáp án có thể gõ nhiều dòng.
- Nút kiểm tra và chấm mức độ tương đồng.
- Nút xóa bài làm và chuyển câu tiếp theo.
- Có thể tải một file `.xlsx` khác từ thanh bên của ứng dụng.
- Giao diện co giãn cho máy tính và điện thoại.

## 5. Thay đổi tiêu đề

Mở `app.py`, sửa dòng:

```python
APP_TITLE = "Kiểm tra thông tư"
```

## 6. Lưu ý khi chấm đáp án

Ứng dụng chuẩn hóa chữ hoa/chữ thường, khoảng trắng và dấu câu trước khi tính mức tương đồng. Điểm số chỉ hỗ trợ tự học; người học vẫn nên mở đáp án mẫu để đối chiếu đầy đủ từng ý.
