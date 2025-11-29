# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.models import load_model
import urllib.parse

st.set_page_config(page_title="Mount Jawa", layout="wide")

# ---------- load data & artifacts ----------
df = pd.read_csv("dataset_gunung_preprocessed.csv")
scaler = joblib.load("scaler.pkl")
le_diff = joblib.load("le_diff.pkl")
mlp_model = load_model("mlp_model_gunung.keras", compile=False)

features = ["elevation_scaled","duration_scaled","distance_scaled","gain_scaled","difficulty_encoded"]

# ---------- helper functions ----------
def get_user_vector_from_input(user_input):
    scaled = scaler.transform([[user_input['elevation_m'],
                                user_input['hiking_duration_hours'],
                                user_input['distance_km'],
                                user_input['Elevation_gain']]])[0]
    diff_enc = le_diff.transform([user_input['difficulty_level']])[0]

    return np.array([[scaled[0], scaled[1], scaled[2], scaled[3], diff_enc]])

def content_based_candidates(user_vector, df_local, top_n=20):
    sims = cosine_similarity(user_vector, df_local[features]).flatten()
    df2 = df_local.copy()
    df2["similarity"] = sims
    return df2.sort_values("similarity", ascending=False).head(top_n)

def score_with_mlp(df_candidates):
    Xc = df_candidates[features].values.astype(float)
    preds = mlp_model.predict(Xc).flatten()
    dfc = df_candidates.copy()
    dfc["mlp_score"] = preds
    dfc["final_score"] = dfc["similarity"]*0.6 + dfc["mlp_score"]*0.4
    return dfc.sort_values("final_score", ascending=False)

def maps_link_from_row(row):
    lat = row.get("Latitude")
    lon = row.get("Longitude")
    if pd.notna(lat) and pd.notna(lon):
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(str(row.get("Name","")))

# ---------- UI CSS ----------
st.markdown("""
<style>
.card {
  background-color: white;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
  margin-bottom: 18px;
}
.hero {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HERO SECTION ----------
with st.container():
    st.markdown(
    """
    <div class="hero" style="background-image:url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=80'); background-size:cover; padding:60px;">
        <h1 style="color:white; text-shadow:2px 2px 6px rgba(0,0,0,0.6); font-size:48px; margin:0;">Welcome to Mount Jawa</h1>
        <p style="color:white; text-shadow:1px 1px 4px rgba(0,0,0,0.5); font-size:18px;">Temukan rekomendasi gunung terbaik sesuai preferensimu</p>
    </div>
    """,
    unsafe_allow_html=True)

# ---------- SIDEBAR (FINAL FIXED VERSION) ----------
with st.sidebar:
    st.markdown("## 🎒 Input Pendaki")
    st.markdown("Masukkan preferensi kamu untuk mendapatkan rekomendasi terbaik 💚")
    st.markdown("---")

    st.markdown("### 🌍 Lokasi Pendakian")
    province_options = ["All"] + sorted(df["Province"].dropna().unique().tolist())
    province = st.selectbox("Pilih Provinsi (opsional)", province_options)

    st.markdown("---")
    st.markdown("### 🧭 Preferensi Pendakian")

    elev = st.number_input(
        "Elevasi yang diinginkan (meter)",
        min_value=0, max_value=6000,
        value=int(df["elevation_m"].median())
    )

    dur = st.number_input(
        "Durasi pendakian (jam)",
        min_value=0.5, max_value=72.0,
        value=float(df["hiking_duration_hours"].median())
    )

    dist = st.number_input(
        "Jarak pendakian (km)",
        min_value=0.1, max_value=200.0,
        value=float(df["distance_km"].median())
    )

    gain = st.number_input(
        "Elevation gain (meter)",
        min_value=0, max_value=5000,
        value=int(df["Elevation_gain"].median())
    )

    st.markdown("---")
    st.markdown("### 🧗 Tingkat Kesulitan")

    diff_choices = list(le_diff.classes_)
    difficulty = st.selectbox(
        "Tingkat kesulitan",
        diff_choices,
        index=diff_choices.index("Moderate") if "Moderate" in diff_choices else 0
    )

    st.markdown("---")
    submit = st.button("🔎 Tampilkan Rekomendasi", use_container_width=True)

# ---------- PROCESS ----------
if submit:

    if province != "All":
        df_use = df[df["Province"] == province].reset_index(drop=True)
    else:
        df_use = df.copy()

    user_input = {
        "elevation_m": float(elev),
        "hiking_duration_hours": float(dur),
        "distance_km": float(dist),
        "Elevation_gain": float(gain),
        "difficulty_level": difficulty
    }

    user_vector = get_user_vector_from_input(user_input)
    candidates = content_based_candidates(user_vector, df_use, top_n=20)
    scored = score_with_mlp(candidates).head(10)

    st.subheader("✨ Rekomendasi Gunung untukmu")

    for _, row in scored.iterrows():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # image on top
        img_url = row.get("image_url")
        if isinstance(img_url, str) and img_url.strip() != "":
            st.image(img_url, use_column_width=True)
        else:
            st.image("https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=80")

        # info
        c1, c2 = st.columns([2,1])
        with c1:
            st.markdown(f"### {row['Name']}")
            st.write(f"**Provinsi:** {row['Province']}")
            st.write(f"**Elevasi:** {int(row['elevation_m'])} m")
            st.write(f"**Durasi:** {row['hiking_duration_hours']:.2f} jam")
            st.write(f"**Jarak:** {row['distance_km']} km")
            st.write(f"**Elevation Gain:** {int(row['Elevation_gain'])} m")
            st.write(f"**Kesulitan:** {row['difficulty_level']}")
            if pd.notna(row.get("recommended_for", None)):
                st.write(f"**Direkomendasikan untuk:** {row['recommended_for']}")

        with c2:
            maps_url = maps_link_from_row(row)
            st.markdown(
                f'<a href="{maps_url}" target="_blank">'
                f'<button style="background:#1976d2;color:white;padding:10px 14px;border-radius:8px;border:none;">📍 Lihat Rute</button>'
                f'</a>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)
