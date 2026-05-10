"""
ГЛАВНОЕ ПРИЛОЖЕНИЕ - УПРОЩЁННАЯ ВЕРСИЯ БЕЗ МОДУЛЕЙ
Цифровая система управления историей лекарственных назначений
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# ============================================================================
# ЦВЕТОВАЯ ПАЛИТРА
# ============================================================================

COLORS = {
    "primary": "#3B82F6",
    "accent": "#4FD1C5",
    "bg_light": "#F7FAFC",
    "bg_white": "#FFFFFF",
    "error": "#EF4444",
    "warning": "#F59E0B",
    "success": "#22C55E",
    "text_dark": "#1F2937",
    "text_light": "#6B7280",
}

# ============================================================================
# КОНФИГУРАЦИЯ STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="💊 Цифровая история лекарственных назначений",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Применяем кастомные стили
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ SESSION STATE
# ============================================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "current_patient" not in st.session_state:
    st.session_state.current_patient = None
if "current_prescription" not in st.session_state:
    st.session_state.current_prescription = None
if "patients_db" not in st.session_state:
    st.session_state.patients_db = None

# Кэшируем БД пациентов
if st.session_state.patients_db is None:
    st.session_state.patients_db = generate_patients_database()

patients_db = st.session_state.patients_db

# ============================================================================
# СТРАНИЦА ВХОДА
# ============================================================================

def page_login():
    """Экран аутентификации"""
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; margin: 3rem 0; padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">💊</div>
            <h1 style="margin: 0; color: {COLORS['primary']};">
                MediScript Pro
            </h1>
            <div style="font-size: 1.2rem; color: {COLORS['text_medium']}; margin: 1rem 0 3rem 0;">
                Цифровая история лекарственных назначений
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Форма входа
        st.markdown("### 🔐 Вход в систему")
        
        username = st.text_input("Имя пользователя", placeholder="doctor1, pharmacist1, patient1...")
        password = st.text_input("Пароль", type="password", placeholder="Введите пароль")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Вход", use_container_width=True, type="primary"):
                success, user_data, error = authenticate_user(username, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data
                    st.session_state.page = f"{user_data['role']}_dashboard"
                    st.rerun()
                else:
                    st.error(f"❌ {error}")
        
        with col2:
            if st.button("👤 Выбрать роль", use_container_width=True):
                st.session_state.page = "role_selection"
                st.rerun()
        
        st.divider()
        
        # Демо данные
        st.markdown("### 📋 Демо учетные данные")
        
        with st.expander("Показать демо аккаунты"):
            credentials = get_demo_credentials()
            
            for role in ["doctor", "pharmacist", "patient"]:
                if credentials[role]:
                    st.markdown(f"**{role.upper()}:**")
                    for cred in credentials[role]:
                        st.code(f"Пользователь: {cred['username']}\nПароль: {cred['password']}")

def page_role_selection():
    """Выбор роли для MVP"""
    
    render_header_with_subtitle(
        "Выберите вашу роль",
        "Выберите роль для демонстрации системы",
        "👥"
    )
    
    col1, col2, col3 = st.columns(3)
    
    roles = [
        {
            "role": "doctor",
            "title": "Врач",
            "icon": "👨‍⚕️",
            "description": "Создание и анализ рецептов, проверка взаимодействий",
            "col": col1
        },
        {
            "role": "pharmacist",
            "title": "Фармацевт",
            "icon": "💊",
            "description": "Проверка рецептов, отпуск лекарств",
            "col": col2
        },
        {
            "role": "patient",
            "title": "Пациент",
            "icon": "🧑‍⚕️",
            "description": "Просмотр истории лечения",
            "col": col3
        }
    ]
    
    for role_info in roles:
        with role_info["col"]:
            if st.button("", use_container_width=True, key=f"select_{role_info['role']}"):
                st.session_state.user = {
                    "role": role_info["role"],
                    "name": f"Демо {role_info['title']}",
                }
                st.session_state.page = f"{role_info['role']}_dashboard"
                st.rerun()
            
            st.markdown(f"""
            <div class="role-card">
                <div class="role-icon">{role_info['icon']}</div>
                <div class="role-title">{role_info['title']}</div>
                <div class="role-description">{role_info['description']}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# ДАШБОРД ВРАЧА
# ============================================================================

def page_doctor_dashboard():
    """Дашборд врача"""
    
    col1, col2, col3, col4 = st.columns([0.7, 0.1, 0.1, 0.1])
    with col1:
        st.markdown(f"## 👨‍⚕️ Дашборд врача")
    with col4:
        if st.button("🚪 Выход"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()
    
    st.divider()
    
    # МЕТРИКИ
    col1, col2, col3, col4 = st.columns(4)
    
    high_risk_count = len(get_high_risk_patients(patients_db))
    
    with col1:
        render_metric_card("Пациентов в системе", str(len(patients_db)), "👥", "primary")
    with col2:
        render_metric_card("Высокого риска", str(high_risk_count), "⚠️", "warning")
    with col3:
        render_metric_card("Рецептов сегодня", "12", "📝", "success")
    with col4:
        render_metric_card("Требуют внимания", "3", "🔴", "error")
    
    st.divider()
    
    # ДВЕ КОЛОНКИ
    col1, col2 = st.columns([0.5, 0.5])
    
    with col1:
        st.markdown("### 🔍 Поиск пациента")
        
        search_query = st.text_input("Введите ФИО или ID пациента", "")
        
        if search_query:
            found_patients = search_patients(patients_db, search_query)
            
            if found_patients:
                patient_options = [
                    f"{p['last_name']} {p['first_name']} ({p['age']} л.) - {p['id']}"
                    for p in found_patients
                ]
                selected_patient_str = st.selectbox("Выберите пациента:", patient_options)
                
                selected_idx = patient_options.index(selected_patient_str)
                st.session_state.current_patient = found_patients[selected_idx]
    
    with col2:
        if st.session_state.current_patient:
            patient = st.session_state.current_patient
            st.markdown(f"""
            <div class="card">
                <h3>Информация о пациенте</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div><strong>ФИО:</strong><br/>{patient['last_name']} {patient['first_name']}</div>
                    <div><strong>Возраст:</strong><br/>{patient['age']} лет ({patient['gender']})</div>
                    <div><strong>ID:</strong><br/>{patient['id']}</div>
                    <div><strong>Крeatinin:</strong><br/>{patient['creatinine']} мг/дл</div>
                    <div><strong>Диагноз:</strong><br/>{patient['diagnosis'][0] if patient['diagnosis'] else 'Не указан'}</div>
                    <div><strong>Аллергии:</strong><br/>{patient['allergies'] or 'Нет'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # НАЗНАЧЕНИЕ ПРЕПАРАТОВ
    if st.session_state.current_patient:
        st.markdown("### 💊 Назначение препаратов")
        
        col1, col2 = st.columns([0.5, 0.5])
        
        with col1:
            # Показываем текущие препараты
            st.markdown("**Текущие назначения:**")
            render_medication_table(st.session_state.current_patient['medications'])
        
        with col2:
            st.markdown("**Добавить новые препараты:**")
            
            from modules.database import MEDICATIONS_CATALOG
            
            num_new = st.number_input("Количество новых препаратов:", 1, 5, 1)
            
            new_meds = []
            for i in range(num_new):
                col_med, col_dose = st.columns([0.6, 0.4])
                
                with col_med:
                    med_name = st.selectbox(
                        f"Препарат {i+1}",
                        [m["name"] for m in MEDICATIONS_CATALOG],
                        key=f"new_med_{i}"
                    )
                
                with col_dose:
                    med = next((m for m in MEDICATIONS_CATALOG if m["name"] == med_name), None)
                    dose = st.text_input(
                        "Доза",
                        med["typical_dosage"] if med else "",
                        key=f"new_dose_{i}"
                    )
                
                new_meds.append({
                    "name": med_name,
                    "group": med["group"] if med else "",
                    "dosage": dose,
                    "frequency": "1 раз в день",
                    "duration": "1 месяц",
                    "notes": med["notes"] if med else ""
                })
        
        st.divider()
        
        # АНАЛИЗ РЕЦЕПТА
        if st.button("🔍 Выписать и проанализировать рецепт", type="primary", use_container_width=True):
            
            # Объединяем текущие и новые лекарства
            all_meds = st.session_state.current_patient['medications'] + new_meds
            
            # Анализируем
            analysis = analyze_prescription_comprehensive(
                st.session_state.current_patient,
                all_meds
            )
            
            st.session_state.current_prescription = {
                "patient": st.session_state.current_patient,
                "medications": all_meds,
                "analysis": analysis
            }
            
            st.session_state.page = "prescription_detailed"
            st.rerun()

# ============================================================================
# СТРАНИЦА АНАЛИЗА РЕЦЕПТА
# ============================================================================

def page_prescription_detailed():
    """Детальная страница анализа рецепта"""
    
    if not st.session_state.current_prescription:
        st.error("Нет данных для анализа")
        return
    
    rx = st.session_state.current_prescription
    patient = rx["patient"]
    medications = rx["medications"]
    analysis = rx["analysis"]
    
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown(f"## 📊 Анализ рецепта")
    with col2:
        if st.button("◀️ Назад"):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
    
    st.divider()
    
    # ИНФОРМАЦИЯ О РЕЦЕПТЕ
    st.markdown(f"""
    <div class="card">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div><strong>Пациент:</strong> {patient['last_name']} {patient['first_name']}</div>
            <div><strong>ID рецепта:</strong> RX-{datetime.now().strftime('%Y%m%d%H%M%S')}</div>
            <div><strong>Дата:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ОБЩИЙ РИСК
    risk_level = analysis["overall_risk_level"]
    risk_colors = {
        "low": ("🟢 НИЗКИЙ РИСК", "#D1FAE5", "#065F46"),
        "medium": ("🟡 СРЕДНИЙ РИСК", "#FEF3C7", "#92400E"),
        "high": ("🟠 ВЫСОКИЙ РИСК", "#FECACA", "#7C2D12"),
        "critical": ("🔴 КРИТИЧЕСКИЙ РИСК", "#FEE2E2", "#991B1B"),
    }
    
    risk_label, risk_bg, risk_text = risk_colors[risk_level]
    
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: {risk_bg}; 
                    border: 2px solid {risk_text}; border-radius: 12px; color: {risk_text};">
            <div style="font-size: 1.5rem; font-weight: 700;">{risk_label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ТАБЛИЦА ПРЕПАРАТОВ
    st.markdown("### 💊 Назначенные препараты")
    render_medication_table(medications)
    
    st.divider()
    
    # АНАЛИЗ ПОЛИПРАГМАЗИИ
    poly = analysis["polypharmacy"]
    st.markdown(f"### 📈 Анализ полипрагмазии")
    
    col1, col2 = st.columns([0.3, 0.7])
    
    with col1:
        render_metric_card(
            "Препаратов",
            str(poly["num_medications"]),
            "💊",
            poly["overall_risk"]
        )
    
    with col2:
        render_alert(
            f"{poly['base_description']} (Риск: {poly['risk_score']}/10)",
            poly["base_description"],
            poly["overall_risk"]
        )
    
    if poly.get("complexity_issues"):
        with st.expander("📋 Детали анализа полипрагмазии"):
            for issue in poly["complexity_issues"]:
                st.markdown(f"- {issue}")
    
    st.divider()
    
    # ВЗАИМОДЕЙСТВИЯ
    interactions = analysis["interactions"]
    st.markdown(f"### ⚡ Лекарственные взаимодействия ({len(interactions)} найдено)")
    
    if interactions:
        for interaction in interactions:
            render_interaction_card(
                interaction["drug1"],
                interaction["drug2"],
                interaction["severity"],
                interaction.get("mechanism", ""),
                interaction.get("recommendation", "")
            )
    else:
        render_alert(
            "✅ Взаимодействия не выявлены",
            "Комбинация препаратов безопасна для сочетанного применения",
            "success"
        )
    
    st.divider()
    
    # РЕКОМЕНДАЦИИ
    if analysis["recommendations"]:
        st.markdown("### 💡 Рекомендации")
        for rec in analysis["recommendations"][:5]:
            st.markdown(f"- {rec}")
    
    st.divider()
    
    # КНОПКИ
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("◀️ Редактировать", use_container_width=True):
            st.session_state.page = "doctor_dashboard"
            st.rerun()
    
    with col2:
        if st.button("💾 Выписать", type="primary", use_container_width=True):
            render_alert(
                "✅ Рецепт успешно выписан",
                f"ID: RX-{datetime.now().strftime('%Y%m%d%H%M%S')}\n"
                f"Отправлен в аптеку {patient['last_name']} {patient['first_name']}",
                "success",
                "✅"
            )
            st.balloons()
    
    with col3:
        if st.button("🚪 Завершить", use_container_width=True):
            st.session_state.current_prescription = None
            st.session_state.page = "doctor_dashboard"
            st.rerun()

# ============================================================================
# ДАШБОРД ФАРМАЦЕВТА
# ============================================================================

def page_pharmacist_dashboard():
    """Дашборд фармацевта"""
    
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown(f"## 💊 Дашборд фармацевта")
    with col2:
        if st.button("🚪 Выход", key="logout_pharm"):
            st.session_state.page = "login"
            st.rerun()
    
    st.divider()
    
    # МЕТРИКИ
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("В очереди", "8", "📋", "warning")
    with col2:
        render_metric_card("Обработано", "23", "✅", "success")
    with col3:
        render_metric_card("Требуют внимания", "2", "⚠️", "error")
    with col4:
        render_metric_card("На складе", "156", "📦", "primary")
    
    st.divider()
    
    st.markdown("### 📝 Очередь рецептов для проверки")
    
    # Генерируем примеры рецептов
    queue_data = []
    for i in range(8):
        queue_data.append({
            "ID": f"RX-202603{12+i}-{1001+i}",
            "Пациент": f"{patients_db[i]['last_name']} {patients_db[i]['first_name']}",
            "Препаратов": len(patients_db[i]['medications']),
            "Риск": ["НИЗКИЙ", "СРЕДНИЙ", "ВЫСОКИЙ"][min(i // 3, 2)],
            "Статус": "⏳ На проверке" if i < 3 else "🕐 Ожидает"
        })
    
    df_queue = pd.DataFrame(queue_data)
    st.dataframe(df_queue, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # АНАЛИЗ ЗАПАСОВ
    st.markdown("### 📦 Анализ запасов препаратов")
    
    from modules.database import MEDICATIONS_CATALOG
    
    stock_data = []
    for med in MEDICATIONS_CATALOG[:10]:
        stock_data.append({
            "Препарат": med["name"],
            "В наличии": f"{random.randint(10, 200)} шт",
            "Цена": f"{random.randint(50, 500)} руб",
            "Статус": ["✅ Достаточно", "⚠️ Маловато"][random.randint(0, 1)]
        })
    
    df_stock = pd.DataFrame(stock_data)
    st.dataframe(df_stock, use_container_width=True, hide_index=True)

# ============================================================================
# ДАШБОРД ПАЦИЕНТА
# ============================================================================

def page_patient_dashboard():
    """Дашборд пациента"""
    
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown(f"## 🧑‍⚕️ Мой кабинет пациента")
    with col2:
        if st.button("🚪 Выход", key="logout_patient"):
            st.session_state.page = "login"
            st.rerun()
    
    st.divider()
    
    # ИНФО О ПАЦИЕНТЕ
    st.markdown("""
    <div class="card">
        <h3>👤 Моя информация</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div><strong>ФИО:</strong> Иванов И.И.</div>
            <div><strong>Возраст:</strong> 65 лет</div>
            <div><strong>ID пациента:</strong> PAT-2026-00001</div>
            <div><strong>Врач:</strong> Петров П.И.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # АКТИВНЫЕ НАЗНАЧЕНИЯ
    st.markdown("### 💊 Мои активные назначения")
    
    meds_example = [
        {"name": "Метопролол", "dosage": "50 мг", "frequency": "1 раз в день"},
        {"name": "Амлодипин", "dosage": "5 мг", "frequency": "1 раз в день"},
        {"name": "Омепразол", "dosage": "20 мг", "frequency": "1 раз в день"},
    ]
    
    render_medication_table(meds_example)
    
    st.divider()
    
    # ГРАФИКИ
    st.markdown("### 📊 История лечения")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card("Рецептов", "24", "📋", "primary")
    with col2:
        render_metric_card("Врачей", "5", "👨‍⚕️", "accent")
    with col3:
        render_metric_card("Препаратов", "18", "💊", "success")
    
    # График рецептов
    fig = go.Figure()
    
    months = ["Янв", "Фев", "Март", "Апр", "Май", "Июнь"]
    counts = [4, 3, 5, 4, 6, 5]
    
    fig.add_trace(go.Bar(
        x=months,
        y=counts,
        marker=dict(color=COLORS["primary"]),
        text=counts,
        textposition="auto"
    ))
    
    fig.update_layout(
        title="Динамика назначений (6 месяцев)",
        xaxis_title="Месяц",
        yaxis_title="Количество рецептов",
        height=400,
        template="plotly_light",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# МАРШРУТИЗАТОР СТРАНИЦ
# ============================================================================

import random

if st.session_state.page == "login":
    page_login()
elif st.session_state.page == "role_selection":
    page_role_selection()
elif st.session_state.page == "doctor_dashboard":
    page_doctor_dashboard()
elif st.session_state.page == "prescription_detailed":
    page_prescription_detailed()
elif st.session_state.page == "pharmacist_dashboard":
    page_pharmacist_dashboard()
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
