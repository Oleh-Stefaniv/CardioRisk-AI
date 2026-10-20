import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_radial_gauge(prob, risk_color, risk_label, delta_total):
    """Create a precision semi-circular risk gauge (light theme)."""
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=prob * 100,
        number={
            'suffix': '%',
            'font': {'size': 44, 'family': 'Plus Jakarta Sans', 'color': '#1E293B', 'weight': 800}
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': '#94A3B8',
                'tickvals': [0, 10, 20, 35, 50, 75, 100],
                'ticktext': ['0%', '10%', '20%', '35%', '50%', '75%', '100%'],
                'tickfont': {'size': 10, 'color': '#64748B'}
            },
            'bar': {'color': risk_color, 'thickness': 0.28},
            'bgcolor': '#F1F5F9',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 10], 'color': '#DCFCE7'},
                {'range': [10, 20], 'color': '#FEF3C7'},
                {'range': [20, 35], 'color': '#FFEDD5'},
                {'range': [35, 100], 'color': '#FEE2E2'}
            ]
        }
    ))
    fig.update_layout(
        height=195,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif')
    )
    return fig


def calculate_radar_scores(input_row, is_clinical):
    """Map patient factors into 6 normalized health dimensions."""
    if not is_clinical:
        bp_score = 40.0 if input_row['HighBP'].iloc[0] == 1 else 95.0
        chol_score = 45.0 if input_row['HighChol'].iloc[0] == 1 else 95.0
        gluc_score = 40.0 if input_row['Diabetes'].iloc[0] == 1 else 95.0
        bmi = float(input_row['BMI'].iloc[0])
        if bmi < 25.0: bmi_score = 95.0
        elif bmi < 27.5: bmi_score = 75.0
        elif bmi < 30.0: bmi_score = 60.0
        else: bmi_score = 35.0
        act_score = 95.0 if input_row['PhysActivity'].iloc[0] == 1 else 40.0
        life_score = 95.0
        if input_row['Smoker'].iloc[0] == 1: life_score -= 35.0
        if input_row['Alcohol'].iloc[0] == 1: life_score -= 25.0
    else:
        sbp = float(input_row['ap_hi'].iloc[0])
        dbp = float(input_row['ap_lo'].iloc[0])
        if sbp < 120 and dbp < 80: bp_score = 98.0
        elif sbp < 130 and dbp < 85: bp_score = 85.0
        elif sbp < 140 and dbp < 90: bp_score = 65.0
        else: bp_score = 35.0

        ldl = float(input_row['ldl_chol'].iloc[0])
        if ldl < 1.8: chol_score = 98.0
        elif ldl < 2.6: chol_score = 80.0
        elif ldl < 3.0: chol_score = 60.0
        else: chol_score = 35.0

        glu = float(input_row['glucose_fasting'].iloc[0])
        hba = float(input_row['hba1c'].iloc[0])
        if glu < 5.6 and hba < 5.7: gluc_score = 98.0
        elif glu < 6.5 and hba < 6.0: gluc_score = 70.0
        else: gluc_score = 35.0

        bmi = float(input_row['BMI'].iloc[0])
        if bmi < 25.0: bmi_score = 95.0
        elif bmi < 27.5: bmi_score = 75.0
        elif bmi < 30.0: bmi_score = 60.0
        else: bmi_score = 35.0

        act = float(input_row['physical_activity'].iloc[0])
        act_score = 95.0 if act == 1 else 40.0

        cigs = float(input_row['cigs_per_day'].iloc[0])
        alco = float(input_row['alcohol_status'].iloc[0])
        life_score = 95.0
        if cigs > 0: life_score -= min(40.0, 15.0 + cigs)
        if alco == 1: life_score -= 25.0

    return [max(15.0, min(100.0, s)) for s in [bp_score, chol_score, gluc_score, bmi_score, act_score, life_score]]


def create_radar_chart(scores):
    """Create a 6-axis radar chart comparing patient vs ESC target (light theme)."""
    categories = [
        'Артеріальний тиск',
        'Ліпідний статус',
        'Глікемія',
        'Маса тіла (ІМТ)',
        'Рухова активність',
        'Спосіб життя'
    ]
    fig = go.Figure()

    # Target Safe Zone (100% ideal)
    fig.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100, 100, 100],
        theta=categories,
        fill='toself',
        name='Цільова норма (ESC)',
        line=dict(color='#10B981', width=1.5, dash='dot'),
        fillcolor='rgba(16, 185, 129, 0.08)'
    ))

    avg_score = sum(scores) / len(scores)
    patient_color = '#059669' if avg_score >= 80 else ('#D97706' if avg_score >= 60 else '#DC2626')
    fill_rgba = 'rgba(5, 150, 105, 0.15)' if avg_score >= 80 else ('rgba(217, 119, 6, 0.15)' if avg_score >= 60 else 'rgba(220, 38, 38, 0.15)')

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Профіль пацієнта',
        line=dict(color=patient_color, width=2.5),
        fillcolor=fill_rgba
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9, color='#94A3B8'),
                gridcolor='#E2E8F0'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color='#475569', family='Plus Jakarta Sans'),
                linecolor='#CBD5E1',
                gridcolor='#E2E8F0'
            ),
            bgcolor='#FFFFFF'
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.22,
            xanchor='center',
            x=0.5,
            font=dict(size=11, color='#64748B')
        ),
        height=320,
        margin=dict(l=45, r=45, t=25, b=35),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif')
    )
    return fig


def create_whatif_comparison_chart(prob, sim_new_prob):
    """Create dual before/after gauges with delta (light theme)."""
    p_orig = prob * 100
    p_sim = sim_new_prob * 100
    p_diff = p_orig - p_sim
    rel_diff = (p_diff / p_orig * 100) if p_orig > 0 else 0

    sim_clr = "#059669" if sim_new_prob < 0.18 else ("#D97706" if sim_new_prob < 0.35 else "#DC2626")
    orig_clr = "#059669" if prob < 0.18 else ("#D97706" if prob < 0.35 else "#DC2626")

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        column_widths=[0.5, 0.5]
    )

    fig.add_trace(
        go.Indicator(
            mode='gauge+number',
            value=p_orig,
            title={'text': 'Вихідний ризик', 'font': {'size': 13, 'color': '#64748B', 'family': 'Plus Jakarta Sans'}},
            number={'suffix': '%', 'font': {'size': 32, 'color': orig_clr, 'weight': 800}},
            gauge={
                'axis': {'range': [0, 100], 'tickvals': [0, 20, 50, 100], 'tickfont': {'size': 9, 'color': '#94A3B8'}},
                'bar': {'color': orig_clr, 'thickness': 0.3},
                'bgcolor': '#F1F5F9',
                'borderwidth': 0
            }
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Indicator(
            mode='gauge+number+delta',
            value=p_sim,
            title={'text': 'Модифікований ризик', 'font': {'size': 13, 'color': '#64748B', 'family': 'Plus Jakarta Sans'}},
            delta={
                'reference': p_orig,
                'valueformat': '.1f',
                'suffix': '%',
                'decreasing': {'color': '#059669'},
                'increasing': {'color': '#DC2626'},
                'font': {'size': 13, 'weight': 700}
            },
            number={'suffix': '%', 'font': {'size': 32, 'color': sim_clr, 'weight': 800}},
            gauge={
                'axis': {'range': [0, 100], 'tickvals': [0, 20, 50, 100], 'tickfont': {'size': 9, 'color': '#94A3B8'}},
                'bar': {'color': sim_clr, 'thickness': 0.3},
                'bgcolor': '#F1F5F9',
                'borderwidth': 0
            }
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=185,
        margin=dict(l=15, r=15, t=25, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, sans-serif')
    )
    return fig, p_diff, rel_diff
