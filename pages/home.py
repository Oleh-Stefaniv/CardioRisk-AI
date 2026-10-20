import streamlit as st
from components.styles import render_html


def render_home_page():
    # Hero Section
    render_html("""
    <div class="hero-section">
        <div style="display:inline-block; background:#DBEAFE; color:#1E40AF; padding:0.35rem 0.9rem; border-radius:999px; font-size:0.8rem; font-weight:700; margin-bottom:1.2rem; border:1px solid #BFDBFE;">
            🛡️ Доказова кардіологічна система підтримки клінічних рішень (CDSS)
        </div>
        <h1 class="hero-title">
            Оцініть свій кардіоваскулярний ризик<br>за 2 хвилини за допомогою ШІ
        </h1>
        <p class="hero-subtitle">
            Інтелектуальна система на базі передових моделей машинного навчання та Explainable AI (TreeSHAP), навчена на понад 429 000 пацієнтів для раннього виявлення серцево-судинних загроз.
        </p>
    </div>
    """)

    # Main CTA Button row
    col_cta1, col_cta2, col_cta3 = st.columns([1, 1.6, 1])
    with col_cta2:
        if st.button("🫀 Перейти до калькулятора ризику", type="primary", use_container_width=True):
            st.switch_page("pages/calculator.py")

    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)

    # 3 Key Feature Cards
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        render_html("""
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">Високоточний ML-прогноз</div>
            <div class="feature-desc">
                Дворівнева діагностика: експрес-скринінг (12 ознак) та поглиблена клініка (23 біомаркери) на базі каліброваного XGBoost із ROC-AUC 0.848.
            </div>
        </div>
        """)
    with c2:
        render_html("""
        <div class="feature-card">
            <span class="feature-icon">🔍</span>
            <div class="feature-title">Пояснюваний ШІ (TreeSHAP)</div>
            <div class="feature-desc">
                Жодних "чорних скриньок": система деталізує внесок кожного окремого біомаркера, тиску чи холестерину у загальний показник серцевого ризику.
            </div>
        </div>
        """)
    with c3:
        render_html("""
        <div class="feature-card">
            <span class="feature-icon">💊</span>
            <div class="feature-title">What-If Симулятор & Економіка</div>
            <div class="feature-desc">
                Моделювання ефекту зміни способу життя і медикаментів, а також розрахунок річної економії сімейного бюджету за програмою «Доступні ліки» (НСЗУ).
            </div>
        </div>
        """)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    # How it works section
    render_html("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <h2 style="font-size:1.6rem; font-weight:800; color:#1E293B; margin-bottom:0.4rem;">Як працює CardioRisk AI</h2>
        <div style="color:#64748B; font-size:0.92rem;">Три прості кроки від введення показників до персонального клінічного плану</div>
    </div>
    <div class="steps-container">
        <div class="step-item">
            <div class="step-number">1</div>
            <div>
                <div class="step-text">Введіть показники</div>
                <div style="font-size:0.75rem; color:#94A3B8;">Скринінг або аналізи крові</div>
            </div>
        </div>
        <div class="step-arrow">➔</div>
        <div class="step-item">
            <div class="step-number">2</div>
            <div>
                <div class="step-text">ШІ аналізує ризик</div>
                <div style="font-size:0.75rem; color:#94A3B8;">XGBoost + SHAP розрахунок</div>
            </div>
        </div>
        <div class="step-arrow">➔</div>
        <div class="step-item">
            <div class="step-number">3</div>
            <div>
                <div class="step-text">Отримайте протокол</div>
                <div style="font-size:0.75rem; color:#94A3B8;">План, What-If та PDF-звіт</div>
            </div>
        </div>
    </div>
    """)

    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)

    # Trust & Cohorts Section
    render_html("""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:20px; padding:2rem; text-align:center;">
        <h3 style="font-size:1.25rem; font-weight:700; color:#1E293B; margin-bottom:0.4rem;">Наукова доказовість та міжкогортна валідація</h3>
        <p style="color:#64748B; font-size:0.86rem; max-width:650px; margin:0 auto 1.5rem;">
            Алгоритми платформи пройшли валідацію на чотирьох незалежних міжнародних медичних когортах пацієнтів та відповідають настановам ESC 2024.
        </p>
        <div class="trust-grid">
            <div class="trust-stat">
                <div class="trust-number">429 686</div>
                <div class="trust-label">Пацієнтів у вибірці</div>
            </div>
            <div class="trust-stat">
                <div class="trust-number">0.848</div>
                <div class="trust-label">Точність ROC-AUC</div>
            </div>
            <div class="trust-stat">
                <div class="trust-number">&lt; 2 мс</div>
                <div class="trust-label">Швидкість SHAP аналізу</div>
            </div>
            <div class="trust-stat">
                <div class="trust-number">100%</div>
                <div class="trust-label">Реімбурсація НСЗУ</div>
            </div>
        </div>
    </div>
    """)

    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)

    # Bottom Quick Action
    b_col1, b_col2, b_col3 = st.columns([1, 1.2, 1])
    with b_col2:
        if st.button("🚀 Розпочати розрахунок ризику", type="primary", use_container_width=True):
            st.switch_page("pages/calculator.py")


render_home_page()
