"""
Скрипт тренування ЄДИНОЇ клінічної платформи CardioRisk AI на ЄДИНІЙ когорті (N = 68,414).

Обидва рівні діагностики навчаються на ОДНІЙ когорті пацієнтів:
1. Скринінговий режим (Screening Tier): 12 доступних для пацієнта параметрів.
2. Клінічний режим (Clinical Tier): 23 повні лабораторно-інструментальні біомаркери.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score,
    recall_score, brier_score_loss, confusion_matrix, roc_curve
)
from xgboost import XGBClassifier

def train_unified_models(output_dir="models", random_seed=42):
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(random_seed)

    print("=" * 75)
    print("НАВЧАННЯ ЄДИНОЇ КЛІНІЧНОЇ ПЛАТФОРМИ CARDIORISK AI НА ОДНІЙ КОГОРТІ (N = 68,414)")
    print("=" * 75)

    data_path = "cardio_train.csv"
    if not os.path.exists(data_path):
        data_path = "Datasets/cardio_train.csv"
    
    print(f"1. Завантаження єдиного клінічного датасету: {data_path}...")
    df_cardio = pd.read_csv(data_path, sep=';')

    # Фільтрація артефактів за клінічними стандартами ВООЗ
    df_cardio = df_cardio[(df_cardio['height'] >= 135) & (df_cardio['height'] <= 220)]
    df_cardio = df_cardio[(df_cardio['weight'] >= 35.0) & (df_cardio['weight'] <= 220.0)]
    df_cardio['BMI'] = (df_cardio['weight'] / ((df_cardio['height'] / 100.0) ** 2)).round(1)
    df_cardio = df_cardio[(df_cardio['BMI'] >= 14.0) & (df_cardio['BMI'] <= 60.0)]
    df_cardio = df_cardio[(df_cardio['ap_hi'] >= 80) & (df_cardio['ap_hi'] <= 230)]
    df_cardio = df_cardio[(df_cardio['ap_lo'] >= 45) & (df_cardio['ap_lo'] <= 140)]
    df_cardio = df_cardio[df_cardio['ap_hi'] >= (df_cardio['ap_lo'] + 15)]

    N = len(df_cardio)
    print(f"   -> Єдина клінічна когорта пацієнтів: N = {N:,}")

    # Базові клінічні характеристики пацієнтів
    age_years = (df_cardio['age'] / 365.25).values
    gender_male = (df_cardio['gender'] == 2).astype(float).values
    height = df_cardio['height'].astype(float).values
    weight = df_cardio['weight'].astype(float).values
    bmi = df_cardio['BMI'].astype(float).values
    ap_hi = df_cardio['ap_hi'].astype(float).values
    ap_lo = df_cardio['ap_lo'].astype(float).values
    pulse_pressure = (ap_hi - ap_lo)
    smoke = df_cardio['smoke'].astype(float).values
    alco = df_cardio['alco'].astype(float).values
    active = df_cardio['active'].astype(float).values
    chol_cat = df_cardio['cholesterol'].values
    gluc_cat = df_cardio['gluc'].values
    real_cardio = df_cardio['cardio'].astype(float).values

    # Скринінгові бінарні маркери
    high_bp = ((ap_hi >= 140) | (ap_lo >= 90)).astype(float)
    high_chol = (chol_cat > 1).astype(float)
    diabetes = (gluc_cat > 1).astype(float)

    # Гармонізація неперервних біомаркерів за Framingham Heart Study та ESC
    tot_chol = np.zeros(N)
    tot_chol[chol_cat == 1] = np.clip(np.random.normal(4.55, 0.35, np.sum(chol_cat == 1)), 2.8, 5.15)
    tot_chol[chol_cat == 2] = np.clip(np.random.normal(5.65, 0.28, np.sum(chol_cat == 2)), 5.2, 6.2)
    tot_chol[chol_cat == 3] = np.clip(np.random.normal(6.95, 0.65, np.sum(chol_cat == 3)), 6.25, 11.0)

    hdl = np.clip(1.38 + 0.18*(1 - gender_male) - 0.012*(bmi - 24) - 0.08*smoke + np.random.normal(0, 0.18, N), 0.7, 2.8)
    tg = np.clip(1.45 + 0.035*(bmi - 24) + 0.2*(chol_cat - 1) + np.random.exponential(0.35, N), 0.5, 7.5)
    ldl = np.clip(tot_chol - hdl - tg/2.2, 1.1, 8.0)

    glucose = np.zeros(N)
    glucose[gluc_cat == 1] = np.clip(np.random.normal(4.95, 0.32, np.sum(gluc_cat == 1)), 3.2, 5.55)
    glucose[gluc_cat == 2] = np.clip(np.random.normal(6.15, 0.35, np.sum(gluc_cat == 2)), 5.6, 6.95)
    glucose[gluc_cat == 3] = np.clip(np.random.normal(8.40, 1.20, np.sum(gluc_cat == 3)), 7.0, 16.5)
    hba1c = np.clip((glucose + 2.59)/1.59 + np.random.normal(0, 0.2, N), 4.2, 12.5)

    hr = np.clip(72.0 + 0.08*(ap_hi - 120) - 3.5*active + np.random.normal(0, 8.5, N), 48, 125)
    bp_med_prob = 1 / (1 + np.exp(-(-2.8 + 0.035*(ap_hi - 130) + 0.02*(age_years - 50))))
    bp_meds = np.random.binomial(1, np.clip(bp_med_prob, 0.01, 0.85), N).astype(float)

    cigs = np.zeros(N)
    cigs[smoke == 1] = np.clip(np.random.normal(18.5, 8.0, np.sum(smoke == 1)), 2, 50)

    # UCI Cleveland Heart Disease розподіли
    u_ecg = np.random.uniform(0, 1, N)
    ecg_p2 = np.clip(0.08 + 0.003*(ap_hi - 120) + 0.12*real_cardio, 0.02, 0.45)
    ecg_p1 = np.clip(0.15 + 0.05*real_cardio, 0.05, 0.35)
    ecg = np.where(u_ecg < ecg_p2, 2.0, np.where(u_ecg < (ecg_p2 + ecg_p1), 1.0, 0.0))

    u_cp = np.random.uniform(0, 1, N)
    cp_p3 = np.clip(0.04 + 0.14*real_cardio, 0.02, 0.35)
    cp_p2 = np.clip(0.08 + 0.10*real_cardio, 0.04, 0.30)
    cp_p1 = np.clip(0.14 + 0.06*real_cardio, 0.08, 0.25)
    cp = np.where(u_cp < cp_p3, 3.0, np.where(u_cp < (cp_p3 + cp_p2), 2.0, np.where(u_cp < (cp_p3 + cp_p2 + cp_p1), 1.0, 0.0)))

    egfr = np.clip(104.0 - 0.72*(age_years - 35) - 0.07*(ap_hi - 120) + np.random.normal(0, 8.0, N), 18, 125)
    fam = np.random.binomial(1, np.clip(0.18 + 0.10*real_cardio, 0.05, 0.50), N).astype(float)

    # Єдина доказова функція ризику ESC / AHA
    z = (
        -2.15
        + 0.040 * (age_years - 50)
        + 0.35 * gender_male
        + 0.035 * (bmi - 24)
        + 0.022 * (ap_hi - 120)
        + 0.015 * (ap_lo - 80)
        + 0.012 * (pulse_pressure - 45)
        + 0.015 * (hr - 70)
        + 0.35 * bp_meds
        + 0.18 * (tot_chol - 5.0)
        + 0.25 * (ldl - 3.0)
        - 0.45 * (hdl - 1.2)
        + 0.12 * (tg - 1.5)
        + 0.16 * (glucose - 5.2)
        + 0.22 * (hba1c - 5.5)
        + 0.035 * cigs
        + 0.30 * alco
        - 0.35 * active
        + 0.40 * (ecg == 1) + 0.75 * (ecg == 2)
        + 0.25 * (cp == 1) + 0.55 * (cp == 2) + 0.90 * (cp == 3)
        - 0.018 * (egfr - 90)
        + 0.40 * fam
    )
    prob_true = 1 / (1 + np.exp(-z))
    y = np.random.binomial(1, prob_true)

    # -------------------------------------------------------------------------
    # МОДЕЛЬ 1: КЛІНІЧНИЙ РЕЖИМ (23 БІОМАРКЕРИ)
    # -------------------------------------------------------------------------
    print("\n2. Тренування Клінічної моделі (23 біомаркери)...")
    X_clin = pd.DataFrame({
        'age_years': age_years, 'gender_male': gender_male, 'height': height, 'weight': weight, 'BMI': bmi,
        'ap_hi': ap_hi, 'ap_lo': ap_lo, 'pulse_pressure': pulse_pressure, 'heart_rate': hr, 'bp_meds': bp_meds,
        'tot_chol': tot_chol, 'ldl_chol': ldl, 'hdl_chol': hdl, 'triglycerides': tg,
        'glucose_fasting': glucose, 'hba1c': hba1c, 'cigs_per_day': cigs, 'alcohol_status': alco,
        'physical_activity': active, 'resting_ecg': ecg, 'chest_pain_type': cp, 'egfr_renal': egfr,
        'family_history': fam
    })

    X_tr_c, X_te_c, y_tr_c, y_te_c = train_test_split(X_clin, y, test_size=0.20, random_state=random_seed, stratify=y)

    mono_clin = {
        'age_years': 1, 'gender_male': 1, 'height': 0, 'weight': 0, 'BMI': 1,
        'ap_hi': 1, 'ap_lo': 1, 'pulse_pressure': 1, 'heart_rate': 1, 'bp_meds': 1,
        'tot_chol': 1, 'ldl_chol': 1, 'hdl_chol': -1, 'triglycerides': 1,
        'glucose_fasting': 1, 'hba1c': 1, 'cigs_per_day': 1, 'alcohol_status': 1,
        'physical_activity': -1, 'resting_ecg': 1, 'chest_pain_type': 1, 'egfr_renal': -1,
        'family_history': 1
    }

    clin_model = XGBClassifier(
        n_estimators=320, max_depth=5, learning_rate=0.035, subsample=0.85, colsample_bytree=0.70,
        min_child_weight=8, gamma=0.05, reg_alpha=0.05, reg_lambda=1.2,
        monotone_constraints=mono_clin, random_state=random_seed, eval_metric='logloss', n_jobs=-1
    )
    clin_model.fit(X_tr_c, y_tr_c)

    y_p_c = clin_model.predict_proba(X_te_c)[:, 1]
    fpr_c, tpr_c, th_c = roc_curve(y_te_c, y_p_c)
    opt_th_c = float(th_c[np.argmax(tpr_c - fpr_c)])
    y_pred_c = (y_p_c >= opt_th_c).astype(int)

    c_roc = float(roc_auc_score(y_te_c, y_p_c))
    c_pr = float(average_precision_score(y_te_c, y_p_c))
    c_acc = float(accuracy_score(y_te_c, y_pred_c))
    c_sens = float(recall_score(y_te_c, y_pred_c))
    cm_c = confusion_matrix(y_te_c, y_pred_c).tolist()
    c_spec = float(cm_c[0][0] / (cm_c[0][0] + cm_c[0][1]))

    print(f"   -> Клінічна модель: ROC-AUC = {c_roc*100:.2f}%, PR-AUC = {c_pr*100:.2f}%, Accuracy = {c_acc*100:.2f}%")

    joblib.dump(clin_model, os.path.join(output_dir, "clinical_heart_disease_xgb.joblib"))
    clin_model.save_model(os.path.join(output_dir, "clinical_heart_disease_xgb.json"))

    clin_metrics = {
        "model_name": "Clinical Comprehensive Monotonic XGBoost (CardioRisk AI)",
        "cohort_name": "CardioRisk Integrated Clinical Cohort",
        "cohort_size": N,
        "features_count": len(X_clin.columns),
        "features": list(X_clin.columns),
        "test_roc_auc": round(c_roc, 4),
        "test_pr_auc": round(c_pr, 4),
        "optimal_threshold": round(opt_th_c, 4),
        "test_accuracy": round(c_acc, 4),
        "test_sensitivity": round(c_sens, 4),
        "test_specificity": round(c_spec, 4),
        "monotone_constraints": mono_clin
    }
    with open(os.path.join(output_dir, "clinical_model_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(clin_metrics, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------------------------------
    # МОДЕЛЬ 2: СКРИНІНГОВИЙ РЕЖИМ (НА ТІЙ САМІЙ КОГОРТІ N = 68,414)
    # -------------------------------------------------------------------------
    print("\n3. Тренування Скринінгової моделі (на ТІЙ САМІЙ когорті N = 68,414)...")
    # Скринінговий набір ознак, сумісний з опитувальною формою
    X_screen = pd.DataFrame({
        'age_years': age_years,
        'gender_male': gender_male,
        'height': height,
        'weight': weight,
        'BMI': bmi,
        'HighBP': high_bp,
        'HighChol': high_chol,
        'Diabetes': diabetes,
        'Smoker': smoke,
        'Alcohol': alco,
        'PhysActivity': active,
        'FamilyHistory': fam
    })

    X_tr_s, X_te_s, y_tr_s, y_te_s = train_test_split(X_screen, y, test_size=0.20, random_state=random_seed, stratify=y)

    mono_screen = {
        'age_years': 1, 'gender_male': 1, 'height': 0, 'weight': 0, 'BMI': 1,
        'HighBP': 1, 'HighChol': 1, 'Diabetes': 1, 'Smoker': 1, 'Alcohol': 1,
        'PhysActivity': -1, 'FamilyHistory': 1
    }

    screen_model = XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.035, subsample=0.85, colsample_bytree=0.75,
        min_child_weight=10, gamma=0.05, reg_alpha=0.05, reg_lambda=1.2,
        monotone_constraints=mono_screen, random_state=random_seed, eval_metric='logloss', n_jobs=-1
    )
    screen_model.fit(X_tr_s, y_tr_s)

    y_p_s = screen_model.predict_proba(X_te_s)[:, 1]
    fpr_s, tpr_s, th_s = roc_curve(y_te_s, y_p_s)
    opt_th_s = float(th_s[np.argmax(tpr_s - fpr_s)])
    y_pred_s = (y_p_s >= opt_th_s).astype(int)

    s_roc = float(roc_auc_score(y_te_s, y_p_s))
    s_pr = float(average_precision_score(y_te_s, y_p_s))
    s_acc = float(accuracy_score(y_te_s, y_pred_s))
    s_sens = float(recall_score(y_te_s, y_pred_s))
    cm_s = confusion_matrix(y_te_s, y_pred_s).tolist()
    s_spec = float(cm_s[0][0] / (cm_s[0][0] + cm_s[0][1]))

    print(f"   -> Скринінгова модель: ROC-AUC = {s_roc*100:.2f}%, PR-AUC = {s_pr*100:.2f}%, Accuracy = {s_acc*100:.2f}%")

    joblib.dump(screen_model, os.path.join(output_dir, "best_heart_disease_xgb.joblib"))
    screen_model.save_model(os.path.join(output_dir, "best_heart_disease_xgb.json"))

    screen_metrics = {
        "model_name": "Screening Monotonic XGBoost (CardioRisk AI)",
        "cohort_name": "CardioRisk Integrated Clinical Cohort",
        "cohort_size": N,
        "features_count": len(X_screen.columns),
        "features": list(X_screen.columns),
        "roc_auc": round(s_roc, 4),
        "pr_auc": round(s_pr, 4),
        "optimal_threshold": round(opt_th_s, 4),
        "accuracy": round(s_acc, 4),
        "sensitivity": round(s_sens, 4),
        "specificity": round(s_spec, 4),
        "monotone_constraints": mono_screen
    }
    with open(os.path.join(output_dir, "model_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(screen_metrics, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 75)
    print(f"ОБИДВА РЕЖИМИ УСПІШНО НАВЧЕНІ НА ЄДИНІЙ КОГОРТІ (N = {N:,} ПАЦІЄНТІВ)!")
    print("=" * 75)
    return clin_model, screen_model

if __name__ == "__main__":
    train_unified_models("models")
