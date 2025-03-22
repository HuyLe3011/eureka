import streamlit as st
import base64

st.set_page_config(page_title="Applying deep learning to portfolio optimization in the Vietnamese stock market",page_icon="📊")

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

st.logo("big_logo.png",size='large',icon_image="small_logo.png")
st.image("banner.png")

st.markdown('<h1 class="custom-title">Applying deep learning to portfolio optimization in the Vietnamese stock market.".</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #30475E;">Select the data input method you want.</p>', unsafe_allow_html=True)

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

if st.button("Import .csv file", use_container_width=True,icon="📁"):
    st.switch_page("pages/1_Choose_csv.py")
if st.button("Enter the data collection period (HOSE only supported)", use_container_width=True,icon="🗓️"):
    st.switch_page("pages/2_Choose_date.py")
