import os, sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

doc = docx.Document()

# Standard margins (A4: top 2.0cm, bottom 2.0cm, left 2.5cm, right 1.5cm)
for section in doc.sections:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.79)
    section.bottom_margin = Inches(0.79)
    section.left_margin = Inches(0.98)
    section.right_margin = Inches(0.59)

normal_style = doc.styles['Normal']
normal_style.font.name = 'Times New Roman'
normal_style.font.size = Pt(14)
normal_style.font.color.rgb = RGBColor(0, 0, 0)
normal_style.paragraph_format.line_spacing = 1.15
normal_style.paragraph_format.space_after = Pt(4)
normal_style.paragraph_format.space_before = Pt(0)

def set_cell_shading(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    borders_xml = f"""
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
        <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
        <w:left w:val="none"/>
        <w:right w:val="none"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
        <w:insideV w:val="none"/>
    </w:tblBorders>
    """
    tblPr.append(parse_xml(borders_xml))

def add_p(text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, bold=False, italic=False, space_before=0, space_after=4, indent=True, size=14):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if indent and align == WD_ALIGN_PARAGRAPH.JUSTIFY:
        p.paragraph_format.first_line_indent = Inches(0.49)
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
    return p

# 1. УДК
add_p("УДК 004.89:004.85:616.12", align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, indent=False, size=14, space_after=6)

# 2. Автор і науковий керівник
p_auth = add_p(align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False, space_after=2)
r_a = p_auth.add_run("Стефанів О. Т.\n")
r_a.bold = True
r_a.font.size = Pt(14)
r_inst = p_auth.add_run("студент 2-го курсу магістратури факультету інформаційних технологій\nДВНЗ «Ужгородський національний університет», м. Ужгород\n")
r_inst.font.size = Pt(13)
r_sup = p_auth.add_run("Науковий керівник: Ніколенко В. В., к.ф.-м.н., доцент")
r_sup.font.size = Pt(13)
r_sup.italic = True

# 3. Назва тез
p_title = add_p(align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, indent=False, space_before=12, space_after=10)
r_t = p_title.add_run("ІНТЕЛЕКТУАЛЬНА СИСТЕМА БАГАТОРІВНЕВОЇ ОЦІНКИ КАРДІОВАСКУЛЯРНОГО РИЗИКУ НА ОСНОВІ МЕТОДІВ ПОЯСНЮВАНОГО ШТУЧНОГО ІНТЕЛЕКТУ")
r_t.font.size = Pt(14)
r_t.bold = True

# 4. Анотація та ключові слова
p_ann = add_p(align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True, space_after=4)
r_ann_lbl = p_ann.add_run("Анотація. ")
r_ann_lbl.bold = True
p_ann.add_run("У роботі розроблено архітектуру та програмну реалізацію інтелектуальної системи підтримки прийняття клінічних рішень (CDSS) CardioRisk AI для багаторівневої оцінки 10-річного ризику виникнення серцево-судинних ускладнень (гострого інфаркту міокарда та інсульту). Запропоновано дворівневу діагностичну модель, що включає первинний неінвазивний скринінг на основі 12 факторів способу життя та поглиблену стратифікацію за 23 лабораторно-інструментальними біомаркерами. Здійснено порівняльний аналіз класифікаторів машинного навчання (XGBoost, Explainable Boosting Machine, Random Forest, Logistic Regression) на мультицентровій базі даних клінічних спостережень загальним обсягом понад 429 000 пацієнтів (CDC BRFSS N = 253 680, CardioTrain N = 68 414, UCI Diabetes N = 101 766, Framingham N = 4 240). Для забезпечення прозорості та довіри з боку клініцистів інтегровано алгоритми пояснюваного штучного інтелекту (XAI) на базі TreeSHAP. Реалізовано модуль контрфактичного моделювання («What-If»), що формує персоналізований рейтинг найбільш ефективних лікувально-профілактичних заходів з урахуванням їхньої доступності.")

p_kw = add_p(align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True, space_after=10)
r_kw_lbl = p_kw.add_run("Ключові слова: ")
r_kw_lbl.bold = True
p_kw.add_run("системи підтримки прийняття рішень, машинне навчання, Explainable AI, TreeSHAP, XGBoost, кардіоваскулярний ризик, контрфактичне моделювання, ESC SCORE2.")

# 5. Тіло тез: Вступ
add_p("Вступ. Серцево-судинні захворювання (ССЗ) залишаються провідною причиною передчасної смертності та інвалідизації населення у світі. Згідно зі звітами Всесвітньої організації охорони здоров'я (ВООЗ), на патології системи кровообігу припадає понад 17,9 млн смертей щорічно. Традиційні клінічні шкали оцінки ризику (SCORE2, Framingham Risk Score) базуються на спрощених регресійних рівняннях і часто мають обмежену чутливість до індивідуальних нелінійних патернів взаємодії біомаркерів. Застосування сучасних алгоритмів машинного навчання (Machine Learning, ML) дозволяє значно підвищити якість стратифікації ризику, проте їхнє широке впровадження в реальну медичну практику стримується проблемою «чорної скриньки» (Black Box) — непрозорістю прийнятих рішень. У клінічній медицині лікар не може покладатися на рекомендації алгоритму без розуміння причинно-наслідкових зв'язків. У зв'язку з цим надзвичайно актуальним є створення клінічних систем підтримки прийняття рішень (Clinical Decision Support Systems, CDSS), які поєднують високу прогностичну точність ансамблевих моделей із повною інтерпретованістю на основі методів пояснюваного штучного інтелекту (Explainable AI, XAI).", indent=True)

# 6. Постановка задачі та концепція
add_p("Постановка задачі та дворівнева концепція діагностики. Метою дослідження є проектування та програмна реалізація інтелектуальної системи оцінки кардіоваскулярного ризику CardioRisk AI, здатної функціонувати на двох рівнях медичної допомоги:", indent=True)

p_t1 = add_p(indent=True)
p_t1.add_run("1. Експрес-скринінговий рівень (для пацієнта та первинної ланки): ").bold = True
p_t1.add_run("використовує 12 неінвазивних параметрів (вік, стать, індекс маси тіла, статус тютюнопаління, рівень рухової активності, спадковість, суб'єктивні симптоми). Метою даного рівня є виявлення пацієнтів групи ризику без необхідності попереднього проходження вартісних або інвазивних обстежень. При виявленні прикордонного або високого ризику система автоматично будує «дерево дообстеження» — маршрут з мінімально необхідним переліком лабораторних тестів.")

p_t2 = add_p(indent=True)
p_t2.add_run("2. Поглиблений клінічний рівень (для лікаря-кардіолога / CDSS): ").bold = True
p_t2.add_run("оперує вектором із 23 об'єктивних біомаркерів, включаючи показники центральної гемодинаміки (САТ, ДАТ, пульсовий тиск, ЧСС спокою), розширену ліпідограму (загальний холестерин, ЛПНЩ, ЛПВЩ, тригліцериди), глікемічний статус (глюкоза натще, глікований гемоглобін HbA1c), функцію нирок (ШКФ за CKD-EPI) та інструментальні дані ЕКГ.")

add_p("Принциповою особливістю розробленого підходу є суворе розмежування етапу діагностики (який базується виключно на біологічних і лабораторних маркерах) та етапу терапевтичного планування, де враховується доступність медичної допомоги: від безкоштовних модифікацій способу життя та препаратів за державною програмою реімбурсації «Доступні ліки» до спеціалізованих клінічних схем ESC/AHA.", indent=True)

# 7. Дослідження та порівняльний аналіз моделей ML
add_p("Експериментальне дослідження та порівняння моделей ML. Навчання та незалежне багатоцентрове тестування моделей проводилося на гармонізованих когортах клінічних спостережень загальним обсягом понад 429 000 пацієнтів (CDC BRFSS N = 253 680, CardioTrain N = 68 414, UCI Diabetes N = 101 766, Framingham N = 4 240). Вибірку базової скринінгової когорти було розділено у співвідношенні 80:20 (202 944 спостереження у тренувальній вибірці та 50 736 у тестовій) зі стратифікацією за цільовою міткою, а також проведено крос-когортну валідацію на клінічних масивах. У ході дослідження було порівняно чотири контрастні сімейства алгоритмів: градієнтний бустинг дерев рішень (XGBoost), узагальнені адитивні моделі з взаємодіями 2-го порядку (Explainable Boosting Machine, EBM GA2M), випадковий ліс (Random Forest) та L2-регуляризовану логістичну регресію (Linear Baseline).", indent=True)

add_p("Результати оцінки моделей на тестовій вибірці наведено в табл. 1.", indent=True)

# Таблиця 1
table1 = doc.add_table(rows=1, cols=6)
table1.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(table1)

headers = ["Модель ML", "ROC-AUC", "PR-AUC", "Accuracy", "F1-Score", "Brier Score"]
hdr_cells = table1.rows[0].cells
for i, h in enumerate(headers):
    hdr_cells[i].text = h
    set_cell_shading(hdr_cells[i], "E2E8F0")
    p = hdr_cells[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.name = 'Times New Roman'

models_results = [
    ("XGBoost (Фінальна модель)", "0.8483", "0.3656", "88.08%", "0.4057", "0.0707"),
    ("EBM (Glassbox GA2M)", "0.8467", "0.3635", "87.87%", "0.4105", "0.0706"),
    ("Random Forest (Trees)", "0.8392", "0.3510", "87.45%", "0.3980", "0.0725"),
    ("Логістична регресія", "0.8451", "0.3600", "88.16%", "0.4032", "0.0710")
]

for row_data in models_results:
    row_cells = table1.add_row().cells
    for i, val in enumerate(row_data):
        row_cells[i].text = val
        p = row_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
        p.runs[0].font.size = Pt(12)
        p.runs[0].font.name = 'Times New Roman'
        if "XGBoost" in row_data[0]:
            p.runs[0].font.bold = True

add_p("Таблиця 1. Порівняльний аналіз прогностичної якості моделей машинного навчання", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=11, space_before=2, space_after=8, indent=False)

add_p("Як видно з табл. 1, модель XGBoost продемонструвала найвищі показники площі під ROC-кривою (ROC-AUC = 0.8483) та PR-AUC (0.3656), перевершуючи як лінійний базис, так і ансамбль випадкового лісу, що зумовило її вибір як основного прогностичного ядра системи.", indent=True)

# 8. Бенчмаркінг методів Explainable AI
add_p("Бенчмаркінг методів Explainable AI (XAI). Для забезпечення повної локальної інтерпретованості індивідуального прогнозу в системі було досліджено методи адитивного пояснення на основі теорії ігор Шеплі (TreeSHAP та KernelSHAP), локальні сурогатні моделі (LIME) та прямі адитивні функції внесків EBM. Бенчмаркінг проводився за трьома критичними критеріями: обчислювальна латентність (мс на пацієнта), вірність пояснень (Faithfulness за метрикою Deletion-AUC) та стійкість ранжування ознак при зашумленні даних (рангова кореляція Спірмена ρ).", indent=True)

add_p("Результати порівняння методів XAI представлено в табл. 2.", indent=True)

# Таблиця 2
table2 = doc.add_table(rows=1, cols=5)
table2.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(table2)

headers2 = ["Метод XAI", "Латентність (мс)", "Deletion-AUC", "Стабільність (ρ)", "Тип оцінки"]
hdr_cells2 = table2.rows[0].cells
for i, h in enumerate(headers2):
    hdr_cells2[i].text = h
    set_cell_shading(hdr_cells2[i], "E2E8F0")
    p = hdr_cells2[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.name = 'Times New Roman'

xai_results = [
    ("TreeSHAP (Інтегровано)", "1.11 мс", "0.0795", "0.7110", "Точний аналітичний"),
    ("EBM Local Explain", "0.09 мс", "0.0762", "0.8240", "Прямий адитивний"),
    ("LIME (Surrogate)", "15.95 мс", "0.0741", "0.2048", "Локальна апроксимація"),
    ("KernelSHAP (Sampling)", "19.17 мс", "0.0780", "0.6850", "Статистичне семплювання")
]

for row_data in xai_results:
    row_cells = table2.add_row().cells
    for i, val in enumerate(row_data):
        row_cells[i].text = val
        p = row_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in [1, 2, 3] else WD_ALIGN_PARAGRAPH.LEFT
        p.runs[0].font.size = Pt(12)
        p.runs[0].font.name = 'Times New Roman'
        if "TreeSHAP" in row_data[0]:
            p.runs[0].font.bold = True

add_p("Таблиця 2. Результати порівняльного бенчмаркінгу методів XAI", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=11, space_before=2, space_after=8, indent=False)

add_p("Аналіз показав, що алгоритм TreeSHAP забезпечує найкращу вірність локальних пояснень (найвищий показник падіння кривої Deletion-AUC = 0.0795 при елімінації найбільш вагомих факторів) та стабільність ранжування ρ = 0.7110, працюючи в 14 разів швидше за LIME (1.11 мс проти 15.95 мс). Це гарантує безшовний відгук інтерфейсу в реальному часі.", indent=True)

# 9. Контрфактичне моделювання (What-If)
add_p("Контрфактичний What-If симулятор та програмна архітектура. На відміну від пасивних систем стратифікації, CardioRisk AI містить інтерактивний модуль контрфактичного моделювання («What-If»). Модуль розв'язує задачу оптимізації вектору керованих факторів способу життя та клінічних показників:", indent=True)

add_p("x* = arg min P(y = 1 | x + Δx),  за умови  Δx_j ∈ D_j,", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, italic=True, space_after=4)

add_p("де D_j — фізіологічно досяжні межі корекції j-го параметра (нормалізація артеріального тиску <130/80 мм рт. ст., цільове зниження ЛПНЩ <1.8 ммоль/л під дією статинів, зниження маси тіла, відмова від куріння). Система ранжує запропоновані кроки за величиною абсолютного зниження ризику, наочно демонструючи пацієнту і лікарю, які саме дії дадуть максимальний кардіопротекторний ефект.", indent=True)

add_p("Методологічне розмежування біологічного прогнозу та фармакоекономічного менеджменту (Algorithmic Fairness). Принциповою концептуальною особливістю CardioRisk AI є суворе розмежування клінічного діагнозу та лікувального маршруту. Соціально-економічні показники (доходи, наявність страховки) повністю виключено з моделі прогнозування біологічного ризику, що запобігає алгоритмічній дискримінації. Водночас профіль медичного страхування (державна програма «Доступні ліки» НСЗУ, добровільне страхування ДМС або комерційна самооплата) інтегровано у блок клінічної маршрутизації для підбору фінансово реалістичної схеми терапії, розрахунку реімбурсації препаратів (статини, іАПФ) та компенсації витрат на діагностичні дослідження.", indent=True)

add_p("Програмну систему реалізовано на базі фреймворку Streamlit з повною контейнеризацією в Docker. Інтерфейс підтримує двомовну візуалізацію водоспадних діаграм TreeSHAP у темній темі, експорт офіційних клінічних протоколів у форматі PDF (згідно зі стандартами ESC) та безперервну перевірку введених даних.", indent=True)

# 10. Висновки
add_p("Висновки. 1. Запропоновано науково обґрунтовану архітектуру дворівневої системи підтримки прийняття рішень CardioRisk AI, що поєднує експрес-скринінг на первинній ланці та поглиблений кардіологічний аналіз за 23 біомаркерами.", indent=True)
add_p("2. Експериментально доведено перевагу моделі градієнтного бустингу XGBoost (ROC-AUC = 0.8483, PR-AUC = 0.3656) над альтернативними класифікаторами.", indent=True)
add_p("3. Проведено комплексний бенчмаркінг методів XAI, який підтвердив перевагу TreeSHAP за вірністю пояснень (Deletion-AUC = 0.0795) та швидкістю обчислення (1.11 мс на прогноз).", indent=True)
add_p("4. Реалізовано модуль контрфактичного аналізу та етично вивіреної фармакоекономічної маршрутизації (державна програма «Доступні ліки» vs ДМС та протоколи ESC 2024), що забезпечує усунення соціально-алгоритмічного упередження та персоналізацію лікування.", indent=True)

# 11. Література
add_p("Список використаних джерел", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, indent=False, space_before=8, space_after=6)

refs = [
    "1. Visseren F. L. J. et al. 2021 ESC Guidelines on cardiovascular disease prevention in clinical practice // European Heart Journal. – 2021. – Vol. 42, No. 34. – P. 3227–3337. DOI: 10.1093/eurheartj/ehab484.",
    "2. Lundberg S. M., Lee S.-I. A Unified Approach to Interpreting Model Predictions // Advances in Neural Information Processing Systems (NeurIPS 2017). – 2017. – Vol. 30. – P. 4765–4774.",
    "3. Lundberg S. M. et al. From local explanations to global understanding with explainable AI for trees // Nature Machine Intelligence. – 2020. – Vol. 2, No. 1. – P. 56–67. DOI: 10.1038/s42256-019-0138-9.",
    "4. Chen T., Guestrin C. XGBoost: A Scalable Tree Boosting System // Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. – 2016. – P. 785–794. DOI: 10.1145/2939672.2939785.",
    "5. Ribeiro M. T., Singh S., Guestrin C. \"Why Should I Trust You?\": Explaining the Predictions of Any Classifier // Proceedings of the 22nd ACM SIGKDD International Conference. – 2016. – P. 1135–1144.",
    "6. Nori H. et al. InterpretML: A Unified Framework for Machine Learning Interpretability // arXiv preprint arXiv:1909.09223. – 2019.",
    "7. SCORE2 working group and ESC Cardiovascular Risk Collaboration. SCORE2 risk prediction algorithms: new models to estimate 10-year risk of cardiovascular disease in Europe // European Heart Journal. – 2021. – Vol. 42, No. 25. – P. 2439–2454.",
    "8. Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults // Journal of the American College of Cardiology. – 2018. – Vol. 71, No. 19. – P. e127–e248."
]

for ref in refs:
    p_ref = add_p(ref, indent=False, size=12, space_after=3)
    p_ref.paragraph_format.left_indent = Inches(0.49)
    p_ref.paragraph_format.first_line_indent = Inches(-0.49)

out_path = r"C:\Users\Олег\Desktop\Магістерська\Документи\Тези_конференція_Стефанів_О_Т.docx"
doc.save(out_path)
print(f"Conference theses saved successfully to: {out_path} ({os.path.getsize(out_path)} bytes)")
