import streamlit as st
import streamlit.components.v1 as components


def inject_styles():
    """Inject the complete light-theme CSS design system and enforce light theme."""
    st.markdown("""
<style>
/* ── ШРИФТИ ТА БАЗОВИЙ РЕСЕТ ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

/* ── ПРИМУСОВИЙ СВІТЛИЙ РЕЖИМ НЕЗАЛЕЖНО ВІД СИСТЕМИ КОРИСТУВАЧА ── */
:root, [data-theme="dark"], [data-theme="light"] {
    color-scheme: light !important;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* Повне перекриття всіх контейнерів Streamlit у білий колір */
html, body, .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main, .main {
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    color: #1E293B !important;
    color-scheme: light !important;
}

header, [data-testid="stHeader"] {
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
}

[data-testid="stAppViewBlockContainer"], [data-testid="stVerticalBlock"] {
    background: transparent !important;
    background-color: transparent !important;
}

/* ── ПОВНЕ ВИДАЛЕННЯ БІЧНОЇ ПАНЕЛІ ── */
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
button[aria-label="Expand sidebar"],
header[data-testid="stHeader"] button[aria-label="Expand sidebar"] {
    display: none !important;
    width: 0px !important;
    min-width: 0px !important;
    max-width: 0px !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* ── ПРИХОВАТИ СЛУЖБОВИЙ HEADER STREAMLIT ТА СТАТУС ── */
.stDeployButton, [data-testid="stDeployButton"], button[data-testid="stDeployButton"],
header, header[data-testid="stHeader"], [data-testid="stHeader"],
.stAppHeader, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], #MainMenu {
    display: none !important;
    height: 0px !important;
    max-height: 0px !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
[data-testid="InputInstructions"] {
    display: none !important;
}

/* ── РОБОЧИЙ КОНТЕЙНЕР ── */
.block-container {
    max-width: 1200px !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
    width: 100% !important;
    background: #FFFFFF !important;
}

/* ── ГЛОБАЛЬНА НАВІГАЦІЙНА ПАНЕЛЬ ── */
.nav-header {
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    border-radius: 0;
    padding: 0.85rem 1.6rem;
    margin: -1rem -2rem 1.5rem -2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.nav-brand-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #0F172A !important;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 0;
}
.nav-brand-subtitle {
    font-size: 0.8rem;
    color: #64748B !important;
    margin: 0.2rem 0 0 0;
    font-weight: 500;
}
.pulse-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 999px;
    padding: 0.2rem 0.65rem;
    font-size: 0.72rem;
    font-weight: 700;
    color: #059669;
}
.pulse-dot {
    width: 7px;
    height: 7px;
    background: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 6px #10B981;
    animation: pulseAnim 2s infinite;
}
@keyframes pulseAnim {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1.15); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* ── HERO SECTION (LANDING) ── */
.hero-section {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 50%, #E0F2FE 100%);
    border-radius: 24px;
    padding: 3.5rem 2.5rem;
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
    border: 1px solid #BFDBFE;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #0F172A !important;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 1rem;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #334155 !important;
    font-weight: 500;
    max-width: 650px;
    margin: 0 auto 2rem;
    line-height: 1.6;
}

/* ── FEATURE CARDS ── */
.feature-card {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 16px;
    padding: 1.8rem 1.5rem;
    text-align: center;
    transition: all 0.25s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    height: 100%;
}
.feature-card:hover {
    border-color: #3B82F6;
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.12);
    transform: translateY(-3px);
}
.feature-icon {
    font-size: 2.8rem;
    margin-bottom: 1rem;
    display: block;
}
.feature-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0F172A !important;
    margin-bottom: 0.5rem;
}
.feature-desc {
    font-size: 0.88rem;
    color: #475569 !important;
    line-height: 1.55;
}

/* ── STEPS & TRUST ── */
.steps-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0;
    flex-wrap: wrap;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
}
.step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #2563EB;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.85rem;
    flex-shrink: 0;
}
.step-text {
    font-size: 0.88rem;
    font-weight: 600;
    color: #1E293B !important;
}
.step-arrow {
    font-size: 1.3rem;
    color: #94A3B8;
}

.trust-grid {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin: 1.5rem 0;
}
.trust-stat {
    text-align: center;
    padding: 1.2rem 1.5rem;
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 14px;
    min-width: 160px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.trust-number {
    font-size: 1.8rem;
    font-weight: 800;
    color: #2563EB;
    letter-spacing: -0.02em;
}
.trust-label {
    font-size: 0.8rem;
    color: #64748B;
    font-weight: 600;
    margin-top: 0.2rem;
}

/* ── MODE BANNERS ── */
.mode-banner-screening {
    background: #F0FDF4;
    border-left: 5px solid #10B981;
    border-top: 1px solid #BBF7D0;
    border-right: 1px solid #BBF7D0;
    border-bottom: 1px solid #BBF7D0;
    border-radius: 12px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 1.2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;
}
.mode-banner-clinical {
    background: #EFF6FF;
    border-left: 5px solid #2563EB;
    border-top: 1px solid #BFDBFE;
    border-right: 1px solid #BFDBFE;
    border-bottom: 1px solid #BFDBFE;
    border-radius: 12px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 1.2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;
}

/* ── РЕФАЙНИНГ ТАБІВ (SEGMENTED CONTROL STYLE — М'ЯКИЙ, НЕ ГРУБИЙ) ── */
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"],
div[data-baseweb="tab-highlight"],
div[data-baseweb="tab-border"] {
    display: none !important;
    background: transparent !important;
    height: 0px !important;
    visibility: hidden !important;
}

.stTabs [data-baseweb="tab-list"], [data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 6px !important;
    background: #F1F5F9 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 5px !important;
    margin-bottom: 1.2rem !important;
}
.stTabs [data-baseweb="tab"], [data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    padding: 0.5rem 1.1rem !important;
    color: #64748B !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    transition: all 0.18s ease !important;
}
.stTabs [data-baseweb="tab"]:hover, [data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #1E293B !important;
    background: rgba(255, 255, 255, 0.7) !important;
}
.stTabs [aria-selected="true"], [data-testid="stTabs"] [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #2563EB !important;
    font-weight: 700 !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08) !important;
}

/* ── ЧІТКЕ РОЗДІЛЕННЯ ПОЛІВ ВВЕДЕННЯ (НЕ ЗЛИВАЮТЬСЯ) ── */
[data-testid="stWidgetLabel"] p {
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: #0F172A !important;
    margin-bottom: 0.4rem !important;
}

[data-testid="stNumberInput"] {
    margin-bottom: 0.9rem !important;
}
[data-testid="stNumberInputContainer"] {
    border: 1.5px solid #94A3B8 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    overflow: hidden !important;
}
[data-testid="stNumberInputContainer"]:focus-within {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
}
[data-testid="stNumberInputField"], [data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    color: #0F172A !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 0.8rem !important;
}
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"], [data-testid="stNumberInput"] button {
    background: #F1F5F9 !important;
    border-left: 1px solid #CBD5E1 !important;
    color: #334155 !important;
}
[data-testid="stNumberInputStepDown"]:hover, [data-testid="stNumberInputStepUp"]:hover, [data-testid="stNumberInput"] button:hover {
    background: #E2E8F0 !important;
    color: #0F172A !important;
}

/* Радіо кнопки — чіткі контури */
[data-testid="stRadio"] {
    margin-bottom: 0.9rem !important;
}
[data-testid="stRadio"] div[role="radiogroup"], [data-testid="stRadio"] > div {
    display: flex;
    gap: 0.8rem;
    background: #F8FAFC !important;
    border: 1.5px solid #94A3B8 !important;
    border-radius: 10px !important;
    padding: 0.45rem 0.85rem !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
}
[data-testid="stRadio"] div[role="radiogroup"]:focus-within, [data-testid="stRadio"] > div:hover {
    border-color: #2563EB !important;
}
[data-testid="stRadio"] label span {
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    color: #1E293B !important;
}

/* Селектбокс */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #F8FAFC !important;
    border: 1.5px solid #94A3B8 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    color: #0F172A !important;
    font-weight: 600 !important;
}
}
[data-testid="stRadio"] label span {
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    color: #1E293B !important;
}

/* Селектбокс */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    font-weight: 600 !important;
    color: #0F172A !important;
}

/* Слайдери */
[data-testid="stSlider"] {
    margin-bottom: 0.8rem !important;
}

/* ── КАРТКА HERO РЕЗУЛЬТАТУ ── */
.risk-card {
    background: #FFFFFF !important;
    border-radius: 16px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1.1rem;
    position: relative;
    overflow: hidden;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}
.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.risk-percent {
    font-size: 3.4rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0.4rem 0 0.3rem;
}

/* ── ЧІПИ ТА СТАТУСИ ── */
.bio-pill-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
    padding-top: 0.8rem;
    border-top: 1px solid #E2E8F0;
}
.bio-pill {
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 0.35rem 0.7rem;
    font-size: 0.76rem;
    font-weight: 600;
    color: #334155;
}
.status-pill-bar {
    border-radius: 10px;
    padding: 0.65rem 0.95rem;
    font-size: 0.86rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0.5rem 0 0.8rem;
    border: 1.5px solid;
}

/* ── WHAT-IF СИМУЛЯТОР ── */
.whatif-box {
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    margin-top: 1rem;
}
.action-item-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    transition: background 0.2s, border-color 0.2s;
}
.action-item-card:hover {
    background: #EFF6FF;
    border-color: #93C5FD;
}

/* ── ПОКРАЩЕННЯ КНОПОК ── */
.stButton button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.2s ease !important;
    background: #FFFFFF;
    color: #1E293B;
    border: 1px solid #CBD5E1;
}
.stButton button:hover {
    background: #F8FAFC;
    border-color: #94A3B8;
}
.stButton button[kind="primary"] {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
}
.stButton button[kind="primary"]:hover {
    background: #1D4ED8 !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
}
.stDownloadButton button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.2rem !important;
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
}

/* ── ВІДЖЕТ РЕЇМБУРСАЦІЇ ── */
.savings-card {
    background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%);
    border: 1.5px solid #86EFAC;
    border-radius: 14px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.06);
}
.savings-metric-box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.8rem;
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
    margin-top: 0.6rem;
}
.savings-big-number {
    font-size: 1.8rem;
    font-weight: 800;
    color: #059669;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.savings-tag {
    background: #D1FAE5;
    color: #059669;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    text-transform: uppercase;
}

.audience-banner {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 10px;
    padding: 0.6rem 0.95rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.83rem;
    color: #1E40AF;
}

/* ── ФУТЕР ── */
.footer-container {
    text-align: center;
    padding: 2rem 0 1rem;
    color: #64748B;
    font-size: 0.77rem;
    line-height: 1.6;
    border-top: 1px solid #E2E8F0;
    margin-top: 3rem;
    background: #FFFFFF;
}

h1, h2, h3, h4, h5, h6 {
    color: #0F172A !important;
}

[data-testid="stCheckbox"] label span {
    color: #1E293B !important;
    font-weight: 600 !important;
}

[data-testid="stExpander"] {
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
}
[data-testid="stExpander"] summary {
    color: #0F172A !important;
    font-weight: 700 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

    # Force Light Theme on Root Document via JavaScript
    components.html("""
<script>
function enforceLightTheme() {
    try {
        const rootDoc = window.parent.document;
        rootDoc.documentElement.setAttribute('data-theme', 'light');
        rootDoc.documentElement.style.setProperty('background-color', '#FFFFFF', 'important');
        rootDoc.body.setAttribute('data-theme', 'light');
        rootDoc.body.style.setProperty('background-color', '#FFFFFF', 'important');
        
        const appContainers = rootDoc.querySelectorAll('.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main');
        appContainers.forEach(el => {
            el.style.setProperty('background', '#FFFFFF', 'important');
            el.style.setProperty('background-color', '#FFFFFF', 'important');
            el.style.setProperty('color', '#1E293B', 'important');
        });

        rootDoc.querySelectorAll('[data-testid="stDeployButton"]').forEach(el => el.style.setProperty('display', 'none', 'important'));
        rootDoc.querySelectorAll('[data-testid="InputInstructions"]').forEach(el => el.style.setProperty('display', 'none', 'important'));
        rootDoc.querySelectorAll('[data-testid="stSidebar"], [data-testid="collapsedControl"]').forEach(el => el.style.setProperty('display', 'none', 'important'));
        rootDoc.querySelectorAll('[data-testid="stHeader"], header, [data-testid="stToolbar"]').forEach(el => el.style.setProperty('display', 'none', 'important'));
    } catch (err) {}
}
try {
    enforceLightTheme();
    const rootDoc = window.parent.document;
    const observer = new MutationObserver(enforceLightTheme);
    observer.observe(rootDoc.body, { childList: true, subtree: true });
    setInterval(enforceLightTheme, 300);
} catch(e) {}
</script>
""", height=0, width=0)


def render_html(html_str):
    """Render pure HTML without Markdown misinterpretation."""
    clean = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)
