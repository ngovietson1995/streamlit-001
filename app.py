import streamlit as st
import pandas as pd
import numpy as np

# 1. Thêm tiêu đề và văn bản
st.title("Chào mừng đến với Streamlit! 🚀")
st.write("Đây là ứng dụng web đầu tiên của bạn.")

# 2. Thêm tính năng tương tác (Nhập tên)
ten_cua_ban = st.text_input("Hãy nhập tên của bạn vào đây:")
if ten_cua_ban:
    st.success(f"Xin chào {ten_cua_ban}! Chúc bạn code vui vẻ.")

# 3. Vẽ một biểu đồ đường đơn giản
st.subheader("Biểu đồ dữ liệu ngẫu nhiên")
# Tạo một bảng dữ liệu ngẫu nhiên gồm 20 hàng và 3 cột
du_lieu = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Cột A', 'Cột B', 'Cột C']
)
# Hiển thị biểu đồ
st.line_chart(du_lieu)