import streamlit as st


def apply_styles():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink:#142b3b; --muted:#637889; --blue:#216b91; --blue2:#164e70; --line:#e1e9ee; --paper:#ffffff; --canvas:#f3f7f9; --mint:#e7f5f0; }
    html, body, [class*="css"] {font-family:'DM Sans',sans-serif; color:var(--ink)}
    .stApp {background:linear-gradient(180deg,#f8fbfc 0%,var(--canvas) 100%)}
    [data-testid="stHeader"] {background:transparent}
    .block-container {max-width:1320px;padding-top:2rem;padding-bottom:4rem}
    h1,h2,h3 {font-family:'Manrope',sans-serif;color:var(--ink);letter-spacing:-.035em}
    h1 {font-size:2.45rem!important;font-weight:800!important;margin-bottom:.25rem}
    h2 {font-size:1.55rem!important;font-weight:750!important}
    h3 {font-size:1.15rem!important;font-weight:700!important}
    p, .stMarkdown {line-height:1.65}
    [data-testid="stSidebar"] {background:#eef4f6;border-right:1px solid var(--line)}
    [data-testid="stSidebar"] > div:first-child {padding-top:1.5rem}
    [data-testid="stMetric"] {background:var(--paper);padding:1rem 1.15rem;border:1px solid var(--line);border-radius:16px;box-shadow:0 5px 20px #163c4b08}
    [data-testid="stMetricLabel"] {color:var(--muted);font-size:.82rem;font-weight:600}
    [data-testid="stMetricValue"] {font-family:'Manrope',sans-serif;color:var(--blue2);font-weight:800}
    .stButton button, .stDownloadButton button {border-radius:11px;font-weight:700;min-height:2.7rem;border:1px solid #d1e0e7;transition:all .15s ease}
    .stButton button[kind="primary"] {background:linear-gradient(135deg,var(--blue),var(--blue2));border:0;color:white}
    .stButton button:hover, .stDownloadButton button:hover {transform:translateY(-1px);border-color:#8bb3c4;box-shadow:0 5px 14px #163c4b14}
    [data-baseweb="tab-list"] {gap:.55rem;border-bottom:1px solid var(--line)}
    [data-baseweb="tab"] {height:3.3rem;padding:0 1rem;color:var(--muted);font-weight:700}
    [aria-selected="true"][data-baseweb="tab"] {color:var(--blue2)}
    [data-testid="stChatMessage"] {background:#fff;border:1px solid var(--line);border-radius:16px;padding:.75rem 1rem}
    [data-testid="stFileUploader"] {background:#fff;border:1px dashed #9db9c6;border-radius:14px;padding:.7rem}
    div[data-testid="stAlert"] {border-radius:12px}
    .hero {background:radial-gradient(circle at 90% 0%,#8bc6d12b,transparent 32%),linear-gradient(120deg,#123f5a,#1d6b85);border-radius:22px;padding:1.75rem 2rem;color:white;margin:.7rem 0 1.3rem;box-shadow:0 15px 38px #123f5a20}
    .hero-kicker {font-size:.76rem;text-transform:uppercase;letter-spacing:.16em;font-weight:700;color:#b7dce6;margin-bottom:.55rem}
    .hero-title {font-family:'Manrope',sans-serif;font-size:1.85rem;font-weight:800;line-height:1.18;color:#fff;letter-spacing:-.04em}
    .hero-copy {font-size:.98rem;color:#deedf1;margin-top:.55rem;max-width:720px}
    .eyebrow {color:var(--blue);font-weight:800;text-transform:uppercase;font-size:.74rem;letter-spacing:.12em}
    .card-note {background:#fff;border:1px solid var(--line);border-radius:15px;padding:1rem 1.15rem;color:var(--muted)}
    </style>""", unsafe_allow_html=True)
