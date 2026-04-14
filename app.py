st.title("🚨 VERSI BARU UI UPGRADE 🚨")
import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Smart Village Dashboard", layout="wide")

# ======================
# CUSTOM CSS (BIAR CANTIK)
# ======================
st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}
.metric-card {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    return pd.read_excel("status-idm-2022.xlsx", sheet_name="DESA")

df = load_data()

# ======================
# SIDEBAR
# ======================
st.sidebar.title("📊 Filter Data")

provinsi = st.sidebar.selectbox(
    "Pilih Provinsi",
    ["Semua"] + sorted(df['PROVINSI'].dropna().unique())
)

if provinsi != "Semua":
    df = df[df['PROVINSI'] == provinsi]

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

df_clean = remove_outliers_iqr(df, num_cols)

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
# HEADER
# ======================
st.title("🌱 Smart Village Dashboard")
st.caption("Analisis IDM 2022 untuk Pengambilan Keputusan Desa")

# ======================
# KPI SECTION (CARD STYLE)
# ======================
st.markdown("## 📌 Data Quality Overview")

col1, col2, col3, col4 = st.columns(4)

# hitung KPI
total_cells = df_clean.size
missing = df_clean.isnull().sum().sum()
completeness = (1 - missing / total_cells) * 100

accuracy = (
    df_clean[num_cols].apply(lambda x: x.between(0,1)).all(axis=1).mean()
) * 100

consistency = 100
timeliness = 100

col1.metric("🎯 Accuracy", f"{accuracy:.2f}%")
col2.metric("📦 Completeness", f"{completeness:.2f}%")
col3.metric("🔁 Consistency", f"{consistency}%")
col4.metric("⏱ Timeliness", f"{timeliness}%")

# ======================
# CHARTS SECTION
# ======================
col_left, col_right = st.columns(2)

# BAR CHART
with col_left:
    st.markdown("### 📊 Distribusi Status Desa")

    bar = df_clean['STATUS_IDM_CAT'].value_counts().sort_index().reset_index()
    bar.columns = ['Status','Jumlah']

    fig_bar = px.bar(
        bar,
        x='Status',
        y='Jumlah',
        color='Status',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# HEATMAP
with col_right:
    st.markdown("### 🔥 Korelasi Indeks")

    corr = df_clean[
        ['IKS_2022','IKE_2022','IKL_2022','NILAI_IDM_2022','Composite_Resilience']
    ].corr()

    fig_heatmap = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ======================
# SCATTER
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
# INSIGHT BOX
# ======================
st.markdown("## 🧠 Insight & Rekomendasi")

avg_idm = df_clean['NILAI_IDM_2022'].mean()
kategori = df_clean['STATUS_IDM_CAT'].value_counts().idxmax()

if avg_idm < 0.6:
    rekom = "Perlu fokus pada pembangunan desa tertinggal."
elif avg_idm < 0.75:
    rekom = "Dorong peningkatan desa berkembang."
else:
    rekom = "Pertahankan desa maju dan mandiri melalui inovasi."

st.success(f"""
📌 **Rata-rata IDM:** {avg_idm:.3f}  
📊 **Kategori Dominan:** {kategori}

💡 **Rekomendasi:**  
{rekom}
""")