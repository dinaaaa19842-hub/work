import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
import hashlib

# ============================================================================
# КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ
# ============================================================================

st.set_page_config(
    page_title="Цифровая история лекарственных назначений",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ПАЛИТРА ЦВЕТОВ (из ТЗ, адаптирована)
# ============================================================================

COLORS = {
    "primary": "#3B82F6",           # Медицинский синий
    "accent": "#4FD1C5",            # Неоновый голубой
    "bg_light": "#F7FAFC",          # Светлый фон
    "bg_white": "#FFFFFF",          # Белый
    "error": "#EF4444",             # Красный
    "warning": "#F59E0B",           # Жёлтый
    "success": "#22C55E",           # Зелёный
    "text_dark": "#1F2937",         # Тёмный текст
    "text_light": "#6B7280",        # Светлый текст
    "border": "#E5E7EB",            # Граница
}

# ============================================================================
# КАСТОМНЫЕ СТИЛИ
# ============================================================================

CUSTOM_CSS = f"""
<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {COLORS["bg_light"]};
    }}
    
    [data-testid="stMainBlockContainer"] {{
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS["text_dark"]};
        font-weight: 700;
        letter-spacing: -0.5px;
    }}
    
    h1 {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }}
    
    h2 {{
        font-size: 2rem;
        margin-bottom: 1.5rem;
    }}
    
    h3 {{
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }}
    
    .metric-card {{
        background: {COLORS["bg_white"]};
        border-radius: 16px;
        padding: 1.5rem;
        border-left: 5px solid {COLORS["primary"]};
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        border-left-color: {COLORS["accent"]};
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {COLORS["primary"]};
        margin-bottom: 0.5rem;
    }}
    
    .metric-label {{
        font-size: 0.95rem;
        color: {COLORS["text_light"]};
        font-weight: 500;
    }}
    
    .status-badge {{
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.5rem 0.5rem 0 0;
    }}
    
    .status-low {{
        background-color: #D1FAE5;
        color: #065F46;
    }}
    
    .status-medium {{
        background-color: #FEF3C7;
        color: #92400E;
    }}
    
    .status-high {{
        background-color: #FEE2E2;
        color: #991B1B;
    }}
    
    .warning-box {{
        background-color: #FEF3C7;
        border: 2px solid {COLORS["warning"]};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #92400E;
    }}
    
    .error-box {{
        background-color: #FEE2E2;
        border: 2px solid {COLORS["error"]};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #991B1B;
    }}
    
    .success-box {{
        background-color: #D1FAE5;
        border: 2px solid {COLORS["success"]};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #065F46;
    }}
    
    .info-box {{
        background-color: #DBEAFE;
        border: 2px solid {COLORS["primary"]};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #1E40AF;
    }}
    
    .card {{
        background: {COLORS["bg_white"]};
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1.5rem;
        border: 1px solid {COLORS["border"]};
        transition: all 0.3s ease;
    }}
    
    .card:hover {{
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        border-color: {COLORS["accent"]};
    }}
    
    .btn-primary {{
        background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["accent"]} 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1rem;
    }}
    
    .btn-primary:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }}
    
    .divider {{
        height: 1px;
        background: {COLORS["border"]};
        margin: 2rem 0;
    }}
    
    .role-card {{
        background: {COLORS["bg_white"]};
        border: 2px solid {COLORS["border"]};
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 1rem;
    }}
    
    .role-card:hover {{
        border-color: {COLORS["accent"]};
        background: linear-gradient(135deg, rgba(79,209,197,0.05) 0%, rgba(59,130,246,0.05) 100%);
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }}
    
    .role-icon {{
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }}
    
    .role-title {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLORS["text_dark"]};
        margin-bottom: 0.5rem;
    }}
    
    .role-description {{
        font-size: 0.95rem;
        color: {COLORS["text_light"]};
    }}
    
    table {{
        width: 100%;
        border-collapse: collapse;
    }}
    
    th {{
        background-color: {COLORS["bg_light"]};
        color: {COLORS["text_dark"]};
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid {COLORS["primary"]};
    }}
    
    td {{
        padding: 1rem;
        border-bottom: 1px solid {COLORS["border"]};
    }}
    
    tr:hover {{
        background-color: rgba(79,209,197,0.05);
    }}
    
    .header-title {{
        color: {COLORS["primary"]};
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }}
    
    .header-subtitle {{
        color: {COLORS["text_light"]};
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
    }}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ SESSION STATE
# ============================================================================

if "page" not in st.session_state:
    st.session_state.page = "role_selection"
if "role" not in st.session_state:
    st.session_state.role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "current_patient" not in st.session_state:
    st.session_state.current_patient = None
if "current_prescription" not in st.session_state:
    st.session_state.current_prescription = None
if "prescriptions_history" not in st.session_state:
    st.session_state.prescriptions_history = []

# ============================================================================
# БАЗА ДАННЫХ ЛЕКАРСТВЕННЫХ ВЗАИМОДЕЙСТВИЙ
# ============================================================================

DRUG_INTERACTIONS = {
    ("Аспирин", "Варфарин"): {
        "severity": "critical",
        "description": "Опасное взаимодействие - повышение риска кровотечения",
        "recommendation": "Требуется осторожность и мониторинг"
    },
    ("Ибупрофен", "Варфарин"): {
        "severity": "high",
        "description": "Опасное взаимодействие - усиление антикоагулянтного эффекта",
        "recommendation": "Рассмотрите альтернативные препараты"
    },
    ("Метформин", "Контрастное вещество"): {
        "severity": "high",
        "description": "Риск острой почечной недостаточности",
        "recommendation": "Отменить за 48 часов до процедуры"
    },
    ("Аспирин", "Ибупрофен"): {
        "severity": "medium",
        "description": "Усиление побочных эффектов со стороны ЖКТ",
        "recommendation": "Избегать одновременного приема"
    },
    ("Амиодарон", "Бета-блокаторы"): {
        "severity": "medium",
        "description": "Риск брадикардии и нарушений проводимости",
        "recommendation": "Требуется контроль ЭКГ"
    },
    ("Симвастатин", "Эритромицин"): {
        "severity": "medium",
        "description": "Повышение риска рабдомиолиза",
        "recommendation": "Снизить дозу статина или выбрать другой"
    }
}

# ============================================================================
# БАЗА ДАННЫХ ЛЕКАРСТВ
# ============================================================================

MEDICATIONS_DB = [
    {"name": "Аспирин", "group": "НПВС", "indication": "Боль, воспаление"},
    {"name": "Ибупрофен", "group": "НПВС", "indication": "Боль, жар"},
    {"name": "Парацетамол", "group": "Анальгетик", "indication": "Боль, жар"},
    {"name": "Варфарин", "group": "Антикоагулянт", "indication": "Тромбоз"},
    {"name": "Метопролол", "group": "Бета-блокатор", "indication": "АГ, аритмия"},
    {"name": "Амлодипин", "group": "Антагонист кальция", "indication": "АГ, стенокардия"},
    {"name": "Эналаприл", "group": "АПФ ингибитор", "indication": "АГ, СН"},
    {"name": "Аторвастатин", "group": "Статин", "indication": "Гиперхолестеринемия"},
    {"name": "Омепразол", "group": "ППИ", "indication": "ГЭРБ, язва"},
    {"name": "Амиодарон", "group": "Антиаритмик", "indication": "Аритмия"},
    {"name": "Метформин", "group": "Бигуанид", "indication": "Сахарный диабет"},
    {"name": "Глибенкламид", "group": "Сульфонилмочевина", "indication": "Сахарный диабет"},
    {"name": "Фуросемид", "group": "Диуретик", "indication": "Отеки, АГ"},
    {"name": "Спиронолактон", "group": "Диуретик", "indication": "СН, АГ"},
    {"name": "Прокаинамид", "group": "Антиаритмик", "indication": "Аритмия"},
]

# ============================================================================
# ГЕНЕРАЦИЯ ПРИМЕРОВ ПАЦИЕНТОВ
# ============================================================================

@st.cache_resource
def generate_patients_db() -> List[Dict]:
    """Генерирует 50+ примеров пациентов с реальными данными"""
    
    first_names = ["Иван", "Петр", "Сергей", "Анна", "Мария", "Елена", "Ольга", "Юлия",
                   "Наталья", "Александр", "Виктор", "Дмитрий", "Павел", "Андрей", "Владимир"]
    last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Волков", "Морозов",
                  "Орлов", "Павлов", "Федоров", "Степанов", "Александров", "Никитин", "Соколов"]
    
    diagnoses = ["Гипертоническая болезнь", "Ишемическая болезнь сердца", "Сахарный диабет",
                 "Фибрилляция предсердий", "ГЭРБ", "Остеоартроз", "Остеопороз", "Депрессия",
                 "Тромбоз глубоких вен", "Стенокардия", "Инфаркт миокарда в анамнезе"]
    
    allergies = [
        None, 
        "Пенициллин",
        "Аспирин",
        "Сульфаниламиды",
        "Йод",
        "Аллергия на морепродукты",
        "Лактоза"
    ]
    
    patients = []
    for i in range(55):
        age = random.randint(35, 85)
        gender = random.choice(["М", "Ж"])
        
        # Выбираем препараты в зависимости от возраста и диагнозов
        num_medications = random.randint(1, 6)
        medications = random.sample(MEDICATIONS_DB, min(num_medications, len(MEDICATIONS_DB)))
        
        patient = {
            "id": f"PAT-2026-{i+1:05d}",
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "age": age,
            "gender": gender,
            "diagnosis": random.choice(diagnoses),
            "allergies": random.choice(allergies),
            "medications": [
                {
                    "name": med["name"],
                    "dosage": f"{random.randint(1, 3)} таб.",
                    "frequency": random.choice(["1 раз в день", "2 раза в день", "3 раза в день"]),
                    "duration": f"{random.randint(1, 12)} месяцев"
                }
                for med in medications
            ],
            "created_at": datetime.now() - timedelta(days=random.randint(1, 365))
        }
        patients.append(patient)
    
    return patients

# ============================================================================
# АНАЛИЗ ВЗАИМОДЕЙСТВИЙ И РИСКОВ
# ============================================================================

def check_drug_interactions(medications: List[Dict]) -> Dict:
    """Проверяет взаимодействия между лекарствами"""
    
    drug_names = [med["name"] for med in medications]
    interactions = []
    
    for i, drug1 in enumerate(drug_names):
        for drug2 in drug_names[i+1:]:
            # Проверяем оба порядка
            key1 = (drug1, drug2)
            key2 = (drug2, drug1)
            
            if key1 in DRUG_INTERACTIONS:
                interactions.append({
                    "drug1": drug1,
                    "drug2": drug2,
                    **DRUG_INTERACTIONS[key1]
                })
            elif key2 in DRUG_INTERACTIONS:
                interactions.append({
                    "drug1": drug1,
                    "drug2": drug2,
                    **DRUG_INTERACTIONS[key2]
                })
    
    return {"interactions": interactions, "count": len(interactions)}

def detect_polypharmacy(medications: List[Dict]) -> Dict:
    """Выявляет полипрагмазию (5+ препаратов)"""
    
    num_meds = len(medications)
    
    if num_meds >= 10:
        risk_level = "critical"
        description = "Критическая полипрагмазия - очень высокий риск побочных эффектов"
    elif num_meds >= 7:
        risk_level = "high"
        description = "Высокая полипрагмазия - требуется проверка назначений"
    elif num_meds >= 5:
        risk_level = "medium"
        description = "Полипрагмазия - требуется дополнительное внимание"
    else:
        risk_level = "low"
        description = "Количество препаратов в норме"
    
    return {
        "count": num_meds,
        "risk_level": risk_level,
        "description": description
    }

def analyze_prescription(patient: Dict) -> Dict:
    """Комплексный анализ рецепта"""
    
    medications = patient["medications"]
    
    # Проверка взаимодействий
    interactions = check_drug_interactions(medications)
    
    # Проверка полипрагмазии
    polypharmacy = detect_polypharmacy(medications)
    
    # Определение общего уровня риска
    max_interaction_severity = "low"
    for interaction in interactions["interactions"]:
        if interaction["severity"] == "critical":
            max_interaction_severity = "critical"
            break
        elif interaction["severity"] == "high" and max_interaction_severity != "critical":
            max_interaction_severity = "high"
        elif interaction["severity"] == "medium" and max_interaction_severity == "low":
            max_interaction_severity = "medium"
    
    # Объединяем риски
    if max_interaction_severity == "critical" or polypharmacy["risk_level"] in ["critical", "high"]:
        overall_risk = "high"
    elif max_interaction_severity == "high" or polypharmacy["risk_level"] == "medium":
        overall_risk = "medium"
    else:
        overall_risk = "low"
    
    return {
        "overall_risk": overall_risk,
        "interactions": interactions,
        "polypharmacy": polypharmacy,
        "analysis_date": datetime.now()
    }

# ============================================================================
# UI КОМПОНЕНТЫ
# ============================================================================

def render_metric_card(label: str, value: str, icon: str = "", color: str = "primary"):
    """Отображает карточку метрики"""
    color_hex = COLORS[color] if color in COLORS else color
    
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {color_hex};">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value" style="color: {color_hex};">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_status_badge(status: str) -> str:
    """Возвращает HTML для статус-бейджа"""
    
    status_map = {
        "low": ("LOW RISK", "status-low"),
        "medium": ("MEDIUM RISK", "status-medium"),
        "high": ("HIGH RISK", "status-high"),
        "critical": ("CRITICAL", "status-high")
    }
    
    text, css_class = status_map.get(status.lower(), ("UNKNOWN", "status-medium"))
    return f'<span class="status-badge {css_class}">{text}</span>'

def render_warning_card(title: str, description: str, severity: str = "warning"):
    """Отображает карточку предупреждения"""
    
    css_class = f"{severity}-box"
    icon_map = {
        "warning": "⚠️",
        "error": "🚨",
        "success": "✅",
        "info": "ℹ️"
    }
    icon = icon_map.get(severity, "ℹ️")
    
    st.markdown(f"""
    <div class="{css_class}">
        <div style="font-weight: 700; margin-bottom: 0.5rem; font-size: 1.1rem;">
            {icon} {title}
        </div>
        <div>{description}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# СТРАНИЦЫ ПРИЛОЖЕНИЯ
# ============================================================================

def page_role_selection():
    """Экран выбора роли (MVP)"""
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <div class="header-title">💊 Цифровая история лекарственных назначений</div>
        <div class="header-subtitle">Выберите вашу роль в системе</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("", use_container_width=True, key="btn_doctor"):
            st.session_state.page = "doctor_dashboard"
            st.session_state.role = "doctor"
            st.rerun()
        
        st.markdown(f"""
        <div class="role-card">
            <div class="role-icon">👨‍⚕️</div>
            <div class="role-title">Врач</div>
            <div class="role-description">Создание и анализ рецептов, проверка взаимодействий препаратов</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("", use_container_width=True, key="btn_pharmacist"):
            st.session_state.page = "pharmacist_dashboard"
            st.session_state.role = "pharmacist"
            st.rerun()
        
        st.markdown(f"""
        <div class="role-card">
            <div class="role-icon">💊</div>
            <div class="role-title">Фармацевт</div>
            <div class="role-description">Проверка рецептов, подтверждение отпуска лекарств</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("", use_container_width=True, key="btn_patient"):
            st.session_state.page = "patient_dashboard"
            st.session_state.role = "patient"
            st.rerun()
        
        st.markdown(f"""
        <div class="role-card">
            <div class="role-icon">🧑‍🤝‍🧑</div>
            <div class="role-title">Пациент</div>
            <div class="role-description">Просмотр истории лечения и активных назначений</div>
        </div>
        """, unsafe_allow_html=True)

def page_doctor_dashboard():
    """Дашборд врача"""
    
    # Получаем БД пациентов
    patients_db = generate_patients_db()
    
    # Верхняя часть - заголовок с выходом
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("## 👨‍⚕️ Дашборд врача")
    with col2:
        if st.button("🚪 Выход"):
            st.session_state.page = "role_selection"
            st.session_state.role = None
            st.rerun()
    
    st.divider()
    
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Активные пациенты", str(len(patients_db)), "👥", "primary")
    
    with col2:
        high_risk_count = sum(1 for p in patients_db if len(p["medications"]) >= 5)
        render_metric_card("Пациентов высокого риска", str(high_risk_count), "⚠️", "warning")
    
    with col3:
        render_metric_card("Рецептов сегодня", "12", "📝", "success")
    
    with col4:
        render_metric_card("Требуют внимания", "3", "🔴", "error")
    
    st.divider()
    
    # Создание нового рецепта
    st.markdown("### ➕ Создание нового рецепта")
    
    col1, col2 = st.columns([0.5, 0.5])
    
    with col1:
        patient_search = st.text_input("🔍 Поиск пациента по ФИО или ID", "")
        
        # Фильтруем пациентов
        filtered_patients = [
            p for p in patients_db
            if patient_search.lower() in f"{p['last_name']} {p['first_name']} {p['id']}".lower()
        ]
        
        if filtered_patients:
            patient_options = [
                f"{p['last_name']} {p['first_name']} ({p['age']} л.) - {p['id']}"
                for p in filtered_patients
            ]
            selected_patient_str = st.selectbox("Выберите пациента:", patient_options)
            
            # Находим выбранного пациента
            selected_idx = patient_options.index(selected_patient_str)
            st.session_state.current_patient = filtered_patients[selected_idx]
    
    # Если пациент выбран - показываем его информацию
    if st.session_state.current_patient:
        st.markdown(f"""
        <div class="card">
            <h3>Информация о пациенте</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div><strong>ФИО:</strong> {st.session_state.current_patient['last_name']} {st.session_state.current_patient['first_name']}</div>
                <div><strong>Возраст:</strong> {st.session_state.current_patient['age']} лет</div>
                <div><strong>Пол:</strong> {st.session_state.current_patient['gender']}</div>
                <div><strong>ID пациента:</strong> {st.session_state.current_patient['id']}</div>
                <div><strong>Диагноз:</strong> {st.session_state.current_patient['diagnosis']}</div>
                <div><strong>Аллергии:</strong> {st.session_state.current_patient['allergies'] or 'Нет данных'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Добавление препаратов
        st.markdown("### 💊 Назначение препаратов")
        
        num_medications = st.number_input("Количество препаратов:", 1, 10, 
                                         len(st.session_state.current_patient.get('new_medications', [])) or 1)
        
        if 'new_medications' not in st.session_state:
            st.session_state.new_medications = []
        
        new_medications = []
        for i in range(num_medications):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                med_name = st.selectbox(
                    f"Препарат {i+1}",
                    [m["name"] for m in MEDICATIONS_DB],
                    key=f"med_{i}"
                )
            
            with col2:
                dosage = st.text_input(f"Дозировка {i+1}", "1 таб.", key=f"dose_{i}")
            
            with col3:
                frequency = st.selectbox(
                    f"Частота {i+1}",
                    ["1 раз в день", "2 раза в день", "3 раза в день"],
                    key=f"freq_{i}"
                )
            
            new_medications.append({
                "name": med_name,
                "dosage": dosage,
                "frequency": frequency,
                "duration": "1 месяц"
            })
        
        st.session_state.new_medications = new_medications
        
        # Кнопка проверки рецепта
        if st.button("🔍 Проверить рецепт", type="primary", use_container_width=True):
            
            # Создаем временный пациент с новыми лекарствами
            temp_patient = st.session_state.current_patient.copy()
            temp_patient["medications"] = new_medications
            
            # Анализируем рецепт
            analysis = analyze_prescription(temp_patient)
            
            st.session_state.current_prescription = {
                "patient": st.session_state.current_patient,
                "medications": new_medications,
                "analysis": analysis,
                "created_at": datetime.now()
            }
            
            st.session_state.page = "prescription_analysis"
            st.rerun()

def page_prescription_analysis():
    """Страница анализа рецепта (врач)"""
    
    if not st.session_state.current_prescription:
        st.warning("Нет данных для анализа")
        return
    
    rx = st.session_state.current_prescription
    patient = rx["patient"]
    medications = rx["medications"]
    analysis = rx["analysis"]
    
    # Заголовок
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("## 📊 Анализ рецепта")
    with col2:
        if st.button("◀️ Назад"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
    
    st.divider()
    
    # Информация о пациенте
    st.markdown(f"**Пациент:** {patient['last_name']} {patient['first_name']} ({patient['age']} л.)")
    st.markdown(f"**ID рецепта:** RX-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}")
    
    st.divider()
    
    # Общая оценка риска
    st.markdown("### ⚠️ Общая оценка риска")
    
    risk_level = analysis["overall_risk"]
    risk_colors = {
        "low": "#22C55E",
        "medium": "#F59E0B",
        "high": "#EF4444"
    }
    risk_labels = {
        "low": "НИЗКИЙ РИСК",
        "medium": "СРЕДНИЙ РИСК",
        "high": "ВЫСОКИЙ РИСК"
    }
    
    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: {risk_colors[risk_level]}20; 
                    border: 2px solid {risk_colors[risk_level]}; border-radius: 12px;">
            <div style="font-size: 2rem; font-weight: 700; color: {risk_colors[risk_level]};">
                {risk_labels[risk_level]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Блок полипрагмазии
    polypharmacy = analysis["polypharmacy"]
    st.markdown("### 💊 Анализ полипрагмазии")
    
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        render_metric_card("Количество препаратов", str(polypharmacy["count"]), "💊", polypharmacy["risk_level"])
    with col2:
        severity_colors = {
            "low": "success",
            "medium": "warning",
            "high": "error",
            "critical": "error"
        }
        render_warning_card(
            "Полипрагмазия",
            polypharmacy["description"],
            severity_colors[polypharmacy["risk_level"]]
        )
    
    st.divider()
    
    # Блок взаимодействий
    interactions = analysis["interactions"]["interactions"]
    st.markdown(f"### ⚡ Взаимодействия препаратов ({len(interactions)} найдено)")
    
    if interactions:
        for interaction in interactions:
            severity = interaction["severity"]
            severity_colors = {
                "critical": "error",
                "high": "warning",
                "medium": "info"
            }
            severity_icons = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "ℹ️"
            }
            
            render_warning_card(
                f"{severity_icons[severity]} {interaction['drug1']} + {interaction['drug2']}",
                f"{interaction['description']}\n\n**Рекомендация:** {interaction['recommendation']}",
                severity_colors[severity]
            )
    else:
        render_warning_card(
            "✅ Взаимодействия не найдены",
            "Комбинация препаратов безопасна",
            "success"
        )
    
    st.divider()
    
    # Таблица назначений
    st.markdown("### 📋 Назначенные препараты")
    
    df_medications = pd.DataFrame([
        {
            "№": i+1,
            "Препарат": med["name"],
            "Дозировка": med["dosage"],
            "Частота": med["frequency"],
            "Длительность": med["duration"]
        }
        for i, med in enumerate(medications)
    ])
    
    st.dataframe(df_medications, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Кнопки действий
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("◀️ Вернуться к редактированию", use_container_width=True):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
    
    with col2:
        if st.button("💾 Сохранить рецепт", type="primary", use_container_width=True):
            st.session_state.prescriptions_history.append(st.session_state.current_prescription)
            st.success("✅ Рецепт успешно сохранен!")
            st.balloons()
            
            # QR-код
            st.markdown("### 📱 QR-код рецепта")
            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <div style="font-size: 4rem; margin: 2rem 0;">
                    ██████████<br>
                    ██░░░░░░██<br>
                    ██░░░░░░██<br>
                    ██░░░░░░██<br>
                    ██████████
                </div>
                <div style="font-weight: 600; margin: 1rem 0;">Рецепт: RX-{datetime.now().strftime('%Y%m%d%H%M%S')}</div>
                <div style="color: #6B7280;">Пациент: {patient['last_name']} {patient['first_name']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Завершить", use_container_width=True):
            st.session_state.page = "doctor_dashboard"
            st.session_state.current_prescription = None
            st.rerun()

def page_pharmacist_dashboard():
    """Дашборд фармацевта"""
    
    patients_db = generate_patients_db()
    
    # Верхняя часть
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("## 💊 Дашборд фармацевта")
    with col2:
        if st.button("🚪 Выход", key="logout_pharmacist"):
            st.session_state.page = "role_selection"
            st.session_state.role = None
            st.rerun()
    
    st.divider()
    
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Рецептов в очереди", "8", "📋", "warning")
    
    with col2:
        render_metric_card("Обработано сегодня", "23", "✅", "success")
    
    with col3:
        render_metric_card("С высоким риском", "2", "🚨", "error")
    
    with col4:
        render_metric_card("На складе", "156", "📦", "primary")
    
    st.divider()
    
    # Поиск рецепта
    st.markdown("### 🔍 Проверка рецепта")
    
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        search_type = st.radio("Способ поиска:", ["По номеру рецепта", "По пациенту"], 
                               horizontal=True, label_visibility="collapsed")
        
        if search_type == "По номеру рецепта":
            prescription_id = st.text_input("Введите номер рецепта (RX-...)")
        else:
            patient_search = st.text_input("Введите ФИО или ID пациента")
    
    # История рецептов в очереди
    st.markdown("### 📋 Рецепты в очереди на проверку")
    
    # Генерируем примеры рецептов в очереди
    queue_prescriptions = []
    for i, patient in enumerate(patients_db[:8]):
        queue_prescriptions.append({
            "ID": f"RX-{datetime.now().strftime('%Y%m%d')}-{1000+i}",
            "Пациент": f"{patient['last_name']} {patient['first_name']}",
            "Возраст": f"{patient['age']} л.",
            "Препараты": len(patient["medications"]),
            "Риск": random.choice(["НИЗКИЙ", "СРЕДНИЙ", "ВЫСОКИЙ"]),
            "Статус": random.choice(["Ожидает", "На проверке"])
        })
    
    df_queue = pd.DataFrame(queue_prescriptions)
    
    # Раскраска в зависимости от риска
    def highlight_risk(val):
        if val == "ВЫСОКИЙ":
            return "background-color: #FEE2E2; color: #991B1B;"
        elif val == "СРЕДНИЙ":
            return "background-color: #FEF3C7; color: #92400E;"
        else:
            return "background-color: #D1FAE5; color: #065F46;"
    
    st.dataframe(
        df_queue.style.applymap(lambda x: highlight_risk(x) if x in ["ВЫСОКИЙ", "СРЕДНИЙ", "НИЗКИЙ"] else ""),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Выбор рецепта для проверки
    st.markdown("### ✅ Проверка и подтверждение")
    
    selected_rx = st.selectbox("Выберите рецепт:", 
                               [rx["ID"] + " - " + rx["Пациент"] for rx in queue_prescriptions])
    
    if selected_rx:
        if st.button("📂 Открыть рецепт", type="primary", use_container_width=True):
            st.session_state.page = "pharmacist_check"
            st.rerun()

def page_pharmacist_check():
    """Страница проверки рецепта фармацевтом"""
    
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("## ✅ Проверка рецепта")
    with col2:
        if st.button("◀️ Назад"):
            st.session_state.page = "pharmacist_dashboard"
            st.rerun()
    
    st.divider()
    
    # Пример рецепта
    st.markdown("### Информация о рецепте")
    st.markdown("""
    <div class="card">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div><strong>ID рецепта:</strong> RX-20260312-1001</div>
            <div><strong>Дата выписания:</strong> 12.03.2026</div>
            <div><strong>Врач:</strong> Петров И.И.</div>
            <div><strong>Клиника:</strong> МЦ "Здоровье"</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Данные пациента")
    st.markdown("""
    <div class="card">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div><strong>ФИО:</strong> Иванов И.И.</div>
            <div><strong>Возраст:</strong> 65 лет</div>
            <div><strong>Диагноз:</strong> Гипертоническая болезнь</div>
            <div><strong>Аллергии:</strong> Пенициллин</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 💊 Назначенные препараты")
    
    medications_data = [
        {"Препарат": "Метопролол", "Дозировка": "50 мг", "Частота": "1 раз в день"},
        {"Препарат": "Амлодипин", "Дозировка": "5 мг", "Частота": "1 раз в день"},
        {"Препарат": "Омепразол", "Дозировка": "20 мг", "Частота": "1 раз в день"}
    ]
    
    df_meds = pd.DataFrame(medications_data)
    st.dataframe(df_meds, use_container_width=True, hide_index=True)
    
    st.divider()
    
    st.markdown("### ✅ Проверка безопасности")
    
    render_warning_card(
        "✅ Взаимодействия не найдены",
        "Комбинация препаратов безопасна",
        "success"
    )
    
    st.markdown("### 📦 Наличие в аптеке")
    
    availability = [
        {"Препарат": "Метопролол", "В наличии": "✅ Да (45 шт.)", "Цена": "120 руб."},
        {"Препарат": "Амлодипин", "В наличии": "✅ Да (32 шт.)", "Цена": "180 руб."},
        {"Препарат": "Омепразол", "В наличии": "✅ Да (58 шт.)", "Цена": "95 руб."}
    ]
    
    df_avail = pd.DataFrame(availability)
    st.dataframe(df_avail, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Кнопки
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Отклонить рецепт", use_container_width=True):
            st.error("❌ Рецепт отклонен. Причина отправлена врачу.")
            st.session_state.page = "pharmacist_dashboard"
            st.rerun()
    
    with col2:
        if st.button("✅ Подтвердить отпуск", type="primary", use_container_width=True):
            st.success("✅ Лекарства успешно отпущены пациенту!")
            st.balloons()
            st.session_state.page = "pharmacist_dashboard"
            st.rerun()

def page_patient_dashboard():
    """Дашборд пациента"""
    
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("## 🧑‍⚕️ Мой кабинет пациента")
    with col2:
        if st.button("🚪 Выход", key="logout_patient"):
            st.session_state.page = "role_selection"
            st.session_state.role = None
            st.rerun()
    
    st.divider()
    
    # Информация о пациенте
    st.markdown("### 👤 Моя информация")
    st.markdown("""
    <div class="card">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div><strong>ФИО:</strong> Иванов И.И.</div>
            <div><strong>Возраст:</strong> 65 лет</div>
            <div><strong>ID пациента:</strong> PAT-2026-00015</div>
            <div><strong>Страховка:</strong> Полис № 1234567890</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Активные назначения
    st.markdown("### 💊 Мои активные назначения")
    
    active_meds = [
        {"Препарат": "Метопролол", "Дозировка": "50 мг", "Частота": "1 раз в день", "Назначено": "12.02.2026"},
        {"Препарат": "Амлодипин", "Дозировка": "5 мг", "Частота": "1 раз в день", "Назначено": "12.02.2026"},
        {"Препарат": "Омепразол", "Дозировка": "20 мг", "Частота": "1 раз в день", "Назначено": "01.03.2026"}
    ]
    
    df_active = pd.DataFrame(active_meds)
    st.dataframe(df_active, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # История лечения
    st.markdown("### 📚 История лечения")
    
    tabs = st.tabs(["Последние рецепты", "Статистика", "Графики"])
    
    with tabs[0]:
        history_data = [
            {"Дата": "12.03.2026", "Врач": "Петров И.И.", "Препараты": 3, "Статус": "✅ Выполнен"},
            {"Дата": "01.03.2026", "Врач": "Волков В.В.", "Препараты": 2, "Статус": "✅ Выполнен"},
            {"Дата": "15.02.2026", "Врач": "Сидоров С.С.", "Препараты": 4, "Статус": "✅ Выполнен"},
        ]
        
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
    
    with tabs[1]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            render_metric_card("Всего рецептов", "24", "📋", "primary")
        with col2:
            render_metric_card("Врачей", "5", "👨‍⚕️", "accent")
        with col3:
            render_metric_card("Препаратов", "18", "💊", "success")
    
    with tabs[2]:
        # График частоты назначений
        fig = go.Figure()
        
        months = ["Янв", "Фев", "Март", "Апр"]
        prescriptions = [4, 3, 5, 4]
        
        fig.add_trace(go.Bar(
            x=months,
            y=prescriptions,
            marker=dict(color=COLORS["primary"]),
            name="Рецепты"
        ))
        
        fig.update_layout(
            title="Динамика назначений",
            xaxis_title="Месяц",
            yaxis_title="Количество",
            height=400,
            template="plotly_light",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Предупреждения и рекомендации
    st.markdown("### ⚠️ Рекомендации")
    
    render_warning_card(
        "ℹ️ Правильный прием лекарств",
        "Принимайте препараты в одно и то же время каждый день. "
        "Если пропустили прием, не удваивайте дозу в следующий раз.",
        "info"
    )

# ============================================================================
# ГЛАВНЫЙ МАРШРУТИЗАТОР
# ============================================================================

if st.session_state.page == "role_selection":
    page_role_selection()
elif st.session_state.page == "doctor_dashboard":
    page_doctor_dashboard()
elif st.session_state.page == "prescription_analysis":
    page_prescription_analysis()
elif st.session_state.page == "pharmacist_dashboard":
    page_pharmacist_dashboard()
elif st.session_state.page == "pharmacist_check":
    page_pharmacist_check()
elif st.session_state.page == "patient_dashboard":
    page_patient_dashboard()

# ============================================================================
# ФУТЕР
# ============================================================================

st.divider()
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: {COLORS['text_light']}; font-size: 0.9rem;">
    <p>💊 Цифровая история лекарственных назначений</p>
    <p>© 2026 • Магистерская диссертация • Все права защищены</p>
</div>
""", unsafe_allow_html=True)
