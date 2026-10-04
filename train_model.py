"""
Модуль навчання високоефективної моделі машинного навчання: XGBoost (Extreme Gradient Boosting).
Використовує клінічні дані CDC BRFSS (253,680 пацієнтів) для прогнозування кардіоваскулярного ризику
з подальшою інтерпретацією через TreeSHAP.
"""

import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    roc_curve
)

def main():
    print("=" * 70)
    print("ПОЧАТОК НАВЧАННЯ ВИСОКОТОЧНОЇ КЛІНІЧНОЇ МОДЕЛІ (XGBOOST)")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(base_dir, "Datasets", "processed")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    # 1. Завантаження тренувального та тестового наборів даних
    print("\n1. Завантаження підготовлених вибірок даних...")
    t0 = time.time()
    X_train = pd.read_csv(os.path.join(datasets_dir, "X_train.csv"))
    y_train = pd.read_csv(os.path.join(datasets_dir, "y_train.csv")).values.ravel()
    X_test = pd.read_csv(os.path.join(datasets_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(datasets_dir, "y_test.csv")).values.ravel()

    print(f"   - Тренувальна вибірка: {X_train.shape[0]:,} пацієнтів, {X_train.shape[1]} ознак")
    print(f"   - Тестова вибірка:     {X_test.shape[0]:,} пацієнтів")
    print(f"   - Позитивний клас у тренувальній вибірці: {np.mean(y_train):.1%}")

    # 2. Ініціалізація та оптимізація моделі XGBoost
    print("\n2. Конфігурація та запуск Extreme Gradient Boosting (XGBoost)...")
    print("   Параметри: 350 дерев, глибина=5, learning_rate=0.05, регуляризація L1/L2...")

    # Монотонні клінічні обмеження: гарантують, що погіршення кожного окремого фактора
    # (зростання ІМТ, стрес, тиск, куріння, вік, алкоголь тощо) строго підвищує ризик
    # і виключає будь-які парадоксальні спади ризику
    constraints = {
        'HighBP': 1,            # Гіпертензія підвищує ризик
        'HighChol': 1,          # Холестерин підвищує ризик
        'BMI': 1,               # Зростання маси тіла / ІМТ строго підвищує ризик
        'Smoker': 1,            # Куріння підвищує ризик
        'Stroke': 1,            # Інсульт підвищує ризик
        'Diabetes': 1,          # Діабет підвищує ризик
        'PhysActivity': -1,     # Фізична активність знижує ризик
        'Fruits': -1,           # Щоденне вживання фруктів знижує ризик
        'Veggies': -1,          # Споживання овочів знижує ризик
        'HvyAlcoholConsump': 1, # Токсичне вживання алкоголю підвищує ризик
        'GenHlth': 1,           # Погіршення самооцінки (1->5) підвищує ризик
        'MentHlth': 1,          # Дні стресу/тривоги МОНОТОННО підвищують ризик
        'PhysHlth': 1,          # Дні нездужання МОНОТОННО підвищують ризик
        'DiffWalk': 1,          # Складнощі ходьби підвищують ризик
        'Sex': 1,               # Чоловіча стать підвищує базовий ризик
        'Age': 1                # Старший вік МОНОТОННО підвищує ризик
    }
    mono_tuple = tuple(constraints[col] for col in X_train.columns)

    # Оптимальні гіперпараметри для високої точності та клінічної стабільності
    xgb_model = XGBClassifier(
        n_estimators=350,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.5,     # L1 регуляризація для відбору стабільних ваг
        reg_lambda=2.0,    # L2 регуляризація для запобігання парадоксальних стрибків ваг
        min_child_weight=3,
        monotone_constraints=mono_tuple,
        random_state=42,
        eval_metric='logloss',
        n_jobs=-1
    )

    t_train_start = time.time()
    xgb_model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=50
    )
    t_train_end = time.time()
    print(f"   -> Навчання завершено за {t_train_end - t_train_start:.2f} сек.")

    # 3. Оцінка метрик якості на тестовій вибірці
    print("\n3. Оцінка метрик точності на тестовій вибірці (50,736 пацієнтів):")
    y_probs = xgb_model.predict_proba(X_test)[:, 1]
    
    roc_auc = roc_auc_score(y_test, y_probs)
    pr_auc = average_precision_score(y_test, y_probs)
    
    # Визначення оптимального клінічного порогу за критерієм Юдена
    fpr, tpr, thresholds = roc_curve(y_test, y_probs)
    youden_idx = np.argmax(tpr - fpr)
    optimal_threshold = float(thresholds[youden_idx])
    
    # Стандартний поріг (0.5) та клінічний оптимізований поріг
    y_pred_std = (y_probs >= 0.50).astype(int)
    y_pred_opt = (y_probs >= optimal_threshold).astype(int)

    acc_std = accuracy_score(y_test, y_pred_std)
    bal_acc_opt = balanced_accuracy_score(y_test, y_pred_opt)

    print(f"   * ROC-AUC (дискримінаційна здатність): {roc_auc:.4f} ({roc_auc*100:.2f}%)")
    print(f"   * PR-AUC (точність для рідкісних подій): {pr_auc:.4f}")
    print(f"   * Загальна точність (Accuracy, поріг 0.5): {acc_std:.4f} ({acc_std*100:.2f}%)")
    print(f"   * Збалансована точність (Balanced Acc, поріг {optimal_threshold:.2f}): {bal_acc_opt:.4f} ({bal_acc_opt*100:.2f}%)")

    cm = confusion_matrix(y_test, y_pred_opt)
    print(f"\n   Матриця невідповідностей (Confusion Matrix при порозі {optimal_threshold:.2f}):")
    print(f"   [[TN={cm[0,0]}, FP={cm[0,1]}],")
    print(f"    [FN={cm[1,0]}, TP={cm[1,1]}]]")

    # 4. Збереження навченої моделі
    print("\n4. Збереження моделі в директорію models/...")
    joblib_path = os.path.join(models_dir, "best_heart_disease_xgb.joblib")
    json_path = os.path.join(models_dir, "best_heart_disease_xgb.json")
    metrics_path = os.path.join(models_dir, "model_metrics.json")

    joblib.dump(xgb_model, joblib_path)
    xgb_model.save_model(json_path)

    metrics_data = {
        "model_name": "XGBoost (Extreme Gradient Boosting)",
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "accuracy": round(float(acc_std), 4),
        "balanced_accuracy": round(float(bal_acc_opt), 4),
        "optimal_threshold": round(float(optimal_threshold), 4),
        "total_train_samples": int(len(X_train)),
        "total_test_samples": int(len(X_test)),
        "features": list(X_train.columns)
    }

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, ensure_ascii=False, indent=2)

    print(f"   -> Модель збережено: {joblib_path}")
    print(f"   -> Нативний бустер:  {json_path}")
    print(f"   -> Метрики збережено: {metrics_path}")
    print("\n" + "=" * 70)
    print("НАВЧАННЯ УСПІШНО ЗАВЕРШЕНО!")
    print("=" * 70)

if __name__ == "__main__":
    main()
