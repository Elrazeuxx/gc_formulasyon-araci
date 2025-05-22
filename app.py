import streamlit as st

from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 12)
pdf.cell(200, 10, txt="Formülasyon başarıyla oluşturuldu. İçeriğinde çözücü oranları ve tahmini yorumlar mevcuttur.", ln=True, align='L')
pdf.output("formulasyon.pdf")


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

from fpdf import FPDF
import base64
from io import BytesIO

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", '', 14)
        self.cell(0, 10, "SolventLab | Proses Asistanı Raporu", ln=True, align="C")

    def add_content(self, data_lines):
        self.set_font("DejaVu", '', 12)
        for line in data_lines:
            self.multi_cell(0, 10, line)

if st.button("PDF Oluştur"):
    pdf = PDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)

    # İçerik örneği — burayı kendi verilerinle dinamik hale getireceğiz
    satirlar = [
        "Firma: Bilinmiyor",
        "Tahmini Maliyet: 27 TL",
        "Solvent Oranları:",
        "- Etanol: 10%",
        "- IPA: 25%",
        "- Toluen: 15%",
        "Yorumlar: Oranlar iyi, kuruma hızlı olabilir.",
    ]

    pdf.add_content(satirlar)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    b64_pdf = base64.b64encode(buffer.read()).decode("utf-8")
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="formulasyon_raporu.pdf">PDF dosyasını indir</a>'
    st.markdown(href, unsafe_allow_html=True)


