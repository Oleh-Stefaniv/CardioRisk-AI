import streamlit as st
from components.styles import render_html


def render_navbar(current_page="home"):
    """Render the global navigation header."""
    home_cls = "nav-link nav-link-active" if current_page == "home" else "nav-link"
    calc_cls = "nav-link nav-link-active" if current_page == "calculator" else "nav-link"
    results_cls = "nav-link nav-link-active" if current_page == "results" else "nav-link"

    render_html(f"""
    <div class="nav-header">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
            <div style="display:flex; align-items:center; gap:0.8rem;">
                <div style="font-size:2.2rem; line-height:1; filter: drop-shadow(0 2px 8px rgba(220,38,38,0.25));">🫀</div>
                <div>
                    <div class="nav-brand-title">CardioRisk AI <span class="pulse-badge"><span class="pulse-dot"></span> CDSS</span></div>
                    <div class="nav-brand-subtitle">Інтелектуальна система оцінки кардіоваскулярного ризику</div>
                </div>
            </div>
        </div>
    </div>
    """)


def render_footer():
    """Render the global footer."""
    render_html("""
    <div class="footer-container">
        <div style="font-weight:700; color:#64748B; font-size:0.86rem; margin-bottom:0.3rem;">
            🫀 CardioRisk AI · Клінічна система підтримки рішень (CDSS)
        </div>
        Система розроблена відповідно до міжнародних клінічних настанов ESC / AHA / ВООЗ на базі мультицентрової когорти понад 429 000 пацієнтів.<br>
        Використовує моделі машинного навчання з повною інтерпретованістю рішень (XGBoost + TreeSHAP).<br>
        <span style="color:#94A3B8;">Конфіденційно. Інформація призначена для консультативних та скринінгових цілей і не замінює очного огляду лікаря.</span>
    </div>
    """)
