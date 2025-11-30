# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from PIL import Image
from modeling_gunung import recommend

# ==================================
# CONFIG
# ==================================
st.set_page_config(page_title="Mount Jawa", layout="wide")

# ==================================
# CSS Tombol Google Maps (DITAMBAHKAN)
# ==================================
st.markdown("""
<style>
.map-button {
    display: inline-block;
    padding: 10px 18px;
    background-color: #4285F4;
    color: white !important;
    border-radius: 10px;
    text-decoration: none;
    font-weight: 600;
    border: 1px solid #3367D6;
    transition: 0.2s;
}
.map-button:hover {
    background-color: #3367D6;
}
</style>
""", unsafe_allow_html=True)

# ==================================
# CSS untuk dua halaman
# ==================================

homepage_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url('https://raw.githubusercontent.com/acah21/test3/3c6e1ac5d34c1efc2b113c0c99113b05c4152e6f/background_gunung.jpeg');
    background-size: cover;
    background-position: center;
}
</style>
"""

recommend_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: #ffffff !important;
}
</style>
"""

# ==================================
# STATE
# ==================================
if "page" not in st.session_state:
    st.session_state.page = "home"

# ==================================
# LOAD DATA
# ==================================
df = pd.read_csv("dataset_gunung_fix.csv")

# ==================================
# SIDEBAR
# ==================================
st.sidebar.header("Pilih Preferensi Pendakian")
province = st.sidebar.selectbox("Provinsi:", sorted(df['Province'].unique()))
difficulty = st.sidebar.selectbox("Tingkat Kesulitan:", sorted(df['difficulty_level'].unique()))
duration = st.sidebar.slider("Durasi Pendakian (jam):", 1, 20, 5)

if st.sidebar.button("Tampilkan Rekomendasi ➜"):
    st.session_state.page = "result"  # pindah halaman

# ==================================
# PAGE 1: HOMEPAGE
# ==================================
if st.session_state.page == "home":
    st.markdown(homepage_bg, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: rgba(255,255,255,0.85);
        padding: 40px;
        border-radius: 20px;
        margin-top: 100px;
        text-align: center;">
        <h1>Selamat Datang di <b>Mount Jawa</b> 🏔️</h1>
        <p>Aplikasi untuk menemukan rekomendasi gunung terbaik di Pulau Jawa.</p>
        <p>Pilih preferensi di sidebar, lalu klik tombol rekomendasi.</p>
    </div>
    """, unsafe_allow_html=True)

# ==================================
# PAGE 2: REKOMENDASI
# ==================================
elif st.session_state.page == "result":
    st.markdown(recommend_bg, unsafe_allow_html=True)

    user_pref = {
        "Province": province,
        "difficulty_level": difficulty,
        "hiking_duration_hours": duration
    }

    rec = recommend(user_pref)

    st.header("🔥 Rekomendasi Gunung Untuk Kamu")

    if isinstance(rec, str):
        st.warning(rec)
    else:
        for idx, row in rec.iterrows():
            st.subheader(row['Name'])

            # Gambar rapih
            img_path = row.get("image_file", None)
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img = img.resize((650, 400))
                    st.image(img)
                except:
                    st.write("📷 Tidak bisa membuka gambar")
            else:
                st.write("📷 Gambar tidak tersedia")

            # Info
            st.markdown(f"- **Provinsi:** {row['Province']}")
            st.markdown(f"- **Elevation:** {row.get('elevation_m', 'N/A')} m")
            st.markdown(f"- **Difficulty:** {row.get('difficulty_level', 'N/A')}")
            st.markdown(f"- **Durasi:** {row.get('hiking_duration_hours', 'N/A')} jam")
            st.markdown(f"- **Recommend For:** {row.get('recommended_for', 'N/A')}")

            # Maps (TOMBOL KOTAK DITAMBAHKAN DI SINI)
            lat, lon = row.get("Latitude"), row.get("Longitude")
            if lat and lon:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                st.markdown(
                    f'<a class="map-button" href="{maps_url}" target="_blank">📍 Lihat di Google Maps</a>',
                    unsafe_allow_html=True
                )

            st.markdown("---")

    # Tombol kembali
    if st.button("⬅️ Kembali ke Beranda"):
        st.session_state.page = "home"
