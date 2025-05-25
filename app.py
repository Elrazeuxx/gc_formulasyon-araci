import streamlit as st
import pandas as pd
import os
from datetime import datetime
import sqlite3
import logging

st.set_page_config(page_title="GC Formülasyon Aracı", layout="centered")

background_image = "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=1500&q=80"
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #23272b 0%, #2c3e50 100%), url("{background_image}");
        background-blend-mode: darken;
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: #f5f6fa !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(30,34,40,0.97);
        color: #f5f6fa !important;
    }}
    .st-cq, .st-bx, .st-ag, .st-cc {{
        background: rgba(44, 62, 80, 0.93) !important;
        color: #f5f6fa !important;
        border-radius: 12px;
        border: 1px solid #353b48;
    }}
    h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: #f5f6fa !important;
    }}
    .highlight, .kirmizi, .stMarkdown strong {{
        color: #ff4b5c !important;
        font-weight: bold !important;
    }}
    .stAlert-success {{
        background: #263238 !important;
        color: #00e676 !important;
        border-left: 8px solid #00e676 !important;
    }}
    .stAlert-warning {{
        background: #363636 !important;
        color: #ffd600 !important;
        border-left: 8px solid #ffd600 !important;
    }}
    .stAlert-info {{
        background: #263238 !important;
        color: #29b6f6 !important;
        border-left: 8px solid #29b6f6 !important;
    }}
    .stAlert-error {{
        background: #2c2c2c !important;
        color: #ff1744 !important;
        border-left: 8px solid #ff1744 !important;
    }}
    .element-container .stMetric-value, .element-container .stMetric-label {{
        color: #f5f6fa !important;
    }}
    a {{
        color: #40c9ff !important;
    }}
    .stButton > button {{
        color: #fff !important;
        background-color: #1976d2 !important;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1.5em;
        font-weight: bold;
        transition: background 0.2s;
        box-shadow: 0 2px 8px #0002;
    }}
    .stButton > button:hover {{
        color: #222 !important;
        background: #90caf9 !important;
    }}
    .stButton + div .highlight, .stButton + div .kirmizi {{
        color: #ff4b5c !important;
        font-weight: bold !important;
    }}
    .stFileUploader label, .stFileUploader span {{
        color: #f5f6fa !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

logging.basicConfig(filename="log_kaydi.log", level=logging.INFO, format='%(asctime)s - %(message)s')

language = st.sidebar.selectbox("🌍 Dil / Language", ["Türkçe", "English"])
def _(tr, en): return tr if language == "Türkçe" else en

st.image("https://i.imgur.com/4dVjR8r.png", width=100)
st.title(_("🔬 GC Formülasyon Aracı", "🔬 GC Formulation Tool"))
st.caption(_("Kimya ve endüstriyel solvent yönetiminde akıllı asistan.", "Smart assistant for chemical and industrial solvent management."))

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

st.sidebar.markdown("---")
st.sidebar.info("🛠 Versiyon: 1.0.0\n📅 Güncelleme: 2025-05-25\n📌 Koyu Tema, okunaklı bildirimler, GC modülü ve Solvent paneli")

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
    # --- Tüm solventleri topla ---
    solventler = []
    for csv_path in KATEGORILER.values():
        if os.path.isfile(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if "İsim" in df.columns:
                    solventler += df["İsim"].dropna().tolist()
            except Exception:
                pass
    # Elle eklenenler de dahil et
    solventler = sorted(set(solventler + [
        "Etanol", "IPA", "N-Propanol", "Etil Asetat", "PM", "MEK", "Bütanol", "Toluen", "Ksilen",
        "Aseton", "Metil Asetat", "Butil Asetat", "Etil Laktat", "DPM", "Texanol", "Metanol", "Benzin", "Heptan",
        "Dietil Eter", "Propilen Karbonat", "Su", "NMP", "DMF", "Tetrahydrofuran"
    ]))

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

    st.subheader(_("GC Pik Görseli (Varsa)", "GC Chromatogram Image (Optional)"))
    uploaded_file = st.file_uploader(_("GC analiz görüntüsü yükle (isteğe bağlı)", "Upload GC analysis image (optional)"), type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.image(uploaded_file, caption=_("GC Analiz Görseli", "GC Chromatogram Image"), use_column_width=True)

    # --- Seçmeli GC analiz veri girişi ---
    st.subheader(_("GC Analiz Verisi Girişi", "GC Analysis Data Input"))
    secili_solventler = st.multiselect(
        _("GC analizine dahil etmek istediğiniz solventleri seçin", "Select solvents to include in GC analysis"),
        solventler,
        default=[s for s in target_formulation.keys() if s in solventler]
    )
    gc_data = {}
    cols = st.columns(3)
    for i, bilesen in enumerate(secili_solventler):
        with cols[i % 3]:
            oran = st.number_input(f"{bilesen} (%)", min_value=0.0, max_value=100.0, step=0.1, key="GC_" + bilesen)
            gc_data[bilesen] = oran

    total_percent = sum(gc_data.values())
    if total_percent > 100:
        st.warning(_("Uyarı: Toplam oran %100'ü aştı! (Şu an: %{:.2f})", "Warning: Total ratio exceeds 100%! (Now: %{:.2f})").format(total_percent))
    elif total_percent < 99:
        st.warning(_("Uyarı: Toplam oran %100'den düşük. (Şu an: %{:.2f})", "Warning: Total ratio is less than 100%. (Now: %{:.2f})").format(total_percent))

    vp_values = {
        "Etanol": 59, "IPA": 33, "N-Propanol": 21, "Etil Asetat": 73, "MEK": 70,
        "PM": 5, "DPM": 1.5, "Toluen": 22, "Ksilen": 10, "Aseton": 180, "Bütanol": 4,
        "Metil Asetat": 88, "Butil Asetat": 13, "Texanol": 0.8, "Heptan": 45, "Benzin": 60,
        "Dietil Eter": 440, "Su": 23, "NMP": 0.3, "DMF": 2.7, "Tetrahydrofuran": 143
    }

    formul_farki = {key: target_formulation.get(key, 0) - gc_data.get(key, 0) for key in secili_solventler}
    sorted_farklar = sorted(formul_farki.items(), key=lambda x: abs(x[1]), reverse=True)

    if st.button(_("Formülasyonu Hesapla", "Calculate Formulation")):
        st.subheader(_("Girdi & Hedef Karşılaştırma Tablosu", "Input & Target Comparison Table"))
        tablo = pd.DataFrame({
            _("GC Analiz (%)", "GC Analysis (%)"): [gc_data.get(b, 0) for b in secili_solventler],
            _("Hedef (%)", "Target (%)"): [target_formulation.get(b, 0) for b in secili_solventler],
            _("Fark (%)", "Difference (%)"): [formul_farki.get(b, 0) for b in secili_solventler]
        }, index=secili_solventler)
        st.dataframe(tablo.style.highlight_max(axis=0, color='#1976d2').highlight_min(axis=0, color='#ff4b5c'))

        st.subheader(_("Önerilen Formülasyon Değişiklikleri", "Suggested Formulation Adjustments"))
        for bileşen, fark in sorted_farklar:
            if abs(fark) < 0.01:
                continue
            elif fark > 0:
                st.markdown(f'<span class="highlight">+ {fark:.2f}% {bileşen} eklenmeli</span>', unsafe_allow_html=True)
            elif fark < 0:
                st.markdown(f'<span class="highlight">- {abs(fark):.2f}% {bileşen} azaltılmalı</span>', unsafe_allow_html=True)

        def hesapla_toplam_vp(formulasyon):
            toplam = sum(formulasyon.values())
            if toplam == 0:
                return 0
            return sum((formulasyon[b] / toplam) * vp_values.get(b, 0) for b in formulasyon if b in vp_values)

        mevcut_vp = hesapla_toplam_vp(gc_data)
        hedef_vp = hesapla_toplam_vp(target_formulation)
        st.subheader(_("Buhar Basıncı (VP) Karşılaştırması", "Vapor Pressure (VP) Comparison"))
        st.info(_("- Şu anki karışım VP: **{:.2f} mmHg**".format(mevcut_vp),
                  "- Current mix VP: **{:.2f} mmHg**".format(mevcut_vp)))
        st.info(_("- Hedeflenen karışım VP: **{:.2f} mmHg**".format(hedef_vp),
                  "- Target mix VP: **{:.2f} mmHg**".format(hedef_vp)))
        st.info(_("VP'yi artırmak için yüksek VP'li solventlerden eklenebilir, düşürmek için düşük VP'li solventler arttırılabilir.",
                  "To increase VP, add more high-VP solvents; to decrease, increase low-VP solvents."))

        st.subheader(_("VP'yi Artıracak Solventler (Yüksekten Düşüğe)", "Solvents That Increase VP (Highest to Lowest)"))
        for bilesen, vp in sorted(vp_values.items(), key=lambda x: -x[1]):
            st.markdown(f"- **{bilesen}** (VP: {vp} mmHg)")

        st.subheader(_("Koku Giderme Önerileri", "Odor Removal Recommendations"))
        st.warning(_("Aktif karbon filtresi ile destilasyon sonrası arıtım", "Post-distillation treatment with activated carbon filter"))
        st.warning(_("Amonyak kokusu varsa: pH kontrolü yapılıp sodyum bikarbonatla nötrleştirilmeli", "If ammonia odor: check pH, neutralize with sodium bicarbonate"))
        st.warning(_("Epoksi bozunmaları varsa ağır fraksiyonlar ayrılmalı", "If epoxy decomposition: separate heavy fractions"))

        st.subheader(_("Renk Giderme Önerileri", "Color Removal Recommendations"))
        st.warning(_("Fraksiyonel damıtma ile koyu fraksiyonları ayır", "Separate dark fractions by fractional distillation"))
        st.warning(_("Silika jel veya bentonit filtrelemesi", "Silica gel or bentonite filtration"))
        st.warning(_("Aldol tipi kalıntılar varsa bazla nötralize et ve kısa süreli ısıtma yap", "If aldol-type residues: neutralize with base and short heating"))

elif MODUL == _("Solvent Bilgi Paneli", "Solvent Info Panel"):
    # --- Solvent Bilgi Paneli'nde "Tüm Solventler" seçeneği ---
    kategori_listesi = ["Tüm Solventler"] + list(KATEGORILER.keys())
    kategori = st.sidebar.selectbox(_("Solvent/Sınıf Grubu Seçin", "Select Solvent/Class Group"), kategori_listesi)

    if kategori == "Tüm Solventler":
        df_list = []
        for csv_yolu in KATEGORILER.values():
            if os.path.isfile(csv_yolu):
                try:
                    df = pd.read_csv(csv_yolu)
                    df["Kategori"] = os.path.splitext(os.path.basename(csv_yolu))[0]
                    df_list.append(df)
                except Exception as e:
                    st.warning(f"{csv_yolu} okunamadı: {e}")
        if df_list:
            df_all = pd.concat(df_list, ignore_index=True)
            st.subheader(_("Tüm Solventler Listesi", "Full Solvent List"))
            st.dataframe(df_all, use_container_width=True)
            isimler = df_all["İsim"].dropna().tolist()
            secili = st.selectbox(_("Solvent Seç", "Select Solvent"), isimler)
            bilgi = df_all[df_all["İsim"] == secili].iloc[0]
            st.markdown(f"""
**Kategori:** {bilgi.get('Kategori', '-')}
**Kapalı Formül:** {bilgi.get('Kapalı Formül', '-')}
**Kaynama Noktası:** {bilgi.get('Kaynama Noktası (°C)', '-')} °C
**Yoğunluk:** {bilgi.get('Yoğunluk (g/cm³)', '-')} g/cm³
**pH:** {bilgi.get('pH', '-')}
**Çözünürlük:** {bilgi.get('Suda Çözünürlük (%)', '-')} %
**Max Su Oranı:** {bilgi.get('Max Su Oranı (%)', '-')}
**Uyumlu Solventler:** {bilgi.get('Uyumlu Solventler', '-')}
**Kullanım Alanları:** {bilgi.get('Kullanım Alanları', '-')}
**Toksisite:** {bilgi.get('Toksisite / Güvenlik', '-')}
""")
        else:
            st.warning("Hiçbir solvent dosyası bulunamadı veya okunamadı.")
        st.stop()

    # --- Klasik kategoriye göre gösterim ---
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
        st.error(_("CSV'de eksik sütunlar var: ", "Missing columns in CSV: ") + ", ".join(eksik))
    elif len(df) == 0:
        st.warning(_(f"{kategori} için veri bulunamadı.", f"No data for {kategori}."))
    else:
        isimler = df["İsim"].dropna().tolist()
        if not isimler:
            st.warning(_("Seçilebilecek isim yok.", "No names to select."))
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
