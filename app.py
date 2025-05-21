from fpdf import FPDF
import streamlit as st
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="SolventLab | Proses Asistanı", layout="wide")

st.markdown("""
<div style='background-color:#2C5E50;padding:10px;border-radius:8px'>
<h1 style='color:white;text-align:center;'>GC Verisi ile Solvent Formülasyon ve Proses Asistanı</h1>
</div>
""", unsafe_allow_html=True)
st.markdown("""
Bu araç, GC analizine dayalı solvent formülasyonu, proses hazırlığı, maliyet hesabı, AI yorumları ve reçete kaydı sağlar.
""")

# Reçete kayıt sistemi
if "saved_recipes" not in st.session_state:
    st.session_state["saved_recipes"] = {}

load_data = st.selectbox(
    "Kayıtlı Reçete Yükle (Tarayıcı içi)",
    options=["---"] + list(st.session_state["saved_recipes"].keys())
)

veri = None
if load_data != "---":
    veri = st.session_state["saved_recipes"][load_data]

# Solventler ve veri giriş
cols = st.columns(2)
solventler = [
    "Etanol", "IPA", "N-Propanol", "Etil Asetat", "PM", "MEK", "Bütanol",
    "Toluen", "Ksilen", "Aseton", "Metil Asetat", "Butil Asetat",
    "Etil Laktat", "DPM", "Texanol"
]

veriler = {}
for i, solvent in enumerate(solventler):
    with cols[i % 2]:
        default = veri[solvent] if veri and solvent in veri else 0.0
        veriler[solvent] = st.number_input(f"{solvent} (%)", min_value=0.0, max_value=100.0, step=0.01, value=default)

# Tahmini litre başına maliyet
def fiyat_getir():
    return {
        "Etanol": 24, "IPA": 27, "N-Propanol": 31, "Etil Asetat": 26, "PM": 34,
        "MEK": 33, "Bütanol": 28, "Toluen": 29, "Ksilen": 28, "Aseton": 25,
        "Metil Asetat": 27, "Butil Asetat": 31, "Etil Laktat": 36, "DPM": 35, "Texanol": 38
    }
fiyatlar = fiyat_getir()
maliyet = sum([(veriler[k] / 100) * fiyatlar.get(k, 0) for k in veriler])
st.markdown(f"### Tahmini Litre Başı Maliyet: {maliyet:.2f} TL")

# AI Yorumları
yorumlar = []
if veriler["PM"] > 60:
    yorumlar.append("PM oranı çok yüksek, kuruma süresi uzayabilir.")
if veriler["Etil Asetat"] < 5:
    yorumlar.append("Etil Asetat düşük, uçuculuk yetersiz olabilir.")

for yorum in yorumlar:
    st.warning(yorum)

# Proses hesaplama
litre_secimi = st.selectbox("İşlem hacmi (Litre)", options=[9000, 19000])
soda = round(250 * (litre_secimi / 9000))
amonyak = round(50 * (litre_secimi / 9000))
st.info(f"Sodyum Karbonat (Na2CO3): {soda} kg, Amonyak (%25): {amonyak} L")

# PDF çıktısı
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "SolventLab | Proses Asistanı Raporu", ln=True, align='C')

if st.button("PDF Oluştur"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(
        0, 10,
        f"Firma: Bilinmiyor\n\nSolvent Oranları:\n" +
        ", ".join([f"{k}: {v}%" for k, v in veriler.items()]) +
        f"\n\nTahmini Maliyet: {maliyet:.2f} TL\n\nYorumlar: {'; '.join(yorumlar)}"
    )
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    st.download_button("PDF İndir", data=buffer, file_name="rapor.pdf", mime="application/pdf")
