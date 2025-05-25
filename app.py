import streamlit as st
import pandas as pd
import os
from datetime import datetime
import sqlite3
import logging

# EN ÜSTTE OLMALI!
st.set_page_config(page_title="GC Formülasyon Aracı", layout="centered")

# Kimya laboratuvarı ve mavi-gri arka plan (Unsplash)
background_image = "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=1500&q=80"
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%), url("{background_image}");
        background-blend-mode: lighten;
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: #111 !important;
    }}
    /* Sidebar için yarı şeffaf, açık mavi-gri */
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(236, 239, 241, 0.88);
        color: #111 !important;
    }}
    /* Tüm kutular ve kartlar için açık gri arka plan */
    .st-cq, .st-bx, .st-ag, .st-cc {{
        background: rgba(255,255,255,0.91) !important;
        color: #111 !important;
        border-radius: 12px;
    }}
    /* Başlıklar siyah, önemli başlıklar/küçük başlıklar kırmızı */
    h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: #111 !important;
    }}
    .kirmizi, .highlight, .stAlert, .stMarkdown strong {{
        color: #d32f2f !important;
        font-weight: bold !important;
    }}
    /* Uyarı ve başarı kutularını daha belirgin yap */
    .stAlert {{
        border-left: 8px solid #d32f2f !important;
        background: #fff3e0 !important;
        color: #d32f2f !important;
    }}
    a {{
        color: #0288d1 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- LOG dosyası ---
logging.basicConfig(filename="log_kaydi.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# --- Dil Ayarı ---
language = st.sidebar.selectbox("🌍 Dil / Language", ["Türkçe", "English"])
def _(tr, en): return tr if language == "Türkçe" else en

st.image("https://i.imgur.com/4dVjR8r.png", width=100)
st.title(_("🔬 GC Formülasyon Aracı", "🔬 GC Formulation Tool"))
st.caption(_("Kimya ve endüstriyel solvent yönetiminde akıllı asistan.", "Smart assistant for chemical and industrial solvent management."))

# --- Admin Paneli ---
with st.sidebar.expander(_("⚙️ Ayarlar ve Geri Bildirim", "⚙️ Settings & Feedback")):
    tema = st.radio(_("Tema Renk Seçimi:", "Select Theme Color:"), ["Varsayılan", "Açık", "Koyu"])
    geri_bildirim = st.text_area(_("Görüş ve önerilerinizi yazabilirsiniz:", "You can share feedback or suggestions:"))
    if st.button(_("Gönder", "Submit")):
        try:
            conn = sqlite3.connect("kullanici_geri_bildirim.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarih TEXT,
                    icerik TEXT
                )
            """)
            cursor.execute(
                "INSERT INTO feedback (tarih, icerik) VALUES (?, ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M"), geri_bildirim)
            )
            conn.commit()
            conn.close()
            st.success(_("Teşekkür ederiz! Geri bildiriminiz alınmıştır.", "Thank you! Your feedback has been submitted."))
            logging.info("Yeni geri bildirim kaydedildi.")
        except Exception as e:
            st.error(_("Bir hata oluştu.", "An error occurred."))
            logging.error(f"Geri bildirim hatası: {e}")

# --- Kullanım İstatistikleri ---
with st.sidebar.expander(_("📊 Kullanım İstatistikleri", "📊 Usage Statistics")):
    conn = sqlite3.connect("kullanici_geri_bildirim.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            icerik TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM feedback")
    toplam_geri_bildirim = cursor.fetchone()[0]
    st.metric(_("Gelen Geri Bildirim Sayısı", "Total Feedbacks"), toplam_geri_bildirim)
    cursor.execute("SELECT tarih FROM feedback ORDER BY id DESC LIMIT 1")
    son = cursor.fetchone()
    st.metric(_("Son Bildirim Tarihi", "Last Feedback"), son[0] if son else "-")
    if st.button(_("📥 Veritabanını CSV Olarak İndir", "📥 Download Feedback DB as CSV")):
        df_feedback = pd.read_sql_query("SELECT * FROM feedback", conn)
        csv_yolu = "feedback_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv"
        df_feedback.to_csv(csv_yolu, index=False)
        st.success(_("CSV dosyası oluşturuldu: ", "CSV file created: ") + csv_yolu)
    conn.close()

# --- Versiyon Bilgisi ---
st.sidebar.markdown("---")
st.sidebar.info("🛠 Versiyon: 1.0.0\n📅 Güncelleme: 2025-05-24\n📌 Yeni: Kimya laboratuvarı arka planı, GC modülü, Solvent paneli, Veritabanı, Çoklu Dil")

# --- Solvent & GC Bölümü ---
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

MODUL = st.sidebar.radio(
    _("Modül Seç", "Select Module"),
    (_("GC Formülasyon Karşılaştırma", "GC Formulation Comparison"), _("Solvent Bilgi Paneli", "Solvent Info Panel"))
)

if MODUL == _("GC Formülasyon Karşılaştırma", "GC Formulation Comparison"):
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
    # Sık kullanılanları da ekle
    solventler = sorted(list(set(solventler + [
        "Etanol", "IPA", "N-Propanol", "Etil Asetat", "PM", "MEK", "Bütanol", "Toluen", "Ksilen",
        "Aseton", "Metil Asetat", "Butil Asetat", "Etil Laktat", "DPM", "Texanol", "Metanol", "Benzin", "Heptan",
        "Dietil Eter", "Propilen Karbonat", "Su", "NMP", "DMF", "Tetrahydrofuran"
    ])))

    # --- Çoklu endüstriyel formülasyon tipi ---
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

    st.header(_("GC Analizine Göre Formülasyon Karşılaştırma", "Formulation Comparison by GC Analysis"))
    kullanim = st.selectbox(_("Formülasyon Tipi", "Formulation Type"), list(FORMULASYONLAR.keys()))
    target_formulation = FORMULASYONLAR[kullanim]
    st.markdown(_("Kendi GC analiz verinizi girin ve hedef formül ile karşılaştırın.", "Enter your GC analysis data and compare with the target formulation."))

    # --- GC Pik Görseli (isteğe bağlı) ---
    st.subheader(_("GC Pik Görseli (Varsa)", "GC Chromatogram Image (Optional)"))
    uploaded_file = st.file_uploader(_("GC analiz görüntüsü yükle (isteğe bağlı)", "Upload GC analysis image (optional)"), type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.image(uploaded_file, caption=_("GC Analiz Görseli", "GC Chromatogram Image"), use_column_width=True)

    # --- GC analiz girişi ---
    st.subheader(_("GC Analiz Verisi Girişi", "GC Analysis Data Input"))
    gc_data = {}
    cols = st.columns(3)
    for i, bilesen in enumerate(target_formulation):
        with cols[i % 3]:
            oran = st.number_input(f"{bilesen} (%)", min_value=0.0, max_value=100.0, step=0.1, key="GC_" + bilesen)
            gc_data[bilesen] = oran

    total_percent = sum(gc_data.values())
    if total_percent > 100:
        st.markdown('<span class="kirmizi">Uyarı: Toplam oran %100\'ü aştı! (Şu an: %{:.2f})</span>'.format(total_percent), unsafe_allow_html=True)
    elif total_percent < 99:
        st.markdown('<span class="kirmizi">Uyarı: Toplam oran %100\'den düşük. (Şu an: %{:.2f})</span>'.format(total_percent), unsafe_allow_html=True)

    # --- VP değerleri (örnek) ---
    vp_values = {
        "Etanol": 59, "IPA": 33, "N-Propanol": 21, "Etil Asetat": 73, "MEK": 70,
        "PM": 5, "DPM": 1.5, "Toluen": 22, "Ksilen": 10, "Aseton": 180, "Bütanol": 4,
        "Metil Asetat": 88, "Butil Asetat": 13, "Texanol": 0.8, "Heptan": 45, "Benzin": 60,
        "Dietil Eter": 440, "Su": 23, "NMP": 0.3, "DMF": 2.7, "Tetrahydrofuran": 143
    }

    formul_farki = {key: target_formulation.get(key, 0) - gc_data.get(key, 0) for key in target_formulation}
    sorted_farklar = sorted(formul_farki.items(), key=lambda x: abs(x[1]), reverse=True)

    if st.button(_("Formülasyonu Hesapla", "Calculate Formulation")):
        st.subheader(_("Girdi & Hedef Karşılaştırma Tablosu", "Input & Target Comparison Table"))
        tablo = pd.DataFrame({
            _("GC Analiz (%)", "GC Analysis (%)"): [gc_data.get(b, 0) for b in target_formulation],
            _("Hedef (%)", "Target (%)"): [target_formulation.get(b, 0) for b in target_formulation],
            _("Fark (%)", "Difference (%)"): [formul_farki.get(b, 0) for b in target_formulation]
        }, index=target_formulation)
        st.dataframe(tablo.style.highlight_max(axis=0, color='lightgreen').highlight_min(axis=0, color='lightcoral'))

        st.subheader(_("Önerilen Formülasyon Değişiklikleri", "Suggested Formulation Adjustments"))
        for bileşen, fark in sorted_farklar:
            if abs(fark) < 0.01:
                continue
            elif fark > 0:
                st.markdown(f'<span class="kirmizi">+ {fark:.2f}% {bileşen} eklenmeli</span>', unsafe_allow_html=True)
            elif fark < 0:
                st.markdown(f'<span class="kirmizi">- {abs(fark):.2f}% {bileşen} azaltılmalı</span>', unsafe_allow_html=True)

        def hesapla_toplam_vp(formulasyon):
            toplam = sum(formulasyon.values())
            if toplam == 0:
                return 0
            return sum((formulasyon[b] / toplam) * vp_values.get(b, 0) for b in formulasyon if b in vp_values)

        mevcut_vp = hesapla_toplam_vp(gc_data)
        hedef_vp = hesapla_toplam_vp(target_formulation)
        st.subheader(_("Buhar Basıncı (VP) Karşılaştırması", "Vapor Pressure (VP) Comparison"))
        st.markdown(_("- Şu anki karışım VP: **{:.2f} mmHg**".format(mevcut_vp),
                      "- Current mix VP: **{:.2f} mmHg**".format(mevcut_vp)))
        st.markdown(_("- Hedeflenen karışım VP: **{:.2f} mmHg**".format(hedef_vp),
                      "- Target mix VP: **{:.2f} mmHg**".format(hedef_vp)))
        st.info(_("VP'yi artırmak için yüksek VP'li solventlerden eklenebilir, düşürmek için düşük VP'li solventler arttırılabilir.",
                  "To increase VP, add more high-VP solvents; to decrease, increase low-VP solvents."))

        st.subheader(_("VP'yi Artıracak Solventler (Yüksekten Düşüğe)", "Solvents That Increase VP (Highest to Lowest)"))
        for bilesen, vp in sorted(vp_values.items(), key=lambda x: -x[1]):
            st.markdown(f"- **{bilesen}** (VP: {vp} mmHg)")

        st.subheader(_("Koku Giderme Önerileri", "Odor Removal Recommendations"))
        st.markdown('<span class="kirmizi">- Aktif karbon filtresi ile destilasyon sonrası arıtım</span>', unsafe_allow_html=True)
        st.markdown('<span class="kirmizi">- Amonyak kokusu varsa: pH kontrolü yapılıp sodyum bikarbonatla nötrleştirilmeli</span>', unsafe_allow_html=True)
        st.markdown('<span class="kirmizi">- Epoksi bozunmaları varsa ağır fraksiyonlar ayrılmalı</span>', unsafe_allow_html=True)

        st.subheader(_("Renk Giderme Önerileri", "Color Removal Recommendations"))
        st.markdown('<span class="kirmizi">- Fraksiyonel damıtma ile koyu fraksiyonları ayır</span>', unsafe_allow_html=True)
        st.markdown('<span class="kirmizi">- Silika jel veya bentonit filtrelemesi</span>', unsafe_allow_html=True)
        st.markdown('<span class="kirmizi">- Aldol tipi kalıntılar varsa bazla nötralize et ve kısa süreli ısıtma yap</span>', unsafe_allow_html=True)

elif MODUL == _("Solvent Bilgi Paneli", "Solvent Info Panel"):
    kategori = st.sidebar.selectbox(_("Solvent/Sınıf Grubu Seçin", "Select Solvent/Class Group"), list(KATEGORILER.keys()))
    csv_yolu = KATEGORILER[kategori]

    if not os.path.isfile(csv_yolu):
        st.error(f"{kategori} için '{csv_yolu}' dosyası bulunamadı. Lütfen '{csv_yolu}' dosyasını oluşturun!")
        st.stop()

    try:
        df = pd.read_csv(csv_yolu)
    except Exception as e:
        st.error(_("CSV okunurken hata oluştu: ", "Error while reading CSV: ") + str(e))
        st.stop()

    st.subheader(_(f"{kategori} Listesi", f"{kategori} List"))
    st.dataframe(df, use_container_width=True)

    gerekli_sutunlar = [
        "İsim", "Kapalı Formül", "Kaynama Noktası (°C)", "Yoğunluk (g/cm³)", "pH",
        "Suda Çözünürlük (%)", "Max Su Oranı (%)", "Uyumlu Solventler",
        "Kullanım Alanları", "Toksisite / Güvenlik"
    ]
    eksik = [s for s in gerekli_sutunlar if s not in df.columns]
    if eksik:
        st.markdown('<span class="kirmizi">CSV\'de eksik sütunlar var: ' + ", ".join(eksik) + '</span>', unsafe_allow_html=True)
    elif len(df) == 0:
        st.markdown('<span class="kirmizi">' + _(f"{kategori} için veri bulunamadı.", f"No data for {kategori}.") + '</span>', unsafe_allow_html=True)
    else:
        isimler = df["İsim"].dropna().tolist()
        if not isimler:
            st.markdown('<span class="kirmizi">Seçilebilecek isim yok.</span>', unsafe_allow_html=True)
        else:
            secili = st.selectbox(_(f"{kategori} Seç", f"Select {kategori}"), isimler)
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

    st.info(_("Yeni bir kategori eklemek için, sadece yeni bir CSV dosyası oluşturup KATEGORILER sözlüğüne eklemen yeterli!",
             "To add a new category, simply create a new CSV file and add it to the KATEGORILER dictionary!"))

    st.markdown("""
---
**Örnek CSV Başlığı:**

`İsim,Kapalı Formül,Yoğunluk (g/cm³),pH,Kaynama Noktası (°C),Suda Çözünürlük (%),Max Su Oranı (%),Uyumlu Solventler,Kullanım Alanları,Toksisite / Güvenlik`

**Örnek Satır:**

`Etanol,C2H5OH,0.789,Nötr,78.4,100,Sınırsız,Su;Metanol;IPA,Temizlik;Laboratuvar,Düşük`
""")
