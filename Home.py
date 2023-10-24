import streamlit as st
from PIL import Image

st.header("Sabin F1")

image = Image.open('./images/ALO.png')

st.image(image)
