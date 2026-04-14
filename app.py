import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Smart Village Dashboard", layout="wide")

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    file_path = "status-idm-2022.xlsx"
    df = pd.read_excel(file_path, sheet_name="DESA")
    return df

df = load_data()

# ======================
# TITLE
# ======================
st.title("Dashboard Smart Village - IDM 2022")

# ======================
# PREVIEW DATA
# ======================
st.subheader("Preview Dataset Desa")
st.dataframe(df.head())

# ======================
# CLEANING (SAMA SEPERTI COLAB)
# ======================
num_cols = ['IKS_2022','IKE_2022','IKL_2022','NILAI_IDM_2022']

def remove_outliers_iqr(df, columns):
    df_clean = df.copy()
    for col in columns:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df_clean = df_clean[(df_clean[col] >= lower) & (df_clean[col] <= upper)]
    return df_clean

df_clean = df.drop_duplicates()
df_clean = remove_outliers_iqr(df_clean, num_cols)

# ======================
# FEATURE ENGINEERING
# ======================
df_clean['Composite_Resilience'] = (
    df_clean['IKS_2022'] +
    df_clean['IKE_2022'] +
    df_clean['IKL_2022']
)

status_order = ['SANGAT TERTINGGAL','TERTINGGAL','BERKEMBANG','MAJU','MANDIRI']
df_clean['STATUS_IDM_CAT'] = pd.Categorical(
    df_clean['STATUS_IDM_2022'],
    categories=status_order,
    ordered=True
)

# ======================
# BAR CHART (SESUAI COLAB)
# ======================
st.subheader("Distribusi Desa Berdasarkan Status IDM 2022")

category_counts = df_clean['STATUS_IDM_CAT'].value_counts().sort_index()
df_bar = category_counts.reset_index()
df_bar.columns = ['STATUS_IDM_CAT','Jumlah_Desa']

fig_bar = px.bar(
    df_bar,
    x='STATUS_IDM_CAT',
    y='Jumlah_Desa',
    color='STATUS_IDM_CAT',
    title='Distribusi Desa Berdasarkan Status IDM 2022',
    color_discrete_sequence=px.colors.qualitative.Vivid
)

st.plotly_chart(fig_bar, use_container_width=True)

# ======================
# HEATMAP (PLOTLY BIAR AMAN)
# ======================
st.subheader("Heatmap Korelasi Indeks Desa 2022")

corr_matrix = df_clean[
    ['IKS_2022','IKE_2022','IKL_2022','NILAI_IDM_2022','Composite_Resilience']
].corr()

fig_heatmap = px.imshow(
    corr_matrix,
    text_auto='.2f',
    color_continuous_scale='RdBu_r',
    title='Heatmap Korelasi Indeks Desa 2022'
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# ======================
# SCATTER (SESUAI COLAB)
# ======================
st.subheader("Composite Resilience vs Nilai IDM")

fig_scatter = px.scatter(
    df_clean,
    x='Composite_Resilience',
    y='NILAI_IDM_2022',
    color='STATUS_IDM_CAT',
    hover_data=['PROVINSI','KABUPATEN','KECAMATAN','DESA'],
    title='Composite Resilience vs Nilai IDM 2022',
    color_discrete_sequence=px.colors.qualitative.Vivid
)

st.plotly_chart(fig_scatter, use_container_width=True)