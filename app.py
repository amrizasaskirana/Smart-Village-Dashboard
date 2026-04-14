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
# CLEANING
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
# KPI DATA QUALITY
# ======================
st.subheader("Data Quality Metrics")

col1, col2, col3, col4 = st.columns(4)

# Completeness
total_cells = df_clean.shape[0] * df_clean.shape[1]
missing_cells = df_clean.isnull().sum().sum()
completeness = (1 - (missing_cells / total_cells)) * 100

# Accuracy
valid_range = df_clean[
    (df_clean['IKS_2022'].between(0,1)) &
    (df_clean['IKE_2022'].between(0,1)) &
    (df_clean['IKL_2022'].between(0,1)) &
    (df_clean['NILAI_IDM_2022'].between(0,1))
].shape[0]
accuracy = (valid_range / len(df_clean)) * 100

# Consistency
calc_check = (
    df_clean['Composite_Resilience'] ==
    (df_clean['IKS_2022'] + df_clean['IKE_2022'] + df_clean['IKL_2022'])
)
consistency = (calc_check.sum() / len(df_clean)) * 100

# Timeliness
timeliness = 100

col1.metric("Accuracy", f"{accuracy:.2f}%")
col2.metric("Completeness", f"{completeness:.2f}%")
col3.metric("Consistency", f"{consistency:.2f}%")
col4.metric("Timeliness", f"{timeliness}%")

# ======================
# BAR CHART
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
# HEATMAP
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
# SCATTER
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

# ======================
# REKOMENDASI
# ======================
st.subheader("Rekomendasi Strategis")

avg_idm = df_clean['NILAI_IDM_2022'].mean()
kategori_terbanyak = df_clean['STATUS_IDM_CAT'].value_counts().idxmax()

if avg_idm < 0.6:
    rekom = "Fokus pada peningkatan infrastruktur dan ekonomi desa tertinggal."
elif avg_idm < 0.75:
    rekom = "Perkuat program pemberdayaan desa berkembang menuju desa maju."
else:
    rekom = "Optimalkan inovasi dan digitalisasi untuk mempertahankan desa mandiri."

st.info(f"""
📌 Rata-rata Nilai IDM: **{avg_idm:.3f}**  
📊 Kategori Dominan: **{kategori_terbanyak}**

💡 **Rekomendasi:**
{rekom}
""")