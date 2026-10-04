"""
Модуль генерації офіційного клінічного PDF-звіту (Clinical Decision Support Report)
для системи CardioRisk AI.
"""

import os
import io
import datetime
import threading
import matplotlib.pyplot as plt
import shap

# Глобальний блокувальник для запобігання гонкам (race conditions) у matplotlib при швидкому кліканні
matplotlib_lock = threading.RLock()

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.font_manager as fm

# Реєстрація українських шрифтів DejaVu Sans
def _init_fonts():
    try:
        regular_path = fm.findfont('DejaVu Sans')
        bold_path = fm.findfont('DejaVu Sans:weight=bold')
        italic_path = fm.findfont('DejaVu Sans:style=italic')
        
        pdfmetrics.registerFont(TTFont('DejaVuSans', regular_path))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_path))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', italic_path))
        return True
    except Exception as e:
        print(f"Помилка реєстрації шрифтів: {e}")
        return False

_FONTS_INITIALIZED = _init_fonts()


class NumberedCanvas:
    """Канва для нумерації сторінок 'Сторінка X з Y' та нижнього колонтитула."""
    def __init__(self, *args, **kwargs):
        self.canvas_maker = None

    @staticmethod
    def create_canvas_class():
        from reportlab.pdfgen import canvas
        class CustomCanvas(canvas.Canvas):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._saved_page_states = []

            def showPage(self):
                self._saved_page_states.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                num_pages = len(self._saved_page_states)
                for state in self._saved_page_states:
                    self.__dict__.update(state)
                    self.draw_page_decorations(num_pages)
                    super().showPage()
                super().save()

            def draw_page_decorations(self, page_count):
                self.saveState()
                self.setFont("DejaVuSans", 8)
                self.setFillColor(colors.HexColor("#64748B"))
                
                # Верхній колонтитул
                self.drawString(36, 815, "CardioRisk AI • Клінічна система підтримки прийняття рішень (CDSS)")
                self.drawRightString(559, 815, "Конфіденційно • Медичний висновок")
                self.setStrokeColor(colors.HexColor("#CBD5E1"))
                self.setLineWidth(0.6)
                self.line(36, 808, 559, 808)

                # Нижній колонтитул
                self.line(36, 42, 559, 42)
                self.drawString(36, 30, "CardioRisk Clinical Cohort (N=68,414). Метод інтерпретації: TreeSHAP. Протоколи ESC / AHA.")
                self.drawRightString(559, 30, f"Сторінка {self._pageNumber} з {page_count}")
                self.restoreState()

        return CustomCanvas


def generate_shap_chart_bytes(shap_val_display):
    """Створює графік SHAP Waterfall у пам'яті та повертає BytesIO (потокобезпечно)."""
    with matplotlib_lock:
        plt.close('all')
        plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['text.usetex'] = False
        
        for attempt in range(2):
            try:
                fig = plt.figure(figsize=(8.2, 4.4), dpi=160)
                shap.plots.waterfall(shap_val_display, max_display=9, show=False)
                plt.tight_layout()
                
                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png', dpi=160, bbox_inches='tight')
                plt.close('all')
                img_buf.seek(0)
                return img_buf
            except Exception:
                plt.close('all')
                if attempt == 1:
                    return None
        return None


def build_clinical_report_pdf(
    patient_info: dict,
    prob: float,
    risk_label: str,
    risk_color_hex: str,
    risk_desc: str,
    shap_val_display,
    top_risks: list,
    top_protect: list,
    opt_prob: float,
    delta_total: float,
    candidate_actions: list,
    sim_patient_data: dict = None
) -> io.BytesIO:
    """
    Генерує повний медичний PDF-звіт на 2 сторінках у пам'яті.
    Повертає об'єкт io.BytesIO з байтами PDF.
    """
    pdf_buffer = io.BytesIO()
    
    # 36 pt = 0.5 дюйма поля
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    # Користувацькі типографічні стилі з підтримкою кирилиці
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='DejaVuSans-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=0,
        spaceAfter=3
    )

    sub_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='DejaVuSans-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1E293B')
    )

    body_bold = ParagraphStyle(
        'CustomBodyBold',
        parent=styles['Normal'],
        fontName='DejaVuSans-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1E293B')
    )

    caption_style = ParagraphStyle(
        'CustomCaption',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#64748B')
    )

    elements = []

    # 1. Заголовний блок
    now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    report_id = f"CR-{datetime.datetime.now().strftime('%Y%m%d')}-{abs(hash(str(patient_info))) % 10000:04d}"

    header_table_data = [
        [
            Paragraph("<b>КЛІНІЧНИЙ КОНСУЛЬТАТИВНИЙ ЗВІТ</b><br/><font size='8' color='#475569'>Оцінка серцево-судинних ризиків та факторний аналіз (XAI)</font>", title_style),
            Paragraph(f"<b>Протокол:</b> {report_id}<br/><b>Дата створення:</b> {now_str}", ParagraphStyle('HeadMeta', parent=body_style, alignment=2))
        ]
    ]
    t_head = Table(header_table_data, colWidths=[340, 183])
    t_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(t_head)
    elements.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#1E3A8A"), spaceBefore=4, spaceAfter=8))

    # 2. Секція 1: Паспортні та клініко-анамнестичні параметри
    elements.append(Paragraph("1. КЛІНІКО-АНАМНЕСТИЧНІ ДАНІ ПАЦІЄНТА", h2_style))

    p_data = [
        [
            Paragraph("<b>Параметр</b>", body_bold),
            Paragraph("<b>Значення</b>", body_bold),
            Paragraph("<b>Параметр</b>", body_bold),
            Paragraph("<b>Значення</b>", body_bold)
        ],
        [
            Paragraph("Біологічна стать", body_style),
            Paragraph(f"{patient_info.get('sex_str', 'Не вказано')}", body_style),
            Paragraph("Артеріальний тиск", body_style),
            Paragraph(f"{patient_info.get('bp_str') if patient_info.get('is_clinical') else ('Гіпертензія (≥140/90)' if patient_info.get('HighBP') else 'Нормальний (<130/80)')}", body_style)
        ],
        [
            Paragraph("Вік пацієнта", body_style),
            Paragraph(f"{patient_info.get('age_str', 'Не вказано')}", body_style),
            Paragraph("Рівень холестерину", body_style),
            Paragraph(f"{patient_info.get('chol_str') if patient_info.get('is_clinical') else ('Гіперхолестеринемія' if patient_info.get('HighChol') else 'У межах норми')}", body_style)
        ],
        [
            Paragraph("Зріст / Маса тіла", body_style),
            Paragraph(f"{patient_info.get('height', '-')} см / {patient_info.get('weight', '-')} кг", body_style),
            Paragraph("Цукровий діабет / Глікемія", body_style),
            Paragraph(f"{patient_info.get('gluc_str') if patient_info.get('is_clinical') else patient_info.get('diabetes_str', 'Ні')}", body_style)
        ],
        [
            Paragraph("Індекс маси тіла (ІМТ)", body_style),
            Paragraph(f"<b>{patient_info.get('bmi', '-')} кг/м²</b> ({patient_info.get('bmi_status', '-')})", body_style),
            Paragraph("Перенесений інсульт", body_style),
            Paragraph(f"{'Так (в анамнезі)' if patient_info.get('Stroke') else 'Ні'}", body_style)
        ],
        [
            Paragraph("Статус куріння", body_style),
            Paragraph(f"{'Тютюнопаління регулярне' if patient_info.get('Smoker') else 'Не палить'}", body_style),
            Paragraph("Рухова активність", body_style),
            Paragraph(f"{'Регулярна (≥150 хв/тижд)' if patient_info.get('PhysActivity') else 'Гіподинамія'}", body_style)
        ],
        [
            Paragraph("Вживання фруктів / овочів", body_style),
            Paragraph(f"{'Щодня' if (patient_info.get('Fruits') and patient_info.get('Veggies')) else 'Недостатнє'}", body_style),
            Paragraph("Вживання алкоголю", body_style),
            Paragraph(f"{'Надмірне (токсичне)' if patient_info.get('HvyAlcoholConsump') else 'Помірне / не вживає'}", body_style)
        ],
        [
            Paragraph("Загальне самопочуття", body_style),
            Paragraph(f"{patient_info.get('GenHlth_str', 'Середньо')}", body_style),
            Paragraph("Психоемоційний стрес", body_style),
            Paragraph(f"{patient_info.get('MentHlth', 0)} дн./міс. стресу", body_style)
        ],
        [
            Paragraph("Фізичне нездужання", body_style),
            Paragraph(f"{patient_info.get('PhysHlth', 0)} дн./міс. болю/слабкості", body_style),
            Paragraph("Труднощі при ходьбі", body_style),
            Paragraph(f"{'Так (задишка / дискомфорт)' if patient_info.get('DiffWalk') else 'Ні (відсутні)'}", body_style)
        ]
    ]

    t_profile = Table(p_data, colWidths=[130, 131, 130, 132])
    t_profile.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_profile)

    # 3. Секція 2: Стратифікація кардіоваскулярного ризику
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("2. РЕЗУЛЬТАТИ СТРАТИФІКАЦІЇ КАРДІОВАСКУЛЯРНОГО РИЗИКУ", h2_style))

    risk_box_color = colors.HexColor(risk_color_hex)
    risk_summary_data = [
        [
            Paragraph(f"<font size='18' color='{risk_color_hex}'><b>{prob:.1%}</b></font><br/><font size='9' color='{risk_color_hex}'><b>{risk_label.upper()}</b></font>", ParagraphStyle('ScoreStyle', parent=body_style, alignment=1)),
            Paragraph(
                f"<b>Клінічна інтерпретація за протоколами ESC / AHA:</b><br/>"
                f"{risk_desc}<br/>"
                f"<font color='#64748B' size='7.5'><i>*Розрахунок базується на моделі машинного навчання XGBoost (TreeSHAP), "
                f"валідованій на клінічній когорті пацієнтів (N = 68,414).</i></font>",
                body_style
            )
        ]
    ]
    t_risk = Table(risk_summary_data, colWidths=[140, 383])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1.2, risk_box_color),
        ('LINELEFT', (0,0), (0,0), 5, risk_box_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_risk)

    # 4. Секція 3: Факторний аналіз та інтерпретованість SHAP (Explainable AI)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("3. ФАКТОРНИЙ XAI-АНАЛІЗ (SHAPLEY ADDITIVE EXPLANATIONS)", h2_style))
    elements.append(Paragraph(
        "Індивідуальний внесок кожного фактора у відхилення від базового рівня (TreeSHAP). "
        "Червоні показники збільшують ризик, сині — мають захисну (кардіопротекторну) дію:",
        caption_style
    ))
    elements.append(Spacer(1, 3))

    # Генерація та вбудовування зображення водоспаду SHAP
    shap_img_buf = generate_shap_chart_bytes(shap_val_display)
    if shap_img_buf:
        # Ширина сторінки 523 pt, пропорція графіка 8.2 x 4.4 (~490 x 225 pt)
        shap_img = Image(shap_img_buf, width=495, height=225)
        elements.append(shap_img)

    # Текстова декомпозиція факторів
    shap_desc_data = []
    col_l = []
    if top_risks:
        col_l.append("<b>Фактори, що найбільше збільшують ризик:</b>")
        for name, s_v, _ in top_risks[:3]:
            col_l.append(f"• <b>{name}</b>: внесок <font color='#DC2626'>+{s_v:.3f}</font>")
    else:
        col_l.append("<i>Виражених патологічних факторів не виявлено.</i>")

    col_r = []
    if top_protect:
        col_r.append("<b>Фактори кардіопротекторного захисту:</b>")
        for name, s_v, _ in top_protect[:3]:
            col_r.append(f"• <b>{name}</b>: внесок <font color='#2563EB'>{s_v:.3f}</font>")
    else:
        col_r.append("<i>Захисні фактори перебувають на базовому рівні.</i>")

    t_shap_desc = Table([
        [
            Paragraph("<br/>".join(col_l), body_style),
            Paragraph("<br/>".join(col_r), body_style)
        ]
    ], colWidths=[260, 263])
    t_shap_desc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_shap_desc)

    # ========================== СТОРІНКА 2 ==========================
    elements.append(PageBreak())

    # 5. Секція 4: Контрфактичне моделювання та персоналізований план
    elements.append(Paragraph("4. КОНТРФАКТИЧНИЙ АНАЛІЗ ТА ПЛАН ОПТИМІЗАЦІЇ РИЗИКУ (WHAT-IF)", h2_style))
    elements.append(Paragraph(
        "Метод контрфактичних пояснень (Counterfactual Explanations) демонструє математичний прогноз зниження ризику "
        "при усуненні керованих факторів небезпеки:",
        caption_style
    ))
    elements.append(Spacer(1, 4))

    # Метрична таблиця потенціалу
    plan_card_data = [
        [
            Paragraph(f"<b>Поточний ризик:</b><br/><font size='13' color='#DC2626'><b>{prob:.1%}</b></font>", ParagraphStyle('C1', parent=body_style, alignment=1)),
            Paragraph(f"<b>Досяжний мінімум:</b><br/><font size='13' color='#059669'><b>{opt_prob:.1%}</b></font>", ParagraphStyle('C2', parent=body_style, alignment=1)),
            Paragraph(f"<b>Сумарний потенціал:</b><br/><font size='13' color='#2563EB'><b>-{delta_total*100:.1f}%</b></font>", ParagraphStyle('C3', parent=body_style, alignment=1))
        ]
    ]
    t_plan_card = Table(plan_card_data, colWidths=[174, 174, 175])
    t_plan_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_plan_card)
    elements.append(Spacer(1, 6))

    # Рейтинг терапевтичних заходів
    elements.append(Paragraph("<b>Пріоритетний рейтинг коригувальних інтервенцій (маржинальний ефект):</b>", body_bold))
    elements.append(Spacer(1, 2))

    action_table_rows = [
        [
            Paragraph("<b>№</b>", body_bold),
            Paragraph("<b>Клінічний захід / Модифікація способу життя</b>", body_bold),
            Paragraph("<b>Очікуваний патофізіологічний ефект</b>", body_bold),
            Paragraph("<b>Зниження</b>", body_bold)
        ]
    ]

    if candidate_actions:
        for idx, (act_name, act_diff, act_reason) in enumerate(candidate_actions, 1):
            action_table_rows.append([
                Paragraph(str(idx), body_style),
                Paragraph(f"<b>{act_name}</b>", body_style),
                Paragraph(act_reason, body_style),
                Paragraph(f"<font color='#059669'><b>-{act_diff*100:.1f}%</b></font>", ParagraphStyle('DiffStyle', parent=body_style, alignment=1))
            ])
    else:
        action_table_rows.append([
            Paragraph("—", body_style),
            Paragraph("Усі модифіковані фактори пацієнта перебувають у цільовому фізіологічному діапазоні.", body_style),
            Paragraph("Підтримання поточного терапевтичного балансу.", body_style),
            Paragraph("0.0%", body_style)
        ])

    t_actions = Table(action_table_rows, colWidths=[24, 219, 210, 70])
    t_actions.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_actions)

    # Змодельований сценарій (якщо пацієнт обрав індивідуальні галочки)
    if sim_patient_data:
        elements.append(Spacer(1, 6))
        sim_col_hex = sim_patient_data.get('color', '#059669')
        sim_box = [
            [
                Paragraph(
                    f"<b>Змодельований лікарем/пацієнтом сценарій змін:</b><br/>"
                    f"Обрані заходи: {sim_patient_data.get('selected_steps', 'Комплекс заходів')}. "
                    f"Прогнозований оновлений ризик: <font color='{sim_col_hex}'><b>{sim_patient_data.get('new_prob', 0):.1%}</b></font> "
                    f"(чисте зниження на <b>{sim_patient_data.get('diff', 0)*100:.1f}%</b>, категорія: <b>{sim_patient_data.get('category', '')}</b>).",
                    body_style
                )
            ]
        ]
        t_sim = Table(sim_box, colWidths=[523])
        t_sim.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0FDF4')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(sim_col_hex)),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_sim)

    # 6. Секція 5: Адресні клінічні рекомендації
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("5. АДРЕСНІ КЛІНІЧНІ РЕКОМЕНДАЦІЇ ДЛЯ ЛІКАРЯ ТА ПАЦІЄНТА", h2_style))

    recs_list = []
    if patient_info.get('HighBP'):
        recs_list.append("• <b>Контроль артеріального тиску:</b> щоденний дворазовий моніторинг АТ, корекція антигіпертензивної фармакотерапії, суворе дотримання дієти DASH з обмеженням натрію хлориду до <5 г/добу.")
    if patient_info.get('HighChol'):
        recs_list.append("• <b>Ліпідний менеджмент:</b> проведення розгорнутої ліпідограми (холестерин, ЛПНЩ, ЛПВЩ, тригліцериди), оцінка необхідності призначення або титрації дози статинів/інгібіторів PCSK9.")
    if patient_info.get('bmi', 0) >= 25.0:
        recs_list.append(f"• <b>Маса тіла (ІМТ = {patient_info.get('bmi')} кг/м²):</b> цільове поступове зниження маси на 5–10% протягом 6 місяців для усунення перевантаження лівого шлуночка.")
    if patient_info.get('Smoker'):
        recs_list.append("• <b>Тютюнопаління:</b> обов'язкова категорична відмова від вживання тютюну/нікотиновмісних продуктів; за потреби — програма нікотинозамісної підтримки.")
    if patient_info.get('diabetes_val', 0) > 0:
        recs_list.append("• <b>Цукровий діабет / глікемія:</b> регулярний контроль рівня глікованого гемоглобіну (HbA1c < 7.0%), оптимізація цукрознижувальної терапії з нефро- та кардіопротекторним профілем (SGLT2i / GLP-1RA).")
    if not patient_info.get('PhysActivity'):
        recs_list.append("• <b>Фізична реабілітація:</b> поступове розширення аеробних навантажень (дозована ходьба ≥150 хв на тиждень або від 7 000 кроків щоденно).")
    
    if not recs_list:
        recs_list.append("• <b>Профілактичний режим:</b> всі досліджувані параметри перебувають у межах клінічної норми. Рекомендовано щорічний скринінговий огляд лікаря.")

    elements.append(Paragraph("<br/>".join(recs_list), ParagraphStyle('RecList', parent=body_style, leading=13)))

    # 7. Секція 6: Юридичний статус та підпис лікаря
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("6. ЮРИДИЧНИЙ СТАТУС ТА ЗАСВІДЧЕННЯ ЛІКАРЕМ", h2_style))

    disclaimer_text = (
        "<b>Застереження CDSS:</b> Даний звіт згенеровано інтелектуальною системою підтримки прийняття клінічних рішень "
        "CardioRisk AI на основі методів інтерпретованого машинного навчання. Інформація має дорадчо-консультативний характер, "
        "не є остаточним діагнозом і повинна оцінюватися сертифікованим лікарем-кардіологом у комплексі з клінічним анамнезом, "
        "лабораторними та інструментальними даними (ЕКГ, ЕхоКГ, коронарографія)."
    )
    elements.append(Paragraph(disclaimer_text, caption_style))
    elements.append(Spacer(1, 10))

    sign_data = [
        [
            Paragraph("<b>Лікар-консультант:</b><br/>________________________________________", body_style),
            Paragraph("<b>Місце для печатки:</b><br/><br/>[ М. П. ]", ParagraphStyle('Seal', parent=body_style, alignment=1)),
            Paragraph("<b>Підпис лікаря:</b><br/>_______________________<br/><b>Дата:</b> «____» ___________ 2026 р.", body_style)
        ]
    ]
    t_sign = Table(sign_data, colWidths=[200, 123, 200])
    t_sign.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t_sign)

    # Збірка документа за допомогою двопрохідної канви з нумерацією
    canvas_class = NumberedCanvas.create_canvas_class()
    doc.build(elements, canvasmaker=canvas_class)

    pdf_buffer.seek(0)
    return pdf_buffer
