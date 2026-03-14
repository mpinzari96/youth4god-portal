import streamlit as st
import pandas as pd
import re

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Youth for God – Conference Registrations",
    page_icon="✝️",
    layout="wide",
)

# ── Mobile-friendly CSS + row highlighting ─────────────────────────────────────
st.markdown("""
<style>
/* Tighten padding on mobile */
@media (max-width: 768px) {
    .block-container { padding: 1rem 0.75rem; }
    h1 { font-size: 1.4rem !important; }
}
/* Unpaid / pending rows → soft yellow background */
[data-testid="stDataFrame"] tr.pending td {
    background-color: #fff9c4 !important;
}
/* Make the dataframe fill width */
[data-testid="stDataFrame"] { width: 100% !important; }
/* Stat cards */
.stat-card {
    background: #f0f4ff;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    text-align: center;
    margin-bottom: 0.5rem;
}
.stat-number { font-size: 2rem; font-weight: 700; color: #1a56db; }
.stat-label  { font-size: 0.85rem; color: #555; }
</style>
""", unsafe_allow_html=True)

# ── State normalisation map ────────────────────────────────────────────────────
STATE_MAP = {
    # USA
    "california": "CA", "ca": "CA", "californi": "CA",
    "washington": "WA", "wa": "WA",
    "oregon": "OR", "or": "OR",
    "indiana": "IN", "in": "IN",
    "pennsylvania": "PA", "pa": "PA",
    "massachusetts": "MA", "ma": "MA",
    "georgia": "GA", "ga": "GA", "goergia": "GA",
    "south carolina": "SC", "sc": "SC",
    "north carolina": "NC", "nc": "NC",
    "florida": "FL", "fl": "FL",
    "idaho": "ID", "id": "ID",
    "minnesota": "MN", "mn": "MN",
    "nebraska": "NE", "ne": "NE",
    "missouri": "MO", "mo": "MO",
    "tennessee": "TN", "tn": "TN",
    "utah": "UT", "ut": "UT",
    "colorado": "CO", "co": "CO",
    "connecticut": "CT", "ct": "CT",
    "alaska": "AK", "ak": "AK",
    "hawaii": "HI", "hi": "HI",
    "arizona": "AZ", "az": "AZ",
    # Canada
    "manitoba": "MB (Canada)", "mb": "MB (Canada)",
    "manitoba canada": "MB (Canada)", "mb, canada": "MB (Canada)",
    "alberta": "AB (Canada)", "ab": "AB (Canada)",
    # International
    "australia": "Australia",
}

def normalize_state(val):
    if pd.isna(val) or str(val).strip() == "":
        return "Unknown"
    return STATE_MAP.get(str(val).strip().lower(), str(val).strip().upper())

def normalize_city(val):
    if pd.isna(val) or str(val).strip() == "":
        return "Unknown"
    return str(val).strip().title()

def normalize_church(val):
    if pd.isna(val) or str(val).strip() == "":
        return "Unknown"
    return str(val).strip().title()

# ── Load & clean data ──────────────────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        raw = pd.read_csv(uploaded_file, dtype=str)
    else:
        # Fallback: load from same directory (for Streamlit Cloud deployment)
        raw = pd.read_csv("registrations.csv", dtype=str)

    # Keep only real registrant rows (sub-rows have blank First name)
    df = raw[raw["First name"].notna() & (raw["First name"].str.strip() != "")].copy()

    df["State_clean"] = df["State"].apply(normalize_state)
    df["City_clean"]  = df["City"].apply(normalize_city)
    df["Church_clean"] = df["What church are you from?"].apply(normalize_church)

    # Friendly column rename for display
    df["Full Name"]       = df["First name"].str.strip() + " " + df["Last name"].str.strip()
    df["Email"]           = df["Email"].str.strip()
    df["Phone"]           = df["Phone number"].str.strip()
    df["Church"]          = df["Church_clean"]
    df["Ticket Type"]     = df["Ticket type"].str.strip()
    df["Price"]           = df["Ticket price"].str.strip()
    df["Payment Status"]  = df["Payment status"].str.strip().str.lower()
    df["Primary Contact"] = df["Primary Contact Name"].str.strip().fillna("")
    df["Primary Email"]   = df["Primary Contact Email"].str.strip().fillna("")
    df["Party ID"]        = df["Party ID"].str.strip().fillna("")

    # Party size: count how many share the same Party ID
    party_counts = df[df["Party ID"] != ""].groupby("Party ID")["Party ID"].transform("count")
    df["Party Size"] = party_counts.fillna(1).astype(int)

    return df

# ── Sidebar / upload ───────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/holy-bible.png", width=60)
    st.title("Youth for God\nRegistrations")
    st.markdown("---")
    uploaded = st.file_uploader("📂 Upload updated CSV", type="csv")
    st.markdown("---")
    st.markdown("**Colour key**")
    st.markdown("🟠 `transfer pending`")
    st.markdown("✅ `success`")

df = load_data(uploaded)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("✝️ Youth for God – Conference Registrations")

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1, 1.5])

with col1:
    states = sorted(df["State_clean"].dropna().unique())
    state_choice = st.selectbox("🗺️ State", ["All"] + states)

with col2:
    if state_choice != "All":
        city_options = sorted(df[df["State_clean"] == state_choice]["City_clean"].dropna().unique())
    else:
        city_options = sorted(df["City_clean"].dropna().unique())
    city_choice = st.selectbox("🏙️ City", ["All"] + city_options)

with col3:
    church_search = st.text_input("⛪ Search Church (partial match)", "")

# Apply filters
filtered = df.copy()
if state_choice != "All":
    filtered = filtered[filtered["State_clean"] == state_choice]
if city_choice != "All":
    filtered = filtered[filtered["City_clean"] == city_choice]
if church_search.strip():
    filtered = filtered[
        filtered["Church_clean"].str.contains(church_search.strip(), case=False, na=False)
    ]

# ── Stats row ──────────────────────────────────────────────────────────────────
total     = len(filtered)
paid      = (filtered["Payment Status"] == "success").sum()
pending   = (filtered["Payment Status"] != "success").sum()

s1, s2, s3, s4 = st.columns(4)
for col, number, label in [
    (s1, total,   "Total Shown"),
    (s2, paid,    "✅ Paid"),
    (s3, pending, "🟡 Pending"),
    (s4, len(df), "All Registrations"),
]:
    col.markdown(
        f'<div class="stat-card"><div class="stat-number">{number}</div>'
        f'<div class="stat-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Build display table ────────────────────────────────────────────────────────
display_cols = [
    "Full Name", "Email", "Phone", "Church",
    "Ticket Type", "Price", "Payment Status",
    "Primary Contact", "Primary Email", "Party Size",
    "State_clean", "City_clean",
]

table = filtered[display_cols].rename(columns={
    "State_clean": "State",
    "City_clean":  "City",
}).reset_index(drop=True)

# Highlight pending rows using pandas Styler
def highlight_pending(row):
    if str(row["Payment Status"]).strip().lower() != "success":
        return ["color: #e67e00; font-weight: 600"] * len(row)
    return [""] * len(row)

styled = table.style.apply(highlight_pending, axis=1)

st.dataframe(
    styled,
    use_container_width=True,
    height=520,
    column_config={
        "Email":           st.column_config.TextColumn("Email", width="medium"),
        "Phone":           st.column_config.TextColumn("Phone", width="small"),
        "Party Size":      st.column_config.NumberColumn("Party Size", width="small"),
        "Price":           st.column_config.TextColumn("Price", width="small"),
        "Payment Status":  st.column_config.TextColumn("Status", width="small"),
    },
)

# ── Download filtered results ──────────────────────────────────────────────────
csv_bytes = table.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download filtered list as CSV",
    data=csv_bytes,
    file_name="filtered_registrations.csv",
    mime="text/csv",
)
