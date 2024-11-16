import streamlit as st
import base64

st.set_page_config(page_title="Ứng dụng LSTM cho danh mục đầu tư",page_icon="📊")

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
        background-color: rgba(255, 255, 255, 0.7); /* Điều chỉnh độ mờ ở đây */
        background-blend-mode: overlay;
    }}
    .custom-title {{
        color: #F05454;
    }}
    .stMarkdown, .stText {{
        color: #30475E !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

add_bg_from_local('background.png')

st.image("big_logo.png")
st.image("banner.png")

st.markdown('<h1 class="custom-title">App phân bổ danh mục đầu tư theo chỉ báo kĩ thuật</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #30475E;">Chọn phương thức nhập dữ liệu mà bạn muốn</p>', unsafe_allow_html=True)

custom_css = """
<style>
    html, body, [class*="css"] {
        font-size: 20px;
        color: #30475E;
    }
    .stButton > button {
        font-weight: bold !important;
        font-size: 20px !important;
        color: #30475E !important;
        border: 2px solid #30475E !important;
        border-radius: 5px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: #30475E !important;
        color: white !important;
    }
}
</style>
"""

# Áp dụng CSS tùy chỉnh
st.markdown(custom_css, unsafe_allow_html=True)

if st.button("Nhập file .csv", use_container_width=True,icon="📁"):
    st.switch_page("pages/1_Choose_csv.py")
if st.button("Nhập khoảng thời gian thu thập dữ liệu (chỉ hỗ trợ HOSE)", use_container_width=True,icon="🗓️"):
    st.switch_page("pages/2_Choose_date.py")
