import streamlit as st
from fpdf import FPDF
from io import BytesIO
import base64
import os

# Sayfa başlığı
st.set_page_config(page_title="SolventLab | Proses Asistanı", layout="wide")

# Başlık
st.markdown("""
<div style='background-color:#2C5E50;padding:10px;border-radius:8px'>
<h1 style='color:white;text-align:center'>GC Verisi ile Solvent Formülasyon ve Proses Asistanı</h1>
</div>
""", unsafe_allow_html=True)

# PDF sınıfı
class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", '', 14)
        self.cell(0, 10, "SolventLab | Proses Asistan Raporu", ln=True, align="C")

    def add_content(self, data_lines):
        self.set_font("DejaVu", '', 12)
        for line in data_lines:
            self.multi_cell(0, 10, line, align="L")

# Font dosyasının mevcut olup olmadığını kontrol edin
FONT_PATH = "DejaVuSans.ttf"
if not os.path.isfile(FONT_PATH):
    st.error(f"{FONT_PATH} dosyası bulunamadı. Lütfen bu font dosyasını uygulama dizinine ekleyin.")
else:
    # Örnek veri
    satirlar = [
        "Firma: Bilinmiyor",
        "Tahmini Maliyet: 27 TL",
        "Solvent Oranları:",
        "- Etanol: 10%",
        "- IPA: 25%",
        "- Toluen: 15%",
        "Yorumlar: Oranlar iyi, kuruma hızlı olabilir."
    ]

    # PDF butonu
    if st.button("📄 PDF Oluştur"):
        satirlar = [
            "Firma: Bilinmiyor",
            "Tahmini Maliyet: 27 TL",
            "Solvent Oranları:",
            "- Etanol: 10%",
            "- IPA: 25%",
            "- Toluen: 15%",
            "AI Yorum: Etil Asetat düşük, kuruma yavaş olabilir."
        ]

        pdf = PDF()
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.add_page()
        pdf.set_font("DejaVu", "", 12)

        for line in satirlar:
            pdf.multi_cell(0, 10, line)

        buffer = BytesIO()
        pdf.output(buffer, 'F')
        buffer.seek(0)

        b64_pdf = base64.b64encode(buffer.read()).decode("utf-8")
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="formulasyon_raporu.pdf">📥 PDF dosyasını indir</a>'
        st.markdown(href, unsafe_allow_html=True)
