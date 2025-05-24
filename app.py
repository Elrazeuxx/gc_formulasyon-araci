import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
from datetime import datetime
import sqlite3
import logging

# Sayfa ayarı (ilk Streamlit fonksiyonu olmalı)
st.set_page_config(page_title="GC Formülasyon Aracı", layout="centered")

# --- LOG dosyası ---
logging.basicConfig(filename="log_kaydi.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# --- Dil Ayarı ---
language = st.sidebar.selectbox("🌍 Dil / Language", ["Türkçe", "English"])

def _(tr, en):
    return tr if language == "Türkçe" else en

st.image("https://i.imgur.com/4dVjR8r.png", width=100)
st.title(_("📘 GC Formülasyon Aracı", "📘 GC Formulation Tool"))
st.caption(_("Gelişmiş solvent veri yönetimi ve formülasyon asistanı.", "Advanced solvent data management and formulation assistant."))

# --- Admin Paneli ---
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

# --- Kullanım İstatistikleri ---
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

# --- Versiyon Bilgisi ---
st.sidebar.markdown("---")
st.sidebar.info("🛠 Versiyon: 1.0.0\n📅 Güncelleme: 2025-05-24\n📌 Yeni: Veritabanı, Geri Bildirim, Loglama, Çoklu Dil Desteği")

# --- Solvent & GC Bölümü ---
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

kategori = st.sidebar.selectbox(_("Solvent/Sınıf Grubu Seçin", "Select Solvent/Class Group"), list(KATEGORILER.keys()))
csv_yolu = KATEGORILER[kategori]

if not os.path.isfile(csv_yolu):
    st.error(f"{kategori} için '{csv_yolu}' dosyası bulunamadı. Lütfen '{csv_yolu}' dosyasını oluşturun!")
    st.stop()

try:
    df = pd.read_csv(csv_yolu)
except Exception as e:
    st.error(_("CSV okunurken hata oluştu: ", "Error while reading CSV: ") + str(e))
    st.stop()

st.subheader(_(f"{kategori} Listesi", f"{kategori} List"))
st.dataframe(df, use_container_width=True)

gerekli_sutunlar = [
    "İsim", "Kapalı Formül", "Kaynama Noktası (°C)", "Yoğunluk (g/cm³)", "pH",
    "Suda Çözünürlük (%)", "Max Su Oranı (%)", "Uyumlu Solventler",
    "Kullanım Alanları", "Toksisite / Güvenlik"
]
eksik = [s for s in gerekli_sutunlar if s not in df.columns]
if eksik:
    st.error(_("CSV'de eksik sütunlar var: ", "Missing columns in CSV: ") + ", ".join(eksik))
elif len(df) == 0:
    st.warning(_(f"{kategori} için veri bulunamadı.", f"No data for {kategori}."))
else:
    isimler = df["İsim"].dropna().tolist()
    if not isimler:
        st.warning(_("Seçilebilecek isim yok.", "No names to select."))
    else:
        secili = st.selectbox(_(f"{kategori} Seç", f"Select {kategori}"), isimler)
        bilgi = df[df["İsim"] == secili].iloc[0]
        st.markdown(f"""
**Kapalı Formül:** {bilgi['Kapalı Formül']}  
**Kaynama Noktası:** {bilgi['Kaynama Noktası (°C)']} °C  
**Yoğunluk:** {bilgi['Yoğunluk (g/cm³)']} g/cm³  
**pH:** {bilgi['pH']}  
**Çözünürlük:** {bilgi['Suda Çözünürlük (%)']} %  
**Max Su Oranı:** {bilgi['Max Su Oranı (%)']}  
**Uyumlu Solventler:** {bilgi['Uyumlu Solventler']}  
**Kullanım Alanları:** {bilgi['Kullanım Alanları']}  
**Toksisite:** {bilgi['Toksisite / Güvenlik']}  
""")

st.info(_("Yeni bir kategori eklemek için, sadece yeni bir CSV dosyası oluşturup KATEGORILER sözlüğüne eklemen yeterli!",
         "To add a new category, simply create a new CSV file and add it to the KATEGORILER dictionary!"))

st.markdown("""
---
**Örnek CSV Başlığı:**

`İsim,Kapalı Formül,Yoğunluk (g/cm³),pH,Kaynama Noktası (°C),Suda Çözünürlük (%),Max Su Oranı (%),Uyumlu Solventler,Kullanım Alanları,Toksisite / Güvenlik`

**Örnek Satır:**

`Etanol,C2H5OH,0.789,Nötr,78.4,100,Sınırsız,Su;Metanol;IPA,Temizlik;Laboratuvar,Düşük`
""")
