import os
import json
import joblib
import shap
import streamlit as st

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
# ЗАВАНТАЖЕННЯ МОДЕЛЕЙ
# ==============================================================================
@st.cache_resource
def load_screening_model():
    """Load the screening XGBoost model, SHAP explainer, and metrics."""
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
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
    """Load the clinical XGBoost model, SHAP explainer, and metrics."""
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
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


def init_models():
    """Initialize models and store in session state. Returns True on success."""
    try:
        screening_model, screening_explainer, screening_metrics = load_screening_model()
        clinical_model, clinical_explainer, clinical_metrics = load_clinical_model()
        st.session_state['screening_model'] = screening_model
        st.session_state['screening_explainer'] = screening_explainer
        st.session_state['screening_metrics'] = screening_metrics
        st.session_state['clinical_model'] = clinical_model
        st.session_state['clinical_explainer'] = clinical_explainer
        st.session_state['clinical_metrics'] = clinical_metrics
        st.session_state['models_loaded'] = True
        return True
    except Exception as e:
        st.error(f"Помилка завантаження моделей: {e}. Переконайтеся, що моделі присутні в папці models/.")
        return False


def get_insurance_profile(insurance_choice):
    """Return insurance profile dict based on the user's selection."""
    if "Доступні ліки" in insurance_choice:
        return {
            'code': "dostupni_liky",
            'title': "Державна програма «Доступні ліки» (НСЗУ)",
            'badge_color': "#059669",
            'cost_patient': "0 грн / міс",
            'covered_pct': "100% реімбурсація за е-рецептом",
            'est_savings': "до 480 грн / міс",
            'meds': [
                ("Еналаприл 10 мг / Амлодипін 5 мг", "Антигіпертензивна базова терапія", "100% безкоштовно (е-рецепт)", "60–120 грн"),
                ("Аторвастатин 20 мг (1 табл на ніч)", "Гіполіпідемічна терапія статинами", "100% безкоштовно (е-рецепт)", "110–180 грн"),
                ("Бісопролол 5 мг (при тахікардії)", "Бета-адреноблокатор, контроль ЧСС", "100% безкоштовно (е-рецепт)", "50–85 грн"),
                ("Метформін 850–1000 мг (при глікемії)", "Цукрознижувальний бігуанід", "100% безкоштовно (е-рецепт)", "95–140 грн")
            ],
            'tests': [
                ("ЕКГ у кабінеті сімейного лікаря", "Безкоштовно за декларацією"),
                ("Загальний холестерин та глюкоза", "Безкоштовно у центрі ПМСД"),
                ("Загальний аналіз крові та сечі", "Безкоштовно за декларацією"),
                ("Розгорнута ліпідограма (ЛПНЩ/ЛПВЩ)", "За електронним направленням у комунальній лабораторії"),
                ("Консультація кардіолога вторинної ланки", "За електронним направленням (0 грн)")
            ],
            'desc': "Пацієнт повністю забезпечується життєво необхідними серцево-судинними ліками за програмою державних гарантій без власних фінансових витрат."
        }
    elif "ДМС" in insurance_choice:
        return {
            'code': "dms",
            'title': "Добровільне медичне страхування (ДМС)",
            'badge_color': "#2563EB",
            'cost_patient': "0–120 грн / міс (франшиза 0–10%)",
            'covered_pct': "Покриття 85–100% оригінальних препаратів",
            'est_savings': "до 2 200 грн / міс",
            'meds': [
                ("Трипліксам (Периндоприл+Індапамід+Амлодипін)", "Потрійна фіксована комбінація в 1 табл.", "Покрито полісом (0–40 грн)", "420–580 грн"),
                ("Розувастатин 20 мг + Езетиміб 10 мг (Зенон/Розуліп)", "Високоінтенсивний ліпідний контроль", "Покрито полісом (0–50 грн)", "650–890 грн"),
                ("Дапагліфлозин 10 мг (Форксіга)", "SGLT2-інгібітор кардіопротекції", "Покрито полісом за погодженням", "980–1250 грн")
            ],
            'tests': [
                ("ЕКГ та ЕхоКГ (УЗД серця) у приватному центрі", "100% покрито полісом ДМС"),
                ("Розгорнута ліпідограма та ApoB/Lp(a)", "100% покрито полісом ДМС"),
                ("Глікований гемоглобін (HbA1c) та eGFR", "100% покрито полісом ДМС"),
                ("Стрес-тест (тредміл) або Холтер-ЕКГ", "100% покрито за направленням"),
                ("Консультація провідного кардіолога", "100% покрито у клініках-партнерах")
            ],
            'desc': "Страховий поліс покриває інноваційні комбіновані препарати оригінальних європейських виробників та повне обстеження у приватних медичних центрах."
        }
    elif "Преміум" in insurance_choice:
        return {
            'code': "vip",
            'title': "Преміум-страхування (VIP кардіоклініка)",
            'badge_color': "#7C3AED",
            'cost_patient': "0 грн / міс",
            'covered_pct': "100% необмежене покриття інновацій та біопрепаратів",
            'est_savings': "понад 6 000 грн / міс",
            'meds': [
                ("Еволокумаб (Репата 140 мг п/ш раз на 14 днів)", "Інгібітор PCSK9 (зниження ЛПНЩ на 60–75%)", "100% покрито VIP-пакетом", "4 800–6 200 грн"),
                ("Семаглутид (Оземпік / Вегові 1 мг)", "GLP-1 RA кардіометаболічний захист", "100% покрито VIP-пакетом", "3 200–4 500 грн"),
                ("Юперіо (Сакубітрил/Валсартан)", "ARNI препарат передової кардіопротекції", "100% покрито VIP-пакетом", "1 800–2 400 грн")
            ],
            'tests': [
                ("КТ-коронарографія з Calcium Score", "100% покрито у приватному стаціонарі"),
                ("Добове холтерівське моніторування ЕКГ + АТ", "100% покрито персональним куратором"),
                ("Консиліум експертів-кардіологів", "100% необмежений супровід"),
                ("Генетичний кардіоскринінг", "100% покрито VIP-пакетом")
            ],
            'desc': "Повний доступ до світових інновацій, таргетної біологічної терапії (інгібітори PCSK9) та високотехнологічної візуалізації серця."
        }
    else:
        return {
            'code': "self_pay",
            'title': "Без страхування (Самооплата / Оптимізація витрат)",
            'badge_color': "#D97706",
            'cost_patient': "180–320 грн / міс",
            'covered_pct': "Самооплата (стратегія максимальної клінічної економії)",
            'est_savings': "заощадження до 1 200 грн на якісних генериках",
            'meds': [
                ("Аторвастатин 20 мг (якісний вітчизняний генерик)", "Базова статинотерапія", "Аптечна купівля (~90–130 грн/міс)", "110–180 грн"),
                ("Еналаприл 10 мг + Амлодипін 5 мг (окремо)", "Гіпотензивна базова схема", "Аптечна купівля (~70–110 грн/міс)", "85–140 грн"),
                ("Немедикаментозна модифікація (рух + дієта DASH)", "Знижує потребу в ліках на 35%", "Безкоштовно (0 грн)", "Безцінно")
            ],
            'tests': [
                ("ЕКГ та базові аналізи", "Обов'язково через е-направлення сімейного лікаря (безкоштовно)"),
                ("Ліпідограма", "Здати в комунальній лабораторії (0 грн замість 650 грн у приватній)"),
                ("ЕхоКГ (УЗД серця)", "Отримати чергу за електронним направленням (0 грн) або 500–800 грн приватно")
            ],
            'desc': "План оптимізовано під обмежений сімейний бюджет: фокус на безкоштовній корекції способу життя та клінічно ефективних доступних генериках."
        }
