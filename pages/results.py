import copy
import pandas as pd
import matplotlib.pyplot as plt
import shap
import streamlit as st
import streamlit.components.v1 as components
import pdf_generator
from components.styles import render_html
from components.charts import create_radial_gauge, calculate_radar_scores, create_radar_chart, create_whatif_comparison_chart
from components.risk_engine import (
    init_models,
    SCREENING_FEATURE_TRANSLATIONS,
    CLINICAL_FEATURE_TRANSLATIONS,
    get_insurance_profile
)


def render_results_page():
    # Ensure models are loaded
    if not st.session_state.get('models_loaded', False):
        init_models()

    # Синхронізація з user_store
    user_store = st.session_state.get('user_store', {})
    if 'mode_selection' in user_store:
        st.session_state['is_clinical_mode'] = ("Клініка" in user_store['mode_selection'])
    if 'persp_selection' in user_store:
        st.session_state['is_doctor_view'] = ("Для лікаря" in user_store['persp_selection'])
    if 'insurance_choice' in user_store:
        st.session_state['insurance_choice'] = user_store['insurance_choice']

    # Fallback default data if visited directly without calculator
    if not st.session_state.get('calculation_done', False):
        if st.session_state.get('is_clinical_mode', False):
            st.session_state['input_data'] = pd.DataFrame([{
                'age_years': 54.0, 'gender_male': 1.0, 'height': 175.0, 'weight': 82.0,
                'BMI': 26.8, 'ap_hi': 140.0, 'ap_lo': 88.0, 'pulse_pressure': 52.0,
                'heart_rate': 74.0, 'bp_meds': 0.0, 'tot_chol': 5.2, 'ldl_chol': 3.2,
                'hdl_chol': 1.25, 'triglycerides': 1.6, 'glucose_fasting': 5.4, 'hba1c': 5.6,
                'cigs_per_day': 0.0, 'alcohol_status': 0.0, 'physical_activity': 1.0,
                'resting_ecg': 0.0, 'chest_pain_type': 0.0, 'egfr_renal': 88.0, 'family_history': 0.0
            }])
            st.session_state['patient_summary'] = {
                'is_clinical': True, 'sex_str': "Чоловік", 'age_str': "54 років",
                'height': 175, 'weight': 82.0, 'bmi': 26.8, 'bmi_status': "Надлишкова маса",
                'bp_str': "140/88 мм рт. ст.", 'HighBP': 1, 'HighChol': 1,
                'chol_str': "ЗХ 5.2 / ЛПНЩ 3.2 / ЛПВЩ 1.25 ммоль/л",
                'gluc_str': "Глюкоза 5.4 ммоль/л / HbA1c 5.6%",
                'Stroke': 0, 'Smoker': 0, 'cigs_per_day': 0, 'PhysActivity': 1,
                'Fruits': 1, 'Veggies': 1, 'HvyAlcoholConsump': 0,
                'GenHlth_str': "ШКФ: 88 мл/хв", 'MentHlth': 0, 'PhysHlth': 0, 'DiffWalk': 0
            }
        else:
            st.session_state['input_data'] = pd.DataFrame([{
                'age_years': 54.0, 'gender_male': 0.0, 'height': 175.0, 'weight': 82.0,
                'BMI': 26.8, 'HighBP': 0.0, 'HighChol': 0.0, 'Diabetes': 0.0,
                'Smoker': 0.0, 'Alcohol': 0.0, 'PhysActivity': 1.0, 'FamilyHistory': 0.0
            }])
            st.session_state['patient_summary'] = {
                'is_clinical': False, 'sex_str': "Жінка", 'age_str': "54 років",
                'height': 175, 'weight': 82.0, 'bmi': 26.8, 'bmi_status': "Надлишкова маса",
                'HighBP': 0, 'HighChol': 0, 'diabetes_str': "Норма", 'Stroke': 0,
                'Smoker': 0, 'PhysActivity': 1, 'Fruits': 1, 'Veggies': 1,
                'HvyAlcoholConsump': 0, 'GenHlth_str': 'Задовільне', 'FamilyHistory': 0
            }
        st.session_state['calculation_done'] = True

    input_data = st.session_state['input_data']
    is_clinical_mode = st.session_state.get('is_clinical_mode', False)
    is_doctor_view = st.session_state.get('is_doctor_view', False)
    insurance_choice = st.session_state.get('insurance_choice', "🏛️ Державна програма «Доступні ліки» (НСЗУ / 100% реімбурсація)")
    patient_info = st.session_state.get('patient_summary', {})

    # Active model and explainer
    if is_clinical_mode:
        active_model = st.session_state['clinical_model']
        active_explainer = st.session_state['clinical_explainer']
        active_translations = CLINICAL_FEATURE_TRANSLATIONS
    else:
        active_model = st.session_state['screening_model']
        active_explainer = st.session_state['screening_explainer']
        active_translations = SCREENING_FEATURE_TRANSLATIONS

    # Top Action Bar
    t_c1, t_c2 = st.columns([1.2, 2.8])
    with t_c1:
        if st.button("← Змінити параметри", use_container_width=True):
            st.switch_page("pages/calculator.py")
    with t_c2:
        render_html(f"""
        <div style="display:flex; justify-content:flex-end; gap:0.5rem; align-items:center; padding-top:0.3rem;">
            <span style="font-size:0.75rem; font-weight:700; padding:0.25rem 0.65rem; border-radius:6px; background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE;">
                {'🩺 Клініка (23 маркери)' if is_clinical_mode else '🟢 Скринінг (12 ознак)'}
            </span>
            <span style="font-size:0.75rem; font-weight:700; padding:0.25rem 0.65rem; border-radius:6px; background:#F8FAFC; color:#475569; border:1px solid #CBD5E1;">
                {'🩺 Режим лікаря' if is_doctor_view else '👤 Режим пацієнта'}
            </span>
        </div>
        """)

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    # Risk Probability & TreeSHAP
    prob = float(active_model.predict_proba(input_data)[0, 1])
    shap_val = active_explainer(input_data)[0]

    shap_val_display = copy.deepcopy(shap_val)
    shap_val_display.feature_names = [active_translations.get(f, f) for f in shap_val.feature_names]

    s_vals = shap_val.values
    f_names = shap_val.feature_names
    factors = list(zip(f_names, s_vals, input_data.iloc[0]))
    top_risks = sorted([f for f in factors if f[1] > 0.015], key=lambda x: x[1], reverse=True)
    top_protect = sorted([f for f in factors if f[1] < -0.015], key=lambda x: x[1])

    # Counterfactual What-If calculation
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

        smoker = int(input_data['Smoker'].iloc[0])
        high_bp = int(input_data['HighBP'].iloc[0])
        high_chol = int(input_data['HighChol'].iloc[0])
        bmi = float(input_data['BMI'].iloc[0])
        phys_activity = int(input_data['PhysActivity'].iloc[0])
        hvy_alcohol = int(input_data['Alcohol'].iloc[0])

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

        # Simulator interactive toggles
        sim_patient = input_data.copy()
        if smoker and st.session_state.get("res_sim_quit_smoke", True):
            sim_patient['Smoker'] = 0.0
        if high_bp and st.session_state.get("res_sim_control_bp", True):
            sim_patient['HighBP'] = 0.0
        if high_chol and st.session_state.get("res_sim_control_chol", False):
            sim_patient['HighChol'] = 0.0
        if not phys_activity and st.session_state.get("res_sim_add_sport", True):
            sim_patient['PhysActivity'] = 1.0
        if hvy_alcohol and st.session_state.get("res_sim_quit_alco", True):
            sim_patient['Alcohol'] = 0.0
        if bmi > 25.0:
            w_val = float(input_data['weight'].iloc[0])
            h_val = float(input_data['height'].iloc[0])
            max_w_loss = float(max(5.0, w_val - (24.5 * ((h_val/100)**2))))
            s_w_loss = st.session_state.get("res_target_w_loss", min(5.0, max_w_loss))
            if s_w_loss > 0:
                sim_patient['BMI'] = round((w_val - s_w_loss) / ((h_val/100)**2), 1)

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

        clin_ap_hi = float(input_data['ap_hi'].iloc[0])
        clin_ap_lo = float(input_data['ap_lo'].iloc[0])
        cigs_per_day = float(input_data['cigs_per_day'].iloc[0])
        ldl_chol = float(input_data['ldl_chol'].iloc[0])
        tot_chol = float(input_data['tot_chol'].iloc[0])
        glucose_fasting = float(input_data['glucose_fasting'].iloc[0])
        hba1c = float(input_data['hba1c'].iloc[0])
        clin_heart_rate = float(input_data['heart_rate'].iloc[0])
        clin_active = int(input_data['physical_activity'].iloc[0])
        clin_bmi = float(input_data['BMI'].iloc[0])

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

        # Simulator interactive toggles
        sim_patient = input_data.copy()
        if (clin_ap_hi > 120 or clin_ap_lo > 80) and st.session_state.get("res_sim_clin_bp", True):
            sim_target_sbp = st.session_state.get("res_sim_target_sbp", 125)
            sim_patient['ap_hi'] = float(sim_target_sbp)
            sim_patient['ap_lo'] = min(float(sim_patient['ap_lo'].iloc[0]), 80.0)
            sim_patient['pulse_pressure'] = sim_patient['ap_hi'] - sim_patient['ap_lo']
        if cigs_per_day > 0 and st.session_state.get("res_sim_clin_smoke", True):
            sim_patient['cigs_per_day'] = 0.0
        if ldl_chol > 2.6 and st.session_state.get("res_sim_clin_ldl", True):
            sim_patient['ldl_chol'] = 1.8
            sim_patient['tot_chol'] = min(float(sim_patient['tot_chol'].iloc[0]), 4.2)
        if (glucose_fasting > 5.6 or hba1c > 5.7) and st.session_state.get("res_sim_clin_gluc", False):
            sim_patient['glucose_fasting'] = 5.0
            sim_patient['hba1c'] = 5.3
        if not clin_active and st.session_state.get("res_sim_clin_act", True):
            sim_patient['physical_activity'] = 1.0
        if clin_heart_rate > 75 and st.session_state.get("res_sim_clin_hr", False):
            sim_patient['heart_rate'] = 68.0
        if clin_bmi > 25.0:
            c_w = float(input_data['weight'].iloc[0])
            c_h = float(input_data['height'].iloc[0])
            max_w_loss = float(max(5.0, c_w - (24.5 * ((c_h/100)**2))))
            s_w_loss = st.session_state.get("res_target_clin_w_loss", min(5.0, max_w_loss))
            if s_w_loss > 0:
                sim_patient['BMI'] = round((c_w - s_w_loss) / ((c_h/100)**2), 1)

    candidate_actions.sort(key=lambda x: x[1], reverse=True)
    sim_new_prob = float(active_model.predict_proba(sim_patient)[0, 1])

    # Risk Stratification according to ESC SCORE2
    if prob >= 0.35:
        risk_color = "#DC2626"
        risk_label = "Високий ризик (≥35%)"
        risk_desc = "Підвищена ймовірність виникнення гострих серцево-судинних подій (інфаркт, інсульт). Показано консультацію кардіолога, дообстеження та превентивну терапію."
        risk_badge_bg = "#FEF2F2"
    elif prob >= 0.18:
        risk_color = "#D97706"
        risk_label = "Помірний ризик (18–34%)"
        risk_desc = "Прикордонні значення ризику. Рекомендовано регулярний моніторинг артеріального тиску, здорове харчування (DASH), модифікацію способу життя та контроль ліпідів."
        risk_badge_bg = "#FFFBEB"
    else:
        risk_color = "#059669"
        risk_label = "Низький ризик (<18%)"
        risk_desc = "Ключові фактори ризику перебувають у межах фізіологічної норми. Рекомендовано підтримувати високий рівень щоденної рухової активності та здоровий раціон."
        risk_badge_bg = "#ECFDF5"

    # Biometric pills
    if not is_clinical_mode:
        chips_html = f'<span class="bio-pill">Стать: {patient_info.get("sex_str","?")}, {patient_info.get("age_str","?")}</span><span class="bio-pill">ІМТ: {patient_info.get("bmi","?")} кг/м²</span><span class="bio-pill">Тиск: {"Підвищений" if input_data["HighBP"].iloc[0] else "В нормі"}</span><span class="bio-pill">Холестерин: {"Підвищений" if input_data["HighChol"].iloc[0] else "В нормі"}</span><span class="bio-pill">Куріння: {"Так" if input_data["Smoker"].iloc[0] else "Ні"}</span>'
    else:
        chips_html = f'<span class="bio-pill">{patient_info.get("sex_str","?")}, {patient_info.get("age_str","?")}</span><span class="bio-pill">ІМТ: {patient_info.get("bmi","?")} кг/м²</span><span class="bio-pill">АТ: {input_data["ap_hi"].iloc[0]:.0f}/{input_data["ap_lo"].iloc[0]:.0f}</span><span class="bio-pill">ЛПНЩ: {input_data["ldl_chol"].iloc[0]} ммоль/л</span><span class="bio-pill">ШКФ: {input_data["egfr_renal"].iloc[0]} мл/хв</span>'

    # HERO RISK CARD (Light Theme)
    render_html(f"""
    <div class="risk-card" style="background:#FFFFFF; border-color:{risk_color}44; border-left:6px solid {risk_color};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
            <div>
                <div class="risk-badge" style="background:{risk_badge_bg}; color:{risk_color}; border:1px solid {risk_color}33;">
                    ● {risk_label}
                </div>
                <div class="risk-percent" style="color:{risk_color};">{prob:.1%}</div>
                <div style="font-size:0.8rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">
                    {'Ймовірність ССЗ за 23 біомаркерами' if is_clinical_mode else 'Оцінка кардіоваскулярного ризику'}
                </div>
            </div>
            <div style="text-align:right; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.7rem 1rem;">
                <div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase;">Потенціал покращення</div>
                <div style="font-size:1.75rem; font-weight:800; color:#059669; line-height:1.2;">-{delta_total*100:.1f}%</div>
                <div style="font-size:0.72rem; color:#94A3B8;">зниження при корекції</div>
            </div>
        </div>
    </div>
    """)

    # Interactive Plotly Radial Speedometer
    st.plotly_chart(
        create_radial_gauge(prob, risk_color, risk_label, delta_total),
        use_container_width=True,
        config={'displayModeBar': False}
    )

    # Risk Explanation Card
    render_html(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.9rem 1.1rem; margin-top:-0.5rem; margin-bottom:1.2rem;">
        <div style="color:#334155; font-size:0.88rem; line-height:1.55;">
            {risk_desc}
        </div>
        <div class="bio-pill-row">
            {chips_html}
        </div>
    </div>
    """)

    # Setup insurance profile
    ins = get_insurance_profile(insurance_choice)
    patient_info['insurance_title'] = ins['title']
    patient_info['insurance_cost'] = ins['cost_patient']
    patient_info['insurance_covered_pct'] = ins['covered_pct']
    patient_info['insurance_plan_desc'] = ins['desc']

    # PDF Report generator function
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

    # 4 CLINICAL TABS
    res_tab1, res_tab2, res_tab3, res_tab4 = st.tabs([
        "🔍 Фактори ризику (SHAP & Профіль)",
        "⚡ Що-якщо? (What-If Симулятор)",
        "💊 План терапії & Фармакоекономіка",
        "📄 Офіційний висновок (PDF)"
    ])

    # ── TAB 1: SHAP & HEALTH RADAR ──
    with res_tab1:
        st.markdown("##### Персоналізований факторний аналіз (Explainable AI):")
        st.caption("Водоспадна діаграма TreeSHAP показує індивідуальні внески параметрів: червоні смуги збільшують ризик, сині — мають захисний вплив.")

        with pdf_generator.matplotlib_lock:
            plt.close('all')
            plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['text.usetex'] = False

            try:
                plt.style.use('default')
                fig = plt.figure(figsize=(8.5, 4.4), dpi=120)
                shap.plots.waterfall(shap_val_display, max_display=9, show=False)
                fig.patch.set_facecolor('#FFFFFF')
                for ax in fig.axes:
                    ax.set_facecolor('#FFFFFF')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close('all')
            except Exception:
                plt.close('all')
                st.info("Перерахунок графічного представлення SHAP...")

        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        st.markdown("##### 🕸️ Функціональний профіль серцево-судинного здоров'я (Radar Chart):")
        st.caption("Багатоосьове зіставлення показників пацієнта проти цільової норми Європейського товариства кардіологів (ESC).")

        radar_scores = calculate_radar_scores(input_data, is_clinical_mode)
        st.plotly_chart(create_radar_chart(radar_scores), use_container_width=True, config={'displayModeBar': False})

        # Key drivers cards
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#DC2626; text-transform:uppercase; margin-bottom:0.4rem;'>▲ Фактори підвищення ризику</div>", unsafe_allow_html=True)
            if top_risks:
                for name, s_v, _ in top_risks[:3]:
                    ua_name = active_translations.get(name, name)
                    render_html(f"""
                    <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:0.5rem 0.8rem; margin-bottom:0.4rem; font-size:0.83rem;">
                        <b style="color:#1E293B;">{ua_name}</b> <span style="color:#DC2626; font-weight:700; float:right;">+{s_v:.3f}</span>
                    </div>
                    """)
            else:
                st.caption("Не виявлено виражених факторів перевантаження.")

        with c_f2:
            st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#059669; text-transform:uppercase; margin-bottom:0.4rem;'>▼ Захисні фактори</div>", unsafe_allow_html=True)
            if top_protect:
                for name, s_v, _ in top_protect[:3]:
                    ua_name = active_translations.get(name, name)
                    render_html(f"""
                    <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:8px; padding:0.5rem 0.8rem; margin-bottom:0.4rem; font-size:0.83rem;">
                        <b style="color:#1E293B;">{ua_name}</b> <span style="color:#059669; font-weight:700; float:right;">{s_v:.3f}</span>
                    </div>
                    """)
            else:
                st.caption("Захисні фактори в межах середніх значень.")

    # ── TAB 2: WHAT-IF SIMULATOR ──
    with res_tab2:
        st.markdown("##### Контрфактичне моделювання рішень (What-If Симулятор):")
        st.caption("Інтерактивна симуляція втручань: оцінка персонального зниження серцево-судинного ризику.")

        comp_fig, p_diff, rel_diff = create_whatif_comparison_chart(prob, sim_new_prob)
        st.plotly_chart(comp_fig, use_container_width=True, config={'displayModeBar': False})

        sim_clr = "#059669" if sim_new_prob < 0.18 else ("#D97706" if sim_new_prob < 0.35 else "#DC2626")
        sim_cat = "Низький ризик" if sim_new_prob < 0.18 else ("Помірний ризик" if sim_new_prob < 0.35 else "Високий ризик")

        render_html(f"""
        <div class="whatif-box" style="background:#F8FAFC; border-color:#E2E8F0; margin-top:-0.4rem; margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                <div>
                    <span style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#64748B;">Результат змодельованих змін:</span>
                    <div style="font-size:1.15rem; font-weight:800; color:{sim_clr}; margin-top:0.15rem;">
                        {prob:.1%} ➔ {sim_new_prob:.1%} <span style="font-size:0.82rem; color:#64748B; font-weight:600;">({sim_cat})</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:0.75rem; font-weight:700; color:#059669; text-transform:uppercase;">Зниження кардіоризику:</span>
                    <div style="font-size:1.35rem; font-weight:800; color:#059669;">
                        ▼ -{p_diff:.1f}% <span style="font-size:0.85rem; color:#059669;">(-{rel_diff:.1f}% відносно)</span>
                    </div>
                </div>
            </div>
        </div>
        """)

        st.markdown("<b style='color:#2563EB; font-size:0.85rem;'>Оберіть цільові втручання для оптимізації:</b>", unsafe_allow_html=True)
        c_w1, c_w2 = st.columns(2)
        if not is_clinical_mode:
            with c_w1:
                if input_data['Smoker'].iloc[0]:
                    st.checkbox("Повна відмова від куріння", value=True, key="res_sim_quit_smoke")
                if input_data['HighBP'].iloc[0]:
                    st.checkbox("Нормалізація тиску (<130/80)", value=True, key="res_sim_control_bp")
                if input_data['HighChol'].iloc[0]:
                    st.checkbox("Зниження холестерину до норми", value=False, key="res_sim_control_chol")
            with c_w2:
                if not input_data['PhysActivity'].iloc[0]:
                    st.checkbox("Регулярні тренування (≥150 хв/тиждень)", value=True, key="res_sim_add_sport")
                if input_data['BMI'].iloc[0] > 25.0:
                    w_v = float(input_data['weight'].iloc[0])
                    h_v = float(input_data['height'].iloc[0])
                    max_w_loss = float(max(5.0, w_v - (24.5 * ((h_v/100)**2))))
                    st.slider("Зниження маси тіла (кг)", min_value=0.0, max_value=max_w_loss, value=min(5.0, max_w_loss), step=0.5, key="res_target_w_loss")
        else:
            with c_w1:
                if clin_ap_hi > 120 or clin_ap_lo > 80:
                    st.checkbox("Антигіпертензивна терапія (цільовий АТ)", value=True, key="res_sim_clin_bp")
                    st.slider("Цільовий САТ (мм рт. ст.)", min_value=110, max_value=int(clin_ap_hi), value=min(125, int(clin_ap_hi)), step=5, key="res_sim_target_sbp")
                if cigs_per_day > 0:
                    st.checkbox("Повна відмова від куріння", value=True, key="res_sim_clin_smoke")
                if ldl_chol > 2.6:
                    st.checkbox("Статинотерапія (ЛПНЩ <1.8 ммоль/л)", value=True, key="res_sim_clin_ldl")
                if clin_heart_rate > 75:
                    st.checkbox("Контроль пульсу (ЧСС <70 уд/хв)", value=False, key="res_sim_clin_hr")
            with c_w2:
                if glucose_fasting > 5.6 or hba1c > 5.7:
                    st.checkbox("Глікемічний контроль (глюкоза <5.6, HbA1c <5.7%)", value=True, key="res_sim_clin_gluc")
                if not clin_active:
                    st.checkbox("Аеробні кардіотренування (≥150 хв)", value=True, key="res_sim_clin_act")
                if clin_bmi > 25.0:
                    c_w = float(input_data['weight'].iloc[0])
                    c_h = float(input_data['height'].iloc[0])
                    max_w_loss = float(max(5.0, c_w - (24.5 * ((c_h/100)**2))))
                    st.slider("Зниження маси тіла (кг)", min_value=0.0, max_value=max_w_loss, value=min(5.0, max_w_loss), step=0.5, key="res_target_clin_w_loss")

        st.markdown("<hr style='margin:1rem 0; border-color:#E2E8F0;'>", unsafe_allow_html=True)
        st.markdown("###### 🏆 Персоналізований рейтинг найефективніших дій:")
        if candidate_actions:
            for i, (act_name, act_diff, act_reason) in enumerate(candidate_actions[:4], 1):
                render_html(f"""
                <div class="action-item-card">
                    <div>
                        <div style="font-size:0.86rem; font-weight:700; color:#1E293B;">{i}. {act_name}</div>
                        <div style="font-size:0.75rem; color:#64748B;">{act_reason}</div>
                    </div>
                    <div style="font-size:1.15rem; font-weight:800; color:#059669; white-space:nowrap;">
                        -{act_diff*100:.1f}%
                    </div>
                </div>
                """)
        else:
            st.success("Усі модифіковані фактори вже знаходяться в цільових фізіологічних межах.")

    # ── TAB 3: THERAPY & PHARMACOECONOMICS ──
    with res_tab3:
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

        # Screening diagnostic pathway
        if not is_clinical_mode:
            high_bp_flag = int(input_data['HighBP'].iloc[0])
            high_chol_flag = int(input_data['HighChol'].iloc[0])
            diabetes_flag = int(input_data['Diabetes'].iloc[0])
            bmi_flag = float(input_data['BMI'].iloc[0])
            age_flag = float(input_data['age_years'].iloc[0])

            tests_needed = []
            if high_bp_flag or prob >= 0.18:
                tests_needed.append(("🫀 Електрокардіографія (ЕКГ спокою)", "Виключення ішемії міокарда, аритмій та гіпертрофії лівого шлуночка (ГЛШ).", "Терміново"))
            if high_chol_flag or prob >= 0.18:
                tests_needed.append(("🧪 Розгорнута ліпідограма крові", "ЗХ, ЛПНЩ (ціль <2.6 ммоль/л), ЛПВЩ, тригліцериди для оцінки коефіцієнта атерогенності.", "Обов'язково"))
            if diabetes_flag or bmi_flag >= 25.0 or prob >= 0.18:
                tests_needed.append(("🩸 Глікемічний профіль (Глюкоза + HbA1c)", "Оцінка глікованого гемоглобіну для виключення прихованого предіабету.", "Обов'язково"))
            if prob >= 0.18 or age_flag >= 50:
                tests_needed.append(("🧬 Нирковий профіль (Креатинін + ШКФ)", "Розрахунок швидкості клубочкової фільтрації (eGFR) для оцінки кардіоренального статусу.", "Бажано"))

            if tests_needed:
                st.markdown("<b style='color:#2563EB; font-size:0.85rem;'>🌳 Дерево клінічного аналізу та рекомендований маршрут дообстеження:</b>", unsafe_allow_html=True)
                for t_name, t_desc, t_urg in tests_needed:
                    urg_color = "#DC2626" if t_urg == "Терміново" else "#2563EB"
                    render_html(f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid {urg_color}; border-radius:8px; padding:0.6rem 0.9rem; margin-bottom:0.4rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:#1E293B; font-size:0.86rem;">{t_name}</b>
                            <span style="font-size:0.72rem; font-weight:700; color:{urg_color}; background:#FFFFFF; padding:0.15rem 0.5rem; border-radius:4px; border:1px solid #E2E8F0;">{t_urg}</span>
                        </div>
                        <div style="font-size:0.78rem; color:#64748B; margin-top:0.2rem;">{t_desc}</div>
                    </div>
                    """)
                st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

            st.markdown("<hr style='margin:1.2rem 0; border-color:#E2E8F0;'>", unsafe_allow_html=True)

        # Doctor vs Patient views
        if is_doctor_view:
            st.markdown("##### 🩺 Клінічний протокол та ведення пацієнта (ESC / AHA 2024):")
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                render_html("""
                <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:12px; padding:0.95rem; height:100%;">
                    <b style="color:#1D4ED8; font-size:0.88rem;">Клінічні мішені та коди МКХ-10:</b>
                    <ul style="font-size:0.8rem; color:#334155; margin-top:0.4rem; padding-left:1.1rem; line-height:1.55;">
                        <li><b>МКХ-10 I10:</b> Артеріальна гіпертензія. Цільовий САТ: 120–129 мм рт. ст., ДАТ: 70–79 мм рт. ст.</li>
                        <li><b>МКХ-10 E78.0:</b> Гіперхолестеринемія. Цільовий ЛПНЩ: &lt;1.4 ммоль/л (дуже високий ризик) або &lt;1.8 ммоль/л (високий).</li>
                        <li><b>МКХ-10 E11:</b> Цукровий діабет 2 типу. Цільовий HbA1c: &lt;6.5–7.0% без гіпоглікемій.</li>
                        <li><b>МКХ-10 N18:</b> Хронічна хвороба нирок. Контроль ШКФ (CKD-EPI) та альбумінурії.</li>
                    </ul>
                </div>
                """)
            with c_p2:
                render_html("""
                <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:12px; padding:0.95rem; height:100%;">
                    <b style="color:#059669; font-size:0.88rem;">Рекомендовані фармакотерапевтичні схеми:</b>
                    <ul style="font-size:0.8rem; color:#334155; margin-top:0.4rem; padding-left:1.1rem; line-height:1.55;">
                        <li><b>Гіпотензивна:</b> Подвійна фіксована комбінація в 1 табл. (іАПФ/БРА + дигідропіридиновий АК).</li>
                        <li><b>Гіполіпідемічна:</b> Високоінтенсивні статини (Аторвастатин 40–80 мг або Розувастатин 20–40 мг) ± Езетиміб 10 мг.</li>
                        <li><b>Органопротекція:</b> SGLT2-інгібітори (Дапагліфлозин 10 мг) при супутньому діабеті або eGFR &lt;60.</li>
                        <li><b>Моніторинг:</b> Контрольна ліпідограма та АЛТ/АСТ через 8–12 тижнів від початку терапії.</li>
                    </ul>
                </div>
                """)
        else:
            st.markdown("##### 👤 Персональні кроки для збереження здоров'я серця:")
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                render_html("""
                <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:12px; padding:0.95rem; height:100%;">
                    <b style="color:#059669; font-size:0.88rem;">Щоденні звички та спосіб життя:</b>
                    <ul style="font-size:0.8rem; color:#334155; margin-top:0.4rem; padding-left:1.1rem; line-height:1.55;">
                        <li><b>Рух — це ліки:</b> 8 000–10 000 щоденних кроків або 30 хвилин швидкої ходьби знижують ризик на 12%.</li>
                        <li><b>Дієта DASH:</b> Зменшіть вживання кухонної солі до &lt;1 чайної ложки на день, додайте рибу, горіхи та зелень.</li>
                        <li><b>Контроль ваги:</b> Зниження маси навіть на 5 кг знижує систолічний тиск на 4–5 мм рт. ст.</li>
                        <li><b>Чисте дихання:</b> Кожен день без тютюнового диму відновлює еластичність судин.</li>
                    </ul>
                </div>
                """)
            with c_p2:
                render_html("""
                <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:12px; padding:0.95rem; height:100%;">
                    <b style="color:#DC2626; font-size:0.88rem;">Тривожні симптоми (Коли терміново до лікаря):</b>
                    <ul style="font-size:0.8rem; color:#334155; margin-top:0.4rem; padding-left:1.1rem; line-height:1.55;">
                        <li><b>Стискаючий біль за грудиною:</b> Особливо якщо віддає в ліву руку, шию чи під лопатку.</li>
                        <li><b>Раптова задишка:</b> Відчуття нестачі повітря при звичному навантаженні або у спокої.</li>
                        <li><b>Симптоми інсульту (тест FAST):</b> Асиметрія обличчя, раптова слабкість у руці, нечітке мовлення.</li>
                        <li><b>Нерегулярний пульс:</b> Раптове сильне серцебиття або перебої в роботі серця.</li>
                    </ul>
                </div>
                """)

        # REIMBURSEMENT SAVINGS WIDGET
        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        render_html(f"""
        <div class="savings-card">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                <div>
                    <span class="savings-tag">🏛️ Державна програма «Доступні ліки» (НСЗУ)</span>
                    <div style="font-size:1.12rem; font-weight:800; color:#1E293B; margin-top:0.25rem;">
                        Калькулятор персональної економії сімейного бюджету
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:0.73rem; color:#64748B;">Покриття в аптеках України:</span>
                    <div style="font-size:0.95rem; font-weight:700; color:#059669;">100% безкоштовно (е-рецепт)</div>
                </div>
            </div>
            <div class="savings-metric-box">
                <div>
                    <div style="font-size:0.72rem; color:#64748B; text-transform:uppercase; font-weight:600;">Вартість препаратів в аптеці:</div>
                    <div style="font-size:1.05rem; font-weight:700; color:#DC2626; text-decoration:line-through;">480 – 650 грн / міс</div>
                </div>
                <div>
                    <div style="font-size:0.72rem; color:#64748B; text-transform:uppercase; font-weight:600;">Витрати за програмою «Доступні ліки»:</div>
                    <div style="font-size:1.45rem; font-weight:800; color:#059669;">0 грн / міс</div>
                </div>
                <div>
                    <div style="font-size:0.72rem; color:#64748B; text-transform:uppercase; font-weight:600;">Річна економія коштів:</div>
                    <div class="savings-big-number">~5 760 – 7 800 грн</div>
                </div>
            </div>
            <div style="margin-top:0.75rem; font-size:0.8rem; color:#475569; line-height:1.5;">
                <b>Як отримати ліки безкоштовно у 3 прості кроки:</b><br>
                1) Зверніться до сімейного лікаря ➔ 2) Отримайте СМС з номером е-рецепта ➔ 3) Отримайте ліки в будь-якій аптеці з наліпкою «Тут є Доступні ліки».
            </div>
        </div>
        """)

        # Medication schedule under selected plan
        st.markdown(f"<b style='color:#2563EB; font-size:0.85rem;'>Рекомендований пакет ліків за планом «{ins['title']}»:</b>", unsafe_allow_html=True)
        meds_df = pd.DataFrame([
            {
                "Препарат / Схема": m[0],
                "Фармакологічна дія": m[1],
                "Умови отримання": m[2],
                "Орієнтовна ринкова ціна": m[3]
            }
            for m in ins['meds']
        ])
        st.dataframe(meds_df, use_container_width=True, hide_index=True)

        st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
        render_html("""
        <div style="background:#F8FAFC; border:1px dashed #CBD5E1; border-radius:8px; padding:0.75rem; font-size:0.78rem; color:#64748B; line-height:1.5;">
            <b style="color:#2563EB;">⚖️ Принцип етичного ШІ (Algorithmic Fairness):</b>
            Оцінка ризику розраховується виключно на основі об'єктивних біомаркерів пацієнта без впливу фінансового або страхового статусу. Профіль покриття використовується суто для підбору фінансово досяжного лікування.
        </div>
        """)

    # ── TAB 4: PDF REPORT ──
    with res_tab4:
        st.markdown("##### Офіційний медичний висновок (CDSS Clinical Summary):")
        st.caption("Згенерований протокол містить повний антропометричний профіль, оцінку ризику, факторний аналіз TreeSHAP та персоналізований план лікування.")

        st.download_button(
            label="📄 Завантажити офіційний кардіологічний висновок (PDF)",
            data=generate_pdf_report_bytes,
            file_name=f"CardioRisk_Report_{patient_info.get('sex_str','Patient')}_{patient_info.get('bmi',0)}BMI.pdf",
            mime="application/pdf",
            help="Завантажити повний консультативний висновок для медичної картки пацієнта",
            use_container_width=True,
            type="primary"
        )

        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        render_html("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:1.1rem; font-size:0.83rem; color:#334155; line-height:1.6;">
            <b>Структура консультативного PDF-звіту:</b><br>
            • Повний антропометричний профіль та біомаркери пацієнта<br>
            • Стратифікація 10-річного кардіоваскулярного ризику за стандартами ESC / AHA<br>
            • Вектор факторного аналізу Explainable AI (SHAP Waterfall Chart)<br>
            • Персоналізований контрфактичний план оптимізації ризику (What-If)<br>
            • Поле для підпису лікаря та печатки закладу охорони здоров'я
        </div>
        """)

    # ── BOTTOM SCIENTIFIC BENCHMARKING BLOCK (COLLAPSIBLE) ──
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("🔬 Клінічна валідація моделі та науковий бенчмаркінг (N = 429 686 пацієнтів, ROC-AUC = 0.848)"):
        st.markdown("<b style='color:#2563EB; font-size:0.88rem;'>1. Порівняння класифікаторів машинного навчання:</b>", unsafe_allow_html=True)
        bench_models_data = pd.DataFrame([
            {"Модель ML": "XGBoost (Фінальна модель)", "ROC-AUC": "0.8483", "PR-AUC": "0.3656", "Accuracy": "88.08%", "F1-Score": "0.4057", "Brier Score": "0.0707", "Тип": "Black-Box + TreeSHAP"},
            {"Модель ML": "Explainable Boosting Machine (EBM)", "ROC-AUC": "0.8467", "PR-AUC": "0.3635", "Accuracy": "87.87%", "F1-Score": "0.4105", "Brier Score": "0.0706", "Тип": "Glassbox GA2M"},
            {"Модель ML": "Random Forest", "ROC-AUC": "0.8392", "PR-AUC": "0.3510", "Accuracy": "87.45%", "F1-Score": "0.3980", "Brier Score": "0.0725", "Тип": "Ensemble Trees"},
            {"Модель ML": "Логістична регресія (Linear Baseline)", "ROC-AUC": "0.8451", "PR-AUC": "0.3600", "Accuracy": "88.16%", "F1-Score": "0.4032", "Brier Score": "0.0710", "Тип": "Linear Model"}
        ])
        st.dataframe(bench_models_data, use_container_width=True, hide_index=True)

        st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
        st.markdown("<b style='color:#2563EB; font-size:0.88rem;'>2. Бенчмаркінг методів пояснюваного ШІ (Explainable AI):</b>", unsafe_allow_html=True)
        bench_xai_data = pd.DataFrame([
            {"Метод XAI": "TreeSHAP (Застосовано в системі)", "Латентність (мс/пацієнт)": "1.11 мс", "Faithfulness (Deletion-AUC)": "0.0795", "Рангова стабільність (ρ Спірмена)": "0.7110", "Особливість": "Точний розрахунок за поліноміальний час"},
            {"Метод XAI": "EBM Local Explain", "Латентність (мс/пацієнт)": "0.09 мс", "Faithfulness (Deletion-AUC)": "0.0762", "Рангова стабільність (ρ Спірмена)": "0.8240", "Особливість": "Пряма адитивна функція ознак"},
            {"Метод XAI": "LIME (Surrogate)", "Латентність (мс/пацієнт)": "15.95 мс", "Faithfulness (Deletion-AUC)": "0.0741", "Рангова стабільність (ρ Спірмена)": "0.2048", "Особливість": "Локальна апроксимація, висока дисперсія"},
            {"Метод XAI": "KernelSHAP (Sampling)", "Латентність (мс/пацієнт)": "19.17 мс", "Faithfulness (Deletion-AUC)": "0.0780", "Рангова стабільність (ρ Спірмена)": "0.6850", "Особливість": "Повільний через семплювання перестановок"}
        ])
        st.dataframe(bench_xai_data, use_container_width=True, hide_index=True)

        st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
        st.markdown("<b style='color:#2563EB; font-size:0.88rem;'>3. Зовнішня міжкогортна валідація моделі (Cross-Cohort Validation):</b>", unsafe_allow_html=True)
        cohort_val_data = pd.DataFrame([
            {"Когорта": "CDC BRFSS (США, популяційна вибірка)", "Вибірка (N)": "253,680", "Позитивні (%)": "9.42%", "ROC-AUC": "0.8483", "Повнота (Recall)": "81.15%", "F1-Score": "0.4057"},
            {"Когорта": "Cardio Train (Європа, клінічна вибірка)", "Вибірка (N)": "68,414", "Позитивні (%)": "49.48%", "ROC-AUC": "0.8321", "Повнота (Recall)": "74.10%", "F1-Score": "0.6915"},
            {"Когорта": "Framingham Heart Study (10-річне спостереження)", "Вибірка (N)": "4,240", "Позитивні (%)": "14.98%", "ROC-AUC": "0.8210", "Повнота (Recall)": "75.52%", "F1-Score": "0.3656"},
            {"Когорта": "UCI Diabetes 130 Hospitals (кардіометаболічна)", "Вибірка (N)": "101,766", "Позитивні (%)": "38.20%", "ROC-AUC": "0.8190", "Повнота (Recall)": "72.40%", "F1-Score": "0.5840"}
        ])
        st.dataframe(cohort_val_data, use_container_width=True, hide_index=True)


render_results_page()
