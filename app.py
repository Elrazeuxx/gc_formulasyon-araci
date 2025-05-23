import streamlit as st
import pandas as pd
import os

# --- Streamlit Sayfa Ayarları ---
st.set_page_config(page_title="GC Formülasyon Aracı", layout="wide")
st.title("Solvent Kategorileri ile GC Formülasyon Aracı")

# --- Kategorileri Tanımla ---
KATEGORILER = {
    "Alkoller": "data/alkoller.csv",
    "Ketonlar": "data/ketonlar.csv",
    "Asetatlar": "data/asetatlar.csv",
    "Asitler": "data/asitler.csv",
    "Bazlar": "data/bazlar.csv",
    "Aldehitler": "data/aldehitler.csv",
    "Aromatikler": "data/aromatikler.csv"
    "Glikoller": "veri/glikoller.csv"

}
# --- Kategori Seçimi ---
kategori = st.sidebar.selectbox("Solvent/Sınıf Grubu Seçin", list(KATEGORILER.keys()))
csv_yolu = KATEGORILER[kategori]

# --- CSV Dosyası Var mı? ---
if not os.path.isfile(csv_yolu):
    st.error(f"{kategori} için '{csv_yolu}' dosyası bulunamadı. Lütfen '{csv_yolu}' dosyasını oluşturun!")
    st.stop()

# --- CSV'den Veri Oku ---
try:
    df = pd.read_csv(csv_yolu)
except Exception as e:
    st.error(f"CSV okunurken hata oluştu: {e}")
    st.stop()

st.subheader(f"{kategori} Listesi")
st.dataframe(df, use_container_width=True)

# --- Solvent Seçimi ve Özellik Gösterimi ---
if len(df) == 0:
    st.warning(f"{kategori} için veri bulunamadı.")
else:
    secili = st.selectbox(f"{kategori} Seç", df["İsim"].tolist())
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

# --- Gelişim İçin Ek Özellik Yeri ---
# Burada teknik uyum, PDF çıktısı, dosya yükleme gibi modülleri ileride kolayca ekleyebilirsin.
# Örn: if st.button("PDF Raporu Oluştur"): ... vs.

st.info("Yeni bir kategori eklemek için, sadece yeni bir CSV dosyası oluşturup KATEGORILER sözlüğüne eklemen yeterli!")

# -- ÖRNEK CSV BAŞLIĞI VE SATIRI (Yardımcı Not Olarak) --
st.markdown("""
---
**Örnek CSV Başlığı:**

`İsim,Kapalı Formül,Yoğunluk (g/cm³),pH,Kaynama Noktası (°C),Suda Çözünürlük (%),Max Su Oranı (%),Uyumlu Solventler,Kullanım Alanları,Toksisite / Güvenlik`

**Örnek Satır:**

`Etanol,C2H5OH,0.789,Nötr,78.4,100,Sınırsız,Su;Metanol;IPA,Temizlik;Laboratuvar,Düşük`
""")
