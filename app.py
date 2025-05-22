import streamlit as st
from fpdf import FPDF
import base64
from io import BytesIO

# Sayfa başlığı
st.set_page_config(page_title="SolventLab | Proses Asistanı", layout="wide")

# Başlık
st.markdown("""
<div style='background-color:#2C5E50;padding:10px;border-radius:8px'>
<h1 style='color:white;text-align:center;'>GC Verisi ile Solvent Formülasyon ve Proses Asistanı</h1>
</div>
""", unsafe_allow_html=True)

# İşlem hacmi seçimi
litre_secimi = st.selectbox("İşlem hacmi (Litre)", [9000, 19000])

# Proses hesaplamaları
soda = round(250 * (litre_secimi / 9000))
amonyak = round(50 * (litre_secimi / 9000))
kostik = "Kokuya göre değişir (%50 NaOH)"

st.info(f"Sodyum Karbonat (Na2CO3): {soda} kg, Amonyak (%25): {amonyak} L, Kostik (%50): {kostik}")

# GC veri girişi
st.subheader("GC Analizi Girişi")
veriler = {}
solventler = ["Etanol", "IPA", "Etil Asetat", "PM", "Toluen", "Ksilen"]
cols = st.columns(3)
for i, solvent in enumerate(solventler):
    with cols[i % 3]:
        veriler[solvent] = st.number_input(f"{solvent} (%)", min_value=0.0, max_value=100.0, step=0.1)

# Basit yorumlar
yorumlar = []
if veriler["PM"] > 60:
    yorumlar.append("PM oranı çok yüksek, kuruma süresi uzayabilir.")
if veriler["Etil Asetat"] < 5:
    yorumlar.append("Etil Asetat düşük, uçuculuk yetersiz olabilir.")

for yorum in yorumlar:
    st.warning(yorum)

# PDF oluşturma butonu
if st.button("PDF Oluştur"):
    pdf = FPDF()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.add_page()

    pdf.multi_cell(0, 10, "SolventLab | Proses Asistanı Raporu\n", align="L")
    pdf.multi_cell(0, 10, f"İşlem Hacmi: {litre_secimi} L\nSodyum Karbonat: {soda} kg\nAmonyak: {amonyak} L\nKostik: {kostik}\n", align="L")
    pdf.multi_cell(0, 10, "\nSolvent Oranları:", align="L")
    for k, v in veriler.items():
        pdf.multi_cell(0, 10, f"- {k}: {v} %", align="L")

    if yorumlar:
        pdf.multi_cell(0, 10, "\nAI Yorumları:", align="L")
        for y in yorumlar:
            pdf.multi_cell(0, 10, f"- {y}", align="L")

    # PDF'i belleğe al
   if st.button("PDF Oluştur"):
    pdf = PDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 12)
    
    # Satırları ekle
    for line in satirlar:
        pdf.multi_cell(0, 10, line, align="L")

    # PDF'i belleğe al
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    b64_pdf = base64.b64encode(buffer.read()).decode("utf-8")
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="formulasyon_raporu.pdf">PDF dosyasını indir</a>'
    st.markdown(href, unsafe_allow_html=True)

