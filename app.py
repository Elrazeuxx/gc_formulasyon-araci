import streamlit as st
import pandas as pd
import os
from datetime import datetime
import sqlite3
import logging

st.set_page_config(page_title="GC Formülasyon Aracı", layout="centered")

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
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(30,34,40,0.97);
        color: #f5f6fa !important;
    }}
    .st-cq, .st-bx, .st-ag, .st-cc {{
        background: rgba(44, 62, 80, 0.93) !important;
        color: #f5f6fa !important;
        border-radius: 12px;
        border: 1px solid #353b48;
    }}
    h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: #f5f6fa !important;
    }}
    .highlight, .kirmizi, .stMarkdown strong {{
        color: #ff4b5c !important;
        font-weight: bold !important;
    }}
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
    .element-container .stMetric-value, .element-container .stMetric-label {{
        color: #f5f6fa !important;
    }}
    a {{
        color: #40c9ff !important;
    }}
    .stButton > button {{
        color: #fff !important;
        background-color: #1976d2 !important;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1.5em;
        font-weight: bold;
        transition: background 0.2s;
        box-shadow: 0 2px 8px #0002;
    }}
    .stButton > button:hover {{
        color: #222 !important;
        background: #90caf9 !important;
    }}
    .stButton + div .highlight, .stButton + div .kirmizi {{
        color: #ff4b5c !important;
        font-weight: bold !important;
    }}
    .stFileUploader label, .stFileUploader span {{
        color: #f5f6fa !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

logging.basicConfig(filename="log_kaydi.log", level=logging.INFO, format='%(asctime)s - %(message)s')

language = st.sidebar.selectbox("🌍 Dil / Language", ["Türkçe", "English"])
def _(tr, en): return tr if language == "Türkçe" else en

st.image("https://i.imgur.com/4dVjR8r.png", width=100)
st.title(_("🔬 GC Formülasyon Aracı", "🔬 GC Formulation Tool"))
st.caption(_("Kimya ve endüstriyel solvent yönetiminde akıllı asistan.", "Smart assistant for chemical and industrial solvent management."))

with st.sidebar.expander(_("⚙️ Ayarlar ve Geri Bildirim", "⚙️ Settings & Feedback")):
    tema = st.radio(_("Tema Renk Seçimi:", "Select Theme Color:"), ["Varsayılan", "Açık", "Koyu"])
    geri_bildirim = st.text_area(_("Görüş ve önerilerinizi yazabilirsiniz:", "You can share feedback or suggestions:"))
    if st.button(_("Gönder", "Submit")):
        try:
            conn = sqlite3.connect("kullanici_geri_bildirim.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarih TEXT,
                    icerik TEXT
                )
            """)
            cursor.execute(
                "INSERT INTO feedback (tarih, icerik) VALUES (?, ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M"), geri_bildirim)
            )
            conn.commit()
            conn.close()
            st.success(_("Teşekkür ederiz! Geri bildiriminiz alınmıştır.", "Thank you! Your feedback has been submitted."))
            logging.info("Yeni geri bildirim kaydedildi.")
        except Exception as e:
            st.error(_("Bir hata oluştu.", "An error occurred."))
            logging.error(f"Geri bildirim hatası: {e}")

with st.sidebar.expander(_("📊 Kullanım İstatistikleri", "📊 Usage Statistics")):
    conn = sqlite3.connect("kullanici_geri_bildirim.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            icerik TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM feedback")
    toplam_geri_bildirim = cursor.fetchone()[0]
    st.metric(_("Gelen Geri Bildirim Sayısı", "Total Feedbacks"), toplam_geri_bildirim)
    cursor.execute("SELECT tarih FROM feedback ORDER BY id DESC LIMIT 1")
    son = cursor.fetchone()
    st.metric(_("Son Bildirim Tarihi", "Last Feedback"), son[0] if son else "-")
    if st.button(_("📥 Veritabanını CSV Olarak İndir", "📥 Download Feedback DB as CSV")):
        df_feedback = pd.read_sql_query("SELECT * FROM feedback", conn)
        csv_yolu = "feedback_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv"
        df_feedback.to_csv(csv_yolu, index=False)
        st.success(_("CSV dosyası oluşturuldu: ", "CSV file created: ") + csv_yolu)
    conn.close()

st.sidebar.markdown("---")
st.sidebar.info("🛠 Versiyon: 1.0.0\n📅 Güncelleme: 2025-05-25\n📌 Koyu Tema, okunaklı bildirimler, GC modülü ve Solvent paneli")

KATEGORILER = {
    "Alkoller": "data/alkoller.csv",
    "Ketonlar": "data/ketonlar.csv",
    "Asetatlar": "data/asetatlar.csv",
    "Asitler": "data/asitler.csv",
    "Bazlar": "data/bazlar.csv",
    "Aldehitler": "data/aldehitler.csv",
    "Aromatikler": "data/aromatikler.csv",
    "Glikoller": "data/glikoller.csv",
    "Aminler": "data/aminler.csv",
    "Esterler": "data/esterler.csv",
    "Eterler": "data/eterler.csv",
    "Klorlu Solventler": "data/klorlu_solventler.csv",
    "Hidrokarbonlar": "data/hidrokarbonlar.csv",
    "Polar Aprotik Solventler": "data/polar_aprotik_solventler.csv",
    "Biyolojik Solventler": "data/biyolojik_solventler.csv",
    "Yüksek Kaynama Noktalı Solventler": "data/yuksek_kaynama_solventler.csv",
    "Metal Temizleme Solventleri": "data/metal_temizleme_solventleri.csv",
    "Reaktif Solventler": "data/reaktif_solventler.csv",
    "Elektronik Sınıf Solventler": "data/elektronik_sinif_solventler.csv"
}

MODUL = st.sidebar.radio(
    _("Modül Seç", "Select Module"),
    (_("GC Formülasyon Karşılaştırma", "GC Formulation Comparison"), _("Solvent Bilgi Paneli", "Solvent Info Panel"))
)

if MODUL == _("GC Formülasyon Karşılaştırma", "GC Formulation Comparison"):
    solventler = []
    for csv_path in KATEGORILER.values():
        if os.path.isfile(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if "İsim" in df.columns:
                    solventler += df["İsim"].dropna().tolist()
            except Exception:
                pass
    solventler = sorted(list(set(solventler + [
        "Etanol", "IPA", "N-Propanol", "Etil Asetat", "PM", "MEK", "Bütanol", "Toluen", "Ksilen",
        "Aseton", "Metil Asetat", "Butil Asetat", "Etil Laktat", "DPM", "Texanol", "Metanol", "Benzin", "Heptan",
        "Dietil Eter", "Propilen Karbonat", "Su", "NMP", "DMF", "Tetrahydrofuran"
    ])))

    FORMULASYONLAR = {
        "Çözücü": {
            "Etanol": 20, "IPA": 20, "Etil Asetat": 20, "MEK": 15, "PM": 15, "DPM": 10
        },
        "Tiner": {
            "Toluen": 30, "Ksilen": 30, "IPA": 10, "Etanol": 10, "MEK": 10, "Etil Asetat": 10
        },
        "Matbaa Solventi": {
            "IPA": 40, "Etanol": 25, "PM": 15, "DPM": 10, "MEK": 5, "Etil Asetat": 5
        },
        "Pas Sökücü": {
            "IPA": 10, "Etanol": 15, "Etil Asetat": 10, "MEK": 10, "DPM": 15, "Ksilen": 20, "Toluen": 20
        },
        "Metal Temizleyici": {
            "IPA": 20, "Etanol": 10, "PM": 30, "DPM": 25, "MEK": 10, "Etil Asetat": 5
        },
        "Cam Temizleyici": {
            "IPA": 20, "Etanol": 10, "Su": 65, "DPM": 3, "Etil Asetat": 2
        },
        "Mürekkep Çözücü": {
            "Etanol": 25, "IPA": 15, "DPM": 15, "Etil Asetat": 20, "MEK": 10, "Toluen": 10, "Ksilen": 5
        },
        "Yağ Sökücü": {
            "IPA": 15, "Etanol": 10, "PM": 30, "DPM": 25, "MEK": 10, "Etil Asetat": 5, "Heptan": 5
        },
        "Universal Temizleyici": {
            "IPA": 10, "Etanol": 10, "Su": 70, "DPM": 5, "Etil Asetat": 5
        },
        "Hızlı Kuruyan Tiner": {
            "Aseton": 30, "IPA": 20, "MEK": 20, "Etil Asetat": 15, "Toluen": 10, "Ksilen": 5
        }
    }

    st.header(_("GC Analizine Göre Formülasyon Karşılaştırma", "Formulation Comparison by GC Analysis"))
    kullanim = st.selectbox(_("Formülasyon Tipi", "Formulation Type"), list(FORMULASYONLAR.keys()))
    target_formulation = FORMULASYONLAR[kullanim]
    st.markdown(_("Kendi GC analiz verinizi girin ve hedef formül ile karşılaştırın.", "Enter your GC analysis data and compare with the target formulation."))

    st.subheader(_("GC Pik Görseli (Varsa)", "GC Chromatogram Image (Optional)"))
    uploaded_file = st.file_uploader(_("GC analiz görüntüsü yükle (isteğe bağlı)", "Upload GC analysis image (optional)"), type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.image(uploaded_file, caption=_("GC Analiz Görseli", "GC Chromatogram Image"), use_column_width=True)

    st.subheader(_("GC Analiz Verisi Girişi", "GC Analysis Data Input"))
    gc_data = {}
    cols = st.columns(3)
    for i, bilesen in enumerate(target_formulation):
        with cols[i % 3]:
            oran = st.number_input(f"{bilesen} (%)", min_value=0.0, max_value=100.0, step=0.1, key="GC_" + bilesen)
            gc_data[bilesen] = oran

    total_percent = sum(gc_data.values())
    if total_percent > 100:
        st.warning(_("Uyarı: Toplam oran %100'ü aştı! (Şu an: %{:.2f})", "Warning: Total ratio exceeds 100%! (Now: %{:.2f})").format(total_percent))
    elif total_percent < 99:
        st.warning(_("Uyarı: Toplam oran %100'den düşük. (Şu an: %{:.2f})", "Warning: Total ratio is less than 100%. (Now: %{:.2f})").format(total_percent))

    vp_values = {
        "Etanol": 59, "IPA": 33, "N-Propanol": 21, "Etil Asetat": 73, "MEK": 70,
        "PM": 5, "DPM": *

