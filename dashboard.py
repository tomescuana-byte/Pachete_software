import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="Beauty Insights Dashboard", layout="wide")

# ── CSS CUSTOM ───────────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0f0f, #1a1a1a);
    color: white;
}

h1, h2, h3 {
    color: #ff4fa3 !important;
}

section[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 2px solid #ff4fa3;
}

div[data-testid="metric-container"] {
    background-color: #1c1c1c;
    border: 1px solid #ff4fa3;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(255,79,163,0.3);
}

.stDataFrame {
    border: 1px solid #ff4fa3;
    border-radius: 10px;
}

.stButton>button {
    background-color: #ff4fa3;
    color: white;
    border-radius: 10px;
    border: none;
}

.stButton>button:hover {
    background-color: #ff2e93;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #ff4fa3, transparent);
}
</style>
""", unsafe_allow_html=True)

# ── TITLU + IMAGINE ──────────────────────────────────────────────
st.title("Beauty Insights Dashboard")
st.markdown("### Analiza interactivă a produselor cosmetice")
st.image("cosmetics.jpg", use_container_width=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ── ÎNCĂRCARE CSV ────────────────────────────────────────────────
fisier = st.file_uploader("Încarcă fișierul CSV", type=["csv"])

if fisier is None:
    st.info("Încarcă un fișier CSV pentru a continua.")
    st.stop()

df = pd.read_csv(fisier)

# curățare nume coloane
df.columns = df.columns.str.strip()

# păstrăm doar coloanele utile
coloane_pastrate = [
    "Product_Name",
    "Brand",
    "Category",
    "Usage_Frequency",
    "Price_USD",
    "Rating",
    "Number_of_Reviews",
    "Skin_Type",
    "Gender_Target",
    "Country_of_Origin"
]

df = df[coloane_pastrate]

# conversii numerice
df["Price_USD"] = pd.to_numeric(df["Price_USD"], errors="coerce")
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Number_of_Reviews"] = pd.to_numeric(df["Number_of_Reviews"], errors="coerce")

# eliminăm valorile lipsă importante
df = df.dropna(subset=["Category", "Brand", "Skin_Type", "Price_USD", "Rating"])

# ── METRICI ──────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

col1.metric("Total produse", len(df))
col2.metric("Rating mediu", round(df["Rating"].mean(), 2))
col3.metric("Preț mediu (USD)", round(df["Price_USD"].mean(), 2))

# ── PREVIEW DATE ─────────────────────────────────────────────────
st.subheader("Preview dataset (primele 10 înregistrări)")
st.dataframe(df.head(10), use_container_width=True)

# ── FILTRE ÎN SIDEBAR ────────────────────────────────────────────
st.sidebar.header("Filtre")

categorii = sorted(df["Category"].dropna().unique().tolist())
branduri = sorted(df["Brand"].dropna().unique().tolist())
tipuri_piele = sorted(df["Skin_Type"].dropna().unique().tolist())

selectie_categorie = st.sidebar.multiselect(
    "Categorie",
    categorii,
    default=categorii
)

selectie_brand = st.sidebar.multiselect(
    "Brand",
    branduri,
    default=branduri
)

selectie_skin = st.sidebar.multiselect(
    "Tip piele",
    tipuri_piele,
    default=tipuri_piele
)

pret_min = float(df["Price_USD"].min())
pret_max = float(df["Price_USD"].max())

interval_pret = st.sidebar.slider(
    "Interval preț (USD)",
    min_value=pret_min,
    max_value=pret_max,
    value=(pret_min, pret_max)
)

# aplicare filtre
df_filtrat = df[
    (df["Category"].isin(selectie_categorie)) &
    (df["Brand"].isin(selectie_brand)) &
    (df["Skin_Type"].isin(selectie_skin)) &
    (df["Price_USD"] >= interval_pret[0]) &
    (df["Price_USD"] <= interval_pret[1])
]

if df_filtrat.empty:
    st.warning("Nu există date pentru filtrele selectate.")
    st.stop()

# ── GRAFIC 1 — PLOTLY ────────────────────────────────────────────
st.subheader("Rating mediu pe categorie")

rating_cat = (
    df_filtrat.groupby("Category")["Rating"]
    .mean()
    .reset_index()
    .sort_values(by="Rating", ascending=False)
)

fig = px.bar(
    rating_cat,
    x="Category",
    y="Rating",
    color="Category",
    title="Rating mediu al produselor pe categorii"
)

st.plotly_chart(fig, use_container_width=True)

# ── GRAFIC 2 — MATPLOTLIB ────────────────────────────────────────
st.subheader("Distribuția prețurilor produselor")

fig2, ax = plt.subplots(figsize=(9, 4))
ax.hist(
    df_filtrat["Price_USD"].dropna(),
    bins=20,
    color="#ff4fa3",
    edgecolor="white"
)
ax.set_title("Distribuția prețurilor")
ax.set_xlabel("Preț (USD)")
ax.set_ylabel("Frecvență")

st.pyplot(fig2)
plt.close(fig2)

# ── DATE FILTRATE ────────────────────────────────────────────────
st.subheader("Date filtrate")
st.dataframe(df_filtrat, use_container_width=True)