import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Judul Dashboard
st.title("Dashboard Smart Village - IDM 2022")

# Load dataset
df = pd.read_excel("status-idm-2022.xlsx", sheet_name="DESA")

# Preview dataset
st.subheader("Preview Dataset Desa")
st.dataframe(df.head())

# Bar chart distribusi desa per kategori
st.subheader("Distribusi Desa per Kategori STATUS_IDM_CAT")
bar_fig = px.bar(df['STATUS_IDM_CAT'].value_counts().sort_index(),
                 labels={'index':'Kategori Desa','value':'Jumlah Desa'},
                 title="Jumlah Desa per Kategori STATUS_IDM_CAT")
st.plotly_chart(bar_fig)

# Heatmap korelasi
st.subheader("Heatmap Korelasi Indeks Desa")
num_cols = ['IKS_2022','IKE_2022','IKL_2022','NILAI_IDM_2022']
corr = df[num_cols].corr()
plt.figure(figsize=(6,4))
sns.heatmap(corr, annot=True, cmap='coolwarm')
st.pyplot(plt)

# Scatter plot Composite vs Nilai IDM
st.subheader("Scatter Plot Composite Resilience vs Nilai IDM")
scatter_fig = px.scatter(df, x='NILAI_IDM_2022', y='Composite_Resilience',
                         color='STATUS_IDM_CAT',
                         labels={'NILAI_IDM_2022':'Nilai IDM','Composite_Resilience':'Composite Resilience'},
                         title='Composite Resilience vs Nilai IDM')
st.plotly_chart(scatter_fig)
