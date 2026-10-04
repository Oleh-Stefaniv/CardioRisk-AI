"""
Модуль незалежної зовнішньої крос-когортної валідації (External Cross-Cohort Validation).

Методологія:
1. Основна гармонізована модель навчається ТІЛЬКИ на тренувальній вибірці CDC BRFSS.
2. Тестові когорти (Cardio Train та Framingham Heart Study) використовуються виключно для зовнішнього тестування.
3. Ніякого перенавчання (fit) на зовнішніх датасетах не проводиться (захист від Data Leakage).
4. Порівняння проводиться за 7 спільними верифікованими клінічними маркерами ризику ВООЗ.
"""

import os
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve
)

def map_age_to_brfss_cat(age_years_series):
    """Відображення віку у роках у стандартні 13 інтервалів опитування BRFSS"""
    bins = [18, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 150]
    return np.digitize(age_years_series, bins=bins, right=False)

def main():
    print("=" * 80)
    print("ЗАПУСК НЕЗАЛЕЖНОЇ ЗОВНІШНЬОЇ КРОС-КОГОРТНОЇ ВАЛІДАЦІЇ (CROSS-COHORT VALIDATION)")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "Datasets")
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. ЗАВАНТАЖЕННЯ ТА ПІДГОТОВКА ОСНОВНОГО ТРЕНУВАЛЬНОГО ДАТАСЕТУ (BRFSS)
    # -------------------------------------------------------------
    print("\n1. Завантаження базового датасету CDC BRFSS (Train/Test)...")
    brfss_train_path = os.path.join(data_dir, "processed", "X_train.csv")
    brfss_ytrain_path = os.path.join(data_dir, "processed", "y_train.csv")
    brfss_test_path = os.path.join(data_dir, "processed", "X_test.csv")
    brfss_ytest_path = os.path.join(data_dir, "processed", "y_test.csv")

    X_train_full = pd.read_csv(brfss_train_path)
    y_train = pd.read_csv(brfss_ytrain_path).values.ravel()
    X_test_full = pd.read_csv(brfss_test_path)
    y_test_brfss = pd.read_csv(brfss_ytest_path).values.ravel()

    # 7 спільних гармонізованих ознак
    common_features = ['Age', 'Sex', 'BMI', 'HighBP', 'HighChol', 'Smoker', 'Diabetes_bin']

    # Бінаризація діабету у BRFSS для гармонізації (0 - норма, 1 - предіабет/діабет)
    X_train_harm = X_train_full[['Age', 'Sex', 'BMI', 'HighBP', 'HighChol', 'Smoker']].copy()
    X_train_harm['Diabetes_bin'] = (X_train_full['Diabetes'] >= 1).astype(float)

    X_test_brfss = X_test_full[['Age', 'Sex', 'BMI', 'HighBP', 'HighChol', 'Smoker']].copy()
    X_test_brfss['Diabetes_bin'] = (X_test_full['Diabetes'] >= 1).astype(float)

    print(f"   - BRFSS Train: {len(X_train_harm):,} записів")
    print(f"   - BRFSS Test (Internal): {len(X_test_brfss):,} записів")

    # -------------------------------------------------------------
    # 2. НАВЧАННЯ МОДЕЛІ ВИКЛЮЧНО НА TRAIN BRFSS
    # -------------------------------------------------------------
    print("\n2. Навчання гармонізованої моделі XGBoost (тільки на BRFSS Train)...")
    mono_constraints = (1, 0, 0, 1, 1, 1, 1) # Age, Sex, BMI, HighBP, HighChol, Smoker, Diabetes

    harmonized_xgb = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.5,
        reg_lambda=2.0,
        min_child_weight=3,
        monotone_constraints=mono_constraints,
        random_state=42,
        eval_metric='logloss',
        n_jobs=-1
    )
    t0 = time.time()
    harmonized_xgb.fit(X_train_harm, y_train)
    print(f"   -> Модель успішно натренована за {time.time() - t0:.2f} сек.")

    # -------------------------------------------------------------
    # 3. ПІДГОТОВКА ЗОВНІШНІХ ТЕСТОВИХ ДАТАСЕТІВ (БЕЗ НАВЧАННЯ)
    # -------------------------------------------------------------
    print("\n3. Підготовка зовнішніх тестових когорт...")

    # А. Cardio Train (Європейська клінічна когорта)
    cardio_raw_path = os.path.join(data_dir, "cardio_train.csv")
    df_cardio = pd.read_csv(cardio_raw_path, sep=';')
    
    # Клінічна валідація фізіологічних меж тиску
    df_cardio_clean = df_cardio[
        (df_cardio['ap_hi'] >= 60) & (df_cardio['ap_hi'] <= 240) &
        (df_cardio['ap_lo'] >= 40) & (df_cardio['ap_lo'] <= 160)
    ].copy()

    c_age_years = df_cardio_clean['age'] / 365.25
    c_age_cat = map_age_to_brfss_cat(c_age_years)
    c_male = (df_cardio_clean['gender'] == 2).astype(float)
    c_bmi = (df_cardio_clean['weight'] / ((df_cardio_clean['height'] / 100.0) ** 2)).astype(float)
    c_hyp = ((df_cardio_clean['ap_hi'] >= 140) | (df_cardio_clean['ap_lo'] >= 90)).astype(float)
    c_chol = (df_cardio_clean['cholesterol'] > 1).astype(float)
    c_smoke = df_cardio_clean['smoke'].astype(float)
    c_diab = (df_cardio_clean['gluc'] > 1).astype(float)

    X_cardio = pd.DataFrame({
        'Age': c_age_cat,
        'Sex': c_male,
        'BMI': c_bmi,
        'HighBP': c_hyp,
        'HighChol': c_chol,
        'Smoker': c_smoke,
        'Diabetes_bin': c_diab
    })
    y_cardio = df_cardio_clean['cardio'].values

    print(f"   - Cardio Train External Test: {len(X_cardio):,} пацієнтів")

    # Б. Framingham Heart Study (Проспективна когорта)
    fram_raw_path = os.path.join(data_dir, "framingham.csv")
    df_fram = pd.read_csv(fram_raw_path).dropna(subset=['BMI', 'totChol', 'sysBP', 'diaBP', 'diabetes', 'currentSmoker']).copy()

    f_age_cat = map_age_to_brfss_cat(df_fram['age'])
    f_male = df_fram['male'].astype(float)
    f_bmi = df_fram['BMI'].astype(float)
    f_hyp = df_fram['prevalentHyp'].astype(float)
    f_chol = (df_fram['totChol'] >= 240.0).astype(float)
    f_smoke = df_fram['currentSmoker'].astype(float)
    f_diab = df_fram['diabetes'].astype(float)

    X_fram = pd.DataFrame({
        'Age': f_age_cat,
        'Sex': f_male,
        'BMI': f_bmi,
        'HighBP': f_hyp,
        'HighChol': f_chol,
        'Smoker': f_smoke,
        'Diabetes_bin': f_diab
    })
    y_fram = df_fram['TenYearCHD'].values

    print(f"   - Framingham Heart Study External Test: {len(X_fram):,} пацієнтів")

    # -------------------------------------------------------------
    # 4. ОБЧИСЛЕННЯ МЕТРИК ДЛЯ ВСІХ ТРЬОХ КОГОРТ
    # -------------------------------------------------------------
    cohorts = [
        ("CDC BRFSS (Internal Test)", X_test_brfss, y_test_brfss, "Внутрішній контроль (США, населення)"),
        ("Cardio Train (External Test)", X_cardio, y_cardio, "Зовнішній клінічний (Європа, клініка)"),
        ("Framingham (External Test)", X_fram, y_fram, "Зовнішній проспективний (США, 10 років)")
    ]

    metrics_summary = []
    curves_data = {}

    print("\n4. Обчислення метрик перенесення (Cross-Cohort Evaluation)...")
    for name, X_eval, y_eval, desc in cohorts:
        probs = harmonized_xgb.predict_proba(X_eval)[:, 1]
        
        # Обчислення порогу за індексом Юдена
        fpr, tpr, thresh = roc_curve(y_eval, probs)
        youd_idx = np.argmax(tpr - fpr)
        opt_thresh = float(thresh[youd_idx])

        # Передбачення при збалансованому порозі когорти
        preds = (probs >= opt_thresh).astype(int)

        roc_auc = float(roc_auc_score(y_eval, probs))
        pr_auc = float(average_precision_score(y_eval, probs))
        acc = float(accuracy_score(y_eval, preds))
        prec = float(precision_score(y_eval, preds, zero_division=0))
        rec = float(recall_score(y_eval, preds, zero_division=0))
        f1 = float(f1_score(y_eval, preds, zero_division=0))
        cm = confusion_matrix(y_eval, preds).tolist()

        prec_curve, rec_curve, _ = precision_recall_curve(y_eval, probs)

        metrics_summary.append({
            "dataset": name,
            "description": desc,
            "n_samples": int(len(y_eval)),
            "positive_prevalence": round(float(np.mean(y_eval)), 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "optimal_threshold": round(opt_thresh, 4),
            "confusion_matrix": cm
        })

        curves_data[name] = {
            "fpr": fpr,
            "tpr": tpr,
            "roc_auc": roc_auc,
            "prec_curve": prec_curve,
            "rec_curve": rec_curve,
            "pr_auc": pr_auc
        }

    # -------------------------------------------------------------
    # 5. ВІДОБРАЖЕННЯ ЗВЕДЕНОЇ ТАБЛИЦІ
    # -------------------------------------------------------------
    df_metrics = pd.DataFrame(metrics_summary)
    print("\n" + "=" * 105)
    print(f"{'Датасет':<32} | {'Когорта':<8} | {'N':<7} | {'Поширеність':<11} | {'ROC-AUC':<8} | {'PR-AUC':<8} | {'Recall':<8} | {'F1':<6}")
    print("-" * 105)
    for _, row in df_metrics.iterrows():
        print(f"{row['dataset']:<32} | {'Test':<8} | {row['n_samples']:<7,} | {row['positive_prevalence']*100:<10.1f}% | {row['roc_auc']:<8.4f} | {row['pr_auc']:<8.4f} | {row['recall']*100:<7.1f}% | {row['f1']:<6.4f}")
    print("=" * 105)

    # -------------------------------------------------------------
    # 6. ПОБУДОВА ТА ЗБЕРЕЖЕННЯ ГРАФІКІВ ROC ТА PR ДЛЯ ВСІХ ТРЬОХ КОГОРТ
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)
    colors = {
        "CDC BRFSS (Internal Test)": "#1E40AF",
        "Cardio Train (External Test)": "#DC2626",
        "Framingham (External Test)": "#059669"
    }

    # ROC Curves
    for name, c_data in curves_data.items():
        ax1.plot(c_data["fpr"], c_data["tpr"], lw=2.2, color=colors[name],
                 label=f"{name} (AUC = {c_data['roc_auc']:.3f})")
    ax1.plot([0, 1], [0, 1], linestyle='--', color='#9CA3AF', lw=1.2, label='Випадкове вгадування (0.500)')
    ax1.set_title('Криві ROC (Дискримінаційна здатність у різних когортах)', fontsize=11, fontweight='bold', pad=10)
    ax1.set_xlabel('Частка хибнопозитивних (1 - Специфічність)')
    ax1.set_ylabel('Частка істиннопозитивних (Чутливість / Recall)')
    ax1.legend(loc='lower right', frameon=True)
    ax1.grid(True, linestyle=':', alpha=0.6)

    # PR Curves
    for name, c_data in curves_data.items():
        ax2.plot(c_data["rec_curve"], c_data["prec_curve"], lw=2.2, color=colors[name],
                 label=f"{name} (PR-AUC = {c_data['pr_auc']:.3f})")
    ax2.set_title('Криві Precision-Recall (Якість прогнозу за дисбалансу)', fontsize=11, fontweight='bold', pad=10)
    ax2.set_xlabel('Повнота (Recall)')
    ax2.set_ylabel('Точність (Precision)')
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    chart_path = os.path.join(reports_dir, "cross_cohort_validation.png")
    fig.savefig(chart_path, bbox_inches='tight')
    plt.close()
    print(f"\nГрафік крос-когортної валідації збережено: {chart_path}")

    # Збереження JSON-звіту для веб-інтерфейсу
    json_path = os.path.join(reports_dir, "external_validation_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, ensure_ascii=False, indent=2)
    print(f"Звіт метрик збережено: {json_path}")
    print("\n" + "=" * 80)
    print("КРОС-КОГОРТНА ВАЛІДАЦІЯ УСПІШНО ЗАВЕРШЕНА!")
    print("=" * 80)

if __name__ == "__main__":
    main()
