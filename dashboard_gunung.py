import streamlit as st
import pandas as pd
from PIL import Image
import io
from modeling_gunung import recommend

# ================================
# CONFIGURASI HALAMAN
# ================================
st.set_page_config(
    page_title="Mount Jawa",
    layout="wide"
)

# ================================
# CSS UNTUK BACKGROUND & BUTTON
# ================================
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1501785888041-af3ef285b470");
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center;
}
.title-home {
    padding: 40px;
    background: rgba(255,255,255,0.8);
    border-radius: 20px;
    text-align: center;
    margin-top: 80px;
}
.btn-map {
    background-color: #4F8BF9;
    color: white;
    padding: 10px 18px;
    border-radius: 10px;
    text-decoration: none;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)


# ================================
# HOMEPAGE (MUNCUL SAAT BELUM INPUT)
# ================================
if "show_result" not in st.session_state:
    st.session_state.show_result = False

if not st.session_state.show_result:
    st.markdown("""
        <div class="title-home">
            <h1>Selamat Datang di <b>Mount Jawa</b> 🏔️</h1>
            <p>Aplikasi rekomendasi pendakian gunung di Pulau Jawa berdasarkan preferensi kamu.
               Pilih provinsi, tingkat kesulitan, dan durasi pendakian yang kamu inginkan.
               Lalu biarkan kami memilihkan gunung terbaik untuk kamu jelajahi!</p>
        </div>
    """, unsafe_allow_html=True)


# ================================
# SIDEBAR INPUT
# ================================
st.sidebar.title("Pilih Preferensi Pendakian")

df = pd.read_csv("dataset_gunung_fix.csv")

provinsi = st.sidebar.selectbox("Provinsi:", sorted(df["provinsi"].unique()))
difficulty = st.sidebar.selectbox("Tingkat Kesulitan:", sorted(df["difficulty"].unique()))
durasi = st.sidebar.slider("Durasi Pendakian Maksimal (jam):", 1, 20, 6)

tampil = st.sidebar.button("Tampilkan Rekomendasi")

if tampil:
    st.session_state.show_result = True
    results = recommend(provinsi, difficulty, durasi)


# ================================
# HASIL REKOMENDASI
# ================================
if st.session_state.show_result:

    st.markdown("<h2>🔥 Rekomendasi Gunung Berdasarkan Preferensimu:</h2>", unsafe_allow_html=True)

    if len(results) == 0:
        st.warning("Tidak ada gunung yang cocok dengan preferensimu.")
    else:
        for _, row in results.iterrows():

            # Bikin ukuran gambar seragam
            try:
                img = Image.open(f"images/{row['image']}")
                img = img.resize((650, 400))  # seragam & lebih besar
            except:
                img = None

            st.markdown(f"### {row['nama_gunung']}")

            if img:
                st.image(img, use_column_width=False)

            st.markdown(f"""
            - **Provinsi:** {row['provinsi']}
            - **Elevation:** {row['elevation']} m  
            - **Difficulty:** {row['difficulty']}
            - **Durasi Rata-rata:** {row['durasi']} jam
            """)

            maps_url = row["maps_url"]
            st.markdown(f'<a class="btn-map" href="{maps_url}" target="_blank">📍 Lihat Rute di Maps</a>', unsafe_allow_html=True)

            st.markdown("---")
