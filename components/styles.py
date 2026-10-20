import streamlit as st
import streamlit.components.v1 as components


def inject_styles():
    """Inject the complete light-theme CSS design system."""
    st.markdown("""
<style>
/* ── ШРИФТИ ТА БАЗОВИЙ РЕСЕТ ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
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

/* ── ПРИХОВАТИ СЛУЖБОВИЙ HEADER STREAMLIT ── */
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

/* ── ОСНОВНИЙ ФОН (СВІТЛА ТЕМА) ── */
.main {
    background: #FFFFFF !important;
    color: #475569 !important;
}
.block-container {
    max-width: 1200px !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
    width: 100% !important;
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
    color: #0F172A;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 0;
}
.nav-brand-subtitle {
    font-size: 0.8rem;
    color: #94A3B8;
    margin: 0.2rem 0 0 0;
    font-weight: 500;
}
.nav-link {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.45rem 1rem;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #64748B;
    text-decoration: none;
    transition: all 0.2s;
    border: 1px solid transparent;
    cursor: pointer;
    background: none;
}
.nav-link:hover {
    color: #2563EB;
    background: #EFF6FF;
}
.nav-link-active {
    color: #2563EB !important;
    background: #EFF6FF !important;
    border-color: #BFDBFE !important;
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

/* ── КАРТКИ ── */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
    transition: box-shadow 0.25s, transform 0.25s;
}
.card:hover {
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.08);
    transform: translateY(-2px);
}
.panel-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.panel-title {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    margin-bottom: 0.85rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
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
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #1E293B;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 1rem;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #475569;
    font-weight: 500;
    max-width: 600px;
    margin: 0 auto 2rem;
    line-height: 1.6;
}

/* ── FEATURE CARDS (LANDING) ── */
.feature-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.8rem 1.5rem;
    text-align: center;
    transition: all 0.25s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    height: 100%;
}
.feature-card:hover {
    border-color: #93C5FD;
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.1);
    transform: translateY(-4px);
}
.feature-icon {
    font-size: 2.8rem;
    margin-bottom: 1rem;
    display: block;
}
.feature-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1E293B;
    margin-bottom: 0.5rem;
}
.feature-desc {
    font-size: 0.88rem;
    color: #64748B;
    line-height: 1.55;
}

/* ── STEP INDICATOR (LANDING) ── */
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
    border: 1px solid #E2E8F0;
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
    color: #334155;
}
.step-arrow {
    font-size: 1.3rem;
    color: #CBD5E1;
}

/* ── TRUST STATS (LANDING) ── */
.trust-grid {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin: 1.5rem 0;
}
.trust-stat {
    text-align: center;
    padding: 1.2rem 1.5rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    min-width: 160px;
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

/* ── MODE BANNER ── */
.mode-banner-screening {
    background: linear-gradient(90deg, #F0FDF4 0%, #FFFFFF 100%);
    border-left: 4px solid #10B981;
    border-top: 1px solid #D1FAE5;
    border-right: 1px solid #D1FAE5;
    border-bottom: 1px solid #D1FAE5;
    border-radius: 12px;
    padding: 0.75rem 1.1rem;
    margin-bottom: 1.1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;
}
.mode-banner-clinical {
    background: linear-gradient(90deg, #EFF6FF 0%, #FFFFFF 100%);
    border-left: 4px solid #3B82F6;
    border-top: 1px solid #BFDBFE;
    border-right: 1px solid #BFDBFE;
    border-bottom: 1px solid #BFDBFE;
    border-radius: 12px;
    padding: 0.75rem 1.1rem;
    margin-bottom: 1.1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;
}

/* ── СТИЛІЗАЦІЯ РАДІО КНОПОК ── */
[data-testid="stRadio"] > div {
    display: flex;
    gap: 0.5rem;
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 0.35rem 0.6rem;
}
[data-testid="stRadio"] label span {
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
}

/* ── КАРТКА РЕЗУЛЬТАТУ РИЗИКУ (HERO RISK CARD) ── */
.risk-card {
    border-radius: 16px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1.1rem;
    position: relative;
    overflow: hidden;
    border: 1px solid;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}
.risk-card-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
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

/* ── ЧІПИ БІОМАРКЕРІВ ── */
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
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 0.3rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #475569;
}

/* ── ІНДИКАТОРИ СТАТУСУ ── */
.status-pill-bar {
    border-radius: 10px;
    padding: 0.55rem 0.85rem;
    font-size: 0.84rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0.3rem 0 0.7rem;
    border: 1px solid;
}

/* ── WHAT-IF СИМУЛЯТОР ── */
.whatif-box {
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    margin-top: 1rem;
}

/* ── ACTION ITEMS ── */
.action-item-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    transition: background 0.2s, border-color 0.2s;
}
.action-item-card:hover {
    background: #EFF6FF;
    border-color: #BFDBFE;
}

/* ── СТИЛІЗАЦІЯ ТАБІВ ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 0.8rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    padding: 0.48rem 0.95rem !important;
    color: #64748B !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: #2563EB !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25) !important;
}

/* ── ПОКРАЩЕННЯ КНОПОК ── */
.stButton button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.2s ease !important;
}
.stButton button[kind="primary"] {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
}
.stButton button[kind="primary"]:hover {
    background: #1D4ED8 !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
}
.stDownloadButton button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.2rem !important;
}

/* ── ВІДЖЕТ ФАРМАКОЕКОНОМІЧНОЇ ЕКОНОМІЇ ── */
.savings-card {
    background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%);
    border: 1px solid #BBF7D0;
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

/* ── CHART WRAPPER ── */
.chart-card-wrapper {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.9rem;
}

/* ── AUDIENCE BANNER ── */
.audience-banner {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 10px;
    padding: 0.55rem 0.9rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.82rem;
    color: #1E40AF;
}

/* ── FOOTER ── */
.footer-container {
    text-align: center;
    padding: 2rem 0 1rem;
    color: #94A3B8;
    font-size: 0.77rem;
    line-height: 1.6;
    border-top: 1px solid #E2E8F0;
    margin-top: 3rem;
}

/* ── BACK LINK ── */
.back-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: #2563EB;
    font-weight: 600;
    font-size: 0.88rem;
    text-decoration: none;
    margin-bottom: 1rem;
    cursor: pointer;
    padding: 0.3rem 0;
}
.back-link:hover {
    color: #1D4ED8;
}

/* ── NUMBER INPUTS LIGHT STYLE ── */
[data-testid="stNumberInput"] input {
    border-color: #CBD5E1 !important;
    border-radius: 10px !important;
    color: #1E293B !important;
    background: #FFFFFF !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

/* ── SELECTBOX LIGHT STYLE ── */
[data-testid="stSelectbox"] > div > div {
    border-color: #CBD5E1 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    color: #1E293B !important;
}

/* ── EXPANDER LIGHT STYLE ── */
[data-testid="stExpander"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    background: #F8FAFC !important;
}
[data-testid="stExpander"] summary {
    color: #334155 !important;
    font-weight: 700 !important;
}

/* ── DATAFRAME LIGHT STYLE ── */
[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
}

/* ── GENERAL HEADINGS COLOR ── */
h1, h2, h3, h4, h5, h6 {
    color: #1E293B !important;
}

/* ── STEP BREADCRUMB ── */
.breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.82rem;
    color: #94A3B8;
    font-weight: 600;
    margin-bottom: 1.2rem;
}
.breadcrumb-active {
    color: #2563EB;
    font-weight: 700;
}

/* ── CTA BUTTON LARGE ── */
.cta-button-wrapper .stButton button {
    width: 100% !important;
    height: 56px !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    letter-spacing: -0.01em !important;
}
.cta-button-wrapper .stButton button:hover {
    background: #1D4ED8 !important;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.45) !important;
    transform: translateY(-1px);
}

/* ── CHECKBOX LIGHT ── */
[data-testid="stCheckbox"] label span {
    color: #334155 !important;
}
</style>
""", unsafe_allow_html=True)

    # Script to hide Streamlit UI elements
    components.html("""
<script>
const dict = {
    'Deploy': '',
    'System': 'Системна',
    'Light': 'Світла',
    'Dark': 'Темна',
    'Rerun': 'Перезапустити',
    'Auto rerun': 'Автоперезапуск',
    'Clear cache': 'Очистити кеш',
    'Print': 'Друкувати',
    'Settings': 'Налаштування'
};
function applyTranslations() {
    try {
        const rootDoc = window.parent.document;
        rootDoc.querySelectorAll('[data-testid="stDeployButton"]').forEach(el => el.style.setProperty('display', 'none', 'important'));
        rootDoc.querySelectorAll('[data-testid="InputInstructions"]').forEach(el => el.style.setProperty('display', 'none', 'important'));
        rootDoc.querySelectorAll('[data-testid="stSidebar"], [data-testid="collapsedControl"]').forEach(el => el.style.setProperty('display', 'none', 'important'));
        rootDoc.querySelectorAll('[data-testid="stHeader"], header, [data-testid="stToolbar"]').forEach(el => el.style.setProperty('display', 'none', 'important'));
    } catch (err) {}
}
try {
    const rootDoc = window.parent.document;
    const observer = new MutationObserver(applyTranslations);
    observer.observe(rootDoc.body, { childList: true, subtree: true });
    setInterval(applyTranslations, 300);
} catch(e) {}
</script>
""", height=0, width=0)


def render_html(html_str):
    """Render pure HTML without Markdown misinterpretation."""
    clean = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)
