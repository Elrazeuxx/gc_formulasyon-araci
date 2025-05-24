import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
import sqlite3
import logging
import matplotlib.pyplot as plt

# --- LOG dosyası ---
logging.basicConfig(filename="log_kaydi.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# --- Dil Ayarı ---
language = st.sidebar.selectbox("🌍 Dil / Language", ["Türkçe", "English"])

def _(tr, en):
    try:
        return tr if language == "Türkçe" else en
    except:
        return en

# --- Tema Desteği ---
tema = st.sidebar.radio(_("Tema Renk Seçimi:", "Select Theme Color:"), ["Varsayılan", "Açık", "Koyu"])
if tema == "Açık":
    st.markdown(
        """
        <style>
            .main {background-color: #f7fafc;}
        </style>
        """,
        unsafe_allow_html=True,
    )
elif tema == "Koyu":
    st.markdown(
        """
        <style>
            .main {background-color: #222831; color: #f7fafc;}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_title=_("GC Formülasyon Aracı", "GC Formulation Tool"), layout="centered")
st.image("https://i.imgur.com/4dVjR8r.png", width=100)
st.title(_("📘 GC Formülasyon Aracı", "📘 GC Formulation Tool"))
st.caption(_("Gelişmiş solvent veri yönetimi ve formülasyon asistanı.", "Advanced solvent data management and formulation assistant."))

# --- Geri Bildirim / Loglama / İstatistik ---
with st.sidebar.expander(_("⚙️ Ayarlar ve Geri Bildirim", "⚙️ Settings & Feedback")):
    geri_bildirim = st.text_area(_("Görüş ve önerilerinizi yazabilirsiniz:", "You can share feedback or suggestions:"))
    if st.button(_("Gönder", "Submit")):
        try:
            conn = sqlite3.connect("kullanici_geri_bildirim.db")
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, tarih TEXT, icerik TEXT)")
            cursor.execute("INSERT INTO feedback (tarih, icerik) VALUES (?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M"), geri_bildirim))
            conn.commit()
            conn.close()
            st.success(_("Teşekkür ederiz! Geri bildiriminiz alınmıştır.", "Thank you! Your feedback has been submitted."))
            logging.info("Yeni geri bildirim kaydedildi.")
        except Exception as e:
            st.error(_("Bir hata oluştu.", "An error occurred."))
            logging.error(f"Geri bildirim hatası: {e}")

    if st.button(_("Geri Bildirimleri Temizle", "Clear Feedback")):
        try:
            conn = sqlite3.connect("kullanici_geri_bildirim.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback")
            conn.commit()
            conn.close()
            st.success(_("Tüm geri bildirimler temizlendi.", "All feedback cleared."))
        except Exception as e:
            st.error(_("Temizleme hatası: ", "Cleanup error: ") + str(e))

with st.sidebar.expander(_("📊 Kullanım İstatistikleri", "📊 Usage Statistics")):
    try:
        conn = sqlite3.connect("kullanici_geri_bildirim.db")
        df_fb = pd.read_sql_query("SELECT * FROM feedback", conn)
        st.metric(_("Geri Bildirim Sayısı", "Feedback Count"), len(df_fb))
        if not df_fb.empty:
            st.metric(_("Son Bildirim", "Last Feedback"), df_fb.iloc[-1]['tarih'])
        if st.button(_("CSV Olarak İndir", "Download as CSV"), key="feedback_csv"):
            path = "feedback_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv"
            df_fb.to_csv(path, index=False)
            st.success(_("İndirildi: ", "Downloaded: ") + path)
        conn.close()
    except Exception as e:
        st.info(_("Henüz kayıt yok.", "No records yet."))

# --- Versiyon Bilgisi ---
st.sidebar.markdown("---")
st.sidebar.info("🛠 Versiyon: 1.1.0\n📅 Güncelleme: 2025-05-24\n📌 Özellikler: GC tahmini, reçete, çoklu dil, veri kaydı, grafik, silme, tema")

# --- Uygulama Durumları ---
if "receteler" not in st.session_state:
    st.session_state.receteler = {}

if "gc_tahminleri" not in st.session_state:
    st.session_state.gc_tahminleri = pd.DataFrame()

# --- Solvent Kategorileri ---
KATEGORILER = {
    "Alkoller": "data/alkoller.csv",
    "Ketonlar": "data/ketonlar.csv",
    "Asetatlar": "data/asetatlar.csv",
    "Aldehitler": "data/aldehitler.csv",
    "Aromatikler": "data/aromatikler.csv",
    "Esterler": "data/esterler.csv",
    "Glikoller": "data/glikoller.csv",
    "Hidrokarbonlar": "data/hidrokarbonlar.csv",
    "Klorlu Solventler": "data/klorlu_solventler.csv",
    "Polar Aprotik Solventler": "data/polar_aprotik_solventler.csv",
    "Biyolojik Solventler": "data/biyolojik_solventler.csv"
}

kategori = st.selectbox("🧪 " + _("Solvent/Sınıf Seç", "Select Solvent/Class"), list(KATEGORILER.keys()))

# Dosya okuma güvenliği
try:
    df = pd.read_csv(KATEGORILER[kategori])
except FileNotFoundError:
    st.error(_("Veri dosyası bulunamadı. Lütfen 'data' klasörünü ve ilgili CSV dosyasını kontrol edin.", 
               "Data file not found. Please check the 'data' folder and the relevant CSV file."))
    st.stop()
except Exception as e:
    st.error(_("Veri dosyası okunamadı: ", "Failed to read data file: ") + str(e))
    st.stop()

if not df.empty and "İsim" in df.columns:
    st.subheader(f"{kategori} - " + _("Liste", "List"))
    st.dataframe(df, use_container_width=True)
    secili = st.selectbox("🔍 " + _("Solvent Seç", "Select Solvent"), df["İsim"].dropna().tolist())
    bilgi = df[df["İsim"] == secili].iloc[0] if not df[df["İsim"] == secili].empty else None
    if bilgi is not None:
        st.markdown(f"""
        **Kapalı Formül:** {bilgi.get('Kapalı Formül','-')}  
        **Kaynama Noktası:** {bilgi.get('Kaynama Noktası (°C)','-')} °C  
        **Yoğunluk:** {bilgi.get('Yoğunluk (g/cm³)','-')} g/cm³  
        **pH:** {bilgi.get('pH', '-')}  
        **Çözünürlük:** {bilgi.get('Suda Çözünürlük (%)','-')} %  
        **Max Su Oranı:** {bilgi.get('Max Su Oranı (%)', '-')}  
        **Uyumlu Solventler:** {bilgi.get('Uyumlu Solventler', '-')}  
        **Kullanım Alanları:** {bilgi.get('Kullanım Alanları','-')}  
        **Toksisite:** {bilgi.get('Toksisite / Güvenlik','-')}  
        """)

        miktar = st.number_input("📦 " + _("Miktar (kg)", "Amount (kg)"), min_value=0.0, step=0.1)
        fiyat = st.number_input("💰 " + _("Fiyat (TL/kg)", "Price (TL/kg)"), min_value=0.0, step=0.1)
        if miktar > 0 and fiyat > 0:
            toplam = miktar * fiyat
            st.success(_("Toplam Maliyet", "Total Cost") + f": {toplam:.2f} TL")

        if st.button("💾 " + _("Reçete Kaydet", "Save Recipe")):
            ad = f"{secili}_{datetime.now().strftime('%H%M%S')}"
            st.session_state.receteler[ad] = {
                "İsim": secili, "Miktar": miktar, "Fiyat": fiyat, "Toplam": toplam if miktar > 0 and fiyat > 0 else 0
            }
            st.success(_("Reçete kaydedildi", "Recipe saved"))
else:
    st.warning(_("Bu kategori için veri bulunamadı.", "No data for this category."))

# --- Reçeteler ---
if st.session_state.receteler:
    st.markdown("### 📄 " + _("Kayıtlı Reçeteler", "Saved Recipes"))
    df_rec = pd.DataFrame.from_dict(st.session_state.receteler, orient="index")
    st.dataframe(df_rec)

    # Reçete silme özelliği
    silinecek = st.multiselect(
        _("Silmek istediğiniz reçeteleri seçin:", "Select recipes to delete:"),
        options=list(st.session_state.receteler.keys()),
    )
    if st.button(_("Seçilenleri Sil", "Delete Selected")) and silinecek:
        for key in silinecek:
            st.session_state.receteler.pop(key, None)
        st.success(_("Seçilen reçeteler silindi.", "Selected recipes deleted."))

    # PDF çıktısı
    if st.button("⬇️ PDF Oluştur"):
        pdf = FPDF()
        pdf.add_page()
        try:
            pdf.set_font("Arial", size=12)
        except:
            pdf.set_font("helvetica", size=12)
        for ad, veri in st.session_state.receteler.items():
            metin = f"{ad}: {veri['İsim']} - {veri['Miktar']} kg x {veri['Fiyat']} = {veri['Toplam']} TL"
            if len(metin) > 90:
                for i in range(0, len(metin), 90):
                    pdf.cell(200, 10, txt=metin[i:i+90], ln=True)
            else:
                pdf.cell(200, 10, txt=metin, ln=True)
        path = "recete_" + datetime.now().strftime("%Y%m%d_%H%M") + ".pdf"
        pdf.output(path)
        st.success("PDF oluşturuldu: " + path)

    # CSV çıktısı
    if st.button("⬇️ CSV Olarak İndir"):
        path = "receteler_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv"
        df_rec.to_csv(path, index=True)
        st.success("CSV indirildi: " + path)

# --- GC Tahmini ---
st.markdown("### 🧬 " + _("GC Pik Listesi ile Tahmin", "GC Peak-Based Estimation"))
pikler = st.text_area("🧪 " + _("Kaynama Noktaları (virgülle)", "Boiling Points (comma-separated)"))
tahminler = []

if st.button("🔍 " + _("Tahmin Et", "Estimate")):
    try:
        piks = []
        for p in pikler.split(","):
            p = p.strip()
            if p:
                try:
                    piks.append(float(p))
                except ValueError:
                    st.warning(f"Geçersiz sayı: {p}")
        if not piks:
            st.warning(_("En az bir geçerli değer giriniz.", "Please enter at least one valid value."))
            st.stop()
        tum = pd.concat([pd.read_csv(v) for v in KATEGORILER.values()], ignore_index=True)
        tum["Kaynama Noktası (°C)"] = pd.to_numeric(tum["Kaynama Noktası (°C)"], errors='coerce')
        for p in piks:
            sec = tum.iloc[(tum["Kaynama Noktası (°C)"].sub(p)).abs().argsort()[:1]]
            if not sec.empty:
                tahminler.append(sec.iloc[0])
        if not tahminler:
            st.error(_("Hiçbir tahmin bulunamadı.", "No prediction found."))
        else:
            df_tahmin = pd.DataFrame(tahminler)
            st.session_state.gc_tahminleri = df_tahmin
            st.dataframe(df_tahmin)

            # GC Pik Tahmini Grafik
            fig, ax = plt.subplots()
            ax.bar(df_tahmin["İsim"], df_tahmin["Kaynama Noktası (°C)"])
            ax.set_ylabel(_("Kaynama Noktası (°C)", "Boiling Point (°C)"))
            ax.set_xlabel(_("Solvent", "Solvent"))
            ax.set_title(_("Tahmin Edilen Solventler", "Estimated Solvents"))
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Tahmin Hatası: {e}")

if isinstance(st.session_state.gc_tahminleri, pd.DataFrame) and not st.session_state.gc_tahminleri.empty:
    st.markdown("### 📌 " + _("Tahmini Karışımı Reçete Olarak Kaydet", "Save Predicted Mix as Recipe"))
    miktar_gc = st.number_input("🔢 " + _("Miktar (kg)", "Amount (kg)"), min_value=0.0, step=0.1, key="gc_miktar")
    fiyat_gc = st.number_input("💸 " + _("Ortalama Fiyat (TL/kg)", "Average Price (TL/kg)"), min_value=0.0, step=0.1, key="gc_fiyat")
    if miktar_gc > 0 and fiyat_gc > 0:
        toplam = miktar_gc * fiyat_gc
        ad = "GC_Tahmini_" + datetime.now().strftime("%H%M%S")
        st.session_state.receteler[ad] = {"İsim": "GC Karışımı", "Miktar": miktar_gc, "Fiyat": fiyat_gc, "Toplam": toplam}
        st.success(_("GC reçetesi eklendi.", "GC recipe added."))
