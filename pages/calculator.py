import pandas as pd
import streamlit as st
from components.styles import render_html


def render_calculator_page():
    # Breadcrumbs & Navigation
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("← Повернутися на головну", key="calc_back_home"):
            st.switch_page("pages/home.py")
    with col_nav2:
        render_html("""
        <div style="text-align:right; font-size:0.82rem; color:#64748B; font-weight:600; padding-top:0.4rem;">
            Крок 1 з 2: <span style="color:#2563EB; font-weight:700;">Введення показників</span> ➔ Крок 2: Результати
        </div>
        """)

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    # Top Configuration: Diagnostic Level & Target Audience
    conf_c1, conf_c2 = st.columns(2, gap="medium")
    with conf_c1:
        st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#64748B; margin-bottom:0.35rem;'>1. Рівень діагностики:</div>", unsafe_allow_html=True)
        mode_selection = st.radio(
            "Рівень діагностики:",
            options=["🟢 Скринінг (12 ознак)", "🩺 Клініка (23 маркери)"],
            horizontal=True,
            key="calc_mode_selection",
            label_visibility="collapsed",
            help="Скринінговий режим — 12 базових факторів для швидкої самооцінки. Клінічний режим — 23 маркери для точного CDSS-аналізу лікарем."
        )
    with conf_c2:
        st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#64748B; margin-bottom:0.35rem;'>2. Аудиторія подання висновку:</div>", unsafe_allow_html=True)
        persp_selection = st.radio(
            "Аудиторія подання:",
            options=["👤 Для пацієнта", "🩺 Для лікаря"],
            horizontal=True,
            key="calc_persp_selection",
            label_visibility="collapsed",
            help="Для пацієнта: доступна мова, практичні звички, «Доступні ліки». Для лікаря: ESC 2024, МКХ-10, цільові рівні ЛПНЩ та АТ."
        )

    is_clinical_mode = "Клініка" in mode_selection
    is_doctor_view = "Для лікаря" in persp_selection

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

    # Active Mode Informational Banner
    if is_clinical_mode:
        render_html("""
        <div class="mode-banner-clinical">
            <div>
                <b style="color:#2563EB; font-size:0.92rem;">🩺 Поглиблений клінічний режим (CDSS Expert)</b><br>
                <span style="font-size:0.8rem; color:#64748B;">
                    23 лабораторно-інструментальні біомаркери: розширена ліпідограма, глікемічний профіль, ШКФ (eGFR), тонометрія та ЕКГ.
                </span>
            </div>
            <div style="font-size:0.75rem; font-weight:700; color:#1D4ED8; background:#DBEAFE; padding:0.25rem 0.65rem; border-radius:6px;">
                ESC / AHA Protocols
            </div>
        </div>
        """)
    else:
        render_html("""
        <div class="mode-banner-screening">
            <div>
                <b style="color:#059669; font-size:0.92rem;">🟢 Експрес-скринінговий режим (Для пацієнта)</b><br>
                <span style="font-size:0.8rem; color:#64748B;">
                    12 ключових факторів: швидка самооцінка ризику інфаркту та інсульту на основі способу життя, симптомів та базових вимірювань.
                </span>
            </div>
            <div style="font-size:0.75rem; font-weight:700; color:#059669; background:#D1FAE5; padding:0.25rem 0.65rem; border-radius:6px;">
                Первинна оцінка
            </div>
        </div>
        """)



    if not is_clinical_mode:
        # ==========================================
        # РЕЖИМ 1: СКРИНІНГ (12 ФАКТОРІВ)
        # ==========================================
        st.markdown("<div class='panel-title'>📋 Параметри пацієнта (Скринінг)</div>", unsafe_allow_html=True)
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
                bmi_status = ("Дефіцит маси", "#0284C7", "#E0F2FE")
            elif bmi < 25.0:
                bmi_status = ("Норма (ВООЗ)", "#059669", "#ECFDF5")
            elif bmi < 30.0:
                bmi_status = ("Надлишкова маса", "#D97706", "#FFFBEB")
            else:
                bmi_status = ("Ожиріння", "#DC2626", "#FEF2F2")

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
                key="scr_hbp",
                help="Артеріальна гіпертензія створює хронічне перевантаження судин."
            )
            high_bp = 1 if high_bp_choice == "Так" else 0

            high_chol_choice = st.radio(
                "Чи виявлено підвищений загальний холестерин (>5.2 ммоль/л)?",
                options=["Ні", "Так"],
                key="scr_hchol",
                help="Гіперхолестеринемія є провідною причиною атеросклеротичних бляшок."
            )
            high_chol = 1 if high_chol_choice == "Так" else 0

            diabetes_choice = st.radio(
                "Чи є діагноз цукрового діабету або підвищеного цукру?",
                options=["Ні (глікемія в нормі)", "Так (діабет або предіабет)"],
                key="scr_diab",
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

        patient_summary = {
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
            'Stroke': 0,
            'Smoker': smoker,
            'PhysActivity': phys_activity,
            'Fruits': 1,
            'Veggies': 1,
            'HvyAlcoholConsump': hvy_alcohol,
            'GenHlth_str': 'Задовільне',
            'FamilyHistory': fam_history
        }

    else:
        # ==========================================
        # РЕЖИМ 2: КЛІНІЧНИЙ CDSS (23 БІОМАРКЕРИ)
        # ==========================================
        st.markdown("<div class='panel-title'>🩺 Клінічні показники та анамнез (23 маркери)</div>", unsafe_allow_html=True)
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
                bmi_status = ("Дефіцит маси", "#0284C7", "#E0F2FE")
            elif clin_bmi < 25.0:
                bmi_status = ("Норма (ВООЗ)", "#059669", "#ECFDF5")
            elif clin_bmi < 30.0:
                bmi_status = ("Надлишкова маса", "#D97706", "#FFFBEB")
            else:
                bmi_status = ("Ожиріння", "#DC2626", "#FEF2F2")

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
            <div class="status-pill-bar" style="background:#F8FAFC; border-color:#E2E8F0; color:#475569;">
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
            <div class="status-pill-bar" style="background:#F8FAFC; border-color:#E2E8F0; color:#475569;">
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

        patient_summary = {
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

    # Медичне страхування та бюджет
    st.markdown("<hr style='margin:1.1rem 0 0.8rem; border-color:#E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#2563EB; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.4rem;'>💳 Медичне страхування та бюджет (для плану лікування):</div>", unsafe_allow_html=True)

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



    # Bottom Actions: Big CTA Button
    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    btn_c1, btn_c2, btn_c3 = st.columns([1, 1.8, 1])
    with btn_c2:
        calc_button = st.button("🫀 Розрахувати кардіоваскулярний ризик", type="primary", use_container_width=True)

    if calc_button:
        # Save results in session state for results.py
        st.session_state['input_data'] = input_data
        st.session_state['is_clinical_mode'] = is_clinical_mode
        st.session_state['is_doctor_view'] = is_doctor_view
        st.session_state['insurance_choice'] = insurance_choice
        st.session_state['patient_summary'] = patient_summary
        st.session_state['calculation_done'] = True
        st.switch_page("pages/results.py")


render_calculator_page()
