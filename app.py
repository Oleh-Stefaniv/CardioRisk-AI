import streamlit as st
from components.styles import inject_styles, render_html
from components.risk_engine import init_models
from components.navbar import render_footer

# ==============================================================================
# СИСТЕМНІ НАЛАШТУВАННЯ СТОРІНКИ (WIDE MEDICAL LAYOUT)
# ==============================================================================
st.set_page_config(
    page_title="CardioRisk AI — Клінічна система оцінки кардіоваскулярного ризику",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ін'єкція дизайн-системи світлої теми
inject_styles()

# Завантаження ML моделей
if not st.session_state.get('models_loaded', False):
    init_models()

# ==============================================================================
# ГЛОБАЛЬНЕ СХОВИЩЕ СТАНУ (USER STORE) ТА СИНХРОНІЗАЦІЯ З URL
# ==============================================================================
if 'user_store' not in st.session_state:
    st.session_state['user_store'] = {
        'mode_selection': "🟢 Скринінг (12 ознак)",
        'persp_selection': "👤 Для пацієнта",
        # Скринінг
        'scr_sex': "Жінка",
        'scr_age': 54,
        'scr_h': 175,
        'scr_w': 82.0,
        'scr_hbp': "Ні",
        'scr_hchol': "Ні",
        'scr_diab': "Ні (глікемія в нормі)",
        'scr_smk': "Не палю",
        'scr_act': "Так",
        'scr_alco': "Помірно або не вживаю",
        'scr_fam': "Ні (або невідомо)",
        # Клініка
        'clin_sex': "Чоловік",
        'clin_age': 54,
        'clin_h': 175,
        'clin_w': 82.0,
        'clin_sbp': 140,
        'clin_dbp': 88,
        'clin_hr': 74,
        'clin_bp_meds': "Ні (без ліків)",
        'clin_ecg': 0,
        'clin_cp': 0,
        'clin_units_lip': "ммоль/л (Україна / ЄС)",
        'clin_tc': 5.2,
        'clin_ldl': 3.2,
        'clin_hdl': 1.25,
        'clin_tg': 1.6,
        'clin_tc_mg': 201.0,
        'clin_ldl_mg': 124.0,
        'clin_hdl_mg': 48.0,
        'clin_tg_mg': 142.0,
        'clin_glu': 5.4,
        'clin_hba': 5.6,
        'clin_egfr': 88.0,
        'clin_smk': "Не палю",
        'clin_cigs': 15,
        'clin_alco': "Помірно або не вживаю",
        'clin_act': "Так",
        'clin_fam': "Ні",
        'insurance_choice': "🏛️ Державна програма «Доступні ліки» (НСЗУ / 100% реімбурсація)"
    }

# Відновлення вибору режиму та аудиторії з URL (якщо сторінку оновлено в браузері)
if 'mode' in st.query_params:
    if st.query_params['mode'] == 'clinical':
        st.session_state['user_store']['mode_selection'] = "🩺 Клініка (23 маркери)"
    elif st.query_params['mode'] == 'screening':
        st.session_state['user_store']['mode_selection'] = "🟢 Скринінг (12 ознак)"

if 'persp' in st.query_params:
    if st.query_params['persp'] == 'doctor':
        st.session_state['user_store']['persp_selection'] = "🩺 Для лікаря"
    elif st.query_params['persp'] == 'patient':
        st.session_state['user_store']['persp_selection'] = "👤 Для пацієнта"

# ==============================================================================
# ДЕКЛАРАЦІЯ СТОРІНОК ТА МАРШРУТИЗАЦІЯ
# ==============================================================================
home_page = st.Page("pages/home.py", title="Головна", icon="🏠", default=True)
calc_page = st.Page("pages/calculator.py", title="Калькулятор", icon="🧮")
results_page = st.Page("pages/results.py", title="Результати", icon="📊")

pg = st.navigation([home_page, calc_page, results_page], position="hidden")

# Отримуємо назву поточної активної сторінки
try:
    current_title = pg.title
except Exception:
    current_title = "Головна"

# ==============================================================================
# ГЛОБАЛЬНИЙ ХЕДЕР ТА НАВІГАЦІЙНА ПАНЕЛЬ
# ==============================================================================
col_brand, col_nav = st.columns([1.5, 1.3], gap="medium")

with col_brand:
    render_html("""
    <div style="display:flex; align-items:center; gap:0.8rem; padding:0.3rem 0;">
        <div style="font-size:2.2rem; line-height:1; filter: drop-shadow(0 2px 8px rgba(220,38,38,0.25));">🫀</div>
        <div>
            <div class="nav-brand-title">CardioRisk AI <span class="pulse-badge"><span class="pulse-dot"></span> CDSS</span></div>
            <div class="nav-brand-subtitle">Інтелектуальна система оцінки кардіоваскулярного ризику</div>
        </div>
    </div>
    """)

with col_nav:
    n1, n2, n3 = st.columns(3, gap="small")
    with n1:
        is_active_home = (current_title == "Головна")
        if st.button("🏠 Головна", type="primary" if is_active_home else "secondary", use_container_width=True, key="app_nav_home"):
            st.switch_page("pages/home.py")
    with n2:
        is_active_calc = (current_title == "Калькулятор")
        if st.button("🧮 Калькулятор", type="primary" if is_active_calc else "secondary", use_container_width=True, key="app_nav_calc"):
            st.switch_page("pages/calculator.py")
    with n3:
        is_active_res = (current_title == "Результати")
        if st.button("📊 Результати", type="primary" if is_active_res else "secondary", use_container_width=True, key="app_nav_res"):
            st.switch_page("pages/results.py")

render_html("<hr style='margin:0.4rem 0 1.2rem 0; border:none; border-bottom:1px solid #E2E8F0;'>")

# ==============================================================================
# ВИКОНАННЯ АКТИВНОЇ СТОРІНКИ
# ==============================================================================
pg.run()

# ==============================================================================
# ГЛОБАЛЬНИЙ ФУТЕР
# ==============================================================================
render_footer()
