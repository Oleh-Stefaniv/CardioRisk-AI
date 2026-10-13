import os, sys
sys.path.insert(0, '.')
sys.path.insert(0, '/app')
import io
import pdf_generator

mock_patient = {
    'is_clinical': False,
    'sex_str': 'Чоловік',
    'age_str': '54 років',
    'height': 175,
    'weight': 82.0,
    'bmi': 26.8,
    'bmi_status': 'Надлишкова маса',
    'HighBP': 1,
    'HighChol': 1,
    'diabetes_str': 'Норма',
    'diabetes_val': 0,
    'Stroke': 0,
    'Smoker': 1,
    'PhysActivity': 0,
    'Fruits': 1,
    'Veggies': 1,
    'HvyAlcoholConsump': 0,
    'GenHlth_str': 'Задовільне',
    'FamilyHistory': 1,
    'insurance_title': 'Державна програма «Доступні ліки» (НСЗУ)',
    'insurance_cost': '0 грн / міс',
    'insurance_covered_pct': '100% реімбурсація за е-рецептом',
    'insurance_plan_desc': 'Пацієнт повністю забезпечується життєво необхідними серцево-судинними ліками без власних фінансових витрат.'
}

class DummyShapVal:
    def __init__(self):
        self.values = [0.05, 0.04, -0.02, 0.03]
        self.base_values = 0.15
        self.data = [54, 1, 175, 82]
        self.feature_names = ['Вік', 'Стать', 'Зріст', 'Вага']

shap_dummy = DummyShapVal()

try:
    pdf_buf = pdf_generator.build_clinical_report_pdf(
        patient_info=mock_patient,
        prob=0.28,
        risk_label='Високий ризик',
        risk_color_hex='#EF4444',
        risk_desc='Висока ймовірність серцево-судинних подій',
        shap_val_display=shap_dummy,
        top_risks=[('HighBP', 0.06, 1), ('HighChol', 0.04, 1)],
        top_protect=[('PhysActivity', -0.02, 0)],
        opt_prob=0.12,
        delta_total=0.16,
        candidate_actions=[
            ('Нормалізація артеріального тиску', 0.08, 'Знижує навантаження на серце'),
            ('Зниження холестерину', 0.05, 'Запобігає бляшкам')
        ],
        sim_patient_data=mock_patient
    )
    pdf_bytes = pdf_buf.getvalue()
    print("SUCCESS: PDF generated successfully with size:", len(pdf_bytes), "bytes")
except Exception as e:
    import traceback
    print("ERROR in PDF generation:", e)
    traceback.print_exc()
