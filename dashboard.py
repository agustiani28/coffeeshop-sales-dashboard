# dashboard.py
# Dashboard Interaktif untuk dataset penjualan coffeeshop
# Requirements:
#   pip install streamlit pandas plotly openpyxl
#
# Usage:
#   streamlit run dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG HALAMAN ----------------
st.set_page_config(
    page_title="Dashboard Penjualan Coffeeshop",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- TITLE & DESKRIPSI ----------------
st.title("Dashboard Penjualan Coffeeshop")
st.markdown("""
Dashboard interaktif untuk menganalisis penjualan makanan dan minuman.  
Gunakan filter di sidebar untuk menyesuaikan tampilan grafik & tabel.  
Dataset: **dataset_clean.xlsx**
""")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(path="dataset_clean.xlsx"):
    df = pd.read_excel(path)
    df = df.rename(columns=lambda c: c.strip())

    # Penyesuaian nama kolom jika berbeda huruf besar-kecil
    expected = ["Tanggal", "Kategori", "Nama_Item", "Jumlah", "Total_Penjualan"]
    lower_map = {c.lower(): c for c in df.columns}
    for col in expected:
        if col not in df.columns:
            if col.lower() in lower_map:
                df = df.rename(columns={lower_map[col.lower()]: col})

    # Konversi tipe data
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0).astype(int)
    df["Total_Penjualan"] = pd.to_numeric(df["Total_Penjualan"], errors="coerce").fillna(0)

    # Isi missing value
    df["Kategori"] = df["Kategori"].fillna("Tidak diketahui").astype(str)
    df["Nama_Item"] = df["Nama_Item"].fillna("Tidak diketahui").astype(str)

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error membaca dataset: {e}")
    st.stop()

# ---------------- SIDEBAR FILTER ----------------
st.sidebar.header("Filter Data")

# Filter tanggal
min_date, max_date = df["Tanggal"].min(), df["Tanggal"].max()
date_range = st.sidebar.date_input("Rentang Tanggal", (min_date, max_date))
start_date, end_date = date_range if len(date_range) == 2 else (min_date, max_date)

# Filter kategori
kategori_list = ["Semua"] + sorted(df["Kategori"].unique())
selected_kat = st.sidebar.selectbox("Kategori", kategori_list)

# Filter item
item_list = sorted(df["Nama_Item"].unique())
selected_items = st.sidebar.multiselect("Nama Item", item_list, default=item_list)

# Slider top N
top_n = st.sidebar.slider("Top N Item (Pie Chart)", 3, 20, 8)

# ---------------- APPLY FILTER ----------------
mask = (df["Tanggal"] >= pd.to_datetime(start_date)) & (df["Tanggal"] <= pd.to_datetime(end_date))

if selected_kat != "Semua":
    mask &= (df["Kategori"] == selected_kat)

if selected_items:
    mask &= df["Nama_Item"].isin(selected_items)

filtered = df[mask]

st.markdown(f"**Jumlah data setelah filter: {len(filtered)} baris**")

# ---------- TEMA WARNA ----------
px_template = "plotly_white"
color_seq = px.colors.qualitative.Safe

# ---------------- VISUALISASI ----------------

# ------- ROW 1 → 3 grafik -------
col1, col2, col3 = st.columns(3)

# 1. Bar chart kategori
with col1:
    st.subheader("Total Penjualan per Kategori")
    bar = filtered.groupby("Kategori")["Total_Penjualan"].sum().reset_index()
    fig1 = px.bar(bar, x="Kategori", y="Total_Penjualan", color="Kategori",
                  color_discrete_sequence=color_seq, template=px_template)
    fig1.update_layout(showlegend=False, yaxis_tickformat=",")
    st.plotly_chart(fig1, use_container_width=True)

# 2. Line chart tren waktu
with col2:
    st.subheader("Tren Penjualan Harian")
    line = filtered.groupby("Tanggal")["Total_Penjualan"].sum().reset_index()
    fig2 = px.line(line, x="Tanggal", y="Total_Penjualan", markers=True, template=px_template)
    fig2.update_layout(yaxis_tickformat=",")
    st.plotly_chart(fig2, use_container_width=True)

# 3. Pie / donut chart item
with col3:
    st.subheader(f"Top {top_n} Item Berdasarkan Total Penjualan")
    pie = filtered.groupby("Nama_Item")["Total_Penjualan"].sum().reset_index()
    pie = pie.sort_values("Total_Penjualan", ascending=False).head(top_n)
    fig3 = px.pie(pie, names="Nama_Item", values="Total_Penjualan", hole=0.45, template=px_template)
    st.plotly_chart(fig3, use_container_width=True)

# ------- ROW 2 → Scatter + Histogram -------
col4, col5 = st.columns(2)

with col4:
    st.subheader("Scatter Plot: Jumlah vs Total Penjualan")
    fig4 = px.scatter(filtered, x="Jumlah", y="Total_Penjualan", color="Kategori",
                      hover_data=["Nama_Item"], template=px_template)
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    st.subheader("Distribusi Total Penjualan")
    fig5 = px.histogram(filtered, x="Total_Penjualan", nbins=20, template=px_template)
    st.plotly_chart(fig5, use_container_width=True)

# ---------------- TABEL DATA ----------------
st.subheader("Tabel Data")
display_df = filtered.copy()
display_df["Total_Penjualan"] = display_df["Total_Penjualan"].map("{:,.0f}".format)
st.dataframe(display_df, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("""
**Catatan:**  
- Gunakan slicer di sidebar untuk mengganti tampilan dashboard.  
- Grafik dapat diunduh menggunakan tombol kamera pada pojok kanan grafik.  
""")
