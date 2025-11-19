import streamlit as st
import pandas as pd
import plotly.express as px

# KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Dashboard Atlet Disabilitas DKI Jakarta 2024",
    layout="wide",
    page_icon="🏅"
)

st.markdown(
    "<h1 style='text-align: center; color:#0066CC;'>🏅 Dashboard Atlet Disabilitas DKI Jakarta 2024</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)

# LOAD DATA
@st.cache_data
def load_data():
    return pd.read_excel("data-atlet-disabilitas.xlsx")

try:
    df = load_data()
    st.success("✅ Data berhasil dimuat dari file: data-atlet-disabilitas.xlsx")

    # PEMBERSIHAN DATA
    df.columns = df.columns.str.strip().str.lower()

    # Normalisasi teks agar konsisten
    text_cols = ["wilayah_domisili", "cabang_olahraga", "jenis_kelamin", "kategori_ketunaan"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Ganti data kosong dengan label default
    df = df.fillna({
        "wilayah_domisili": "Tidak Diketahui",
        "cabang_olahraga": "Tidak Diketahui",
        "jenis_kelamin": "Tidak Diketahui",
        "kategori_ketunaan": "Tidak Diketahui"
    })

    # FILTER
    st.sidebar.header("Filter Data")
    selected_wilayah = st.sidebar.multiselect(
        "Pilih Wilayah Domisili:",
        options=sorted(df["wilayah_domisili"].unique()),
        default=sorted(df["wilayah_domisili"].unique())
    )
    selected_cabor = st.sidebar.multiselect(
        "Pilih Cabang Olahraga:",
        options=sorted(df["cabang_olahraga"].unique()),
        default=sorted(df["cabang_olahraga"].unique())
    )

    # Filter data sesuai pilihan (lebih toleran terhadap data kosong)
    df_filtered = df[
        (df["wilayah_domisili"].isin(selected_wilayah) | (df["wilayah_domisili"] == "Tidak Diketahui")) &
        (df["cabang_olahraga"].isin(selected_cabor) | (df["cabang_olahraga"] == "Tidak Diketahui"))
    ]

    # KPI CARDS
    st.markdown("## 📊 Statistik Utama")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Atlet", len(df_filtered))
    col2.metric("Cabang Olahraga", df_filtered["cabang_olahraga"].nunique())
    col3.metric("Kategori Ketunaan", df_filtered["kategori_ketunaan"].nunique())
    col4.metric("Wilayah Domisili", df_filtered["wilayah_domisili"].nunique())

    st.markdown("<hr>", unsafe_allow_html=True)

    # VISUALISASI DATA
    col1, col2 = st.columns(2)

    # Grafik 1: Jenis Kelamin
    with col1:
        gender_count = df_filtered["jenis_kelamin"].value_counts().reset_index()
        gender_count.columns = ["Jenis Kelamin", "Jumlah"]
        fig_gender = px.pie(
            gender_count,
            names="Jenis Kelamin",
            values="Jumlah",
            title="Distribusi Atlet Berdasarkan Jenis Kelamin",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_gender.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_gender, use_container_width=True)

    # Grafik 2: Cabang Olahraga
    with col2:
        sport_count = df_filtered["cabang_olahraga"].value_counts().reset_index()
        sport_count.columns = ["Cabang Olahraga", "Jumlah"]
        fig_sport = px.bar(
            sport_count,
            x="Cabang Olahraga",
            y="Jumlah",
            title="Jumlah Atlet per Cabang Olahraga",
            color="Cabang Olahraga",
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Set3  

        )
        fig_sport.update_layout(xaxis_title=None, yaxis_title="Jumlah Atlet")
        st.plotly_chart(fig_sport, use_container_width=True)
        st.markdown("")

    # KATEGORI & WILAYAH
    st.markdown("## ♿ Distribusi Berdasarkan Ketunaan dan Wilayah")

    col3, col4 = st.columns(2)

    # Grafik 3: Kategori Ketunaan
    with col3:
        dis_count = df_filtered["kategori_ketunaan"].value_counts().reset_index()
        dis_count.columns = ["Kategori Ketunaan", "Jumlah"]
        fig_dis = px.bar(
            dis_count,
            x="Kategori Ketunaan",
            y="Jumlah",
            title="Atlet Berdasarkan Kategori Ketunaan",
            color="Kategori Ketunaan",
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_dis.update_layout(xaxis_title=None, yaxis_title="Jumlah Atlet")
        st.plotly_chart(fig_dis, use_container_width=True)

    # Grafik 4: Sebaran Wilayah
    with col4:
        wilayah_count = df_filtered["wilayah_domisili"].value_counts().reset_index()
        wilayah_count.columns = ["Wilayah Domisili", "Jumlah"]
        fig_wilayah = px.bar(
            wilayah_count,
            x="Wilayah Domisili",
            y="Jumlah",
            title="Sebaran Atlet Berdasarkan Wilayah Domisili",
            color="Wilayah Domisili",
            text_auto=True,
            color_discrete_sequence=px.colors.sequential.Teal_r
        )
        fig_wilayah.update_layout(xaxis_title=None, yaxis_title="Jumlah Atlet")
        st.plotly_chart(fig_wilayah, use_container_width=True)

    # TABEL DETAIL
    st.markdown("## 📋 Detail Data Atlet")
    st.dataframe(df_filtered, use_container_width=True, height=400)

    # FOOTER
    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("© Dev Dashboard Atlet Disabilitas — Satu Data Jakarta")


# ⚠️ HANDLING FILE ERROR
except FileNotFoundError:
    st.error("❌ File 'data-atlet-disabilitas.xlsx' tidak ditemukan di folder proyek.")
    st.info("Pastikan file berada di direktori yang sama dengan script ini.")
