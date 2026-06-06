import streamlit as st

SENTIMENT_COLORS = {
    "positive": "#059669",
    "negative": "#dc2626",
    "neutral": "#d97706",
}

BASE_CSS = """
<style>
:root {
    --primary: #1e3a5f;
    --primary-light: #eef2f7;
    --surface: #ffffff;
    --surface-muted: #f8fafc;
    --border: #d7dee8;
    --text: #0f172a;
    --text-muted: #64748b;
    --radius: 10px;
    --shadow: 0 2px 12px rgba(15, 23, 42, 0.05);
}

html, body, [class*="css"] {
    font-family: "Segoe UI", "Noto Sans Arabic", Tahoma, Arial, sans-serif;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.hero-banner {
    background: #ffffff;
    border: 1px solid var(--border);
    border-top: 4px solid var(--primary);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin-bottom: 1.5rem;
    color: var(--text);
    box-shadow: var(--shadow);
}
.hero-inner {
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
}
.hero-logo-wrap {
    flex-shrink: 0;
    background: #fff;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 10px;
}
.hero-logo-img {
    width: auto;
    height: 72px;
    max-width: 120px;
    object-fit: contain;
    display: block;
}
.hero-logo-text {
    width: 72px;
    height: 72px;
    border-radius: 8px;
    background: var(--primary-light);
    color: var(--primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: 700;
}
.hero-content { flex: 1; min-width: 260px; }
.hero-uni {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 2px;
}
.hero-uni-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.hero-banner h1 {
    color: var(--text) !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    margin: 0 0 4px 0 !important;
    line-height: 1.3 !important;
}
.hero-banner p {
    color: var(--text-muted);
    margin: 0;
    font-size: 0.9rem;
}
.hero-meta {
    margin-top: 10px;
    font-size: 0.85rem;
    color: var(--text-muted);
}
.hero-meta-sep {
    margin: 0 8px;
    color: #cbd5e1;
}

.author-badge {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--primary-light);
    border: 1px solid var(--border);
    border-right: 3px solid var(--primary);
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 1rem;
}
.author-badge-compact {
    padding: 10px 12px;
    margin-bottom: 0.75rem;
}
.author-icon {
    font-size: 1.6rem;
    line-height: 1;
}
.author-label {
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}
.author-name {
    font-size: 1rem;
    font-weight: 700;
    color: #1e293b;
}
.author-name-en {
    font-size: 0.78rem;
    color: #64748b;
}

.section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}

.result-card {
    border-radius: var(--radius);
    padding: 22px 24px;
    margin-bottom: 12px;
    border: 1px solid var(--border);
    background: var(--surface-muted);
    box-shadow: var(--shadow);
}
.result-badge {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 12px;
}
.result-meta {
    color: var(--text-muted);
    font-size: 0.88rem;
    margin: 6px 0;
}
.confidence-ring {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
}

.compare-card {
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
    background: var(--surface-muted);
}

.demo-panel {
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px 8px;
    margin-bottom: 12px;
}

.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--text-muted);
    background: var(--surface-muted);
    border-radius: var(--radius);
    border: 2px dashed var(--border);
}
.empty-state-icon {
    font-size: 2.5rem;
    margin-bottom: 8px;
}

.app-footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
}

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
    font-weight: 600;
}

div.stButton > button[kind="primary"] {
    background: var(--primary);
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
div.stButton > button[kind="primary"]:hover {
    background: #16304f;
    box-shadow: 0 4px 12px rgba(30, 58, 95, 0.25);
}

div[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 16px;
    box-shadow: var(--shadow);
}
</style>
"""

DARK_CSS = """
<style>
.stApp {
    background-color: #0f172a !important;
    color: #e2e8f0 !important;
}
.main .block-container {
    color: #e2e8f0;
}
h1, h2, h3, h4, h5, h6, p, label, span {
    color: #e2e8f0 !important;
}
.stCaption, [data-testid="stCaptionContainer"] {
    color: #94a3b8 !important;
}

.section-card, div[data-testid="stMetric"] {
    background: #1e293b !important;
    border-color: #334155 !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25) !important;
}

.result-card, .compare-card, .empty-state {
    background: #1e293b !important;
    border-color: #334155 !important;
}
.result-meta { color: #94a3b8 !important; }

.demo-panel {
    background: linear-gradient(180deg, #1e293b 0%, #312e81 100%) !important;
    border-color: #4338ca !important;
}

.hero-banner {
    background: linear-gradient(135deg, #312e81 0%, #4c1d95 50%, #1e3a8a 100%) !important;
}

.author-badge, .author-badge-compact {
    background: linear-gradient(135deg, #1e293b, #312e81) !important;
    border-color: #4338ca !important;
}
.author-name { color: #f1f5f9 !important; }
.author-label, .author-name-en { color: #94a3b8 !important; }

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}

.stTextArea textarea, .stTextInput input {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: #475569 !important;
}

.stTabs [data-baseweb="tab"] {
    background: #1e293b !important;
    color: #94a3b8 !important;
}
.stTabs [aria-selected="true"] {
    background: #334155 !important;
    color: #f1f5f9 !important;
}

.app-footer {
    border-color: #334155 !important;
    color: #94a3b8 !important;
}

[data-testid="stDataFrame"] {
    background: #1e293b;
}
</style>
"""

RTL_CSS = """
<style>
.main .block-container {
    direction: rtl;
    text-align: right;
}
[data-testid="stSidebar"] {
    direction: rtl;
    text-align: right;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown {
    direction: rtl;
    text-align: right;
}
.stTextArea textarea {
    direction: rtl;
    text-align: right;
}
</style>
"""


def apply_app_styles(rtl_mode: bool = True, dark_mode: bool = False) -> None:
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    if dark_mode:
        st.markdown(DARK_CSS, unsafe_allow_html=True)
    if rtl_mode:
        st.markdown(RTL_CSS, unsafe_allow_html=True)
