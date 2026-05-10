import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ========================== НАСТРОЙКА СТРАНИЦЫ ==========================
st.set_page_config(
    page_title="Цифровая история назначений",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================== CSS ДЛЯ ПРОФЕССИОНАЛЬНОГО МЕДИЦИНСКОГО ИНТЕРФЕЙСА ==========================
st.markdown("""
<style>
    /* ОСНОВНЫЕ ЦВЕТА */
    .stApp {
        background-color: #F7F9FC;
    }
    /* Все тексты по умолчанию тёмные */
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, label, .stTextInput label, .stSelectbox label {
        color: #1F2A3E !important;
        background-color: #F7F9FC;
    }
    /* Карточки */
    .card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #E8ECF0;
    }
    .card-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1F2A3E;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3B82F6;
        display: inline-block;
    }
    /* Метрики */
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1F2A3E;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6C757D;
    }
    /* Кнопки */
    .stButton button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
    }
    .stButton button:hover {
        background-color: #2563EB !important;
    }
    /* Таблицы */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th {
        background-color: #F0F2F5;
        color: #1F2A3E;
        padding: 0.75rem;
        text-align: left;
    }
    td {
        padding: 0.75rem;
        border-bottom: 1px solid #E8ECF0;
        color: #1F2A3E;
    }
    /* Чекбоксы */
    .stCheckbox label {
        color: #1F2A3E !important;
    }
    /* Радио-кнопки */
    .stRadio label {
        color: #1F2A3E !important;
    }
    /* Инпуты */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1F2A3E !important;
        border: 1px solid #D1D9E8 !important;
        border-radius: 8px !important;
    }
    /* Заголовки */
    h1, h2, h3, h4, h5, h6 {
        color: #1F2A3E !important;
    }
    /* Разделители */
    hr {
        margin: 1rem 0;
        border-color: #E8ECF0;
    }
</style>
""", unsafe_allow_html=True)

# ========================== ДАННЫЕ ДЛЯ ДЕМОНСТРАЦИИ ==========================
def get_health_data():
    dates = [(datetime.now() - timedelta(days=i)).strftime("%d.%m") for i in range(7, -1, -1)]
    systolic = [118, 120, 122, 125, 119, 121, 118, 117]
    diastolic = [76, 78, 79, 81, 77, 78, 76, 75]
    pulse = [72, 74, 73, 75, 72, 73, 71, 70]
    temperature = [36.6, 36.5, 36.7, 36.6, 36.4, 36.6, 36.5, 36.6]
    return dates, systolic, diastolic, pulse, temperature

def get_medications():
    return [
        {"name": "Энап", "dosage": "5 мг", "form": "таблетки", "quantity": 60, "time": "08:00, 13:05", "food": "За 15 мин до еды", "start": "06.07.2020", "end": "15.07.2020", "reason": "Повышенное артериальное давление", "special": "Измерять пульс и АД"},
        {"name": "Аспирин Кардио", "dosage": "300 мг", "form": "таблетки кишечнорастворимые", "quantity": 20, "time": "17:16", "food": "Не указано", "start": "06.07.2020", "end": "15.07.2020", "reason": "Профилактика тромбозов", "special": "Не принимать натощак"}
    ]

def get_recommendations():
    return {
        "Питание": ["Ограничить соль", "Больше овощей", "Пить 1.5-2 л воды"],
        "Физические нагрузки": ["Ходьба 30 мин/день", "ЛФК по рекомендации"],
        "Ограничения": ["Алкоголь", "Курение", "Острые блюда"],
        "Прием препаратов": ["Ежедневно в одно время", "Не пропускать"],
        "Диагностика": ["ЭКГ 1 раз в месяц", "Анализ крови"]
    }

def get_migraine_questions():
    return {
        "headache": "Была ли у Вас сегодня головная боль?",
        "aura": "Были ли зрительные нарушения (вспышка, слепые пятна)?",
        "location": "Где болела голова?",
        "character": "Какой был характер боли?",
        "physical": "Усиливалась ли боль при физической нагрузке?"
    }

# ========================== СТРАНИЦА ПАЦИЕНТА (полный функционал) ==========================
def patient_dashboard():
    st.markdown('<div class="logo-title">Цифровая история назначений</div>', unsafe_allow_html=True)
    
    # Верхнее меню
    tabs = st.tabs(["Главная", "Мои назначения", "Дневник здоровья", "Дневник мигрени", "Рекомендации"])
    
    # ========== ВКЛАДКА 1: ГЛАВНАЯ ==========
    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card"><div class="card-header">Сегодня, {}</div>'.format(datetime.now().strftime("%d.%m.%Y")), unsafe_allow_html=True)
            for med in get_medications():
                st.markdown(f"""
                <div style="background:#FFFFFF; padding:1rem; border-radius:12px; margin-bottom:0.8rem; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                    <div style="font-weight:600;">{med['name']}, {med['dosage']}, {med['form']}, {med['quantity']} шт.</div>
                    <div style="font-size:0.85rem; color:#6C757D;">Требуется рецепт</div>
                    <label style="display:flex; align-items:center; margin-top:0.5rem;">
                        <input type="checkbox"> <span style="margin-left:0.5rem;">Купить лекарство со скидкой</span>
                    </label>
                    <div style="margin-top:0.5rem;"><a href="#" style="color:#3B82F6;">Информация о препарате</a></div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card"><div class="card-header">График выполнения</div>', unsafe_allow_html=True)
            st.markdown("Ежедневно в 08:00, 13:05")
            st.markdown("За 0 час(а) 15 минут(ы) до приема пищи")
            st.markdown("**Дата начала:** 06.07.2020")
            st.markdown("**Дата окончания:** 15.07.2020")
            st.markdown("**Причина:** Повышенное артериальное давление")
            st.markdown("**Особые указания:** Измерять пульс и АД")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ВКЛАДКА 2: МОИ НАЗНАЧЕНИЯ ==========
    with tabs[1]:
        st.markdown('<div class="card"><div class="card-header">Активные назначения</div>', unsafe_allow_html=True)
        for med in get_medications():
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"**{med['name']}** {med['dosage']} – {med['time']}")
                st.caption(f"{med['form']}, {med['quantity']} шт.")
            with col2:
                done = st.checkbox("Выполнено", key=med['name'])
            st.divider()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ВКЛАДКА 3: ДНЕВНИК ЗДОРОВЬЯ ==========
    with tabs[2]:
        st.markdown('<div class="card"><div class="card-header">Контроль показателей при приёме препаратов</div>', unsafe_allow_html=True)
        st.markdown("### Дневник здоровья")
        st.markdown("Отмечайте изменения, следите за динамикой вашего здоровья")
        
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.markdown('<div class="metric-card"><div class="metric-value">📊</div><div class="metric-label">Давление</div></div>', unsafe_allow_html=True)
        with metric_cols[1]:
            st.markdown('<div class="metric-card"><div class="metric-value">❤️</div><div class="metric-label">Пульс</div></div>', unsafe_allow_html=True)
        with metric_cols[2]:
            st.markdown('<div class="metric-card"><div class="metric-value">🌡️</div><div class="metric-label">Температура</div></div>', unsafe_allow_html=True)
        
        dates, systolic, diastolic, pulse, temperature = get_health_data()
        
        # График давления
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=systolic, mode='lines+markers', name='Систолическое', line=dict(color='#EF4444', width=2)))
        fig.add_trace(go.Scatter(x=dates, y=diastolic, mode='lines+markers', name='Диастолическое', line=dict(color='#3B82F6', width=2)))
        fig.update_layout(title="Артериальное давление", xaxis_title="Дата", yaxis_title="мм рт. ст.", height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        # График пульса и температуры
        col1, col2 = st.columns(2)
        with col1:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=dates, y=pulse, mode='lines+markers', name='Пульс', line=dict(color='#10B981', width=2)))
            fig2.update_layout(title="Пульс (уд/мин)", height=300, template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=dates, y=temperature, mode='lines+markers', name='Температура', line=dict(color='#F59E0B', width=2)))
            fig3.update_layout(title="Температура тела", height=300, template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("**История показаний** – 28 марта 2020")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ВКЛАДКА 4: ДНЕВНИК МИГРЕНИ ==========
    with tabs[3]:
        st.markdown('<div class="card"><div class="card-header">Дневник мигрени</div>', unsafe_allow_html=True)
        
        if st.button("Связаться с врачом", key="contact_doctor"):
            st.info("Запрос отправлен. Врач свяжется с вами в ближайшее время.")
        
        st.markdown("**30.12.2020 - 12.01.2021**")
        st.divider()
        
        # Вопросы дневника мигрени
        headache = st.radio("Была ли у Вас сегодня головная боль?", ["Нет", "Да"])
        if headache == "Да":
            aura = st.radio("Были ли в течение часа до боли зрительные нарушения (вспышка, искажение, слепые пятна)?", ["Нет", "Да"])
            location = st.selectbox("Где болела голова?", ["В затылке", "В виске", "В лобной части", "Глаза", "Вся голова"])
            character = st.selectbox("Какой был характер боли?", ["Тупая, двусторонняя", "Пульсирующая", "Сжимающая", "Острая"])
            physical = st.radio("Усиливалась ли боль при физической нагрузке?", ["Нет", "Да"])
            st.success("Данные сохранены. В этом месяце 7 эпизодов (+5,7 к предыдущему)")
            
        st.markdown("""
        <div style="background:#FFFFFF; border-radius:12px; padding:1rem; margin-top:1rem;">
            <div style="font-weight:600;">Светлая</div>
            <div>После бессонницы сделал ЭКГ</div>
            <img src="https://via.placeholder.com/100x100?text=QR" width="100">
            <div>spargo.ru</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ВКЛАДКА 5: РЕКОМЕНДАЦИИ ==========
    with tabs[4]:
        st.markdown('<div class="card"><div class="card-header">Рекомендации</div>', unsafe_allow_html=True)
        
        rec_cats = ["Все", "Питание", "Физические нагрузки", "Ограничения", "Прием препаратов", "Диагностика"]
        selected_cat = st.radio("Категории:", rec_cats, horizontal=True)
        
        if selected_cat == "Все":
            for cat, items in get_recommendations().items():
                st.markdown(f"**{cat}**")
                for item in items:
                    st.markdown(f"- {item}")
                st.divider()
        else:
            items = get_recommendations().get(selected_cat, [])
            for item in items:
                st.markdown(f"- {item}")
        
        st.markdown("### Особые указания")
        st.info("Измерять пульс и артериальное давление ежедневно. При отклонениях - обратиться к врачу.")
        st.markdown('</div>', unsafe_allow_html=True)

# ========================== СТРАНИЦА ВРАЧА ==========================
def doctor_dashboard():
    st.markdown('<div class="logo-title">Цифровая история назначений - Врач</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown('<div class="card"><div class="card-header">Пациенты</div>', unsafe_allow_html=True)
        patients = ["Иванов И.И.", "Петров П.П.", "Сидоров С.С."]
        for p in patients:
            if st.button(p, use_container_width=True):
                st.session_state.selected_patient = p
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.get('selected_patient'):
            st.markdown(f'<div class="card"><div class="card-header">{st.session_state.selected_patient}</div>', unsafe_allow_html=True)
            st.markdown("**Активные назначения:**")
            for med in get_medications():
                st.checkbox(f"{med['name']} {med['dosage']} – {med['time']}")
            st.markdown("**История болезни:**")
            st.write("Гипертоническая болезнь, риск 3. Назначен Энап и Аспирин Кардио.")
            st.markdown("**Рекомендации:**")
            for cat, items in get_recommendations().items():
                st.markdown(f"- {cat}: {', '.join(items)}")
            st.markdown('</div>', unsafe_allow_html=True)

# ========================== СТРАНИЦА ФАРМАЦЕВТА ==========================
def pharmacist_dashboard():
    st.markdown('<div class="logo-title">Цифровая история назначений - Фармацевт</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('<div class="card"><div class="card-header">Проверка рецепта</div>', unsafe_allow_html=True)
    rx_id = st.text_input("Введите номер рецепта")
    if st.button("Найти рецепт"):
        st.markdown("""
        <div style="background:#FFFFFF; border-radius:12px; padding:1rem;">
            <div><strong>Рецепт №12345</strong></div>
            <div>Пациент: Иванов И.И.</div>
            <div>Препараты: Энап 5 мг, Аспирин Кардио 300 мг</div>
            <div>Статус: <span style="color:#22C55E;">Действителен</span></div>
            <label><input type="checkbox"> Подтвердить отпуск</label>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== ВХОД ==========================
def login_page():
    st.markdown('<div class="logo-title">Цифровая история назначений</div>', unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Вход в систему")
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        role = st.selectbox("Роль", ["patient", "doctor", "pharmacist"])
        if st.button("Войти", use_container_width=True):
            st.session_state['authenticated'] = True
            st.session_state['role'] = role
            st.session_state['user'] = {"username": username, "role": role}
            st.rerun()
        st.caption("Тестовые учётки: любой логин/пароль")
        st.markdown('</div>', unsafe_allow_html=True)

# ========================== ГЛАВНЫЙ МАРШРУТИЗАТОР ==========================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state.authenticated:
    login_page()
else:
    if st.session_state.get('role') == 'doctor':
        doctor_dashboard()
    elif st.session_state.get('role') == 'pharmacist':
        pharmacist_dashboard()
    else:
        patient_dashboard()
