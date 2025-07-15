
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker   
import plotly.express as px
import seaborn as sns

# Load data
df = pd.read_csv('/Users/adityawillianyudhistira/Documents/data_penjualan_1juta.csv')
df['tanggal'] = pd.to_datetime(df['tanggal'])  # Pastikan kolom tanggal bertipe datetime
df = df.sort_values('tanggal')  # Urutkan berdasarkan tanggal

#Jumlah Penjualan per Kategori
jumlah_penjualan_per_kategori = df.groupby('kategori')['jumlah'].sum().reset_index()
jumlah_penjualan_per_kategori = jumlah_penjualan_per_kategori.sort_values(by='jumlah', ascending=False)
print("Jumlah Penjualan per Kategori:", jumlah_penjualan_per_kategori)
#Jumlah Penjualan Per Produk
jumlah_penjualan_per_produk = df.groupby('nama_produk')['jumlah'].sum().reset_index()
jumlah_penjualan_per_produk = jumlah_penjualan_per_produk.sort_values(by='jumlah', ascending=False)
print("Jumlah Penjualan per Produk:", jumlah_penjualan_per_produk)  
#Jumlah Penjualan Per Kota
jumlah_penjualan_per_kota = df.groupby('kota')['jumlah'].sum().reset_index()
jumlah_penjualan_per_kota = jumlah_penjualan_per_kota.sort_values(by='jumlah', ascending=False)
print("Jumlah Penjualan per Kota:", jumlah_penjualan_per_kota)
#Jumlah Penjualan
jumlah_penjualan = df['jumlah'].sum()
print("Jumlah Penjualan: ", jumlah_penjualan)   


#Total Omset Per Kategori
total_omset_per_kategori = df.groupby('kategori')['harga_satuan'].sum().reset_index()
total_omset_per_kategori = total_omset_per_kategori.sort_values(by='harga_satuan', ascending=False)
print("Total Omset per Kategori:", total_omset_per_kategori)
#Total Omset Per Produk
total_omset_per_produk = df.groupby('nama_produk')['harga_satuan'].sum().reset_index()
total_omset_per_produk = total_omset_per_produk.sort_values(by='harga_satuan', ascending=False)
print("Total Omset per Produk:", total_omset_per_produk)
#Total Omset Per Kota
total_omset_per_kota = df.groupby('kota')['harga_satuan'].sum().reset_index()
total_omset_per_kota = total_omset_per_kota.sort_values(by='harga_satuan', ascending=False)
print("Total Omset per Kota:", total_omset_per_kota)
#Total Omset
total_omset = df['harga_satuan'].sum()
print("Total Omset: ", total_omset)         

#Produk Penjualan Tertinggi
produk_terlaris = df.groupby('nama_produk')['jumlah'].sum().sort_values(ascending=False).head(10)
print("Produk Terlaris:", produk_terlaris)


#Tren Penjualan Per kuartal
trends_per_quarter = df.resample('QE', on='tanggal').sum().reset_index()
trends_per_quarter['tanggal'] = pd.to_datetime(trends_per_quarter['tanggal'])
trends_per_quarter = trends_per_quarter.sort_values('tanggal')
print("Tren Penjualan Per Kuartal:", trends_per_quarter)

#Prediksi Penjualan 
from statsmodels.tsa.holtwinters import ExponentialSmoothing
model = ExponentialSmoothing(trends_per_quarter['jumlah'], trend='add', seasonal=None, seasonal_periods=12)
fit = model.fit()
predictions = fit.forecast(12)  # Memprediksi 12 bulan ke depan
print("Prediksi Penjualan 12 Bulan ke Depan:", predictions)


#Dashboard Visualisasi streamlit
import streamlit as st
import plotly.express as px
# ============ LOAD DATA ============
df = pd.read_csv('/Users/adityawillianyudhistira/Documents/data_penjualan_1juta.csv', parse_dates=['tanggal'])

# ============ PREPROCESSING ============
df['bulan'] = df['tanggal'].dt.to_period('M').astype(str)
df['hari'] = df['tanggal'].dt.day_name()
df['jam'] = df['tanggal'].dt.hour

# ============ FILTERS ============
st.set_page_config(page_title="Dashboard Penjualan", layout="wide")
st.title("📊 Dashboard Penjualan")

st.sidebar.header("🎯 Filter Data")
filter_kota = st.sidebar.multiselect("Pilih Kota", options=sorted(df['kota'].unique()), default=df['kota'].unique())
filter_kategori = st.sidebar.multiselect("Pilih Kategori", options=sorted(df['kategori'].unique()), default=df['kategori'].unique())
filter_produk = st.sidebar.multiselect("Pilih Produk", options=sorted(df['nama_produk'].unique()), default=df['nama_produk'].unique())
filter_tanggal = st.sidebar.date_input("Pilih Rentang Tanggal", [df['tanggal'].min(), df['tanggal'].max()])

# Filter dataframe
df_filtered = df[
    (df['kota'].isin(filter_kota)) &
    (df['kategori'].isin(filter_kategori)) &
    (df['nama_produk'].isin(filter_produk)) &
    (df['tanggal'] >= pd.to_datetime(filter_tanggal[0])) &
    (df['tanggal'] <= pd.to_datetime(filter_tanggal[1]))
]

# ============ METRICS ============
total_omset = int((df_filtered['harga_satuan'] * df_filtered['jumlah']).sum())
jumlah_penjualan = int(df_filtered['jumlah'].sum())

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Total Omset", value=f"Rp {total_omset:,.0f}".replace(",", "."))
with col2:
    st.metric(label="Total Penjualan", value=f"{jumlah_penjualan:,} Unit".replace(",", "."))
st.markdown("---")

# ============ TREN PENJUALAN ============
st.subheader("📈 Tren Penjualan")
tren_bulanan = df_filtered.groupby('bulan')['jumlah'].sum().reset_index()
fig_tren = px.line(tren_bulanan, x='bulan', y='jumlah', markers=True, title="")
fig_tren.update_layout(xaxis_title=None, yaxis_title=None)
st.plotly_chart(fig_tren, use_container_width=True)

# ============ PRODUK TERTINGGI & TERENDAH ============
col3, col4 = st.columns(2)

produk_tertinggi = df_filtered.groupby('nama_produk')['jumlah'].sum().nlargest(3).reset_index()
produk_tertinggi['text_format'] = produk_tertinggi['jumlah'].apply(lambda x: f"{x:,}".replace(",", "."))

produk_terendah = df_filtered.groupby('nama_produk')['jumlah'].sum().nsmallest(3).reset_index()
produk_terendah['text_format'] = produk_terendah['jumlah'].apply(lambda x: f"{x:,}".replace(",", "."))

with col3:
    st.subheader("🔥 Penjualan Tertinggi (Unit)")
    fig_top = px.bar(produk_tertinggi, x='jumlah', y='nama_produk', orientation='h', text='text_format')
    fig_top.update_layout(xaxis_title=None, yaxis_title=None)
    fig_top.update_traces(textposition='inside')
    st.plotly_chart(fig_top, use_container_width=True)

with col4:
    st.subheader("🧊 Penjualan Terendah (Unit)")
    fig_low = px.bar(produk_terendah, x='jumlah', y='nama_produk', orientation='h', text='text_format')
    fig_low.update_layout(xaxis_title=None, yaxis_title=None)
    fig_low.update_traces(textposition='inside')
    st.plotly_chart(fig_low, use_container_width=True)

# ============ PIE PER KATEGORI ============
st.subheader("🍰 Distribusi Penjualan per Kategori")
jumlah_kategori = df_filtered.groupby('kategori')['jumlah'].sum().reset_index()
fig_pie = px.pie(jumlah_kategori, names='kategori', values='jumlah', hole=0.4)
fig_pie.update_layout(showlegend=True)
st.plotly_chart(fig_pie, use_container_width=True)

# ============ PER PRODUK / KOTA ============
col5, col6 = st.columns(2)

with col5:
    st.subheader("📦 Penjualan Per Produk")
    per_produk = df_filtered.groupby('nama_produk')['jumlah'].sum().reset_index().sort_values(by='jumlah', ascending=False)
    per_produk['text_format'] = per_produk['jumlah'].apply(lambda x: f"{x:,}".replace(",", "."))
    fig_prod = px.bar(per_produk, x='nama_produk', y='jumlah', text='text_format')
    fig_prod.update_layout(xaxis_title=None, yaxis_title=None)
    fig_prod.update_traces(textposition='outside')
    st.plotly_chart(fig_prod, use_container_width=True)

with col6:
    st.subheader("📍 Penjualan Per Kota")
    per_kota = df_filtered.groupby('kota')['jumlah'].sum().reset_index()
    per_kota['text_format'] = per_kota['jumlah'].apply(lambda x: f"{x:,}".replace(",", "."))
    fig_kota = px.bar(per_kota, x='kota', y='jumlah', text='text_format')
    fig_kota.update_layout(xaxis_title=None, yaxis_title=None)
    fig_kota.update_traces(textposition='outside')
    st.plotly_chart(fig_kota, use_container_width=True)

# ============ TOTAL OMSET PER KATEGORI, PRODUK, KOTA ============
st.subheader('💰 Total Omset per Kategori, Produk, dan Kota')
tab1, tab2, tab3 = st.tabs(["Kategori", "Produk", "Kota"])

# Hitung total omset per kategori
total_omset_per_kategori = df_filtered.groupby('kategori').apply(
    lambda d: (d['harga_satuan'] * d['jumlah']).sum()
).reset_index(name='total_omset')
total_omset_per_kategori['text_format'] = total_omset_per_kategori['total_omset'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

# Hitung total omset per produk
total_omset_per_produk = df_filtered.groupby('nama_produk').apply(
    lambda d: (d['harga_satuan'] * d['jumlah']).sum()
).reset_index(name='total_omset')
total_omset_per_produk['text_format'] = total_omset_per_produk['total_omset'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

# Hitung total omset per kota
total_omset_per_kota = df_filtered.groupby('kota').apply(
    lambda d: (d['harga_satuan'] * d['jumlah']).sum()
).reset_index(name='total_omset')
total_omset_per_kota['text_format'] = total_omset_per_kota['total_omset'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

with tab1:
    fig_kat = px.bar(total_omset_per_kategori, x='kategori', y='total_omset', text='text_format')
    fig_kat.update_traces(textposition='outside')
    fig_kat.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_kat, use_container_width=True)

with tab2:
    fig_prod = px.bar(total_omset_per_produk, x='nama_produk', y='total_omset', text='text_format')
    fig_prod.update_traces(textposition='outside')
    fig_prod.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_prod, use_container_width=True)

with tab3:
    fig_kota = px.bar(total_omset_per_kota, x='kota', y='total_omset', text='text_format')
    fig_kota.update_traces(textposition='outside')
    fig_kota.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_kota, use_container_width=True)

# ============ INSIGHT OTOMATIS ============
st.subheader("📌 Insight Otomatis")
tren_omset = df_filtered.groupby('bulan').apply(lambda d: (d['harga_satuan'] * d['jumlah']).sum()).reset_index(name='omset')
if len(tren_omset) > 1:
    pertumbuhan = (tren_omset['omset'].iloc[-1] - tren_omset['omset'].iloc[-2]) / tren_omset['omset'].iloc[-2] * 100
    status = "⬆️ Naik" if pertumbuhan > 0 else "⬇️ Turun"
    st.info(f"{status} {abs(pertumbuhan):.2f}% dibanding bulan sebelumnya")
else:
    st.info("Belum cukup data untuk analisis pertumbuhan")

# Insight lanjutan: produk dengan tren positif 2 bulan beruntun
produk_bulanan = df_filtered.copy()
produk_bulanan['omset'] = produk_bulanan['harga_satuan'] * produk_bulanan['jumlah']
produk_agg = produk_bulanan.groupby(['nama_produk', 'bulan'])['omset'].sum().reset_index()
produk_agg['prev'] = produk_agg.groupby('nama_produk')['omset'].shift(1)
produk_agg['growth'] = produk_agg['omset'] - produk_agg['prev']
produk_tren_positif = produk_agg.groupby('nama_produk').tail(2).groupby('nama_produk')['growth'].apply(lambda g: all(g > 0)).reset_index()
produk_tren_positif = produk_tren_positif[produk_tren_positif['growth'] == True]['nama_produk'].tolist()

if produk_tren_positif:
    st.success(f"📈 Produk dengan pertumbuhan positif 2 bulan terakhir: {', '.join(produk_tren_positif)}")
else:
    st.warning("Tidak ada produk dengan pertumbuhan positif beruntun")

st.markdown("---")



# ============ TOP PRODUK TERLARIS & TERENDAH ============
st.subheader("🏆 Top 3 Produk Terlaris dan Terendah")
col_top, col_low = st.columns(2)

top_produk = df_filtered.groupby('nama_produk')['jumlah'].sum().nlargest(3).reset_index()
top_produk['text_format'] = top_produk['jumlah'].apply(lambda x: f"{x:,}".replace(",", "."))

low_produk = df_filtered.groupby('nama_produk')['jumlah'].sum().nsmallest(3).reset_index()
low_produk['text_format'] = low_produk['jumlah'].apply(lambda x: f"{x:,}".replace(",", "."))

with col_top:
    st.subheader("Terlaris")
    fig_top = px.bar(top_produk, x='jumlah', y='nama_produk', orientation='h', text='text_format')
    fig_top.update_traces(textposition='inside')
    fig_top.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_top, use_container_width=True, key="top_produk")

with col_low:
    st.subheader("Terendah")
    fig_low = px.bar(low_produk, x='jumlah', y='nama_produk', orientation='h', text='text_format')
    fig_low.update_traces(textposition='inside')
    fig_low.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_low, use_container_width=True, key="low_produk")



# ============ PENJUALAN HARIAN ============
st.subheader("📅 Penjualan Harian (Jumlah Unit)")
penjualan_harian = df_filtered.groupby('tanggal')['jumlah'].sum().reset_index()
fig_harian = px.bar(penjualan_harian, x='tanggal', y='jumlah')
st.plotly_chart(fig_harian, use_container_width=True, key="penjualan_harian")



# ============ PERBANDINGAN OMSET VS UNIT ============
st.subheader("📊 Tren Bulanan: Omset vs Jumlah Penjualan")
tren_bulan = df_filtered.copy()
tren_bulan['omset'] = tren_bulan['harga_satuan'] * tren_bulan['jumlah']
tren_unit = tren_bulan.groupby('bulan')['jumlah'].sum().reset_index()
tren_omset = tren_bulan.groupby('bulan')['omset'].sum().reset_index()
tren_combo = pd.merge(tren_unit, tren_omset, on='bulan')

fig_combo = px.line(tren_combo, x='bulan', y=['jumlah', 'omset'], markers=True, labels={'value': 'Jumlah / Omset', 'variable': 'Tipe'})
fig_combo.update_layout(legend_title_text='')
st.plotly_chart(fig_combo, use_container_width=True, key="omset_vs_unit")

# ============ TOP KOTA TERBAIK ============
st.subheader("🏙️ Top 5 Kota dengan Penjualan Tertinggi")
top_kota = df_filtered.groupby('kota')['jumlah'].sum().nlargest(5).reset_index()
top_kota['jumlah'] = top_kota['jumlah'].apply(lambda x: f"{x:,}".replace(",", "."))

fig_top_kota = px.bar(top_kota, x='jumlah', y='kota', orientation='h', text='jumlah')
fig_top_kota.update_layout(xaxis_title=None, yaxis_title=None)
fig_top_kota.update_traces(textposition='inside')
st.plotly_chart(fig_top_kota, use_container_width=True, key="top_kota")









