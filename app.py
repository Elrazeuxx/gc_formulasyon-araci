import streamlit as st
import pandas as pd
import os
from datetime import datetime
import sqlite3
import logging

st.set_page_config(page_title="GC Formülasyon Aracı", layout="centered")

# Koyu temalı laboratuvar görseli ve renkler
background_image = "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=1500&q=80"
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #23272b 0%, #2c3e50 100%), url("{background_image}");
        background-blend-mode: darken;
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: #f5f6fa !important;
    }}
    /* Sidebar daha koyu ve yazılar beyaz */
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(30,34,40,0.97);
        color: #f5f6fa !important;
    }}
    /* Kutular ve kartlar koyu gri */
    .st-cq, .st-bx, .st-ag, .st-cc {{
        background: rgba(44, 62, 80, 0.93) !important;
        color: #f5f6fa !important;
        border-radius: 12px;
        border: 1px solid #353b48;
    }}
    /* Başlıklar açık gri-beyaz */
    h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: #f5f6fa !important;
    }}
    /* Vurgular kırmızı ve kalın */
    .highlight, .kirmizi, .stMarkdown strong {{
        color: #ff4b5c !important;
        font-weight: bold !important;
    }}
    /* Bildirim kutuları kontrastlı ve parlak metinli */
    .stAlert-success {{
        background: #263238 !important;
        color: #00e676 !important;
        border-left: 8px solid #00e676 !important;
    }}
    .stAlert-warning {{
        background: #363636 !important;
        color: #ffd600 !important;
        border-left: 8px solid #ffd600 !important;
    }}
    .stAlert-info {{
        background: #263238 !important;
        color: #29b6f6 !important;
        border-left: 8px solid #29b6f6 !important;
    }}
    .stAlert-error {{
        background: #2c2c2c !important;
        color: #ff1744 !important;
        border-left: 8px solid #ff1744 !important;
    }}
    /* st.metric yazılarını açık yap */
    .element-container .stMetric-value, .element-container .stMetric-label {{
        color: #f5f6fa !important;
    }}
    a {{
        color: #40c9ff !important;
    }}
    /* Butonlar: Arka plan mavi, yazı beyaz, hover'da açık mavi */
    .stButton > button {{
        color: #fff !important;
        background-color: #1976d2 !important;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1.5em;
        font*

