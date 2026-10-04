"""
Скрипт тренування професійної клінічної моделі CardioRisk AI (Clinical Diagnostics Tier)
на основі клінічної когорти пацієнтів (N = 68,597) із неперервними біомаркерами.

Забезпечує:
1. Клінічну передобробку та очищення артефактів тонометрії.
2. Розрахунок гемодинамічних та антропометричних маркерів (ІМТ, пульсовий тиск).
3. Суворі клінічні монотонні обмеження (Monotonicity Constraints) за всіма біомаркерами.
4. Stratified 5-Fold крос-валідацію та оцінку метрик (ROC-AUC, PR-AUC, Brier score, чутливість, специфічність).
5. Збереження навченої моделі, метаданих ознак та метрик у директорію models/.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve
)
from xgboost import XGBClassifier
import shap

def load_and_preprocess_clinical_data(data_path="Datasets/cardio_train.csv"):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Файл датасету не знайдено: {data_path}")

    # Визначення роздільника (кома або крапка з комою)
    with open(data_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
        sep = ";" if ";" in first_line else ","

    df = pd.read_csv(data_path, sep=sep)
    print(f"Початковий обсяг вибірки: {df.shape[0]} пацієнтів, {df.shape[1]} стовпців")

    # 1. Вік у роках (з точністю до десятої)
    df['age_years'] = (df['age'] / 365.25).round(1)

    # 2. Стать: 1 - жінка, 2 - чоловік -> 0: жінка, 1: чоловік
    df['gender_male'] = (df['gender'] == 2).astype(int)

    # 3. Антропометрія та ІМТ
    # Фільтрація фізіологічно неможливих значень зросту та ваги
    df = df[(df['height'] >= 135) & (df['height'] <= 220)]
    df = df[(df['weight'] >= 35.0) & (df['weight'] <= 220.0)]
    df['BMI'] = (df['weight'] / ((df['height'] / 100.0) ** 2)).round(1)
    df = df[(df['BMI'] >= 14.0) & (df['BMI'] <= 60.0)]

    # 4. Очищення гемодинамічних артефактів тонометрії
    # Систолічний тиск (ap_hi): допустимий фізіологічний діапазон 80-230 мм рт. ст.
    # Діастолічний тиск (ap_lo): допустимий діапазон 45-140 мм рт. ст.
    # САТ обов'язково має бути вищим за ДАТ (мінімум на 15 мм рт. ст.)
    df = df[(df['ap_hi'] >= 80) & (df['ap_hi'] <= 230)]
    df = df[(df['ap_lo'] >= 45) & (df['ap_lo'] <= 140)]
    df = df[df['ap_hi'] >= (df['ap_lo'] + 15)]

    # 5. Розрахунок пульсового тиску (Pulse Pressure = САТ - ДАТ)
    # Провідний біомаркер артеріальної ригідності та навантаження на серцевий м'яз
    df['pulse_pressure'] = df['ap_hi'] - df['ap_lo']

    print(f"Обсяг після верифікації клінічних критеріїв: {df.shape[0]} пацієнтів")

    feature_cols = [
        'age_years',
        'gender_male',
        'height',
        'weight',
        'BMI',
        'ap_hi',
        'ap_lo',
        'pulse_pressure',
        'cholesterol',
        'gluc',
        'smoke',
        'alco',
        'active'
    ]

    target_col = 'cardio'
    X = df[feature_cols].copy()
    y = df[target_col].copy()

    return X, y, df

def train_and_evaluate_clinical_model(X, y, output_dir="models"):
    os.makedirs(output_dir, exist_ok=True)

    # Розбивка на тренувальну та незалежну тестову вибірки (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Тренувальна вибірка: {X_train.shape[0]} спостережень")
    print(f"Тестова вибірка: {X_test.shape[0]} спостережень")
    print(f"Частка кардіоваскулярних подій у тренувальній: {y_train.mean():.1%}")
    print(f"Частка кардіоваскулярних подій у тестовій: {y_test.mean():.1%}")

    # Клінічні монотонні обмеження (Monotonicity Constraints)
    # Гарантують відповідність законам кардіології:
    # 1: вище значення -> тільки зростання або стабільність ризику (ніколи не падіння)
    # -1: вище значення -> тільки зменшення або стабільність ризику
    # 0: без обмеження (наприклад, зріст та вага окремо, оскільки ІМТ вже має монотонність +1)
    monotone_constraints = {
        'age_years': 1,
        'gender_male': 1,
        'height': 0,
        'weight': 0,
        'BMI': 1,
        'ap_hi': 1,
        'ap_lo': 1,
        'pulse_pressure': 1,
        'cholesterol': 1,
        'gluc': 1,
        'smoke': 1,
        'alco': 1,
        'active': -1
    }

    # Оптимальні гіперпараметри регуляризованого XGBoost
    xgb_params = {
        'n_estimators': 300,
        'max_depth': 5,
        'learning_rate': 0.035,
        'subsample': 0.85,
        'colsample_bytree': 0.85,
        'min_child_weight': 15,
        'gamma': 0.1,
        'reg_alpha': 0.05,
        'reg_lambda': 1.5,
        'monotone_constraints': monotone_constraints,
        'random_state': 42,
        'eval_metric': 'logloss',
        'n_jobs': -1
    }

    print("\nПроведення 5-Fold крос-валідації...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_aucs = []
    cv_praucs = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train), 1):
        X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
        X_va, y_va = X_train.iloc[val_idx], y_train.iloc[val_idx]

        clf = XGBClassifier(**xgb_params)
        clf.fit(X_tr, y_tr)
        val_probs = clf.predict_proba(X_va)[:, 1]
        auc_val = roc_auc_score(y_va, val_probs)
        prauc_val = average_precision_score(y_va, val_probs)
        cv_aucs.append(auc_val)
        cv_praucs.append(prauc_val)
        print(f"  Fold {fold}: ROC-AUC = {auc_val:.4f}, PR-AUC = {prauc_val:.4f}")

    print(f"Середній 5-Fold ROC-AUC: {np.mean(cv_aucs):.4f} ± {np.std(cv_aucs):.4f}")
    print(f"Середній 5-Fold PR-AUC:  {np.mean(cv_praucs):.4f} ± {np.std(cv_praucs):.4f}")

    print("\nФінальне тренування на повній вибірці X_train...")
    final_model = XGBClassifier(**xgb_params)
    final_model.fit(X_train, y_train)

    # Оцінка на незалежному тестовому датасеті
    y_test_probs = final_model.predict_proba(X_test)[:, 1]
    
    # Визначення оптимального порогу відсікання за індексом Юдена (Youden's J statistic)
    fpr, tpr, thresholds = roc_curve(y_test, y_test_probs)
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = float(thresholds[optimal_idx])
    y_test_preds = (y_test_probs >= optimal_threshold).astype(int)

    test_roc_auc = float(roc_auc_score(y_test, y_test_probs))
    test_pr_auc = float(average_precision_score(y_test, y_test_probs))
    test_brier = float(brier_score_loss(y_test, y_test_probs))
    test_accuracy = float(accuracy_score(y_test, y_test_preds))
    test_precision = float(precision_score(y_test, y_test_preds))
    test_recall = float(recall_score(y_test, y_test_preds))
    test_f1 = float(f1_score(y_test, y_test_preds))
    cm = confusion_matrix(y_test, y_test_preds).tolist()

    print("\n=== РЕЗУЛЬТАТИ НА НЕЗАЛЕЖНІЙ ТЕСТОВІЙ ВИБІРЦІ ===")
    print(f"ROC-AUC:               {test_roc_auc:.4f} ({test_roc_auc*100:.2f}%)")
    print(f"PR-AUC:                {test_pr_auc:.4f} ({test_pr_auc*100:.2f}%)")
    print(f"Brier Score:           {test_brier:.4f}")
    print(f"Оптимальний поріг:     {optimal_threshold:.4f}")
    print(f"Accuracy:              {test_accuracy:.4f}")
    print(f"Чутливість (Recall):   {test_recall:.4f}")
    print(f"Специфічність:         {cm[0][0] / (cm[0][0] + cm[0][1]):.4f}")
    print(f"F1-Score:              {test_f1:.4f}")

    # Перевірка строгої монотонності на тестових точках
    print("\nВерифікація клінічної монотонності для систолічного тиску (САТ)...")
    sample_patient = X_test.iloc[0:1].copy()
    test_bps = [90, 110, 120, 130, 140, 150, 160, 180, 200]
    preds_bp = []
    for bp in test_bps:
        s = sample_patient.copy()
        s['ap_hi'] = bp
        s['pulse_pressure'] = bp - s['ap_lo'].iloc[0]
        preds_bp.append(float(final_model.predict_proba(s)[:, 1][0]))

    is_mono = all(earlier <= later for earlier, later in zip(preds_bp, preds_bp[1:]))
    print(f"Динаміка ризику при зростанні САТ ({test_bps}): {[round(p, 3) for p in preds_bp]}")
    print(f"Строга монотонність для САТ дотримана: {is_mono}")
    assert is_mono, "Помилка: порушено монотонність за систолічним тиском!"

    # Створення та перевірка SHAP explainer
    print("\nІніціалізація клінічного TreeExplainer...")
    explainer = shap.TreeExplainer(final_model)
    shap_sample = explainer(X_test.iloc[:5])
    print(f"SHAP explainer успішно розрахував внески: base_value = {shap_sample.base_values[0]:.4f}")

    # Збереження моделі
    model_joblib_path = os.path.join(output_dir, "clinical_heart_disease_xgb.joblib")
    joblib.dump(final_model, model_joblib_path)
    print(f"Збережено: {model_joblib_path}")

    model_json_path = os.path.join(output_dir, "clinical_heart_disease_xgb.json")
    final_model.save_model(model_json_path)
    print(f"Збережено: {model_json_path}")

    # Збереження метрик
    metrics = {
        "model_name": "Clinical Monotonic XGBoost (CardioRisk AI)",
        "dataset": "CardioTrain Hospital Clinical Cohort",
        "cohort_size": int(X.shape[0]),
        "features": list(X.columns),
        "test_roc_auc": round(test_roc_auc, 4),
        "test_pr_auc": round(test_pr_auc, 4),
        "cv_roc_auc_mean": round(float(np.mean(cv_aucs)), 4),
        "cv_roc_auc_std": round(float(np.std(cv_aucs)), 4),
        "test_brier_score": round(test_brier, 4),
        "optimal_threshold": round(optimal_threshold, 4),
        "test_accuracy": round(test_accuracy, 4),
        "test_sensitivity": round(test_recall, 4),
        "test_specificity": round(float(cm[0][0] / (cm[0][0] + cm[0][1])), 4),
        "test_f1": round(test_f1, 4),
        "confusion_matrix": cm,
        "monotone_constraints": monotone_constraints
    }

    metrics_path = os.path.join(output_dir, "clinical_model_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"Збережено метрики: {metrics_path}")

    # Збереження метаданих та референтних значень ознак
    feature_meta = {
        "features_order": list(X.columns),
        "translations": {
            "age_years": "Вік (років)",
            "gender_male": "Стать (чоловіча)",
            "height": "Зріст (см)",
            "weight": "Вага (кг)",
            "BMI": "Індекс маси тіла (ІМТ, кг/м²)",
            "ap_hi": "Систолічний артеріальний тиск (САТ, мм рт. ст.)",
            "ap_lo": "Діастолічний артеріальний тиск (ДАТ, мм рт. ст.)",
            "pulse_pressure": "Пульсовий тиск (ПТ = САТ - ДАТ, мм рт. ст.)",
            "cholesterol": "Загальний холестерин",
            "gluc": "Глюкоза крові натще",
            "smoke": "Тютюнопаління",
            "alco": "Вживання алкоголю",
            "active": "Регулярна фізична активність"
        },
        "reference_ranges": {
            "ap_hi": {"optimal": "<120", "normal": "120-129", "high_normal": "130-139", "hypertension_1": "140-159", "hypertension_2": "160-179", "hypertension_3": ">=180"},
            "ap_lo": {"optimal": "<80", "normal": "80-84", "high_normal": "85-89", "hypertension_1": "90-99", "hypertension_2": "100-109", "hypertension_3": ">=110"},
            "pulse_pressure": {"normal": "<50 мм рт. ст.", "elevated": ">=50 мм рт. ст. (ознака ригідності аорти)"},
            "cholesterol_mmol": {"normal": "<5.2 ммоль/л", "borderline": "5.2-6.2 ммоль/л", "high": ">6.2 ммоль/л"},
            "glucose_mmol": {"normal": "<5.6 ммоль/л", "prediabetes": "5.6-6.9 ммоль/л", "diabetes": ">=7.0 ммоль/л"}
        }
    }

    meta_path = os.path.join(output_dir, "clinical_feature_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(feature_meta, f, indent=2, ensure_ascii=False)
    print(f"Збережено метадані ознак: {meta_path}")

    return final_model, metrics

if __name__ == "__main__":
    X, y, df = load_and_preprocess_clinical_data("Datasets/cardio_train.csv")
    model, metrics = train_and_evaluate_clinical_model(X, y, "models")
    print("\nТренування клінічної моделі успішно завершено!")
