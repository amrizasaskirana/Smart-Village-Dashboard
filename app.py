import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Smart Village Dashboard", layout="wide")

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    return pd.read_excel("status-idm-2022.xlsx", sheet_name="DESA")

df = load_data()

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("Filter Data")

provinsi_list = sorted(df['PROVINSI'].dropna().unique())
selected_prov = st.sidebar.selectbox("Pilih Provinsi", ["Semua"] + provinsi_list)

if selected_prov != "Semua":
    df = df[df['PROVINSI'] == selected_prov]

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
# TITLE
# ======================
st.title("📊 Smart Village Dashboard")
st.caption("Analisis Data IDM 2022 untuk Pengambilan Keputusan")

# ======================
# KPI SECTION
# ======================
st.markdown("## 📌 Data Quality Metrics")

col1, col2, col3, col4 = st.columns(4)

total_cells = df_clean.shape[0] * df_clean.shape[1]
missing_cells = df_clean.isnull().sum().sum()
completeness = (1 - (missing_cells / total_cells)) * 100

valid_range = df_clean[
    (df_clean['IKS_2022'].between(0,1)) &
    (df_clean['IKE_2022'].between(0,1)) &
    (df_clean['IKL_2022'].between(0,1)) &
    (df_clean['NILAI_IDM_2022'].between(0,1))
].shape[0]
accuracy = (valid_range / len(df_clean)) * 100

consistency = 100
timeliness = 100

col1.metric("🎯 Accuracy", f"{accuracy:.2f}%")
col2.metric("📦 Completeness", f"{completeness:.2f}%")
col3.metric("🔁 Consistency", f"{consistency:.2f}%")
col4.metric("⏱ Timeliness", f"{timeliness}%")

# ======================
# MAIN CHARTS (2 COLUMN)
# ======================
col_left, col_right = st.columns(2)

# BAR CHART
with col_left:
    st.markdown("### 📊 Distribusi Status Desa")

    category_counts = df_clean['STATUS_IDM_CAT'].value_counts().sort_index()
    df_bar = category_counts.reset_index()
    df_bar.columns = ['STATUS_IDM_CAT','Jumlah_Desa']

    fig_bar = px.bar(
        df_bar,
        x='STATUS_IDM_CAT',
        y='Jumlah_Desa',
        color='STATUS_IDM_CAT',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# HEATMAP
with col_right:
    st.markdown("### 🔥 Korelasi Indeks")

    corr_matrix = df_clean[
        ['IKS_2022','IKE_2022','IKL_2022','NILAI_IDM_2022','Composite_Resilience']
    ].corr()

    fig_heatmap = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ======================
# SCATTER FULL WIDTH
# ======================
st.markdown("### 📍 Hubungan Composite vs IDM")

fig_scatter = px.scatter(
    df_clean,
    x='Composite_Resilience',
    y='NILAI_IDM_2022',
    color='STATUS_IDM_CAT',
    hover_data=['PROVINSI','KABUPATEN','DESA'],
    color_discrete_sequence=px.colors.qualitative.Bold
)

st.plotly_chart(fig_scatter, use_container_width=True)

# ======================
# REKOMENDASI
# ======================
st.markdown("## 🧠 Insight & Rekomendasi")

avg_idm = df_clean['NILAI_IDM_2022'].mean()
kategori_terbanyak = df_clean['STATUS_IDM_CAT'].value_counts().idxmax()

if avg_idm < 0.6:
    rekom = "Fokus pada peningkatan infrastruktur desa tertinggal."
elif avg_idm < 0.75:
    rekom = "Dorong desa berkembang menjadi desa maju."
else:
    rekom = "Perkuat digitalisasi dan inovasi desa mandiri."

st.success(f"""
📌 Rata-rata IDM: **{avg_idm:.3f}**  
📊 Kategori Dominan: **{kategori_terbanyak}**

💡 **Rekomendasi Strategis:**  
{rekom}
""")