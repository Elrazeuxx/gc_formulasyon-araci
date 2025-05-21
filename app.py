import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import json

st.set_page_config(page_title="SolventLab | Proses Asistanı", layout="wide")

st.markdown(""" <div style='background-color:#2C3E50;padding:10px;border-radius:8px'> <h1 style='color:white;text-align:center;margin-bottom:0;'>SolventLab</h1> <h4 style='color:#ECF0F1;text-align:center;margin-top:0;'>Proses Asistanı</h4> </div> <br> """, unsafe_allow_html=True)

st.markdown("Bu araç, GC analizine dayalı solvent formülasyonu, proses hazırlığı, maliyet hesabı, AI yorumları ve reçete kayıt sistemini bir araya getirir.")

Reçete kayıt sistemi

data_store = {} load_data = st.selectbox("Kayıtlı Reçete Yükle (Tarayıcı içi)", options=["---"] + list(st.session_state.get("saved_recipes", {}).keys())) if load_data != "---": veri = st.session_state["saved_recipes"][load_data] firma = veri["firma"] tiner_turu = veri["tiner_turu"] gc_data = veri["gc_data"] fiyatlar = veri["fiyatlar"] litre_secimi = veri["litre"] koku_durumu = veri["koku"] else: firma = st.text_input("Firma adı (isteğe bağlı)") tiner_turu = st.selectbox("Tiner Türü", ["Selülozik", "Poliüretan", "Temizlik"]) gc_data, fiyatlar = {}, {} litre_secimi = st.selectbox("Solvent Miktarı (L)", [9000, 19000]) koku_durumu = st.selectbox("Koku Seviyesi", ["Hafif", "Orta", "Şiddetli"])

Solventler ve veri giriş

gc_cols, fiyat_cols = st.columns(2) solventler = [ "Etanol", "IPA", "N-Propanol", "Etil Asetat", "PM", "MEK", "Bütanol", "Toluen", "Ksilen", "Aseton", "Metil Asetat", "Butil Asetat", "Etil Laktat", "DPM", "Texanol" ] with gc_cols: for b in solventler: gc_data[b] = st.number_input(f"{b} (%)", min_value=0.0, max_value=100.0, step=0.1, key=f"g_{b}") with fiyat_cols: for b in solventler: fiyatlar[b] = st.number_input(f"{b} Fiyat (₺/L)", min_value=0.0, step=0.1, key=f"f_{b}")

formul_litre_maliyeti = sum((gc_data[k] / 100) * fiyatlar.get(k, 0) for k in gc_data) st.markdown(f"### Tahmini Litre Başına Maliyet: {formul_litre_maliyeti:.2f} ₺")

AI Yorumlar

yorumlar = [] if gc_data["PM"] > 60: yorumlar.append("PM oranı çok yüksek, kuruma süresi uzayabilir.") if gc_data.get("Etil Asetat", 0) < 5: yorumlar.append("Etil asetat oranı düşük, uçuculuk yetersiz olabilir.") if formul_litre_maliyeti > 40: yorumlar.append("Maliyet yüksek, alternatif solventler değerlendirilmeli.") if yorumlar: st.subheader("AI Yorumlar") for y in yorumlar: st.warning(y)

Proses hesaplama

soda = round(250 * (litre_secimi / 9000)) amonyak = round(50 * (litre_secimi / 9000), 1) kostik50 = {"Hafif": 5, "Orta": 10, "Şiddetli": 15}[koku_durumu] kostik50_total = round(kostik50 * (litre_secimi / 9000), 1) st.markdown(f"- Sodyum Karbonat: {soda} kg\n- Amonyak (%25): {amonyak} L\n- NaOH (%50): {kostik50_total} L\n- Sıcaklık: 45–55 °C")

PDF çıktısı

class PDF(FPDF): def header(self): self.set_font("Arial", "B", 12) self.cell(0, 10, "SolventLab | Proses Asistanı Raporu", ln=True, align="C") def chapter_title(self, title): self.set_font("Arial", "B", 10) self.cell(0, 10, title, ln=True, align="L") def chapter_body(self, body): self.set_font("Arial", "", 10) self.multi_cell(0, 10, body) def add_section(self, title, lines): self.chapter_title(title) for line in lines: self.chapter_body(line) self.ln()

if st.button("PDF Oluştur"): pdf = PDF() pdf.add_page() pdf.chapter_title(f"Firma: {firma if firma else 'Bilinmiyor'}") pdf.chapter_title(f"Tarih: {datetime.today().strftime('%Y-%m-%d')}") pdf.chapter_title(f"Tiner Türü: {tiner_turu}") pdf.add_section("GC Verileri", [f"{k}: {v}%" for k, v in gc_data.items() if v > 0]) pdf.add_section("Fiyatlar", [f"{k}: {fiyatlar[k]} ₺/L" for k in fiyatlar if fiyatlar[k] > 0] + [f"Toplam Maliyet: {formul_litre_maliyeti:.2f} ₺"]) pdf.add_section("Yorumlar", yorumlar if yorumlar else ["Veriler normal."]) pdf.add_section("Proses Reçetesi", [ f"Solvent: {litre_secimi} L", f"Soda: {soda} kg", f"Amonyak: {amonyak} L", f"NaOH (%50): {kostik50_total} L", "Sıcaklık: 45–55 °C" ]) buffer = BytesIO() pdf.output(buffer) st.download_button("PDF İndir", data=buffer.getvalue(), file_name="solventlab_raporu.pdf", mime="application/pdf")

Reçete kaydet

kayit_adi = st.text_input("Yeni Reçete İsmi (Kaydetmek için yaz)") if kayit_adi and st.button("Reçeteyi Kaydet"): yeni_kayit = { "firma": firma, "tiner_turu": tiner_turu, "gc_data": gc_data, "fiyatlar": fiyatlar, "litre": litre_secimi, "koku": koku_durumu } if "saved_recipes" not in st.session_state: st.session_state["saved_recipes"] = {} st.session_state["saved_recipes"][kayit_adi] = yeni_kayit st.success(f"'{kayit_adi}' adıyla kayıt edildi.")
