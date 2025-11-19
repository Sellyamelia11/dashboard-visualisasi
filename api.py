from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(
    title="API Data Atlet Disabilitas DKI Jakarta",
)

# Izinkan akses dari mana saja (boleh Streamlit / domain lain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# LOAD DATA
# ------------------------------
def load_data():
    df = pd.read_excel("data-atlet-disabilitas.xlsx")

    # Normalisasi kolom seperti dashboard streamlit
    df.columns = df.columns.str.strip().str.lower()

    text_cols = ["wilayah_domisili", "cabang_olahraga", "jenis_kelamin", "kategori_ketunaan"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    df = df.fillna({
        "wilayah_domisili": "Tidak Diketahui",
        "cabang_olahraga": "Tidak Diketahui",
        "jenis_kelamin": "Tidak Diketahui",
        "kategori_ketunaan": "Tidak Diketahui"
    })

    return df


# ENDPOINTS

@app.get("/")
def root():
    return {"status": "OK", "message": "API Atlet Disabilitas aktif"}

@app.get("/atlet")
def get_all_data():
    try:
        df = load_data()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/atlet/{row_id}")
def get_single(row_id: int):
    df = load_data()

    if row_id < 0 or row_id >= len(df):
        raise HTTPException(status_code=404, detail="ID tidak ditemukan")

    return df.iloc[row_id].to_dict()

@app.get("/jeniskelamin")
def get_jk():
    df = load_data()
    jk = sorted(df["jenis_kelamin"].unique())
    return {"jk": jk}

@app.get("/wilayah")
def get_wilayah():
    df = load_data()
    wilayah = sorted(df["wilayah_domisili"].unique())
    return {"wilayah": wilayah}

@app.get("/cabor")
def get_cabor():
    df = load_data()
    cabor = sorted(df["cabang_olahraga"].unique())
    return {"cabang_olahraga": cabor}

@app.get("/periode")
def get_periode():
    df = load_data()

    if "periode_data" not in df.columns:
        raise HTTPException(status_code=404, detail="Kolom 'periode_data' tidak ditemukan")

    # Ekstrak tahun (format 4 digit)
    df["periode_data"] = (
        df["periode_data"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
        .astype("Int64")
    )

    tahun_unik = sorted(df["periode_data"].dropna().unique().tolist())

    return {"periode_data": tahun_unik}


@app.get("/periode/count")
def get_periode_count():
    df = load_data()

    if "periode_data" not in df.columns:
        raise HTTPException(status_code=404, detail="Kolom 'periode_data' tidak ditemukan")

    df["periode_data"] = (
        df["periode_data"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
        .astype("Int64")
    )

    # Hitung jumlah per tahun
    periode_count = (
        df["periode_data"]
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    periode_count.columns = ["tahun", "jumlah_atlet"]
    periode_count["jumlah_atlet"] = periode_count["jumlah_atlet"].astype(int)

    return periode_count.to_dict(orient="records")
