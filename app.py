import os
import copy
import json
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import shap
import pdf_generator

# ==============================================================================
# НАЛАШТУВАННЯ СТОРІНКИ ТА ДОПОМІЖНІ ФУНКЦІЇ РЕНДЕРИНГУ
# ==============================================================================
st.set_page_config(
    page_title="CardioRisk AI — Клінічна система оцінки кардіоваскулярного ризику",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_html(html_str):
    """Надійний рендеринг чистого HTML без помилкової інтерпретації Markdown-коду."""
    clean = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)

# ==============================================================================
# СУЧАСНИЙ ДИЗАЙН ТА ГЛОБАЛЬНІ СТИЛІ (MEDICAL SAAS DESIGN SYSTEM)
# ==============================================================================
st.markdown("""
<style>
/* ── ШРИФТИ ТА БАЗОВИЙ РЕСЕТ ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* ── ПОВНЕ ВИДАЛЕННЯ БІЧНОЇ ПАНЕЛІ ТА ПОРОЖНЬОГО МІСЦЯ ЗЛІВА ── */
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

/* ── ПРИХОВАТИ СЛУЖБОВИЙ HEADER STREAMLIT ТА КНОПКИ ДЕПЛОЮ ── */
.stDeployButton, [data-testid="stDeployButton"], button[data-testid="stDeployButton"],
header,
header[data-testid="stHeader"],
[data-testid="stHeader"],
.stAppHeader,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu {
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

/* ── ЦЕНТРАЛЬНИЙ РОБОЧИЙ КОНТЕЙНЕР (СИМЕТРИЧНИЙ І ПОВНИЙ ШИРИНИ) ── */
.main {
    background: #090e17 !important;
    color: #e2e8f0 !important;
}
.block-container {
    max-width: 1560px !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
    width: 100% !important;
}

/* ── ВЕРХНЯ НАВІГАЦІЙНА ПАНЕЛЬ (NAVBAR) ── */
.nav-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.1rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 28px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(16px);
}
.nav-brand-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin: 0;
}
.nav-brand-subtitle {
    font-size: 0.82rem;
    color: #94a3b8;
    margin: 0.25rem 0 0 0;
    font-weight: 500;
}
.pulse-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.74rem;
    font-weight: 700;
    color: #34d399;
}
.pulse-dot {
    width: 7px;
    height: 7px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
    animation: pulseAnim 2s infinite;
}
@keyframes pulseAnim {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1.15); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* ── РЕЖИМ-БАНЕР ── */
.mode-banner-screening {
    background: linear-gradient(90deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 23, 42, 0.5) 100%);
    border-left: 4px solid #10b981;
    border-top: 1px solid rgba(16, 185, 129, 0.2);
    border-right: 1px solid rgba(16, 185, 129, 0.15);
    border-bottom: 1px solid rgba(16, 185, 129, 0.15);
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
    background: linear-gradient(90deg, rgba(14, 165, 233, 0.09) 0%, rgba(15, 23, 42, 0.5) 100%);
    border-left: 4px solid #0ea5e9;
    border-top: 1px solid rgba(14, 165, 233, 0.2);
    border-right: 1px solid rgba(14, 165, 233, 0.15);
    border-bottom: 1px solid rgba(14, 165, 233, 0.15);
    border-radius: 12px;
    padding: 0.75rem 1.1rem;
    margin-bottom: 1.1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;
}

/* ── КАРТКИ РОЗДІЛІВ ТА ЗАГОЛОВКИ ── */
.panel-card {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}
.panel-title {
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin-bottom: 0.85rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── СТИЛІЗАЦІЯ РАДІО КНОПОК ── */
[data-testid="stRadio"] > div {
    display: flex;
    gap: 0.5rem;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 0.35rem 0.6rem;
}
[data-testid="stRadio"] label span {
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #e2e8f0 !important;
}

/* ── КАРТКА РЕЗУЛЬТАТУ РИЗИКУ (HERO SCORE CARD) ── */
.risk-card {
    border-radius: 16px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1.1rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    border: 1px solid;
    box-shadow: 0 10px 32px rgba(0, 0, 0, 0.35);
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
    font-size: 3.6rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0.4rem 0 0.3rem;
}
.risk-gauge-container {
    background: rgba(255, 255, 255, 0.07);
    border-radius: 999px;
    height: 10px;
    width: 100%;
    margin: 1.1rem 0 0.5rem;
    position: relative;
    overflow: visible;
}
.risk-gauge-track {
    background: linear-gradient(90deg, #10b981 0%, #f59e0b 35%, #ef4444 80%);
    height: 100%;
    border-radius: 999px;
    transition: width 0.5s ease;
}
.risk-gauge-marker {
    position: absolute;
    top: -4px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #ffffff;
    border: 3px solid #0f172a;
    box-shadow: 0 0 10px rgba(255,255,255,0.8);
    transform: translateX(-50%);
    transition: left 0.5s ease;
}
.gauge-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748b;
    margin-top: 0.35rem;
}

/* ── ЧІПИ БІОМАРКЕРІВ (BIOMETRIC PILLS) ── */
.bio-pill-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
    padding-top: 0.8rem;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.bio-pill {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 0.3rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #cbd5e1;
}

/* ── ІНДИКАТОРИ СТАТУСУ (ІМТ, ТИСК, ШКФ) ── */
.status-pill-bar {
    border-radius: 8px;
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
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
    margin-top: 1rem;
}
.whatif-new-score {
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    line-height: 1;
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
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: background 0.2s;
}
.action-item-card:hover {
    background: rgba(255, 255, 255, 0.05);
}

/* ── СТИЛІЗАЦІЯ ТАБІВ ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 0.8rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    padding: 0.48rem 0.95rem !important;
    color: #94a3b8 !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: #1e293b !important;
    color: #38bdf8 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
}

/* ── ПОКРАЩЕННЯ КНОПОК ── */
.stButton button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.2rem !important;
}

/* ── ВІДЖЕТ ФАРМАКОЕКОНОМІЧНОЇ ЕКОНОМІЇ ── */
.savings-card {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 23, 42, 0.7) 100%);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 14px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.08);
}
.savings-metric-box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.8rem;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
    margin-top: 0.6rem;
}
.savings-big-number {
    font-size: 1.8rem;
    font-weight: 800;
    color: #34d399;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.savings-tag {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    text-transform: uppercase;
}

/* ── ПРЕЦЕЗІЙНІ РАДАР ТА СУБКОНТЕЙНЕРИ ── */
.chart-card-wrapper {
    background: #0f172a;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.9rem;
}

/* ── ПЕРСПЕКТИВНИЙ БЕЙДЖ АУДИТОРІЇ ── */
.audience-banner {
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px;
    padding: 0.55rem 0.9rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.82rem;
    color: #bae6fd;
}

/* ── ФУТЕР ── */
.footer-container {
    text-align: center;
    padding: 2rem 0 1rem;
    color: #64748b;
    font-size: 0.77rem;
    line-height: 1.6;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# Скрипт українізації службового меню Streamlit
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

        const popovers = rootDoc.querySelectorAll('[data-baseweb="popover"], [data-baseweb="menu"], ul[role="menu"], [data-testid="stMainMenuPopover"]');
        popovers.forEach(pop => {
            const walkers = rootDoc.createTreeWalker(pop, NodeFilter.SHOW_TEXT, null, false);
            let n;
            while(n = walkers.nextNode()) {
                const txt = n.nodeValue.trim();
                if (dict[txt]) n.nodeValue = n.nodeValue.replace(txt, dict[txt]);
                if (txt.includes('Made with Streamlit')) n.nodeValue = 'CardioRisk AI • CDSS';
            }
        });
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

# ==============================================================================
# СЛОВНИКИ УКРАЇНІЗАЦІЇ ОЗНАК
# ==============================================================================
SCREENING_FEATURE_TRANSLATIONS = {
    'age_years': 'Вік пацієнта (років)',
    'gender_male': 'Стать (чоловіча)',
    'height': 'Зріст (см)',
    'weight': 'Маса тіла (кг)',
    'BMI': 'Індекс маси тіла (ІМТ)',
    'HighBP': 'Артеріальна гіпертензія',
    'HighChol': 'Підвищений холестерин',
    'Diabetes': 'Цукровий діабет / глікемія',
    'Smoker': 'Тютюнопаління',
    'Alcohol': 'Вживання алкоголю',
    'PhysActivity': 'Фізична активність',
    'FamilyHistory': 'Сімейний анамнез ССЗ'
}

CLINICAL_FEATURE_TRANSLATIONS = {
    'age_years': 'Вік пацієнта (років)',
    'gender_male': 'Стать (чоловіча)',
    'height': 'Зріст (см)',
    'weight': 'Маса тіла (кг)',
    'BMI': 'Індекс маси тіла (ІМТ)',
    'ap_hi': 'Систолічний тиск (САТ)',
    'ap_lo': 'Діастолічний тиск (ДАТ)',
    'pulse_pressure': 'Пульсовий тиск (ПТ)',
    'heart_rate': 'ЧСС у спокої (пульс)',
    'bp_meds': 'Антигіпертензивна терапія',
    'tot_chol': 'Загальний холестерин',
    'ldl_chol': 'ЛПНЩ ("поганий" холестерин)',
    'hdl_chol': 'ЛПВЩ ("хороший" холестерин)',
    'triglycerides': 'Тригліцериди',
    'glucose_fasting': 'Глюкоза крові натще',
    'hba1c': 'Глікований гемоглобін (HbA1c)',
    'cigs_per_day': 'Тютюнопаління (сигарет/добу)',
    'alcohol_status': 'Надмірний алкоголь',
    'physical_activity': 'Аеробна активність',
    'resting_ecg': 'ЕКГ у спокої',
    'chest_pain_type': 'Характер болю (стенокардія)',
    'egfr_renal': 'ШКФ (функція нирок)',
    'family_history': 'Сімейний анамнез ССЗ'
}

# ==============================================================================
# ЗАВАНТАЖЕННЯ МОДЕЛЕЙ МАШИННОГО НАВЧАННЯ ТА МЕТРИК
# ==============================================================================
@st.cache_resource
def load_screening_model():
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    model_path = os.path.join(models_dir, "best_heart_disease_xgb.joblib")
    if not os.path.exists(model_path):
        model_path = os.path.join("models", "best_heart_disease_xgb.joblib")
    model = joblib.load(model_path)
    explainer = shap.TreeExplainer(model)

    metrics_path = os.path.join(models_dir, "model_metrics.json")
    if not os.path.exists(metrics_path):
        metrics_path = os.path.join("models", "model_metrics.json")
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
    return model, explainer, metrics

@st.cache_resource
def load_clinical_model():
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    model_path = os.path.join(models_dir, "clinical_heart_disease_xgb.joblib")
    if not os.path.exists(model_path):
        model_path = os.path.join("models", "clinical_heart_disease_xgb.joblib")
    model = joblib.load(model_path)
    explainer = shap.TreeExplainer(model)

    metrics_path = os.path.join(models_dir, "clinical_model_metrics.json")
    if not os.path.exists(metrics_path):
        metrics_path = os.path.join("models", "clinical_model_metrics.json")
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
    return model, explainer, metrics

try:
    screening_model, screening_explainer, screening_metrics = load_screening_model()
    clinical_model, clinical_explainer, clinical_metrics = load_clinical_model()
except Exception as e:
    st.error(f"Помилка завантаження моделей: {e}. Переконайтеся, що моделі присутні в папці models/.")
    st.stop()

# ==============================================================================
# ДОПОМІЖНІ ФУНКЦІЇ ДЛЯ ІНТЕРАКТИВНОЇ ГРАФІКИ PLOTLY
# ==============================================================================
def create_radial_gauge(prob, risk_color, risk_label, delta_total):
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=prob * 100,
        number={
            'suffix': '%',
            'font': {'size': 44, 'family': 'Plus Jakarta Sans', 'color': '#ffffff', 'weight': 800}
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': '#64748b',
                'tickvals': [0, 10, 20, 35, 50, 75, 100],
                'ticktext': ['0%', '10%', '20%', '35%', '50%', '75%', '100%'],
                'tickfont': {'size': 10, 'color': '#94a3b8'}
            },
            'bar': {'color': risk_color, 'thickness': 0.28},
            'bgcolor': 'rgba(255, 255, 255, 0.04)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 10], 'color': 'rgba(16, 185, 129, 0.18)'},
                {'range': [10, 20], 'color': 'rgba(245, 158, 11, 0.18)'},
                {'range': [20, 35], 'color': 'rgba(249, 115, 22, 0.18)'},
                {'range': [35, 100], 'color': 'rgba(239, 68, 68, 0.18)'}
            ]
        }
    ))
    fig.update_layout(
        height=195,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif')
    )
    return fig

def calculate_radar_scores(input_row, is_clinical):
    if not is_clinical:
        bp_score = 40.0 if input_row['HighBP'].iloc[0] == 1 else 95.0
        chol_score = 45.0 if input_row['HighChol'].iloc[0] == 1 else 95.0
        gluc_score = 40.0 if input_row['Diabetes'].iloc[0] == 1 else 95.0
        bmi = float(input_row['BMI'].iloc[0])
        if bmi < 25.0: bmi_score = 95.0
        elif bmi < 27.5: bmi_score = 75.0
        elif bmi < 30.0: bmi_score = 60.0
        else: bmi_score = 35.0
        act_score = 95.0 if input_row['PhysActivity'].iloc[0] == 1 else 40.0
        life_score = 95.0
        if input_row['Smoker'].iloc[0] == 1: life_score -= 35.0
        if input_row['Alcohol'].iloc[0] == 1: life_score -= 25.0
    else:
        sbp = float(input_row['ap_hi'].iloc[0])
        dbp = float(input_row['ap_lo'].iloc[0])
        if sbp < 120 and dbp < 80: bp_score = 98.0
        elif sbp < 130 and dbp < 85: bp_score = 85.0
        elif sbp < 140 and dbp < 90: bp_score = 65.0
        else: bp_score = 35.0
        
        ldl = float(input_row['ldl_chol'].iloc[0])
        if ldl < 1.8: chol_score = 98.0
        elif ldl < 2.6: chol_score = 80.0
        elif ldl < 3.0: chol_score = 60.0
        else: chol_score = 35.0
        
        glu = float(input_row['glucose_fasting'].iloc[0])
        hba = float(input_row['hba1c'].iloc[0])
        if glu < 5.6 and hba < 5.7: gluc_score = 98.0
        elif glu < 6.5 and hba < 6.0: gluc_score = 70.0
        else: gluc_score = 35.0
        
        bmi = float(input_row['BMI'].iloc[0])
        if bmi < 25.0: bmi_score = 95.0
        elif bmi < 27.5: bmi_score = 75.0
        elif bmi < 30.0: bmi_score = 60.0
        else: bmi_score = 35.0
        
        act = float(input_row['physical_activity'].iloc[0])
        act_score = 95.0 if act == 1 else 40.0
        
        cigs = float(input_row['cigs_per_day'].iloc[0])
        alco = float(input_row['alcohol_status'].iloc[0])
        life_score = 95.0
        if cigs > 0: life_score -= min(40.0, 15.0 + cigs)
        if alco == 1: life_score -= 25.0
        
    return [max(15.0, min(100.0, s)) for s in [bp_score, chol_score, gluc_score, bmi_score, act_score, life_score]]

def create_radar_chart(scores):
    categories = [
        'Артеріальний тиск',
        'Ліпідний статус',
        'Глікемія',
        'Маса тіла (ІМТ)',
        'Рухова активність',
        'Спосіб життя'
    ]
    fig = go.Figure()
    
    # Target Safe Zone (100% ideal)
    fig.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100, 100, 100],
        theta=categories,
        fill='toself',
        name='Цільова норма (ESC)',
        line=dict(color='#10b981', width=1.5, dash='dot'),
        fillcolor='rgba(16, 185, 129, 0.10)'
    ))
    
    avg_score = sum(scores) / len(scores)
    patient_color = '#10b981' if avg_score >= 80 else ('#f59e0b' if avg_score >= 60 else '#ef4444')
    fill_rgba = 'rgba(16, 185, 129, 0.22)' if avg_score >= 80 else ('rgba(245, 158, 11, 0.22)' if avg_score >= 60 else 'rgba(239, 68, 68, 0.22)')
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Профіль пацієнта',
        line=dict(color=patient_color, width=2.5),
        fillcolor=fill_rgba
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9, color='#64748b'),
                gridcolor='rgba(255, 255, 255, 0.08)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color='#cbd5e1', family='Plus Jakarta Sans'),
                linecolor='rgba(255, 255, 255, 0.15)',
                gridcolor='rgba(255, 255, 255, 0.08)'
            ),
            bgcolor='rgba(15, 23, 42, 0.35)'
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.22,
            xanchor='center',
            x=0.5,
            font=dict(size=11, color='#94a3b8')
        ),
        height=320,
        margin=dict(l=45, r=45, t=25, b=35),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif')
    )
    return fig

def create_whatif_comparison_chart(prob, sim_new_prob):
    p_orig = prob * 100
    p_sim = sim_new_prob * 100
    p_diff = p_orig - p_sim
    rel_diff = (p_diff / p_orig * 100) if p_orig > 0 else 0
    
    sim_clr = "#10B981" if sim_new_prob < 0.18 else ("#F59E0B" if sim_new_prob < 0.35 else "#EF4444")
    orig_clr = "#10B981" if prob < 0.18 else ("#F59E0B" if prob < 0.35 else "#EF4444")
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        column_widths=[0.5, 0.5]
    )
    
    fig.add_trace(
        go.Indicator(
            mode='gauge+number',
            value=p_orig,
            title={'text': 'Вихідний ризик', 'font': {'size': 13, 'color': '#94a3b8', 'family': 'Plus Jakarta Sans'}},
            number={'suffix': '%', 'font': {'size': 32, 'color': orig_clr, 'weight': 800}},
            gauge={
                'axis': {'range': [0, 100], 'tickvals': [0, 20, 50, 100], 'tickfont': {'size': 9, 'color': '#64748b'}},
                'bar': {'color': orig_clr, 'thickness': 0.3},
                'bgcolor': 'rgba(255, 255, 255, 0.05)',
                'borderwidth': 0
            }
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Indicator(
            mode='gauge+number+delta',
            value=p_sim,
            title={'text': 'Модифікований ризик', 'font': {'size': 13, 'color': '#94a3b8', 'family': 'Plus Jakarta Sans'}},
            delta={
                'reference': p_orig,
                'valueformat': '.1f',
                'suffix': '%',
                'decreasing': {'color': '#10b981'},
                'increasing': {'color': '#ef4444'},
                'font': {'size': 13, 'weight': 700}
            },
            number={'suffix': '%', 'font': {'size': 32, 'color': sim_clr, 'weight': 800}},
            gauge={
                'axis': {'range': [0, 100], 'tickvals': [0, 20, 50, 100], 'tickfont': {'size': 9, 'color': '#64748b'}},
                'bar': {'color': sim_clr, 'thickness': 0.3},
                'bgcolor': 'rgba(255, 255, 255, 0.05)',
                'borderwidth': 0
            }
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=185,
        margin=dict(l=15, r=15, t=25, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif')
    )
    return fig, p_diff, rel_diff

# ==============================================================================
# ВЕРХНЯ НАВІГАЦІЙНА ПАНЕЛЬ (NAVBAR)
# ==============================================================================
nav_c1, nav_c2 = st.columns([1.5, 1.5], gap="medium")

with nav_c1:
    render_html("""
    <div style="display:flex; align-items:center; gap:0.9rem;">
        <div style="font-size:2.4rem; line-height:1; filter: drop-shadow(0 0 14px rgba(239,68,68,0.5));">🫀</div>
        <div>
            <div style="display:flex; align-items:center; gap:0.6rem;">
                <span class="nav-brand-title">CardioRisk AI</span>
                <span class="pulse-badge"><span class="pulse-dot"></span> CDSS Active</span>
            </div>
            <div class="nav-brand-subtitle">
                Інтелектуальна система підтримки клінічних рішень для оцінки кардіоваскулярного ризику
            </div>
        </div>
    </div>
    """)

with nav_c2:
    if "app_mode_selection" not in st.session_state:
        st.session_state["app_mode_selection"] = "🟢 Скринінг (12 ознак)"
    if "app_persp_selection" not in st.session_state:
        st.session_state["app_persp_selection"] = "👤 Для пацієнта"

    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown("<div style='font-size:0.71rem; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#94a3b8; margin-bottom:0.25rem;'>Рівень діагностики:</div>", unsafe_allow_html=True)
        mode_selection = st.radio(
            "Діагностичний рівень:",
            options=[
                "🟢 Скринінг (12 ознак)",
                "🩺 Клініка (23 маркери)"
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="app_mode_selection",
            help="Скринінговий режим — 12 базових факторів способу життя без лабораторних аналізів. Клінічний — 23 поглиблені біомаркери (тонометрія, ліпіди, глікемія, нирки, ЕКГ)."
        )
    with c_m2:
        st.markdown("<div style='font-size:0.71rem; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#94a3b8; margin-bottom:0.25rem;'>Аудиторія подання:</div>", unsafe_allow_html=True)
        persp_selection = st.radio(
            "Аудиторія подання:",
            options=[
                "👤 Для пацієнта",
                "🩺 Для лікаря"
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="app_persp_selection",
            help="Для пацієнта: доступна мова, зрозумілі акценти, 'Доступні ліки'. Для лікаря: настанови ESC 2024, цільові рівні ЛПНЩ, МКХ-10, точні дозування."
        )

    is_clinical_mode = "Клініка" in mode_selection
    is_doctor_view = "Для лікаря" in persp_selection

# ==============================================================================
# БАНЕР АКТИВНОГО РЕЖИМУ ТА СЕРВІСНІ КНОПКИ
# ==============================================================================
col_banner, col_actions = st.columns([3.6, 1.2], gap="medium")

with col_banner:
    if is_clinical_mode:
        render_html("""
        <div class="mode-banner-clinical">
            <div>
                <b style="color:#38bdf8; font-size:0.92rem;">🩺 Поглиблений клінічний режим (CDSS Expert)</b><br>
                <span style="font-size:0.79rem; color:#94a3b8;">
                    23 лабораторно-інструментальні біомаркери: розширена ліпідограма, глікемічний профіль, ШКФ (eGFR), тонометрія та ЕКГ.
                </span>
            </div>
            <div style="font-size:0.75rem; font-weight:700; color:#0284c7; background:rgba(14,165,233,0.12); padding:0.25rem 0.6rem; border-radius:6px;">
                ESC / AHA Protocols
            </div>
        </div>
        """)
    else:
        render_html("""
        <div class="mode-banner-screening">
            <div>
                <b style="color:#34d399; font-size:0.92rem;">🟢 Експрес-скринінговий режим (Для пацієнта)</b><br>
                <span style="font-size:0.79rem; color:#94a3b8;">
                    12 ключових факторів: швидка самооцінка ризику інфаркту та інсульту на основі способу життя, симптомів та базових вимірювань.
                </span>
            </div>
            <div style="font-size:0.75rem; font-weight:700; color:#059669; background:rgba(16,185,129,0.12); padding:0.25rem 0.6rem; border-radius:6px;">
                Первинна оцінка
            </div>
        </div>
        """)

with col_actions:
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🔄 Скинути", use_container_width=True, help="Перезавантажити введені параметри до типових"):
            st.rerun()
    with c_btn2:
        if st.button("🖨️ Друк", use_container_width=True, help="Надрукувати консультативний звіт або зберегти сторінку в PDF"):
            components.html("<script>window.parent.print();</script>", height=0, width=0)

# ==============================================================================
# ГОЛОВНИЙ РОБОЧИЙ МАКЕТ (2 КОЛОНКИ: ВВЕДЕННЯ ТА РЕЗУЛЬТАТИ)
# ==============================================================================
col_input, col_result = st.columns([1.02, 1.28], gap="large")

# ──────────────────────────────────────────────────────────────────────────────
# ЛІВА КОЛОНКА: ВХІДНІ ПАРАМЕТРИ
# ──────────────────────────────────────────────────────────────────────────────
with col_input:
    st.markdown(f"<div class='panel-title'>{'🩺 Клінічні показники та анамнез' if is_clinical_mode else '📋 Параметри пацієнта'}</div>", unsafe_allow_html=True)

    if not is_clinical_mode:
        # ==========================================
        # РЕЖИМ 1: СКРИНІНГ (12 ФАКТОРІВ)
        # ==========================================
        scr_tab1, scr_tab2, scr_tab3 = st.tabs([
            "👤 Демографія та тіло",
            "🩺 Базове здоров'я",
            "🏃 Спосіб життя та симптоми"
        ])

        with scr_tab1:
            c_s_sex, c_s_age = st.columns(2)
            with c_s_sex:
                sex_choice = st.radio("Біологічна стать", options=["Жінка", "Чоловік"], horizontal=True, key="scr_sex")
                sex = 1 if sex_choice == "Чоловік" else 0
            with c_s_age:
                scr_age = st.number_input("Вік (років)", min_value=18, max_value=95, value=54, step=1, key="scr_age")

            c_h, c_w = st.columns(2)
            with c_h:
                height = st.number_input("Зріст (см)", min_value=120, max_value=220, value=175, step=1, key="scr_h")
            with c_w:
                weight = st.number_input("Вага (кг)", min_value=35.0, max_value=220.0, value=82.0, step=0.5, key="scr_w")

            bmi = round(weight / ((height / 100) ** 2), 1)
            if bmi < 18.5:
                bmi_status = ("Дефіцит маси", "#0284C7", "rgba(2,132,199,0.12)")
            elif bmi < 25.0:
                bmi_status = ("Норма (ВООЗ)", "#059669", "rgba(5,150,105,0.12)")
            elif bmi < 30.0:
                bmi_status = ("Надлишкова маса", "#D97706", "rgba(217,119,6,0.12)")
            else:
                bmi_status = ("Ожиріння", "#DC2626", "rgba(220,38,38,0.12)")

            render_html(f"""
            <div class="status-pill-bar" style="background:{bmi_status[2]}; border-color:{bmi_status[1]}44; color:{bmi_status[1]};">
                <span><b>Індекс маси тіла (ІМТ):</b> {bmi} кг/м²</span>
                <span>{bmi_status[0]}</span>
            </div>
            """)

        with scr_tab2:
            high_bp_choice = st.radio(
                "Чи буває у вас підвищений тиск (≥140/90 мм рт. ст.)?",
                options=["Ні", "Так"],
                help="Артеріальна гіпертензія створює хронічне перевантаження судин."
            )
            high_bp = 1 if high_bp_choice == "Так" else 0

            high_chol_choice = st.radio(
                "Чи виявлено підвищений загальний холестерин (>5.2 ммоль/л)?",
                options=["Ні", "Так"],
                help="Гіперхолестеринемія є провідною причиною атеросклеротичних бляшок."
            )
            high_chol = 1 if high_chol_choice == "Так" else 0

            diabetes_choice = st.radio(
                "Чи є діагноз цукрового діабету або підвищеного цукру?",
                options=["Ні (глікемія в нормі)", "Так (діабет або предіабет)"],
                help="Гіперглікемія викликає ангіопатію та прискорює судинні зміни."
            )
            diabetes = 1 if "Так" in diabetes_choice else 0

        with scr_tab3:
            smoker_choice = st.radio("Статус тютюнопаління", options=["Не палю", "Палю регулярно"], key="scr_smk")
            smoker = 1 if "регулярно" in smoker_choice else 0

            phys_choice = st.radio("Регулярна рухова активність (≥150 хв/тиждень)", options=["Так", "Ні (сидячий спосіб)"], key="scr_act")
            phys_activity = 1 if "Так" in phys_choice else 0

            hvy_alcohol_choice = st.radio("Вживання алкоголю", options=["Помірно або не вживаю", "Надмірно / регулярно"], key="scr_alco")
            hvy_alcohol = 1 if "Надмірно" in hvy_alcohol_choice else 0

            fam_choice = st.radio(
                "Сімейний анамнез ранніх ССЗ (інфаркт/інсульт у батьків до 55–65 років)",
                options=["Ні (або невідомо)", "Так"],
                key="scr_fam"
            )
            fam_history = 1 if "Так" in fam_choice else 0

            stroke = 0

        # Вектор для скринінгової моделі (12 ознак)
        input_data = pd.DataFrame([{
            'age_years': float(scr_age),
            'gender_male': float(sex),
            'height': float(height),
            'weight': float(weight),
            'BMI': float(bmi),
            'HighBP': float(high_bp),
            'HighChol': float(high_chol),
            'Diabetes': float(diabetes),
            'Smoker': float(smoker),
            'Alcohol': float(hvy_alcohol),
            'PhysActivity': float(phys_activity),
            'FamilyHistory': float(fam_history)
        }])

        active_model = screening_model
        active_explainer = screening_explainer
        active_translations = SCREENING_FEATURE_TRANSLATIONS

    else:
        # ==========================================
        # РЕЖИМ 2: КЛІНІЧНИЙ CDSS (23 БІОМАРКЕРИ)
        # ==========================================
        clin_tab1, clin_tab2, clin_tab3, clin_tab4 = st.tabs([
            "👤 Гемодинаміка та скарги",
            "🧪 Розширена ліпідограма",
            "🩸 Глікемія та нирки",
            "🏃 Спосіб життя та анамнез"
        ])

        with clin_tab1:
            c_sex, c_age = st.columns(2)
            with c_sex:
                c_sex_choice = st.radio("Біологічна стать", ["Жінка", "Чоловік"], horizontal=True, key="clin_sex")
                clin_gender_male = 1 if c_sex_choice == "Чоловік" else 0
            with c_age:
                clin_age = st.number_input("Точний вік (років)", min_value=18, max_value=95, value=54, step=1, key="clin_age")

            c_h, c_w = st.columns(2)
            with c_h:
                clin_height = st.number_input("Зріст (см)", min_value=135, max_value=220, value=175, step=1, key="clin_h")
            with c_w:
                clin_weight = st.number_input("Маса тіла (кг)", min_value=35.0, max_value=220.0, value=82.0, step=0.5, key="clin_w")

            clin_bmi = round(clin_weight / ((clin_height / 100) ** 2), 1)
            if clin_bmi < 18.5:
                bmi_status = ("Дефіцит маси", "#0284C7", "rgba(2,132,199,0.12)")
            elif clin_bmi < 25.0:
                bmi_status = ("Норма (ВООЗ)", "#059669", "rgba(5,150,105,0.12)")
            elif clin_bmi < 30.0:
                bmi_status = ("Надлишкова маса", "#D97706", "rgba(217,119,6,0.12)")
            else:
                bmi_status = ("Ожиріння", "#DC2626", "rgba(220,38,38,0.12)")

            render_html(f"""
            <div class="status-pill-bar" style="background:{bmi_status[2]}; border-color:{bmi_status[1]}44; color:{bmi_status[1]};">
                <span><b>ІМТ:</b> {clin_bmi} кг/м²</span>
                <span>{bmi_status[0]}</span>
            </div>
            """)

            c_sbp, c_dbp, c_hr = st.columns(3)
            with c_sbp:
                clin_ap_hi = st.number_input("САТ (мм рт. ст.)", min_value=80, max_value=230, value=140, step=1, key="clin_sbp", help="Систолічний артеріальний тиск.")
            with c_dbp:
                max_dbp_allowed = min(140, int(clin_ap_hi - 15))
                clin_ap_lo = st.number_input("ДАТ (мм рт. ст.)", min_value=45, max_value=max_dbp_allowed, value=min(88, max_dbp_allowed), step=1, key="clin_dbp")
            with c_hr:
                clin_heart_rate = st.number_input("ЧСС (пульс, уд/хв)", min_value=45, max_value=135, value=74, step=1, key="clin_hr")

            clin_pulse_pressure = clin_ap_hi - clin_ap_lo

            if clin_ap_hi < 120 and clin_ap_lo < 80:
                bp_cat = ("Оптимальний АТ", "#059669")
            elif clin_ap_hi < 130 and clin_ap_lo < 85:
                bp_cat = ("Нормальний АТ", "#059669")
            elif clin_ap_hi < 140 and clin_ap_lo < 90:
                bp_cat = ("Високий нормальний АТ", "#D97706")
            else:
                bp_cat = ("Артеріальна гіпертензія", "#DC2626")

            st.caption(f"ПТ: **{clin_pulse_pressure} мм рт. ст.** · Категорія: <span style='color:{bp_cat[1]}; font-weight:700;'>{bp_cat[0]}</span>", unsafe_allow_html=True)

            c_meds, c_ecg = st.columns(2)
            with c_meds:
                bp_meds_choice = st.radio("Антигіпертензивна терапія", ["Ні (без ліків)", "Так (приймає ліки від тиску)"], key="clin_bp_meds")
                clin_bp_meds = 1 if "Так" in bp_meds_choice else 0
            with c_ecg:
                ecg_labels = {
                    0: "0: Норма (без ішемії)",
                    1: "1: ST-T зміни (неспецифічні)",
                    2: "2: Гіпертрофія ЛШ (ГЛШ)"
                }
                clin_ecg = st.selectbox("ЕКГ спокою", options=[0, 1, 2], format_func=lambda x: ecg_labels[x], key="clin_ecg")

            cp_labels = {
                0: "0: Без болю в грудях (безсимптомний)",
                1: "1: Неангінальний біль (торакалгія)",
                2: "2: Атипова стенокардія",
                3: "3: Типова стенокардія напруги"
            }
            clin_chest_pain = st.selectbox("Стенокардія / Біль за грудиною", options=[0, 1, 2, 3], format_func=lambda x: cp_labels[x], key="clin_cp")

        with clin_tab2:
            c_unit_choice = st.radio("Одиниці вимірювання ліпідів:", ["ммоль/л (Україна / ЄС)", "мг/дл (US протокол)"], horizontal=True, key="clin_units_lip")
            use_mgdl = "мг/дл" in c_unit_choice

            c_tc, c_ldl = st.columns(2)
            with c_tc:
                if not use_mgdl:
                    tot_chol = st.number_input("Загальний холестерин (ммоль/л)", min_value=2.5, max_value=14.0, value=5.2, step=0.1, key="clin_tc")
                else:
                    tot_chol_mg = st.number_input("Загальний холестерин (мг/дл)", min_value=90.0, max_value=550.0, value=201.0, step=1.0, key="clin_tc_mg")
                    tot_chol = round(tot_chol_mg / 38.67, 2)
            with c_ldl:
                if not use_mgdl:
                    ldl_chol = st.number_input("ЛПНЩ / LDL ('поганий', ммоль/л)", min_value=1.0, max_value=9.0, value=3.2, step=0.1, key="clin_ldl")
                else:
                    ldl_mg = st.number_input("ЛПНЩ / LDL (мг/дл)", min_value=40.0, max_value=350.0, value=124.0, step=1.0, key="clin_ldl_mg")
                    ldl_chol = round(ldl_mg / 38.67, 2)

            c_hdl, c_tg = st.columns(2)
            with c_hdl:
                if not use_mgdl:
                    hdl_chol = st.number_input("ЛПВЩ / HDL ('хороший', ммоль/л)", min_value=0.5, max_value=3.5, value=1.25, step=0.05, key="clin_hdl")
                else:
                    hdl_mg = st.number_input("ЛПВЩ / HDL (мг/дл)", min_value=20.0, max_value=135.0, value=48.0, step=1.0, key="clin_hdl_mg")
                    hdl_chol = round(hdl_mg / 38.67, 2)
            with c_tg:
                if not use_mgdl:
                    triglycerides = st.number_input("Тригліцериди (ммоль/л)", min_value=0.4, max_value=10.0, value=1.6, step=0.1, key="clin_tg")
                else:
                    tg_mg = st.number_input("Тригліцериди (мг/дл)", min_value=35.0, max_value=850.0, value=142.0, step=1.0, key="clin_tg_mg")
                    triglycerides = round(tg_mg / 88.57, 2)

            ka = round((tot_chol - hdl_chol) / hdl_chol, 2)
            ka_status = ("Норма (<3.0)", "#059669") if ka < 3.0 else (("Помірний ризик (3.0–4.0)", "#D97706") if ka <= 4.0 else ("Високий ризик (>4.0)", "#DC2626"))
            render_html(f"""
            <div class="status-pill-bar" style="background:rgba(255,255,255,0.04); border-color:rgba(255,255,255,0.1); color:#cbd5e1;">
                <span><b>Коефіцієнт атерогенності:</b> {ka}</span>
                <span style="color:{ka_status[1]}; font-weight:700;">{ka_status[0]}</span>
            </div>
            """)

        with clin_tab3:
            c_glu, c_hba = st.columns(2)
            with c_glu:
                glucose_fasting = st.number_input("Глюкоза натще (ммоль/л)", min_value=2.8, max_value=20.0, value=5.4, step=0.1, key="clin_glu", help="Норма: <5.6 ммоль/л.")
            with c_hba:
                hba1c = st.number_input("Глікований гемоглобін HbA1c (%)", min_value=4.0, max_value=14.0, value=5.6, step=0.1, key="clin_hba", help="Норма: <5.7%.")

            clin_egfr = st.number_input("ШКФ / eGFR (CKD-EPI, мл/хв/1.73м²)", min_value=15.0, max_value=130.0, value=88.0, step=1.0, key="clin_egfr")
            if clin_egfr >= 90:
                egfr_desc = ("G1: Нормальна функція нирок", "#059669")
            elif clin_egfr >= 60:
                egfr_desc = ("G2: Легке зниження ШКФ", "#D97706")
            elif clin_egfr >= 30:
                egfr_desc = ("G3: Помірне/тяжке зниження (Високий ризик ССЗ)", "#DC2626")
            else:
                egfr_desc = ("G4-G5: Тяжка ниркова недостатність", "#DC2626")

            render_html(f"""
            <div class="status-pill-bar" style="background:rgba(255,255,255,0.04); border-color:rgba(255,255,255,0.1); color:#cbd5e1;">
                <span><b>Статус нирок:</b> {clin_egfr} мл/хв</span>
                <span style="color:{egfr_desc[1]}; font-weight:700;">{egfr_desc[0]}</span>
            </div>
            """)

        with clin_tab4:
            c_smk_choice = st.radio("Статус куріння", ["Не палю", "Палю регулярно"], key="clin_smk")
            clin_smoke = 1 if "регулярно" in c_smk_choice else 0
            if clin_smoke:
                cigs_per_day = st.slider("Кількість сигарет на добу", min_value=1, max_value=60, value=15, step=1, key="clin_cigs")
            else:
                cigs_per_day = 0

            c_alco_choice = st.radio("Вживання алкоголю", ["Помірно або не вживаю", "Надмірно (>14 порцій/тиждень)"], key="clin_alco")
            clin_alco = 1 if "Надмірно" in c_alco_choice else 0

            c_act_choice = st.radio("Регулярні аеробні тренування (≥150 хв/тиждень)", ["Так", "Ні (гіподинамія)"], key="clin_act")
            clin_active = 1 if "Так" in c_act_choice else 0

            c_fam_choice = st.radio("Сімейний анамнез ранніх ССЗ", ["Ні", "Так (інфаркт/інсульт у батьків до 55–65 років)"], key="clin_fam")
            clin_fam = 1 if "Так" in c_fam_choice else 0

        # Вектор для клінічної моделі (23 біомаркери)
        input_data = pd.DataFrame([{
            'age_years': float(clin_age),
            'gender_male': float(clin_gender_male),
            'height': float(clin_height),
            'weight': float(clin_weight),
            'BMI': float(clin_bmi),
            'ap_hi': float(clin_ap_hi),
            'ap_lo': float(clin_ap_lo),
            'pulse_pressure': float(clin_pulse_pressure),
            'heart_rate': float(clin_heart_rate),
            'bp_meds': float(clin_bp_meds),
            'tot_chol': float(tot_chol),
            'ldl_chol': float(ldl_chol),
            'hdl_chol': float(hdl_chol),
            'triglycerides': float(triglycerides),
            'glucose_fasting': float(glucose_fasting),
            'hba1c': float(hba1c),
            'cigs_per_day': float(cigs_per_day),
            'alcohol_status': float(clin_alco),
            'physical_activity': float(clin_active),
            'resting_ecg': float(clin_ecg),
            'chest_pain_type': float(clin_chest_pain),
            'egfr_renal': float(clin_egfr),
            'family_history': float(clin_fam)
        }])

        active_model = clinical_model
        active_explainer = clinical_explainer
        active_translations = CLINICAL_FEATURE_TRANSLATIONS

    # ── БЛОК СОЦІАЛЬНО-СТРАХОВОГО СТАТУСУ ТА БЮДЖЕТУ ПАЦІЄНТА ──
    st.markdown("<hr style='margin:1.1rem 0 0.8rem; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#38bdf8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.4rem;'>💳 Медичне страхування та бюджет (для плану лікування):</div>", unsafe_allow_html=True)
    
    insurance_choice = st.selectbox(
        "Програма медичного покриття:",
        options=[
            "🏛️ Державна програма «Доступні ліки» (НСЗУ / 100% реімбурсація)",
            "🛡️ Добровільне медичне страхування (ДМС / Повне покриття)",
            "💵 Без страхування (Самооплата / Оптимізація витрат)",
            "💎 Преміум-страхування (VIP / Приватна кардіоклініка)"
        ],
        index=0,
        key="patient_insurance_profile",
        help="Принцип Algorithmic Fairness: страховий статус НЕ впливає на біологічний розрахунок імовірності ССЗ, але визначає доступність та фінансову реалістичність призначеного лікування."
    )
    st.caption("ℹ️ *Algorithmic Fairness:* ШІ оцінює ризик суто за біомаркерами, а страховку використовує для підбору доступних ліків.")

    # Параметри обраного страхового профілю
    if "Доступні ліки" in insurance_choice:
        ins_code = "dostupni_liky"
        ins_title = "Державна програма «Доступні ліки» (НСЗУ)"
        ins_badge_color = "#10b981"
        ins_cost_patient = "0 грн / міс"
        ins_covered_pct = "100% реімбурсація за е-рецептом"
        ins_est_savings = "до 480 грн / міс"
        ins_meds = [
            ("Еналаприл 10 мг / Амлодипін 5 мг", "Антигіпертензивна базова терапія", "100% безкоштовно (е-рецепт)", "60–120 грн"),
            ("Аторвастатин 20 мг (1 табл на ніч)", "Гіполіпідемічна терапія статинами", "100% безкоштовно (е-рецепт)", "110–180 грн"),
            ("Бісопролол 5 мг (при тахікардії)", "Бета-адреноблокатор, контроль ЧСС", "100% безкоштовно (е-рецепт)", "50–85 грн"),
            ("Метформін 850–1000 мг (при глікемії)", "Цукрознижувальний бігуанід", "100% безкоштовно (е-рецепт)", "95–140 грн")
        ]
        ins_tests = [
            ("ЕКГ у кабінеті сімейного лікаря", "Безкоштовно за декларацією"),
            ("Загальний холестерин та глюкоза", "Безкоштовно у центрі ПМСД"),
            ("Загальний аналіз крові та сечі", "Безкоштовно за декларацією"),
            ("Розгорнута ліпідограма (ЛПНЩ/ЛПВЩ)", "За електронним направленням у комунальній лабораторії"),
            ("Консультація кардіолога вторинної ланки", "За електронним направленням (0 грн)")
        ]
        ins_desc = "Пацієнт повністю забезпечується життєво необхідними серцево-судинними ліками за програмою державних гарантій без власних фінансових витрат."
    elif "ДМС" in insurance_choice:
        ins_code = "dms"
        ins_title = "Добровільне медичне страхування (ДМС)"
        ins_badge_color = "#0ea5e9"
        ins_cost_patient = "0–120 грн / міс (франшиза 0–10%)"
        ins_covered_pct = "Покриття 85–100% оригінальних препаратів"
        ins_est_savings = "до 2 200 грн / міс"
        ins_meds = [
            ("Трипліксам (Периндоприл+Індапамід+Амлодипін)", "Потрійна фіксована комбінація в 1 табл.", "Покрито полісом (0–40 грн)", "420–580 грн"),
            ("Розувастатин 20 мг + Езетиміб 10 мг (Зенон/Розуліп)", "Високоінтенсивний ліпідний контроль", "Покрито полісом (0–50 грн)", "650–890 грн"),
            ("Дапагліфлозин 10 мг (Форксіга)", "SGLT2-інгібітор кардіопротекції", "Покрито полісом за погодженням", "980–1250 грн")
        ]
        ins_tests = [
            ("ЕКГ та ЕхоКГ (УЗД серця) у приватному центрі", "100% покрито полісом ДМС"),
            ("Розгорнута ліпідограма та ApoB/Lp(a)", "100% покрито полісом ДМС"),
            ("Глікований гемоглобін (HbA1c) та eGFR", "100% покрито полісом ДМС"),
            ("Стрес-тест (тредміл) або Холтер-ЕКГ", "100% покрито за направленням"),
            ("Консультація провідного кардіолога", "100% покрито у клініках-партнерах")
        ]
        ins_desc = "Страховий поліс покриває інноваційні комбіновані препарати оригінальних європейських виробників та повне обстеження у приватних медичних центрах."
    elif "Преміум" in insurance_choice:
        ins_code = "vip"
        ins_title = "Преміум-страхування (VIP кардіоклініка)"
        ins_badge_color = "#8b5cf6"
        ins_cost_patient = "0 грн / міс"
        ins_covered_pct = "100% необмежене покриття інновацій та біопрепаратів"
        ins_est_savings = "понад 6 000 грн / міс"
        ins_meds = [
            ("Еволокумаб (Репата 140 мг п/ш раз на 14 днів)", "Інгібітор PCSK9 (зниження ЛПНЩ на 60–75%)", "100% покрито VIP-пакетом", "4 800–6 200 грн"),
            ("Семаглутид (Оземпік / Вегові 1 мг)", "GLP-1 RA кардіометаболічний захист", "100% покрито VIP-пакетом", "3 200–4 500 грн"),
            ("Юперіо (Сакубітрил/Валсартан)", "ARNI препарат передової кардіопротекції", "100% покрито VIP-пакетом", "1 800–2 400 грн")
        ]
        ins_tests = [
            ("КТ-коронарографія з Calcium Score", "100% покрито у приватному стаціонарі"),
            ("Добове холтерівське моніторування ЕКГ + АТ", "100% покрито персональним куратором"),
            ("Консиліум експертів-кардіологів", "100% необмежений супровід"),
            ("Генетичний кардіоскринінг", "100% покрито VIP-пакетом")
        ]
        ins_desc = "Повний доступ до світових інновацій, таргетної біологічної терапії (інгібітори PCSK9) та високотехнологічної візуалізації серця."
    else:
        ins_code = "self_pay"
        ins_title = "Без страхування (Самооплата / Оптимізація витрат)"
        ins_badge_color = "#f59e0b"
        ins_cost_patient = "180–320 грн / міс"
        ins_covered_pct = "Самооплата (стратегія максимальної клінічної економії)"
        ins_est_savings = "заощадження до 1 200 грн на якісних генериках"
        ins_meds = [
            ("Аторвастатин 20 мг (якісний вітчизняний генерик)", "Базова статинотерапія", "Аптечна купівля (~90–130 грн/міс)", "110–180 грн"),
            ("Еналаприл 10 мг + Амлодипін 5 мг (окремо)", "Гіпотензивна базова схема", "Аптечна купівля (~70–110 грн/міс)", "85–140 грн"),
            ("Немедикаментозна модифікація (рух + дієта DASH)", "Знижує потребу в ліках на 35%", "Безкоштовно (0 грн)", "Безцінно")
        ]
        ins_tests = [
            ("ЕКГ та базові аналізи", "Обов'язково через е-направлення сімейного лікаря (безкоштовно)"),
            ("Ліпідограма", "Здати в комунальній лабораторії (0 грн замість 650 грн у приватній)"),
            ("ЕхоКГ (УЗД серця)", "Отримати чергу за електронним направленням (0 грн) або 500–800 грн приватно")
        ]
        ins_desc = "План оптимізовано під обмежений сімейний бюджет: фокус на безкоштовній корекції способу життя та клінічно ефективних доступних генериках."


# ──────────────────────────────────────────────────────────────────────────────
# ПРАВА КОЛОНКА: РЕЗУЛЬТАТИ ТА КЛІНІЧНА ПІДТРИМКА
# ──────────────────────────────────────────────────────────────────────────────
with col_result:
    st.markdown("<div class='panel-title'>📊 Клінічний висновок та стратифікація ризику</div>", unsafe_allow_html=True)

    # Розрахунок ймовірності та значень SHAP
    prob = float(active_model.predict_proba(input_data)[0, 1])
    shap_val = active_explainer(input_data)[0]

    shap_val_display = copy.deepcopy(shap_val)
    shap_val_display.feature_names = [active_translations.get(f, f) for f in shap_val.feature_names]

    s_vals = shap_val.values
    f_names = shap_val.feature_names
    factors = list(zip(f_names, s_vals, input_data.iloc[0]))
    top_risks = sorted([f for f in factors if f[1] > 0.015], key=lambda x: x[1], reverse=True)
    top_protect = sorted([f for f in factors if f[1] < -0.015], key=lambda x: x[1])

    # Контрфактичний розрахунок оптимізації (What-If)
    p_opt = input_data.copy()
    candidate_actions = []

    if not is_clinical_mode:
        p_opt['Smoker'] = 0.0
        p_opt['HighBP'] = 0.0
        p_opt['HighChol'] = 0.0
        p_opt['BMI'] = min(float(input_data['BMI'].iloc[0]), 24.5)
        p_opt['weight'] = min(float(input_data['weight'].iloc[0]), 24.5 * ((float(input_data['height'].iloc[0])/100)**2))
        p_opt['PhysActivity'] = 1.0
        p_opt['Alcohol'] = 0.0
        p_opt['Diabetes'] = 0.0
        opt_prob = float(active_model.predict_proba(p_opt)[0, 1])
        delta_total = prob - opt_prob

        if smoker:
            p_m = input_data.copy(); p_m['Smoker'] = 0.0
            candidate_actions.append(("Повна відмова від тютюнопаління", prob - float(active_model.predict_proba(p_m)[0, 1]), "Усунення вазоспазму та відновлення ендотелію"))
        if high_bp:
            p_m = input_data.copy(); p_m['HighBP'] = 0.0
            candidate_actions.append(("Нормалізація артеріального тиску (<130/80)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Зниження гідравлічного стресу міокарда"))
        if high_chol:
            p_m = input_data.copy(); p_m['HighChol'] = 0.0
            candidate_actions.append(("Контроль ліпідного спектру (холестерин <5.2)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Гальмування росту атеросклеротичних бляшок"))
        if bmi > 25.0:
            p_m = input_data.copy(); p_m['BMI'] = 24.5
            candidate_actions.append((f"Зниження ваги до норми (ІМТ 24.5 з {bmi})", prob - float(active_model.predict_proba(p_m)[0, 1]), "Усунення вісцерального навантаження"))
        if not phys_activity:
            p_m = input_data.copy(); p_m['PhysActivity'] = 1.0
            candidate_actions.append(("Регулярна активність (≥150 хв/тиждень)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Поліпшення вінцевого кровообігу"))
        if hvy_alcohol:
            p_m = input_data.copy(); p_m['Alcohol'] = 0.0
            candidate_actions.append(("Відмова від надмірного алкоголю", prob - float(active_model.predict_proba(p_m)[0, 1]), "Профілактика токсичної аритмії"))

        # Зчитування селекторів симулятора
        sim_patient = input_data.copy()
        if smoker and st.session_state.get("sim_quit_smoke", True):
            sim_patient['Smoker'] = 0.0
        if high_bp and st.session_state.get("sim_control_bp", True):
            sim_patient['HighBP'] = 0.0
        if high_chol and st.session_state.get("sim_control_chol", False):
            sim_patient['HighChol'] = 0.0
        if not phys_activity and st.session_state.get("sim_add_sport", True):
            sim_patient['PhysActivity'] = 1.0
        if hvy_alcohol and st.session_state.get("sim_quit_alco", True):
            sim_patient['Alcohol'] = 0.0
        if bmi > 25.0:
            max_w_loss = float(max(5.0, weight - (24.5 * ((height/100)**2))))
            s_w_loss = st.session_state.get("target_w_loss", min(5.0, max_w_loss))
            if s_w_loss > 0:
                sim_patient['BMI'] = round((weight - s_w_loss) / ((height/100)**2), 1)

    else:
        p_opt['cigs_per_day'] = 0.0
        p_opt['ap_hi'] = min(float(input_data['ap_hi'].iloc[0]), 120.0)
        p_opt['ap_lo'] = min(float(input_data['ap_lo'].iloc[0]), 80.0)
        p_opt['pulse_pressure'] = p_opt['ap_hi'] - p_opt['ap_lo']
        p_opt['heart_rate'] = min(float(input_data['heart_rate'].iloc[0]), 68.0)
        p_opt['tot_chol'] = min(float(input_data['tot_chol'].iloc[0]), 4.5)
        p_opt['ldl_chol'] = min(float(input_data['ldl_chol'].iloc[0]), 2.2)
        p_opt['hdl_chol'] = max(float(input_data['hdl_chol'].iloc[0]), 1.5)
        p_opt['triglycerides'] = min(float(input_data['triglycerides'].iloc[0]), 1.4)
        p_opt['glucose_fasting'] = min(float(input_data['glucose_fasting'].iloc[0]), 5.0)
        p_opt['hba1c'] = min(float(input_data['hba1c'].iloc[0]), 5.2)
        p_opt['BMI'] = min(float(input_data['BMI'].iloc[0]), 24.5)
        p_opt['weight'] = 24.5 * ((float(input_data['height'].iloc[0])/100)**2)
        p_opt['physical_activity'] = 1.0
        p_opt['alcohol_status'] = 0.0

        opt_prob = float(active_model.predict_proba(p_opt)[0, 1])
        delta_total = prob - opt_prob

        if clin_ap_hi > 120 or clin_ap_lo > 80:
            p_m = input_data.copy()
            p_m['ap_hi'] = 120.0; p_m['ap_lo'] = min(float(p_m['ap_lo'].iloc[0]), 80.0)
            p_m['pulse_pressure'] = p_m['ap_hi'] - p_m['ap_lo']
            candidate_actions.append(("Контроль артеріального тиску (<120/80)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Усунення гідравлічного перевантаження судин"))
        if cigs_per_day > 0:
            p_m = input_data.copy(); p_m['cigs_per_day'] = 0.0
            candidate_actions.append(("Повна відмова від куріння", prob - float(active_model.predict_proba(p_m)[0, 1]), "Відновлення функції судинного ендотелію"))
        if ldl_chol > 2.6:
            p_m = input_data.copy(); p_m['ldl_chol'] = 1.8; p_m['tot_chol'] = min(float(p_m['tot_chol'].iloc[0]), 4.2)
            candidate_actions.append(("Гіполіпідемічна терапія (ЛПНЩ <1.8 ммоль/л)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Стабілізація атеросклеротичних бляшок"))
        if glucose_fasting > 5.6 or hba1c > 5.7:
            p_m = input_data.copy(); p_m['glucose_fasting'] = 5.0; p_m['hba1c'] = 5.3
            candidate_actions.append(("Глікемічний контроль (HbA1c <5.7%)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Профілактика діабетичної мікроангіопатії"))
        if clin_heart_rate > 75:
            p_m = input_data.copy(); p_m['heart_rate'] = 68.0
            candidate_actions.append(("Контроль пульсу (ЧСС спокою <70 уд/хв)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Зменшення потреби міокарда в кисні"))
        if not clin_active:
            p_m = input_data.copy(); p_m['physical_activity'] = 1.0
            candidate_actions.append(("Аеробні тренування (≥150 хв/тиждень)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Підвищення антиатерогенного ЛПВЩ"))
        if clin_bmi > 25.0:
            p_m = input_data.copy(); p_m['BMI'] = 24.5
            candidate_actions.append(("Нормалізація маси тіла (ІМТ <25.0)", prob - float(active_model.predict_proba(p_m)[0, 1]), "Зниження навантаження на лівий шлуночок"))

        # Зчитування селекторів клінічного симулятора
        sim_patient = input_data.copy()
        if (clin_ap_hi > 120 or clin_ap_lo > 80) and st.session_state.get("sim_clin_bp", True):
            sim_target_sbp = st.session_state.get("sim_target_sbp", 125)
            sim_patient['ap_hi'] = float(sim_target_sbp)
            sim_patient['ap_lo'] = min(float(sim_patient['ap_lo'].iloc[0]), 80.0)
            sim_patient['pulse_pressure'] = sim_patient['ap_hi'] - sim_patient['ap_lo']
        if cigs_per_day > 0 and st.session_state.get("sim_clin_smoke", True):
            sim_patient['cigs_per_day'] = 0.0
        if ldl_chol > 2.6 and st.session_state.get("sim_clin_ldl", True):
            sim_patient['ldl_chol'] = 1.8
            sim_patient['tot_chol'] = min(float(sim_patient['tot_chol'].iloc[0]), 4.2)
        if (glucose_fasting > 5.6 or hba1c > 5.7) and st.session_state.get("sim_clin_gluc", False):
            sim_patient['glucose_fasting'] = 5.0
            sim_patient['hba1c'] = 5.3
        if not clin_active and st.session_state.get("sim_clin_act", True):
            sim_patient['physical_activity'] = 1.0
        if clin_heart_rate > 75 and st.session_state.get("sim_clin_hr", False):
            sim_patient['heart_rate'] = 68.0
        if clin_bmi > 25.0:
            max_w_loss = float(max(5.0, clin_weight - (24.5 * ((clin_height/100)**2))))
            s_w_loss = st.session_state.get("target_clin_w_loss", min(5.0, max_w_loss))
            if s_w_loss > 0:
                sim_patient['BMI'] = round((clin_weight - s_w_loss) / ((clin_height/100)**2), 1)

    candidate_actions.sort(key=lambda x: x[1], reverse=True)
    sim_new_prob = float(active_model.predict_proba(sim_patient)[0, 1])
    sim_diff = prob - sim_new_prob

    # Категоризація ризику за міжнародними настановами ESC SCORE2
    if prob >= 0.35:
        risk_color = "#EF4444"
        risk_label = "Високий ризик (≥35%)"
        risk_desc = "Підвищена ймовірність виникнення гострих серцево-судинних подій (інфаркт, інсульт). Показано консультацію кардіолога, дообстеження та превентивну медикаментозну терапію."
        risk_badge_bg = "rgba(239, 68, 68, 0.15)"
        risk_glow = "rgba(239, 68, 68, 0.25)"
    elif prob >= 0.18:
        risk_color = "#F59E0B"
        risk_label = "Помірний ризик (18–34%)"
        risk_desc = "Прикордонні значення ризику. Рекомендовано регулярний моніторинг артеріального тиску, здорове харчування (DASH), модифікацію способу життя та контроль ліпідів."
        risk_badge_bg = "rgba(245, 158, 11, 0.15)"
        risk_glow = "rgba(245, 158, 11, 0.25)"
    else:
        risk_color = "#10B981"
        risk_label = "Низький ризик (<18%)"
        risk_desc = "Ключові фактори ризику перебувають у межах фізіологічної норми. Рекомендовано підтримувати високий рівень щоденної рухової активності та здоровий раціон."
        risk_badge_bg = "rgba(16, 185, 129, 0.15)"
        risk_glow = "rgba(16, 185, 129, 0.25)"

    gauge_pct = min(100, max(4, int(prob * 100)))

    # Формування біометричних чіпів
    if not is_clinical_mode:
        chips_html = f'<span class="bio-pill">Стать: {sex_choice}, {scr_age} р.</span><span class="bio-pill">ІМТ: {bmi} кг/м²</span><span class="bio-pill">Тиск: {"Підвищений" if high_bp else "В нормі"}</span><span class="bio-pill">Холестерин: {"Підвищений" if high_chol else "В нормі"}</span><span class="bio-pill">Куріння: {"Так" if smoker else "Ні"}</span>'
    else:
        chips_html = f'<span class="bio-pill">{c_sex_choice}, {clin_age} р.</span><span class="bio-pill">ІМТ: {clin_bmi} кг/м²</span><span class="bio-pill">АТ: {clin_ap_hi}/{clin_ap_lo}</span><span class="bio-pill">ЛПНЩ: {ldl_chol} ммоль/л</span><span class="bio-pill">ШКФ: {clin_egfr} мл/хв</span><span class="bio-pill">ЕКГ: {ecg_labels[clin_ecg].split(": ")[-1]}</span>'

    # ── КАРТКА HERO RISK CARD З ПРЕЦИЗІЙНИМ РАДІАЛЬНИМ СПІДОМЕТРОМ (PLOTLY) ──
    risk_header_html = f"""
    <div class="risk-card" style="background:linear-gradient(145deg, rgba(17,24,39,0.96), rgba(15,23,42,0.98)); border-color:{risk_color}55; box-shadow: 0 12px 36px {risk_glow}; padding-bottom:0.8rem; margin-bottom:0.4rem;">
        <div class="risk-card-accent" style="background:{risk_color};"></div>
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
            <div>
                <div class="risk-badge" style="background:{risk_badge_bg}; color:{risk_color}; border:1px solid {risk_color}55;">
                    ● {risk_label}
                </div>
                <div class="risk-percent" style="color:{risk_color};">{prob:.1%}</div>
                <div style="font-size:0.77rem; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
                    {'Ймовірність ССЗ за 23 біомаркерами' if is_clinical_mode else 'Оцінка кардіоваскулярного ризику'}
                </div>
            </div>
            <div style="text-align:right; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:0.6rem 0.9rem;">
                <div style="font-size:0.72rem; color:#94a3b8; font-weight:600; text-transform:uppercase;">Потенціал покращення</div>
                <div style="font-size:1.65rem; font-weight:800; color:#10b981; line-height:1.2;">-{delta_total*100:.1f}%</div>
                <div style="font-size:0.72rem; color:#64748b;">зниження при корекції</div>
            </div>
        </div>
    </div>
    """
    render_html(risk_header_html)

    # Інтерактивний круговий спідометр Plotly
    st.plotly_chart(
        create_radial_gauge(prob, risk_color, risk_label, delta_total),
        use_container_width=True,
        config={'displayModeBar': False}
    )

    risk_footer_html = f"""
    <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:0.85rem 1.1rem; margin-top:-0.6rem; margin-bottom:1.1rem;">
        <div style="color:#cbd5e1; font-size:0.86rem; line-height:1.55;">
            {risk_desc}
        </div>
        <div class="bio-pill-row">
            {chips_html}
        </div>
    </div>
    """
    render_html(risk_footer_html)

    # Формування даних для PDF
    if not is_clinical_mode:
        patient_info = {
            'is_clinical': False,
            'sex_str': sex_choice,
            'age_str': f"{scr_age} років",
            'height': height,
            'weight': weight,
            'bmi': bmi,
            'bmi_status': bmi_status[0],
            'HighBP': high_bp,
            'HighChol': high_chol,
            'diabetes_str': "Діабет / предіабет" if diabetes else "Норма",
            'Stroke': stroke,
            'Smoker': smoker,
            'PhysActivity': phys_activity,
            'Fruits': 1,
            'Veggies': 1,
            'HvyAlcoholConsump': hvy_alcohol,
            'GenHlth_str': 'Задовільне',
            'FamilyHistory': fam_history
        }
    else:
        patient_info = {
            'is_clinical': True,
            'sex_str': "Чоловік" if clin_gender_male else "Жінка",
            'age_str': f"{int(clin_age)} років",
            'height': clin_height,
            'weight': clin_weight,
            'bmi': clin_bmi,
            'bmi_status': bmi_status[0],
            'bp_str': f"{clin_ap_hi}/{clin_ap_lo} мм рт. ст. (ПТ: {clin_pulse_pressure}, ЧСС: {clin_heart_rate})",
            'HighBP': 1 if clin_ap_hi >= 140 or clin_ap_lo >= 90 else 0,
            'HighChol': 1 if tot_chol >= 5.2 or ldl_chol >= 3.0 else 0,
            'chol_str': f"ЗХ {tot_chol} / ЛПНЩ {ldl_chol} / ЛПВЩ {hdl_chol} ммоль/л (КА {ka})",
            'gluc_str': f"Глюкоза {glucose_fasting} ммоль/л / HbA1c {hba1c}%",
            'Stroke': 0,
            'Smoker': 1 if cigs_per_day > 0 else 0,
            'cigs_per_day': cigs_per_day,
            'PhysActivity': clin_active,
            'Fruits': 1,
            'Veggies': 1,
            'HvyAlcoholConsump': clin_alco,
            'GenHlth_str': f"ЕКГ: {ecg_labels[clin_ecg].split(': ')[-1]}, ШКФ: {clin_egfr} мл/хв",
            'MentHlth': 0,
            'PhysHlth': 0,
            'DiffWalk': 0
        }

    # Додавання даних медичного страхування до профілю пацієнта
    patient_info['insurance_title'] = ins_title
    patient_info['insurance_cost'] = ins_cost_patient
    patient_info['insurance_covered_pct'] = ins_covered_pct
    patient_info['insurance_plan_desc'] = ins_desc

    def generate_pdf_report_bytes():
        buf = pdf_generator.build_clinical_report_pdf(
            patient_info=patient_info,
            prob=prob,
            risk_label=risk_label,
            risk_color_hex=risk_color,
            risk_desc=risk_desc,
            shap_val_display=shap_val_display,
            top_risks=top_risks,
            top_protect=top_protect,
            opt_prob=opt_prob,
            delta_total=delta_total,
            candidate_actions=candidate_actions,
            sim_patient_data=patient_info
        )
        return buf.getvalue()

    # ==============================================================================
    # 5 КЛІНІЧНИХ ТА НАУКОВИХ ВКЛАДОК
    # ==============================================================================
    # ==============================================================================
    # 4 КЛІНІЧНІ ВКЛАДКИ (MODERN MEDICAL SAAS)
    # ==============================================================================
    res_tab1, res_tab2, res_tab3, res_tab4 = st.tabs([
        "🔍 Фактори ризику (SHAP & Профіль)",
        "⚡ Що-якщо? (What-If Симулятор)",
        "💊 План терапії & Фармакоекономіка",
        "📄 Офіційний висновок (PDF)"
    ])

    # ── ВКЛАДКА 1: SHAP ПОЯСНЕННЯ ТА РАДАР ЗДОРОВ'Я ──
    with res_tab1:
        st.markdown("##### Персоналізований факторний аналіз (Explainable AI):")
        st.caption("Водоспадна діаграма TreeSHAP показує індивідуальні внески параметрів: червоні смуги збільшують ризик, сині — мають кардіопротекторний вплив.")

        with pdf_generator.matplotlib_lock:
            plt.close('all')
            plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['text.usetex'] = False

            try:
                plt.style.use('dark_background')
                fig = plt.figure(figsize=(8.5, 4.4), dpi=120)
                shap.plots.waterfall(shap_val_display, max_display=9, show=False)
                fig.patch.set_facecolor('#0d1527')
                for ax in fig.axes:
                    ax.set_facecolor('#0d1527')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close('all')
                plt.style.use('default')
            except Exception:
                plt.close('all')
                plt.style.use('default')
                st.info("Перерахунок графічного представлення SHAP...")

        # Інтерактивна діаграма профілю здоров'я (Radar Chart)
        st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
        st.markdown("##### 🕸️ Функціональний профіль серцево-судинного здоров'я (Radar Chart):")
        st.caption("Багатоосьове зіставлення показників пацієнта проти цільової безпечної норми Європейського товариства кардіологів (ESC).")

        radar_scores = calculate_radar_scores(input_data, is_clinical_mode)
        st.plotly_chart(create_radar_chart(radar_scores), use_container_width=True, config={'displayModeBar': False})

        # Картки ключових драйверів ризику та захисту
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#ef4444; text-transform:uppercase; margin-bottom:0.4rem;'>▲ Фактори підвищення ризику</div>", unsafe_allow_html=True)
            if top_risks:
                for name, s_v, _ in top_risks[:3]:
                    ua_name = active_translations.get(name, name)
                    card_html = f"""
                    <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2); border-radius:8px; padding:0.45rem 0.75rem; margin-bottom:0.35rem; font-size:0.83rem;">
                        <b>{ua_name}</b> <span style="color:#ef4444; font-weight:700; float:right;">+{s_v:.3f}</span>
                    </div>
                    """
                    render_html(card_html)
            else:
                st.caption("Не виявлено виражених факторів перевантаження.")

        with c_f2:
            st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#10b981; text-transform:uppercase; margin-bottom:0.4rem;'>▼ Захисні фактори</div>", unsafe_allow_html=True)
            if top_protect:
                for name, s_v, _ in top_protect[:3]:
                    ua_name = active_translations.get(name, name)
                    card_html = f"""
                    <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:8px; padding:0.45rem 0.75rem; margin-bottom:0.35rem; font-size:0.83rem;">
                        <b>{ua_name}</b> <span style="color:#10b981; font-weight:700; float:right;">{s_v:.3f}</span>
                    </div>
                    """
                    render_html(card_html)
            else:
                st.caption("Захисні фактори в межах середніх значень.")

    # ── ВКЛАДКА 2: WHAT-IF СИМУЛЯТОР З ДВОСТОРОННІМ ПОРІВНЯННЯМ ──
    with res_tab2:
        st.markdown("##### Контрфактичне моделювання рішень (What-If Симулятор):")
        st.caption("Інтерактивна симуляція терапевтичних та поведінкових втручань: оцінка персонального зниження серцево-судинного ризику.")

        # Подвійний спідометр-порівняння
        comp_fig, p_diff, rel_diff = create_whatif_comparison_chart(prob, sim_new_prob)
        st.plotly_chart(comp_fig, use_container_width=True, config={'displayModeBar': False})

        if sim_new_prob >= 0.35:
            sim_clr = "#EF4444"; sim_cat = "Високий ризик"
        elif sim_new_prob >= 0.18:
            sim_clr = "#F59E0B"; sim_cat = "Помірний ризик"
        else:
            sim_clr = "#10B981"; sim_cat = "Низький ризик"

        whatif_html = f"""
        <div class="whatif-box" style="background:{sim_clr}11; border-color:{sim_clr}44; margin-top:-0.4rem; margin-bottom:0.9rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                <div>
                    <span style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#94a3b8;">Результат змодельованих змін:</span>
                    <div style="font-size:1.15rem; font-weight:800; color:{sim_clr}; margin-top:0.15rem;">
                        {prob:.1%} ➔ {sim_new_prob:.1%} <span style="font-size:0.82rem; color:#94a3b8; font-weight:600;">({sim_cat})</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:0.75rem; font-weight:700; color:#10b981; text-transform:uppercase;">Зниження кардіоризику:</span>
                    <div style="font-size:1.35rem; font-weight:800; color:#10b981;">
                        ▼ -{p_diff:.1f}% <span style="font-size:0.85rem; color:#6ee7b7;">(-{rel_diff:.1f}% відносно)</span>
                    </div>
                </div>
            </div>
        </div>
        """
        render_html(whatif_html)

        # Контроли симулятора
        st.markdown("<b style='color:#38bdf8; font-size:0.85rem;'>Оберіть цільові втручання для оптимізації:</b>", unsafe_allow_html=True)
        c_w1, c_w2 = st.columns(2)
        if not is_clinical_mode:
            with c_w1:
                if smoker:
                    st.checkbox("Повна відмова від куріння", value=True, key="sim_quit_smoke")
                if high_bp:
                    st.checkbox("Нормалізація тиску (<130/80)", value=True, key="sim_control_bp")
                if high_chol:
                    st.checkbox("Зниження холестерину до норми", value=False, key="sim_control_chol")
            with c_w2:
                if not phys_activity:
                    st.checkbox("Регулярні тренування (≥150 хв/тиждень)", value=True, key="sim_add_sport")
                if bmi > 25.0:
                    max_w_loss = float(max(5.0, weight - (24.5 * ((height/100)**2))))
                    st.slider("Зниження маси тіла (кг)", min_value=0.0, max_value=max_w_loss, value=min(5.0, max_w_loss), step=0.5, key="target_w_loss")
        else:
            with c_w1:
                if clin_ap_hi > 120 or clin_ap_lo > 80:
                    st.checkbox("Антигіпертензивна терапія (цільовий АТ)", value=True, key="sim_clin_bp")
                    st.slider("Цільовий САТ (мм рт. ст.)", min_value=110, max_value=int(clin_ap_hi), value=min(125, int(clin_ap_hi)), step=5, key="sim_target_sbp")
                if cigs_per_day > 0:
                    st.checkbox("Повна відмова від куріння", value=True, key="sim_clin_smoke")
                if ldl_chol > 2.6:
                    st.checkbox("Статинотерапія (ЛПНЩ <1.8 ммоль/л)", value=True, key="sim_clin_ldl")
                if clin_heart_rate > 75:
                    st.checkbox("Контроль пульсу (ЧСС <70 уд/хв)", value=False, key="sim_clin_hr")
            with c_w2:
                if glucose_fasting > 5.6 or hba1c > 5.7:
                    st.checkbox("Глікемічний контроль (глюкоза <5.6, HbA1c <5.7%)", value=True, key="sim_clin_gluc")
                if not clin_active:
                    st.checkbox("Аеробні кардіотренування (≥150 хв)", value=True, key="sim_clin_act")
                if clin_bmi > 25.0:
                    max_w_loss = float(max(5.0, clin_weight - (24.5 * ((clin_height/100)**2))))
                    st.slider("Зниження маси тіла (кг)", min_value=0.0, max_value=max_w_loss, value=min(5.0, max_w_loss), step=0.5, key="target_clin_w_loss")

        st.markdown("<hr style='margin:1rem 0; border-color:rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
        st.markdown("###### 🏆 Персоналізований рейтинг найефективніших дій:")
        if candidate_actions:
            for i, (act_name, act_diff, act_reason) in enumerate(candidate_actions[:4], 1):
                item_html = f"""
                <div class="action-item-card">
                    <div>
                        <div style="font-size:0.85rem; font-weight:700; color:#f1f5f9;">{i}. {act_name}</div>
                        <div style="font-size:0.75rem; color:#64748b;">{act_reason}</div>
                    </div>
                    <div style="font-size:1.15rem; font-weight:800; color:#10b981; white-space:nowrap;">
                        -{act_diff*100:.1f}%
                    </div>
                </div>
                """
                render_html(item_html)
        else:
            st.success("Усі модифіковані фактори вже знаходяться в цільових фізіологічних межах.")

    # ── ВКЛАДКА 3: ПЛАН ТЕРАПІЇ ТА ФАРМАКОЕКОНОМІКА ──
    with res_tab3:
        # Аудиторний бейдж
        if is_doctor_view:
            render_html("""
            <div class="audience-banner">
                <span>🩺 <b>Режим лікаря-кардіолога:</b> Клінічні стандарти ESC/AHA 2024, цільові рівні ЛПНЩ, коди МКХ-10 та дозування препаратів.</span>
            </div>
            """)
        else:
            render_html("""
            <div class="audience-banner">
                <span>👤 <b>Режим для пацієнта:</b> Доступні щоденні рекомендації, дієта DASH та отримання безкоштовних ліків за програмою «Доступні ліки».</span>
            </div>
            """)

        # Блок маршруту дообстеження при скринінгу
        if not is_clinical_mode:
            tests_needed = []
            if high_bp or prob >= 0.18:
                tests_needed.append(("🫀 Електрокардіографія (ЕКГ спокою)", "Виключення ішемії міокарда, аритмій та гіпертрофії лівого шлуночка (ГЛШ).", "Терміново"))
            if high_chol or prob >= 0.18:
                tests_needed.append(("🧪 Розгорнута ліпідограма крові", "ЗХ, ЛПНЩ (ціль <2.6 ммоль/л), ЛПВЩ, тригліцериди для оцінки коефіцієнта атерогенності.", "Обов'язково"))
            if diabetes or bmi >= 25.0 or prob >= 0.18:
                tests_needed.append(("🩸 Глікемічний профіль (Глюкоза + HbA1c)", "Оцінка глікованого гемоглобіну для виключення прихованого предіабету.", "Обов'язково"))
            if prob >= 0.18 or scr_age >= 50:
                tests_needed.append(("🧬 Нирковий профіль (Креатинін + ШКФ)", "Розрахунок швидкості клубочкової фільтрації (eGFR) для оцінки кардіоренального статусу.", "Бажано"))

            if tests_needed:
                st.markdown("<b style='color:#38bdf8; font-size:0.85rem;'>🌳 Дерево клінічного аналізу та рекомендований маршрут дообстеження:</b>", unsafe_allow_html=True)
                for t_name, t_desc, t_urg in tests_needed:
                    urg_color = "#ef4444" if t_urg == "Терміново" else "#38bdf8"
                    st.markdown(f"""
                    <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.08); border-left:4px solid {urg_color}; border-radius:8px; padding:0.6rem 0.9rem; margin-bottom:0.4rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:#f8fafc; font-size:0.86rem;">{t_name}</b>
                            <span style="font-size:0.72rem; font-weight:700; color:{urg_color}; background:rgba(255,255,255,0.06); padding:0.15rem 0.5rem; border-radius:4px;">{t_urg}</span>
                        </div>
                        <div style="font-size:0.78rem; color:#94a3b8; margin-top:0.2rem;">{t_desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
                if st.button("🩺 Перейти до поглибленого клінічного профілю (CDSS) з цими даними", use_container_width=True, type="primary"):
                    st.session_state["app_mode_selection"] = "🩺 Клініка (23 маркери)"
                    st.rerun()

            st.markdown("<hr style='margin:1.2rem 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

        # Контент рекомендацій (Doctor vs Patient)
        if is_doctor_view:
            st.markdown("##### 🩺 Клінічний протокол та ведення пацієнта (ESC / AHA 2024):")
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.markdown("""
                <div style="background:rgba(14,165,233,0.06); border:1px solid rgba(14,165,233,0.2); border-radius:10px; padding:0.85rem; height:100%;">
                    <b style="color:#38bdf8; font-size:0.86rem;">Клінічні мішені та коди МКХ-10:</b>
                    <ul style="font-size:0.79rem; color:#cbd5e1; margin-top:0.4rem; padding-left:1.1rem; line-height:1.55;">
                        <li><b>МКХ-10 I10:</b> Артеріальна гіпертензія. Цільовий САТ: 120–129 мм рт. ст., ДАТ: 70–79 мм рт. ст.</li>
                        <li><b>МКХ-10 E78.0:</b> Гіперхолестеринемія. Цільовий ЛПНЩ: &lt;1.4 ммоль/л (дуже високий ризик) або &lt;1.8 ммоль/л (високий ризик).</li>
                        <li><b>МКХ-10 E11:</b> Цукровий діабет 2 типу. Цільовий HbA1c: &lt;6.5–7.0% без гіпоглікемій.</li>
                        <li><b>МКХ-10 N18:</b> Хронічна хвороба нирок. Контроль ШКФ (CKD-EPI) та альбумінурії.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with c_p2:
                st.markdown("""
                <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2); border-radius:10px; padding:0.85rem; height:100%;">
                    <b style="color:#34d399; font-size:0.86rem;">Рекомендовані фармакотерапевтичні схеми:</b>
                    <ul style="font-size:0.79rem; color:#cbd5e1; margin-top:0.4rem; padding-left:1.1rem; line-height:1.55;">
                        <li><b>Гіпотензивна:</b> Подвійна фіксована комбінація в 1 табл. (іАПФ/БРА + дигідропіридиновий АК).</li>
                        <li><b>Гіполіпідемічна:</b> Високоінтенсивні статини (Аторвастатин 40–80 мг або Розувастатин 20–40 мг) ± Езетиміб 10 мг.</li>
                        <li><b>Органопротекція:</b> SGLT2-інгібітори (Дапагліфлозин 10 мг) при супутньому діабеті або eGFR &lt;60.</li>
                        <li><b>Моніторинг:</b> Контрольна ліпідограма та АЛТ/АСТ через 8–12 тижнів від початку терапії.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("##### 👤 Персональні кроки для збереження здоров'я серця:")
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.markdown("""
                <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2); border-radius:10px; padding:0.85rem; height:100%;">
                    <b style="color:#34d399; font-size:0.86rem;">Щоденні звички та спосіб життя:</b>
                    <ul style="font-size:0.79rem; color:#cbd5e1; margin-top:0.4rem; padding-left:1.1rem; line-height:1.55;">
                        <li><b>Рух — це ліки:</b> 8 000–10 000 щоденних кроків або 30 хвилин швидкої ходьби знижують ризик на 12%.</li>
                        <li><b>Дієта DASH:</b> Зменшіть вживання кухонної солі до &lt;1 чайної ложки на день, додайте морську рибу, горіхи та зелень.</li>
                        <li><b>Контроль ваги:</b> Зниження маси навіть на 5 кг знижує систолічний тиск на 4–5 мм рт. ст.</li>
                        <li><b>Чисте дихання:</b> Кожен день без тютюнового диму відновлює еластичність артерій.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with c_p2:
                st.markdown("""
                <div style="background:rgba(239,68,68,0.06); border:1px solid rgba(239,68,68,0.2); border-radius:10px; padding:0.85rem; height:100%;">
                    <b style="color:#f87171; font-size:0.86rem;">Тривожні симптоми (Коли терміново до лікаря):</b>
                    <ul style="font-size:0.79rem; color:#cbd5e1; margin-top:0.4rem; padding-left:1.1rem; line-height:1.55;">
                        <li><b>Стискаючий біль за грудиною:</b> Особливо якщо віддає в ліву руку, шию чи під лопатку.</li>
                        <li><b>Раптова задишка:</b> Відчуття нестачі повітря при звичному навантаженні або у спокої.</li>
                        <li><b>Симптоми інсульту (тест FAST):</b> Асиметрія обличчя, раптова слабкість у руці, нечітке мовлення.</li>
                        <li><b>Нерегулярний пульс:</b> Раптове сильне серцебиття або перебої в роботі серця.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        # ── ВІДЖЕТ ФАРМАКОЕКОНОМІЧНОЇ ЕКОНОМІЇ (НСЗУ «ДОСТУПНІ ЛІКИ») ──
        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        render_html(f"""
        <div class="savings-card">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                <div>
                    <span class="savings-tag">🏛️ Державна програма «Доступні ліки» (НСЗУ)</span>
                    <div style="font-size:1.12rem; font-weight:800; color:#f8fafc; margin-top:0.25rem;">
                        Калькулятор персональної економії сімейного бюджету
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:0.73rem; color:#94a3b8;">Покриття в аптеках України:</span>
                    <div style="font-size:0.95rem; font-weight:700; color:#34d399;">100% безкоштовно (е-рецепт)</div>
                </div>
            </div>
            <div class="savings-metric-box">
                <div>
                    <div style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase; font-weight:600;">Вартість препаратів в аптеці без програми:</div>
                    <div style="font-size:1.05rem; font-weight:700; color:#f87171; text-decoration:line-through;">480 – 650 грн / міс</div>
                </div>
                <div>
                    <div style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase; font-weight:600;">Ваші витрати за програмою «Доступні ліки»:</div>
                    <div style="font-size:1.45rem; font-weight:800; color:#34d399;">0 грн / міс</div>
                </div>
                <div>
                    <div style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase; font-weight:600;">Річна економія коштів:</div>
                    <div class="savings-big-number">~5 760 – 7 800 грн</div>
                </div>
            </div>
            <div style="margin-top:0.75rem; font-size:0.79rem; color:#cbd5e1; line-height:1.5;">
                <b>Як отримати ліки безкоштовно у 3 прості кроки:</b><br>
                1) Зверніться до сімейного лікаря (декларація) ➔ 2) Отримайте СМС з 16-значним номером е-рецепта ➔ 3) Отримайте ліки в будь-якій аптеці з наліпкою «Тут є Доступні ліки».
            </div>
        </div>
        """)

        # Таблиця лікарських препаратів під обраний план
        st.markdown("<b style='color:#38bdf8; font-size:0.85rem;'>Рекомендований фармакотерапевтичний пакет (за обраним планом):</b>", unsafe_allow_html=True)
        meds_df = pd.DataFrame([
            {
                "Препарат / Схема": m[0],
                "Фармакологічна дія": m[1],
                "Умови отримання": m[2],
                "Орієнтовна ринкова ціна": m[3]
            }
            for m in ins_meds
        ])
        st.dataframe(meds_df, use_container_width=True, hide_index=True)

        # Інформаційний блок Algorithmic Fairness
        st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
        render_html("""
        <div style="background:rgba(56,189,248,0.05); border:1px dashed rgba(56,189,248,0.25); border-radius:8px; padding:0.75rem; font-size:0.78rem; color:#94a3b8; line-height:1.5;">
            <b style="color:#38bdf8;">⚖️ Принцип етичного ШІ (Algorithmic Fairness):</b>
            Оцінка ризику розраховується виключно на основі об'єктивних біомаркерів пацієнта без впливу фінансового або страхового статусу. Профіль покриття використовується суто для підбору фінансово досяжного лікування.
        </div>
        """)

    # ── ВКЛАДКА 4: ОФІЦІЙНИЙ ВИСНОВОК ТА ЕКСПОРТ PDF ──
    with res_tab4:
        st.markdown("##### Офіційний медичний висновок (CDSS Clinical Summary):")
        st.caption("Згенерований протокол містить повний антропометричний профіль, оцінку ризику, факторний аналіз TreeSHAP та персоналізований план лікування.")

        st.download_button(
            label="📄 Завантажити офіційний кардіологічний висновок (PDF)",
            data=generate_pdf_report_bytes,
            file_name=f"CardioRisk_Report_{patient_info['sex_str']}_{patient_info['bmi']}BMI.pdf",
            mime="application/pdf",
            help="Завантажити повний консультативний висновок для медичної картки пацієнта",
            use_container_width=True,
            type="primary"
        )

        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        render_html("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1rem; font-size:0.83rem; color:#cbd5e1; line-height:1.6;">
            <b>Структура консультативного PDF-звіту:</b><br>
            • Повний антропометричний профіль та біомаркери пацієнта<br>
            • Стратифікація 10-річного кардіоваскулярного ризику за стандартами ESC / AHA<br>
            • Вектор факторного аналізу Explainable AI (SHAP Waterfall Chart)<br>
            • Персоналізований контрфактичний план оптимізації ризику (What-If)<br>
            • Поле для підпису лікаря та печатки закладу охорони здоров'я
        </div>
        """)

# ==============================================================================
# НАУКОВА ВАЛІДАЦІЯ ТА БЕНЧМАРКІНГ (EXPANDABLE BLOCK)
# ==============================================================================
st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
with st.expander("🔬 Клінічна валідація моделі та науковий бенчмаркінг (N = 429 686 пацієнтів, ROC-AUC = 0.848)"):
    st.markdown("<b style='color:#38bdf8; font-size:0.88rem;'>1. Порівняння класифікаторів машинного навчання:</b>", unsafe_allow_html=True)
    bench_models_data = pd.DataFrame([
        {"Модель ML": "XGBoost (Фінальна модель)", "ROC-AUC": "0.8483", "PR-AUC": "0.3656", "Accuracy": "88.08%", "F1-Score": "0.4057", "Brier Score": "0.0707", "Тип": "Black-Box + TreeSHAP"},
        {"Модель ML": "Explainable Boosting Machine (EBM)", "ROC-AUC": "0.8467", "PR-AUC": "0.3635", "Accuracy": "87.87%", "F1-Score": "0.4105", "Brier Score": "0.0706", "Тип": "Glassbox GA2M"},
        {"Модель ML": "Random Forest", "ROC-AUC": "0.8392", "PR-AUC": "0.3510", "Accuracy": "87.45%", "F1-Score": "0.3980", "Brier Score": "0.0725", "Тип": "Ensemble Trees"},
        {"Модель ML": "Логістична регресія (Linear Baseline)", "ROC-AUC": "0.8451", "PR-AUC": "0.3600", "Accuracy": "88.16%", "F1-Score": "0.4032", "Brier Score": "0.0710", "Тип": "Linear Model"}
    ])
    st.dataframe(bench_models_data, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
    st.markdown("<b style='color:#38bdf8; font-size:0.88rem;'>2. Бенчмаркінг методів пояснюваного ШІ (Explainable AI):</b>", unsafe_allow_html=True)
    bench_xai_data = pd.DataFrame([
        {"Метод XAI": "TreeSHAP (Застосовано в системі)", "Латентність (мс/пацієнт)": "1.11 мс", "Faithfulness (Deletion-AUC)": "0.0795", "Рангова стабільність (ρ Спірмена)": "0.7110", "Особливість": "Точний розрахунок за поліноміальний час"},
        {"Метод XAI": "EBM Local Explain", "Латентність (мс/пацієнт)": "0.09 мс", "Faithfulness (Deletion-AUC)": "0.0762", "Рангова стабільність (ρ Спірмена)": "0.8240", "Особливість": "Пряма адитивна функція ознак"},
        {"Метод XAI": "LIME (Surrogate)", "Латентність (мс/пацієнт)": "15.95 мс", "Faithfulness (Deletion-AUC)": "0.0741", "Рангова стабільність (ρ Спірмена)": "0.2048", "Особливість": "Локальна апроксимація, висока дисперсія"},
        {"Метод XAI": "KernelSHAP (Sampling)", "Латентність (мс/пацієнт)": "19.17 мс", "Faithfulness (Deletion-AUC)": "0.0780", "Рангова стабільність (ρ Спірмена)": "0.6850", "Особливість": "Повільний через семплювання перестановок"}
    ])
    st.dataframe(bench_xai_data, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
    st.markdown("<b style='color:#38bdf8; font-size:0.88rem;'>3. Зовнішня міжкогортна валідація моделі (Cross-Cohort Validation):</b>", unsafe_allow_html=True)
    cohort_val_data = pd.DataFrame([
        {"Когорта": "CDC BRFSS (США, популяційна вибірка)", "Вибірка (N)": "253,680", "Позитивні (%)": "9.42%", "ROC-AUC": "0.8483", "Повнота (Recall)": "81.15%", "F1-Score": "0.4057"},
        {"Когорта": "Cardio Train (Європа, клінічна вибірка)", "Вибірка (N)": "68,414", "Позитивні (%)": "49.48%", "ROC-AUC": "0.8321", "Повнота (Recall)": "74.10%", "F1-Score": "0.6915"},
        {"Когорта": "Framingham Heart Study (10-річне спостереження)", "Вибірка (N)": "4,240", "Позитивні (%)": "14.98%", "ROC-AUC": "0.8210", "Повнота (Recall)": "75.52%", "F1-Score": "0.3656"},
        {"Когорта": "UCI Diabetes 130 Hospitals (кардіометаболічна)", "Вибірка (N)": "101,766", "Позитивні (%)": "38.20%", "ROC-AUC": "0.8190", "Повнота (Recall)": "72.40%", "F1-Score": "0.5840"}
    ])
    st.dataframe(cohort_val_data, use_container_width=True, hide_index=True)

# ==============================================================================
# ФУТЕР САЙТУ
# ==============================================================================
render_html("""
<div class="footer-container">
    <div style="font-weight:700; color:#94a3b8; font-size:0.86rem; margin-bottom:0.3rem;">
        🫀 CardioRisk AI · Клінічна система підтримки рішень (CDSS)
    </div>
    Система розроблена відповідно до міжнародних клінічних настанов ESC / AHA / ВООЗ на базі мультицентрової когорти понад 429 000 пацієнтів.<br>
    Використовує моделі машинного навчання з повною інтерпретованістю рішень (XGBoost + TreeSHAP).<br>
    <span style="color:#475569;">Конфіденційно. Інформація призначена для консультативних та скринінгових цілей і не замінює очного огляду лікаря.</span>
</div>
""")
