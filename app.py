import streamlit as st
from fpdf import FPDF
from io import BytesIO
import base64
import pandas as pd
import os

# ---------- Solvent Teknik Özellikleri ve Kimyasal Sınıflar ----------
solvent_ozellikleri = {
    "Etanol": {
        "sinif": "Alkoller",
        "kapali": "C2H5OH",
        "yogunluk": "0.789 g/cm³",
        "ph": "Nötr (7, saf)",
        "kaynama": "78.4 °C",
        "suda_karisabilirlik": "Tam",
        "max_su_orani": "Sınırsız",
        "uyumlu_solventler": ["Su", "Metanol", "IPA (İzopropanol)", "Aseton", "Toluen", "Etil Asetat"]
    },
    "Metanol": {
        "sinif": "Alkoller",
        "kapali": "CH3OH",
        "yogunluk": "0.792 g/cm³",
        "ph": "Nötr (7, saf)",
        "kaynama": "64.7 °C",
        "suda_karisabilirlik": "Tam",
        "max_su_orani": "Sınırsız",
        "uyumlu_solventler": ["Su", "Etanol", "IPA (İzopropanol)", "Aseton", "Etil Asetat"]
    },
    "IPA (İzopropanol)": {
        "sinif": "Alkoller",
        "kapali": "C3H8O",
        "yogunluk": "0.786 g/cm³",
        "ph": "Nötr",
        "kaynama": "82.6 °C",
        "suda_karisabilirlik": "Tam",
        "max_su_orani": "Sınırsız",
        "uyumlu_solventler": ["Su", "Etanol", "Aseton", "Toluen", "Etil Asetat"]
    },
    "Aseton": {
        "sinif": "Ketonlar",
        "kapali": "C3H6O",
        "yogunluk": "0.784 g/cm³",
        "ph": "Nötr",
        "kaynama": "56 °C",
        "suda_karisabilirlik": "Tam",
        "max_su_orani": "Sınırsız",
        "uyumlu_solventler": ["Su", "Etanol", "IPA (İzopropanol)", "Toluen", "Etil Asetat"]
    },
    "Toluen": {
        "sinif": "Aromatikler",
        "kapali": "C7H8",
        "yogunluk": "0.867 g/cm³",
        "ph": "Nötr",
        "kaynama": "110.6 °C",
        "suda_karisabilirlik": "Çok az",
        "max_su_orani": "%0.05",
        "uyumlu_solventler": ["Etanol", "Aseton", "Etil Asetat", "IPA (İzopropanol)"]
    },
    "Etil Asetat": {
        "sinif": "Esterler",
        "kapali": "C4H8O2",
        "yogunluk": "0.902 g/cm³",
        "ph": "Nötr",
        "kaynama": "77.1 °C",
        "suda_karisabilirlik": "8.3 g/100 ml",
        "max_su_orani": "%8.3",
        "uyumlu_solventler": ["Etanol", "IPA (İzopropanol)", "Aseton", "Toluen"]
    },
    "Su": {
        "sinif": "Diğer",
        "kapali": "H2O",
        "yogunluk": "1.000 g/cm³",
        "ph": "7 (saf)",
        "kaynama": "100 °C",
        "suda_karisabilirlik": "Kendisiyle tam",
        "max_su_orani": "100%",
        "uyumlu_solventler": ["Etanol", "IPA (İzopropanol)", "Aseton"]
    }
}

FONT_PATH = "DejaVuSans.ttf"

st.set_page_config(page_title="SolventLab | Gelişmiş Proses Asistanı", layout="wide")

st.markdown("""
<div style='background-color:#2C5E50;padding:10px;border-radius:8px'>
<h1 style='color:white;text-align:center'>GC Verisi ile Solvent Formülasyon ve Proses Asistanı</h1>
</div>
""", unsafe_allow_html=True)

st.info("GC analiz sonuçlarınızı girin, solvent özelliklerini inceleyin, teknik uyumluluğu ve karışabilirliği kontrol edin, PDF çıktısı alın.")

firma_adi = st.text_input("Firma Adı", value="Bilinmiyor")
maliyet = st.number_input("Tahmini Maliyet (TL)", min_value=0.0, step=0.1, value=0.0)

# ----------- Solvent Seçimi ve Genişletilmiş Özellikler -----------
solvent_options = list(solvent_ozellikleri.keys())
solvent_rows = []

satir_sayisi = st.number_input("Kaç farklı solvent kullanacaksınız?", min_value=1, max_value=10, value=4, step=1)

for i in range(int(satir_sayisi)):
    cols = st.columns([3, 2, 2, 2, 2, 2, 2])
    with cols[0]:
        # Solvent seçimi
        solvent_secim = st.selectbox(f"Solvent {i+1}", solvent_options, key=f"solvent_{i}")
        ozellik = solvent_ozellikleri[solvent_secim]
    with cols[1]:
        oran = st.number_input(f"{solvent_secim} Oranı (%)", min_value=0.0, max_value=100.0, step=0.1, value=0.0, key=f"oran_{i}")
    with cols[2]:
        st.markdown(f"Kapalı: **{ozellik['kapali']}**")
    with cols[3]:
        st.markdown(f"Yoğunluk: **{ozellik['yogunluk']}**")
    with cols[4]:
        st.markdown(f"pH: **{ozellik['ph']}**")
    with cols[5]:
        st.markdown(f"Kaynama: **{ozellik['kaynama']}**")
    with cols[6]:
        st.markdown(f"Suda Karışabilirlik: **{ozellik['suda_karisabilirlik']}**")

    solvent_rows.append({
        "Solvent": solvent_secim,
        "Kimyasal Sınıf": ozellik["sinif"],
        "Kapalı Formül": ozellik["kapali"],
        "Oran (%)": oran,
        "Yoğunluk": ozellik["yogunluk"],
        "pH": ozellik["ph"],
        "Kaynama Noktası": ozellik["kaynama"],
        "Suda Karışabilirlik": ozellik["suda_karisabilirlik"],
        "Max Su Oranı": ozellik["max_su_orani"],
        "Uyumlu Solventler": ", ".join(ozellik["uyumlu_solventler"])
    })

# ----------- Kullanıcı özel solvent ekleyebilir -----------
st.markdown("#### Listede olmayan yeni bir solvent ekleyin")
if "ozel_solventler" not in st.session_state:
    st.session_state["ozel_solventler"] = []

with st.expander("Yeni Solvent Ekle"):
    yeni_isim = st.text_input("Solvent Adı", key="ozel_isim")
    yeni_sinif = st.text_input("Kimyasal Sınıf", key="ozel_sinif")
    yeni_kapali = st.text_input("Kapalı Formül", key="ozel_kapali")
    yeni_yogunluk = st.text_input("Yoğunluk (g/cm³)", key="ozel_yogunluk")
    yeni_ph = st.text_input("pH", key="ozel_ph")
    yeni_kaynama = st.text_input("Kaynama Noktası (°C)", key="ozel_kaynama")
    yeni_sudakar = st.text_input("Suda Karışabilirlik", key="ozel_sudakar")
    yeni_maxsu = st.text_input("Max Su Oranı (%)", key="ozel_maxsu")
    yeni_uyumlu = st.text_area("Uyumlu Solventler (virgülle ayırınız)", key="ozel_uyumlu")
    if st.button("Solventi Ekle"):
        if yeni_isim:
            solvent_ozellikleri[yeni_isim] = {
                "sinif": yeni_sinif,
                "kapali": yeni_kapali,
                "yogunluk": yeni_yogunluk,
                "ph": yeni_ph,
                "kaynama": yeni_kaynama,
                "suda_karisabilirlik": yeni_sudakar,
                "max_su_orani": yeni_maxsu,
                "uyumlu_solventler": [s.strip() for s in yeni_uyumlu.split(",") if s.strip()]
            }
            st.session_state["ozel_solventler"].append(yeni_isim)
            st.success(f"{yeni_isim} başarıyla eklendi! Solvent listesinde kullanılabilir.")

# ----------- Tablo ve Grafik -----------
st.markdown("### Formülasyon Özeti")
df = pd.DataFrame(solvent_rows)
st.dataframe(df, hide_index=True)

st.markdown("### Solvent Dağılımı Grafiği")
if not df.empty:
    st.bar_chart(df.set_index("Solvent")["Oran (%)"])

# ----------- Teknik Uyum ve Karışabilirlik Kontrolü -----------
st.markdown("### Teknik Uyum ve Karışabilirlik Kontrolü")
uyari = []
toplam_oran = df["Oran (%)"].sum()

if toplam_oran > 100:
    uyari.append("Toplam oran 100%'den fazla! Lütfen oranları kontrol edin.")
elif toplam_oran < 100:
    uyari.append("Toplam oran 100%'den az. Formül eksik olabilir.")

for idx, row in df.iterrows():
    solvent = row["Solvent"]
    oran = row["Oran (%)"]
    max_su = solvent_ozellikleri[solvent]["max_su_orani"]
    suda_karisabilirlik = solvent_ozellikleri[solvent]["suda_karisabilirlik"]
    uyumlu_solventler = solvent_ozellikleri[solvent]["uyumlu_solventler"]
    # Su oranı ve karışma uyarısı
    if "Su" in df["Solvent"].values and solvent != "Su":
        if "Sınırsız" not in str(max_su) and "%" in str(max_su):
            try:
                max_su_float = float(str(max_su).replace("%","").replace(",","."))
                su_orani = df[df["Solvent"] == "Su"]["Oran (%)"].values[0]
                if su_orani > max_su_float:
                    uyari.append(f"{solvent} için maksimum su karışım oranı {max_su}. Formülünüzde {su_orani}% su var!")
            except:
                pass
        if suda_karisabilirlik == "Çok az" and df[df["Solvent"] == "Su"]["Oran (%)"].values[0] > 0:
            uyari.append(f"{solvent} suda çok az çözünür, yüksek oranda su eklendiğinde iki faz oluşabilir.")
    # Solvent uyumluluk kontrolü
    digerler = [x for x in df["Solvent"].values if x != solvent]
    for diger in digerler:
        if diger not in uyumlu_solventler:
            uyari.append(f"{solvent} ile {diger} genellikle karıştırılmaz veya dikkat gerektirir.")

if not uyari:
    uyari.append("Formülasyon teknik olarak uyumlu ve oranlar uygun görünüyor.")

for u in uyari:
    st.warning(u)

# ----------- PDF Rapor Fonksiyonu -----------
class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", '', 14)
        self.cell(0, 10, "SolventLab | Proses Asistan Raporu", ln=True, align="C")
        self.ln(4)

    def add_content(self, firma_adi, maliyet, df, uyari):
        self.set_font("DejaVu", '', 12)
        self.cell(0, 10, f"Firma: {firma_adi}", ln=True)
        self.cell(0, 10, f"Tahmini Maliyet: {maliyet} TL", ln=True)
        self.ln(3)
        self.cell(0, 10, "Formülasyon ve Teknik Özellikler:", ln=True)
        for idx, row in df.iterrows():
            self.multi_cell(0, 10, f"- {row['Solvent']} ({row['Kimyasal Sınıf']}, {row['Kapalı Formül']}): {row['Oran (%)']}%\n"
                                   f"  Yoğunluk: {row['Yoğunluk']}, pH: {row['pH']}, Kaynama: {row['Kaynama Noktası']}, "
                                   f"Suda Karışabilirlik: {row['Suda Karışabilirlik']}, Max Su Oranı: {row['Max Su Oranı']}\n"
                                   f"  Uyumlu Solventler: {row['Uyumlu Solventler']}")
        self.ln(3)
        self.cell(0, 10, "Teknik Uyum ve Uyarılar:", ln=True)
        for u in uyari:
            self.multi_cell(0, 10, f"- {u}")

if not os.path.isfile(FONT_PATH):
    st.error(f"{FONT_PATH} dosyası bulunamadı. Lütfen uygulama dizinine ekleyin.")
else:
    if st.button("📄 PDF Oluştur"):
        pdf = PDF()
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.add_page()
        pdf.add_content(firma_adi, maliyet, df, uyari)
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        buffer = BytesIO(pdf_bytes)
        b64_pdf = base64.b64encode(buffer.read()).decode("utf-8")
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="formulasyon_raporu.pdf">📥 PDF dosyasını indir</a>'
        st.markdown(href, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 SolventLab | Geliştirici: Elrazeuxx")
