import streamlit as st
from fpdf import FPDF
from io import BytesIO
import base64
import pandas as pd
import os

st.set_page_config(page_title="SolventLab | Proses Asistanı", layout="wide")

# Başlık ve açıklama
st.markdown("""
<div style='background-color:#2C5E50;padding:10px;border-radius:8px'>
<h1 style='color:white;text-align:center'>GC Verisi ile Solvent Formülasyon ve Proses Asistanı</h1>
</div>
""", unsafe_allow_html=True)

st.info("GC analiz sonuçlarınızı girin ve solvent formülasyonunuzu oluşturun. PDF çıktısı alabilirsiniz.")

# Kullanıcıdan veri al
st.subheader("GC Analiz Sonuçlarınızı Girin")
firma_adi = st.text_input("Firma Adı", value="Bilinmiyor")
maliyet = st.number_input("Tahmini Maliyet (TL)", min_value=0.0, step=0.1, value=0.0)

st.markdown("### Solvent Oranları (%)")
solventler = ["Etanol", "IPA", "Toluen", "Etil Asetat", "Diğer"]
oranlar = []
for solvent in solventler:
    oran = st.number_input(f"{solvent} Oranı", min_value=0.0, max_value=100.0, step=0.1, value=0.0)
    oranlar.append(oran)

# Analiz ve öneri kısmı
st.markdown("### AI Destekli Yorumlar")
yorumlar = []
if oranlar[3] < 5:
    yorumlar.append("Etil Asetat oranı düşük, kuruma yavaş olabilir.")
if oranlar[0] > 20:
    yorumlar.append("Etanol oranı yüksek, buharlaşma hızlı olabilir.")
if sum(oranlar) > 100:
    yorumlar.append("Toplam oran 100%'den fazla! Lütfen kontrol edin.")
if not yorumlar:
    yorumlar.append("Oranlar uygun görünüyor.")

for yorum in yorumlar:
    st.write("- " + yorum)

# Sonuçları tablo olarak göster
st.markdown("### Formülasyon Tablosu")
data = {
    "Solvent": solventler,
    "Oran (%)": oranlar
}
df = pd.DataFrame(data)
st.table(df)

# PDF oluşturma fonksiyonu
class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", '', 14)
        self.cell(0, 10, "SolventLab | Proses Asistan Raporu", ln=True, align="C")
        self.ln(4)

    def add_content(self, firma_adi, maliyet, df, yorumlar):
        self.set_font("DejaVu", '', 12)
        self.cell(0, 10, f"Firma: {firma_adi}", ln=True)
        self.cell(0, 10, f"Tahmini Maliyet: {maliyet} TL", ln=True)
        self.ln(3)
        self.cell(0, 10, "Solvent Oranları:", ln=True)
        # Tablo
        for idx, row in df.iterrows():
            self.cell(0, 10, f"- {row['Solvent']}: {row['Oran (%)']}%", ln=True)
        self.ln(3)
        self.cell(0, 10, "Yorumlar:", ln=True)
        for yorum in yorumlar:
            self.multi_cell(0, 10, f"- {yorum}")

FONT_PATH = "DejaVuSans.ttf"

if not os.path.isfile(FONT_PATH):
    st.error(f"{FONT_PATH} dosyası bulunamadı. Lütfen uygulama dizinine ekleyin.")
else:
    if st.button("📄 PDF Oluştur"):
        pdf = PDF()
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.add_page()
        pdf.add_content(firma_adi, maliyet, df, yorumlar)
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        buffer = BytesIO(pdf_bytes)
        b64_pdf = base64.b64encode(buffer.read()).decode("utf-8")
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="formulasyon_raporu.pdf">📥 PDF dosyasını indir</a>'
        st.markdown(href, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2024 SolventLab | Geliştirici: Elrazeuxx")
