import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="GC Formülasyon & Endüstriyel Solvent Asistanı", layout="centered")
st.title("GC Analizi ile Endüstriyel Solvent Formülasyon Asistanı")

# --- KATEGORILER tanımı ---
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

# --- Tüm solvent adlarını birleştir ---
solventler = []
for csv_path in KATEGORILER.values():
    if os.path.isfile(csv_path):
        try:
            df = pd.read_csv(csv_path)
            if "İsim" in df.columns:
                solventler += df["İsim"].dropna().tolist()
        except Exception:
            pass
solventler = sorted(list(set(solventler + [
    "Etanol", "IPA", "N-Propanol", "Etil Asetat", "PM", "MEK", "Bütanol", "Toluen", "Ksilen",
    "Aseton", "Metil Asetat", "Butil Asetat", "Etil Laktat", "DPM", "Texanol", "Metanol", "Benzin", "Heptan",
    "Dietil Eter", "Propilen Karbonat", "Su", "NMP", "DMF", "Tetrahydrofuran"
])))

# --- Daha fazla örnek formülasyon ---
FORMULASYONLAR = {
    "Çözücü": {
        "Etanol": 20, "IPA": 20, "Etil Asetat": 20, "MEK": 15, "PM": 15, "DPM": 10
    },
    "Tiner": {
        "Toluen": 30, "Ksilen": 30, "IPA": 10, "Etanol": 10, "MEK": 10, "Etil Asetat": 10
    },
    "Matbaa Solventi": {
        "IPA": 40, "Etanol": 25, "PM": 15, "DPM": 10, "MEK": 5, "Etil Asetat": 5
    },
    "Pas Sökücü": {
        "IPA": 10, "Etanol": 15, "Etil Asetat": 10, "MEK": 10, "DPM": 15, "Ksilen": 20, "Toluen": 20
    },
    "Metal Temizleyici": {
        "IPA": 20, "Etanol": 10, "PM": 30, "DPM": 25, "MEK": 10, "Etil Asetat": 5
    },
    "Cam Temizleyici": {
        "IPA": 20, "Etanol": 10, "Su": 65, "DPM": 3, "Etil Asetat": 2
    },
    "Mürekkep Çözücü": {
        "Etanol": 25, "IPA": 15, "DPM": 15, "Etil Asetat": 20, "MEK": 10, "Toluen": 10, "Ksilen": 5
    },
    "Yağ Sökücü": {
        "IPA": 15, "Etanol": 10, "PM": 30, "DPM": 25, "MEK": 10, "Etil Asetat": 5, "Heptan": 5
    },
    "Universal Temizleyici": {
        "IPA": 10, "Etanol": 10, "Su": 70, "DPM": 5, "Etil Asetat": 5
    },
    "Hızlı Kuruyan Tiner": {
        "Aseton": 30, "IPA": 20, "MEK": 20, "Etil Asetat": 15, "Toluen": 10, "Ksilen": 5
    }
}

st.sidebar.header("Formülasyon Tipi Seç")
kullanim = st.sidebar.selectbox("Formülasyon Tipi", list(FORMULASYONLAR.keys()))
target_formulation = FORMULASYONLAR[kullanim]

st.markdown(f"**Seçili Kullanım Alanı:** `{kullanim}`")
st.markdown("Kendi GC analiz verinizi girerek, endüstriyel hedef formülasyonla karşılaştırın.")

# --- GC Görseli (isteğe bağlı) ---
st.subheader("GC Pik Görseli (Varsa)")
uploaded_file = st.file_uploader("GC analiz görüntüsü yükle (isteğe bağlı)", type=["png", "jpg", "jpeg", "pdf"])
if uploaded_file:
    st.image(uploaded_file, caption="GC Analiz Görseli", use_column_width=True)

# --- GC analiz girişi ---
st.subheader("GC Analiz Verisi Girişi")
gc_data = {}
cols = st.columns(3)
for i, bilesen in enumerate(target_formulation):
    with cols[i % 3]:
        oran = st.number_input(f"{bilesen} (%)", min_value=0.0, max_value=100.0, step=0.1, key="GC_" + bilesen)
        gc_data[bilesen] = oran

total_percent = sum(gc_data.values())
if total_percent > 100:
    st.error(f"Uyarı: Toplam oran %100'ü aştı! (Şu an: %{total_percent:.2f})")
elif total_percent < 99:
    st.warning(f"Uyarı: Toplam oran %100'den düşük. (Şu an: %{total_percent:.2f})")

# --- VP değerleri (örnek) ---
vp_values = {
    "Etanol": 59, "IPA": 33, "N-Propanol": 21, "Etil Asetat": 73, "MEK": 70,
    "PM": 5, "DPM": 1.5, "Toluen": 22, "Ksilen": 10, "Aseton": 180, "Bütanol": 4,
    "Metil Asetat": 88, "Butil Asetat": 13, "Texanol": 0.8, "Heptan": 45, "Benzin": 60,
    "Dietil Eter": 440, "Su": 23, "NMP": 0.3, "DMF": 2.7, "Tetrahydrofuran": 143
}

formul_farki = {key: target_formulation.get(key, 0) - gc_data.get(key, 0) for key in target_formulation}
sorted_farklar = sorted(formul_farki.items(), key=lambda x: abs(x[1]), reverse=True)

if st.button("Formülasyonu Hesapla"):
    st.subheader("Girdi & Hedef Karşılaştırma Tablosu")
    tablo = pd.DataFrame({
        "GC Analiz (%)": [gc_data.get(b, 0) for b in target_formulation],
        "Hedef (%)": [target_formulation.get(b, 0) for b in target_formulation],
        "Fark (%)": [formul_farki.get(b, 0) for b in target_formulation]
    }, index=target_formulation)
    st.dataframe(tablo.style.highlight_max(axis=0, color='lightgreen').highlight_min(axis=0, color='lightcoral'))

    st.subheader("Önerilen Formülasyon Değişiklikleri")
    for bileşen, fark in sorted_farklar:
        if abs(fark) < 0.01:
            continue
        elif fark > 0:
            st.success(f"+ {fark:.2f}% {bileşen} eklenmeli")
        elif fark < 0:
            st.warning(f"- {abs(fark):.2f}% {bileşen} azaltılmalı")

    def hesapla_toplam_vp(formulasyon):
        toplam = sum(formulasyon.values())
        if toplam == 0:
            return 0
        return sum((formulasyon[b] / toplam) * vp_values.get(b, 0) for b in formulasyon if b in vp_values)

    mevcut_vp = hesapla_toplam_vp(gc_data)
    hedef_vp = hesapla_toplam_vp(target_formulation)
    st.subheader("Buhar Basıncı (VP) Karşılaştırması")
    st.markdown(f"- Şu anki karışım VP: **{mevcut_vp:.2f} mmHg**")
    st.markdown(f"- Hedeflenen karışım VP: **{hedef_vp:.2f} mmHg**")
    st.info("VP'yi artırmak için yüksek VP'li solventlerden eklenebilir, düşürmek için düşük VP'li solventler arttırılabilir.")

    st.subheader("VP'yi Artıracak Solventler (Yüksekten Düşüğe)")
    for bilesen, vp in sorted(vp_values.items(), key=lambda x: -x[1]):
        st.markdown(f"- **{bilesen}** (VP: {vp} mmHg)")

    st.subheader("Koku Giderme Önerileri")
    st.markdown("- Aktif karbon filtresi ile destilasyon sonrası arıtım")
    st.markdown("- Amonyak kokusu varsa: pH kontrolü yapılıp sodyum bikarbonatla nötrleştirilmeli")
    st.markdown("- Epoksi bozunmaları varsa ağır fraksiyonlar ayrılmalı")

    st.subheader("Renk Giderme Önerileri")
    st.markdown("- Fraksiyonel damıtma ile koyu fraksiyonları ayır")
    st.markdown("- Silika jel veya bentonit filtrelemesi")
    st.markdown("- Aldol tipi kalıntılar varsa bazla nötralize et ve kısa süreli ısıtma yap")
