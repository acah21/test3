# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from modeling_gunung import recommend  # pastikan modeling_gunung.py sudah diupload

# ===============================
# 1️⃣ Load Dataset
# ===============================
df = pd.read_csv("dataset_gunung_fix.csv")  # dataset dengan kolom 'image_file', 'Latitude', 'Longitude'

# ===============================
# 2️⃣ Sidebar Input User
# ===============================
st.sidebar.header("Pilih Preferensi Pendakian")

province = st.sidebar.selectbox("Provinsi:", options=df['Province'].unique())
difficulty = st.sidebar.selectbox("Tingkat Kesulitan:", options=df['difficulty_level'].unique())
duration = st.sidebar.slider("Durasi Pendakian (jam):", min_value=1, max_value=12, value=4)
top_n = st.sidebar.slider("Jumlah Rekomendasi:", min_value=1, max_value=10, value=5)

if st.sidebar.button("Tampilkan Rekomendasi"):

    # ===============================
    # 3️⃣ Buat dictionary input user
    # ===============================
    user_pref = {
        'Province': province,
        'difficulty_level': difficulty,
        'hiking_duration_hours': duration
    }

    # ===============================
    # 4️⃣ Panggil fungsi recommend dari modeling
    # ===============================
    recommendations = recommend(user_pref, top_n=top_n)

    # ===============================
    # 5️⃣ Tampilkan rekomendasi
    # ===============================
    if isinstance(recommendations, str):
        st.warning(recommendations)
    else:
        st.header("🔥 Rekomendasi Gunung Berdasarkan Preferensi Kamu:")
        for idx, row in recommendations.iterrows():
            st.subheader(row['Name'])
            
            # Tampilkan foto dari folder images/
            image_path = row.get('image_file', None)
            if image_path and os.path.exists(image_path):
                st.image(image_path, width=300)
            else:
                st.write("📷 Gambar tidak tersedia")
            
            # Informasi lengkap
            st.markdown(f"- **Provinsi:** {row['Province']}")
            st.markdown(f"- **Elevation:** {row.get('elevation_m','N/A')} m")
            st.markdown(f"- **Difficulty:** {row.get('difficulty_level','N/A')}")
            st.markdown(f"- **Hiking Duration:** {row.get('hiking_duration_hours','N/A')} jam")
            st.markdown(f"- **Recommended for:** {row.get('recommended_for','N/A')}")
            
            # Link Google Maps
            if 'Latitude' in row and 'Longitude' in row:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}"
                st.markdown(f"[🔗 Lihat Rute di Google Maps]({maps_url})")
            
            st.markdown("---")  # garis pemisah antar rekomendasi

# ===============================
# 6️⃣ Footer Info
# ===============================
st.sidebar.markdown("💡 Sistem menggunakan metode Content-Based Filtering + MLP")
st.sidebar.markdown("📂 Pastikan dataset dan folder images berada di lokasi yang sama dengan notebook")
