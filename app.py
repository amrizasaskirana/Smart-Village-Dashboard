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
# LOAD DATA (SAFE)
# ======================
@st.cache_data
def load_data():
    return pd.read_excel("status-idm-2022.xlsx", sheet_name="DESA")

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
# VALIDASI KOLOM
# ======================
required_cols = ['STATUS_IDM_CAT','IKS_2022','IKE_2022','IKL_2022','NILAI_IDM_2022']

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Kolom tidak ditemukan: {missing_cols}")
    st.stop()

# ======================
# BAR CHART
# ======================
st.subheader("Distribusi Desa per Kategori STATUS_IDM_CAT")

bar_data = df['STATUS_IDM_CAT'].value_counts().reset_index()
bar_data.columns = ['Kategori Desa', 'Jumlah Desa']

bar_fig = px.bar(
    bar_data,
    x='Kategori Desa',
    y='Jumlah Desa',
    title="Jumlah Desa per Kategori"
)

st.plotly_chart(bar_fig, use_container_width=True)

# ======================
# HEATMAP
# ======================
st.subheader("Heatmap Korelasi Indeks Desa")

num_cols = ['IKS_2022','IKE_2022','IKL_2022','NILAI_IDM_2022']
corr = df[num_cols].corr()

fig, ax = plt.subplots()
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)

st.pyplot(fig)

# ======================
# SCATTER PLOT
# ======================
st.subheader("Scatter Plot Composite Resilience vs Nilai IDM")

if 'Composite_Resilience' in df.columns:
    scatter_fig = px.scatter(
        df,
        x='NILAI_IDM_2022',
        y='Composite_Resilience',
        color='STATUS_IDM_CAT',
        title='Composite Resilience vs Nilai IDM'
    )
    st.plotly_chart(scatter_fig, use_container_width=True)
else:
    st.warning("Kolom 'Composite_Resilience' belum tersedia di dataset")
