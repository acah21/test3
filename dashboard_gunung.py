# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from PIL import Image
from modeling_gunung import recommend  # pastikan modeling_gunung.py sudah ada

# ===============================
# CONFIGURASI HALAMAN
# ===============================
st.set_page_config(
    page_title="Mount Jawa",
    layout="wide"
)

# ===============================
# CSS KUSTOM
# ===============================
page_style = """
<style>
/* Background halaman awal */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1501785888041-af3ef285b470");
    background-size: cover;
    background-position: center;
}

/* Box selamat datang */
.welcome-box {
    margin-top: 80px;
    padding: 40px;
    background: rgba(255, 255, 255, 0.85);
    border-radius: 20px;
    text-align: center;
}

/* Tombol google maps */
.maps-btn {
    background-color: #4F8BF9;
    color: white;
    padding: 10px 16px;
    border-radius: 10px;
    text-decoration: none;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# ===============================
# LOAD DATASET
# ===============================
df = pd.read_csv("dataset_gunung_fix.csv")

# Session state untuk kontrol tampilan
if "show_result" not in st.session_state:
    st.session_state.show_result = False

# ===============================
# HALAMAN AWAL
# ===============================
if not st.session_state.show_result:
    st.markdown("""
        <div class="welcome-box">
            <h1>Selamat Datang di <b>Mount Jawa</b> 🏔️</h1>
            <p>Aplikasi rekomendasi pendakian gunung di Pulau Jawa berdasarkan preferensi kamu.
            Pilih provinsi, tingkat kesulitan, dan durasi. Kemudian biarkan sistem memberikan rekomendasi terbaik.</p>
        </div>
    """, unsafe_allow_html=True)

# ===============================
# SIDEBAR INPUT USER
# ===============================
st.sidebar.header("Pilih Preferensi Pendakian")

province = st.sidebar.selectbox("Provinsi:", options=sorted(df['Province'].unique()))
difficulty = st.sidebar.selectbox("Tingkat Kesulitan:", options=sorted(df['difficulty_level'].unique()))
duration = st.sidebar.slider("Durasi Pendakian (jam):", min_value=1, max_value=20, value=5)

if st.sidebar.button("Tampilkan Rekomendasi"):
    st.session_state.show_result = True
    
    user_pref = {
        'Province': province,
        'difficulty_level': difficulty,
        'hiking_duration_hours': duration
    }

    recommendations = recommend(user_pref)

# ===============================
# TAMPILKAN HASIL REKOMENDASI
# ===============================
if st.session_state.show_result:

    st.header("🔥 Rekomendasi Gunung Berdasarkan Preferensi Kamu:")

    if isinstance(recommendations, str):
        st.warning(recommendations)

    else:
        for idx, row in recommendations.iterrows():
            st.subheader(row['Name'])

            # ===============================
            # FOTO
            # ===============================
            image_path = row.get('image_file', None)

            if image_path and os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img = img.resize((650, 400))  # ukuran seragam landscape
                    st.image(img)
                except:
                    st.write("📷 Gambar tidak dapat ditampilkan")
            else:
                st.write("📷 Gambar tidak tersedia")

            # ===============================
            # INFORMASI
            # ===============================
            st.markdown(f"- **Provinsi:** {row['Province']}")
            st.markdown(f"- **Elevation:** {row.get('elevation_m','N/A')} m")
            st.markdown(f"- **Difficulty:** {row.get('difficulty_level','N/A')}")
            st.markdown(f"- **Durasi Pendakian:** {row.get('hiking_duration_hours','N/A')} jam")
            st.markdown(f"- **Recommend For:** {row.get('recommended_for','N/A')}")

            # ===============================
            # LINK GOOGLE MAPS
            # ===============================
            if 'Latitude' in row and 'Longitude' in row:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}"
                st.markdown(f'<a class="maps-btn" href="{maps_url}" target="_blank">📍 Lihat Rute di Google Maps</a>',
                            unsafe_allow_html=True)

            st.markdown("---")
