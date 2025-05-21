import streamlit as st
import pandas as pd

st.set_page_config(page_title="GC Analizi Formülasyon Aracı", layout="centered")
st.title("GC Verisi ile Solvent Formülasyon ve İyileştirme Aracı")

st.markdown("Bu araç, GC analizi sonucu elde edilen bileşen oranlarına göre formül önerileri sunar.")

st.subheader("GC Pik Görseli (Varsa)")
uploaded_file = st.file_uploader("GC analiz görüntüsü yükle (isteğe bağlı)", type=["png", "jpg", "jpeg", "pdf"])
if uploaded_file:
    st.image(uploaded_file, caption="GC Analiz Görseli", use_column_width=True)

# Kullanıcıdan solvent verileri
gc_data = {}
st.subheader("GC Analiz Verisi Girişi")
solventler = [
    "Etanol", "IPA", "N-Propanol", "Etil Asetat", "PM", "MEK", "Bütanol", "Toluen", "Ksilen",
    "Aseton", "Metil Asetat", "Butil Asetat", "Etil Laktat", "DPM", "Texanol"
]

cols = st.columns(3)
for i, bilesen in enumerate(solventler):
    with cols[i % 3]:
        oran = st.number_input(f"{bilesen} (%)", min_value=0.0, max_value=100.0, step=0.1, key=bilesen)
        gc_data[bilesen] = oran

# Hedef formülasyon (örnek selülozik tiner için)
target_formulation = {
    "Etanol": 5, "IPA": 10, "N-Propanol": 5, "Etil Asetat": 15, "MEK": 15, "PM": 30,
    "Toluen": 5, "Ksilen": 5, "Aseton": 5, "Bütanol": 5
}

vp_values = {
    "Etanol": 59, "IPA": 33, "N-Propanol": 21, "Etil Asetat": 73, "MEK": 70,
    "PM": 5, "Toluen": 22, "Ksilen": 10, "Aseton": 180, "Bütanol": 4,
    "Metil Asetat": 88, "Butil Asetat": 13, "DPM": 1.5, "Texanol": 0.8
}

formul_farki = {key: target_formulation.get(key, 0) - gc_data.get(key, 0) for key in target_formulation}

if st.button("Formülasyonu Hesapla"):
    st.subheader("Önerilen Formülasyon Değişiklikleri")
    for bileşen, fark in formul_farki.items():
        if fark > 0:
            st.success(f"+ {fark:.2f}% {bileşen} eklenmeli")
        elif fark < 0:
            st.warning(f"- {abs(fark):.2f}% {bileşen} azaltılmalı")

    st.subheader("VP'yi Artıracak Solventler")
    for bilesen, vp in sorted(vp_values.items(), key=lambda x: -x[1]):
        st.markdown(f"- *{bilesen}* (VP: {vp} mmHg)")

    st.subheader("Koku Giderme Önerileri")
    st.markdown("- Aktif karbon filtresi ile destilasyon sonrası arıtım")
    st.markdown("- Amonyak kokusu varsa: pH kontrolü yapılıp sodyum bikarbonatla nötrleştirilmeli")
    st.markdown("- Epoksi bozunmaları varsa ağır fraksiyonlar ayrılmalı")

    st.subheader("Renk Giderme Önerileri")
    st.markdown("- Fraksiyonel damıtma ile koyu fraksiyonları ayır")
    st.markdown("- Silika jel veya bentonit filtrelemesi")
    st.markdown("- Aldol tipi kalıntılar varsa bazla nötralize et ve kısa süreli ısıtma yap")
