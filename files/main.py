import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import hashlib
import qrcode
from io import BytesIO
import base64
import random

# ========================== НАСТРОЙКА СТРАНИЦЫ ==========================
st.set_page_config(page_title="Цифровая история назначений", page_icon="", layout="wide", initial_sidebar_state="collapsed")

# ========================== CSS (МЕДИЦИНСКИЙ ТЁМНО-СИНИЙ СТИЛЬ) ==========================
st.markdown("""
<style>
    .stApp { background-color: #F0F4FA !important; }
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, label, .stCaption {
        color: #1F2A3E !important; background-color: transparent !important;
    }
    h1, h2, h3, h4, h5, h6 { color: #0A2F6C !important; font-weight: 600; }
    .card { background-color: #FFFFFF; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; 
            box-shadow: 0 1px 2px rgba(0,0,0,0.05); border: 1px solid #DCE5F0; }
    .card-header { font-size: 1.3rem; font-weight: 700; color: #0A2F6C; margin-bottom: 1.5rem; 
                   padding-bottom: 0.8rem; border-bottom: 2px solid #0A2F6C; }
    
    /* Стили для полей ввода (логин, пароль) – без selectbox */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #1F2A3E !important;
        border: 1px solid #D1D9E8 !important;
        border-radius: 4px !important;
    }
    
    .stButton button { background-color: #0A2F6C !important; color: #FFFFFF !important; border-radius: 4px !important; 
                       border: none !important; font-weight: 500 !important; padding: 0.5rem 1rem !important; }
    .stButton button:hover { background-color: #1E3A8A !important; }
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #E6EDF6; color: #0A2F6C; padding: 0.8rem; text-align: left; font-weight: 600; border-bottom: 2px solid #0A2F6C; }
    td { padding: 0.8rem; border-bottom: 1px solid #DCE5F0; color: #1F2A3E; }
    .stTabs [data-baseweb="tab-list"] { background-color: #FFFFFF; border-bottom: 1px solid #DCE5F0; }
    .stTabs [data-baseweb="tab"] { color: #4B5563; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #0A2F6C !important; border-bottom-color: #0A2F6C !important; }
    .stTabs [data-baseweb="tab"] svg { display: none; }
    
    .breadcrumb { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; font-size: 0.9rem; color: #6B7280; }
    .breadcrumb span:last-child { color: #0A2F6C; font-weight: 600; }
    .user-info { font-size: 0.9rem; color: #4B5563; }
    .user-info strong { color: #0A2F6C; }
    
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #DCE5F0;
        margin-bottom: 1.5rem;
    }
    .app-header .logo {
        font-size: 1.4rem;
        font-weight: 600;
        color: #0A2F6C;
        font-family: 'Segoe UI', Roboto, system-ui;
    }
    .app-footer {
        margin-top: 2rem;
        padding: 1rem 0;
        border-top: 1px solid #DCE5F0;
        font-size: 0.85rem;
        color: #6B7280;
        text-align: left;
    }
    .login-header {
        margin-bottom: 8rem;
    }
</style>
""", unsafe_allow_html=True)

# ========================== БД ==========================
DB_NAME = "clinic.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("DROP TABLE IF EXISTS patients")
    c.execute("DROP TABLE IF EXISTS prescriptions")
    c.execute("DROP TABLE IF EXISTS messages")
    c.execute("DROP TABLE IF EXISTS intake_log")
    
    c.execute('''CREATE TABLE patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  last_name TEXT, first_name TEXT,
                  birth_date TEXT, policy TEXT, location TEXT,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE prescriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  patient_id INTEGER, 
                  drug_name TEXT,
                  dosage TEXT, 
                  regularity TEXT, 
                  start_date TEXT, 
                  end_date TEXT,
                  FOREIGN KEY(patient_id) REFERENCES patients(id))''')
    
    c.execute('''CREATE TABLE messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  patient_id INTEGER,
                  sender TEXT,
                  message TEXT,
                  timestamp TEXT,
                  FOREIGN KEY(patient_id) REFERENCES patients(id))''')
    
    c.execute('''CREATE TABLE intake_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  prescription_id INTEGER, 
                  intake_date TEXT,
                  FOREIGN KEY(prescription_id) REFERENCES prescriptions(id))''')
    
    conn.commit()
    
    # Тестовые данные (50+ пациентов)
    first_names_m = ["Иван", "Петр", "Сергей", "Александр", "Виктор", "Дмитрий", "Павел", "Андрей", "Владимир", "Николай", "Алексей", "Константин", "Валентин", "Игорь", "Анатолий", "Евгений", "Борис", "Вячеслав", "Валерий", "Юрий"]
    first_names_f = ["Анна", "Мария", "Елена", "Ольга", "Юлия", "Наталья", "Татьяна", "Галина", "Валентина", "Светлана", "Людмила", "Нина", "Раиса", "Вера", "Зинаида", "Маргарита", "Александра", "Ирина", "Виктория", "Екатерина"]
    
    last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Волков", "Морозов", "Орлов", "Павлов", "Федоров", "Степанов", "Александров", "Никитин", "Соколов", "Васильев", "Новиков", "Фомин", "Герасимов", "Лавров", "Панов", "Козлов", "Лобанов", "Раков", "Леонов", "Климов", "Миронов", "Эмелин", "Власов", "Гордеев", "Давыдов", "Егоров", "Ефимов", "Желтов", "Журавлев", "Ильин", "Казаков", "Калинин", "Карпов", "Кольцов", "Лебедев"]
    
    locations = ["Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск", "Пермь", "Челябинск", "Краснодар", "Самара", "Ростов-на-Дону"]
    
    drugs_list = [
        ("Энап", "5 мг"), ("Аспирин Кардио", "100 мг"), ("Метформин", "500 мг"), 
        ("Амлодипин", "5 мг"), ("Метопролол", "50 мг"), ("Аторвастатин", "20 мг"),
        ("Омепразол", "20 мг"), ("Варфарин", "2.5 мг"), ("Глюкофаж", "1000 мг"),
        ("Конкор", "2.5 мг"), ("Норваск", "5 мг"), ("Липримар", "10 мг"),
        ("Кордарон", "200 мг"), ("Ловастатин", "20 мг"), ("Дигоксин", "0.25 мг"),
        ("Вазопрессин", "10 ед"), ("Пропранолол", "40 мг"), ("Нифедипин", "10 мг"),
        ("Спиронолактон", "25 мг"), ("Фуросемид", "40 мг"), ("Диклофенак", "50 мг"),
        ("Ибупрофен", "200 мг"), ("Парацетамол", "500 мг"), ("Аспирин", "500 мг"),
    ]
    
    for i in range(50):
        gender = random.choice(["M", "F"])
        first_name = random.choice(first_names_m if gender == "M" else first_names_f)
        last_name = random.choice(last_names)
        birth_year = random.randint(1950, 2005)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"
        policy = f"{random.randint(1000000000, 9999999999)}"
        location = random.choice(locations)
        
        c.execute('''INSERT INTO patients (last_name, first_name, birth_date, policy, location, created_at) 
                    VALUES (?,?,?,?,?,?)''',
                 (last_name, first_name, birth_date, policy, location, datetime.now().isoformat()))
        
        pid = c.lastrowid
        
        num_drugs = random.randint(2, 5)
        selected_drugs = random.sample(drugs_list, num_drugs)
        
        for drug_name, dosage in selected_drugs:
            regularity = random.choice(["1 раз в день", "2 раза в день", "3 раза в день"])
            start_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            
            c.execute('''INSERT INTO prescriptions 
                       (patient_id, drug_name, dosage, regularity, start_date, end_date)
                       VALUES (?,?,?,?,?,?)''',
                     (pid, drug_name, dosage, regularity, start_date, end_date))
    
    conn.commit()
    conn.close()

init_db()

# ========================== ФУНКЦИИ БД ==========================
def get_all_patients(search_query="", birth_date_filter="", location_filter="", patient_id_filter=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    query = "SELECT id, last_name, first_name, birth_date, policy, location FROM patients WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (last_name LIKE ? OR first_name LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    
    if birth_date_filter:
        query += " AND birth_date = ?"
        params.append(birth_date_filter)
    
    if location_filter:
        query += " AND location LIKE ?"
        params.append(f"%{location_filter}%")
    
    if patient_id_filter:
        query += " AND id = ?"
        params.append(patient_id_filter)
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_patient_by_id(pid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT id, last_name, first_name, birth_date, policy, location FROM patients WHERE id=?", (pid,))
    patient = c.fetchone()
    
    if patient:
        c.execute("SELECT id, drug_name, dosage, regularity, start_date, end_date FROM prescriptions WHERE patient_id=?", (pid,))
        prescs = c.fetchall()
        conn.close()
        return patient, prescs
    
    conn.close()
    return None, []

def save_patient(pid, last_name, first_name, birth_date, policy, location, prescriptions_list):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("UPDATE patients SET last_name=?, first_name=?, birth_date=?, policy=?, location=? WHERE id=?",
             (last_name, first_name, birth_date, policy, location, pid))
    
    c.execute("DELETE FROM prescriptions WHERE patient_id=?", (pid,))
    
    for drug in prescriptions_list:
        c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage, regularity, start_date, end_date) VALUES (?,?,?,?,?,?)",
                 (pid, drug[0], drug[1], drug[2], "2026-05-01", "2026-06-01"))
    
    conn.commit()
    conn.close()

def add_new_patient(last_name, first_name, birth_date, policy, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO patients (last_name, first_name, birth_date, policy, location, created_at) VALUES (?,?,?,?,?,?)",
             (last_name, first_name, birth_date, policy, location, datetime.now().isoformat()))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def add_message(patient_id, sender, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (patient_id, sender, message, timestamp) VALUES (?,?,?,?)",
             (patient_id, sender, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_messages(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT sender, message, timestamp FROM messages WHERE patient_id=? ORDER BY timestamp ASC", (patient_id,))
    messages = c.fetchall()
    conn.close()
    return messages

def get_prescribed_count(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM prescriptions WHERE patient_id=?", (patient_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_all_prescriptions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT drug_name, dosage, regularity, start_date FROM prescriptions")
    data = c.fetchall()
    conn.close()
    return data

# ========================== КОМПОНЕНТЫ UI ==========================
def render_breadcrumb(path):
    breadcrumb_html = '<div class="breadcrumb">'
    for i, item in enumerate(path):
        if i == len(path) - 1:
            breadcrumb_html += f'<span>{item}</span>'
        else:
            breadcrumb_html += f'<span>{item}</span> > '
    breadcrumb_html += '</div>'
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

def render_top_bar(username, role):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown(f"<div class='user-info'>Добро пожаловать, <strong>{username}</strong> ({role.upper()})</div>", unsafe_allow_html=True)
    with col2:
        if st.button("ВЫХОД", use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state.clear()
            st.rerun()

def render_chat_panel(patient_id, current_user):
    st.subheader("Онлайн-чат")
    messages = get_messages(patient_id)
    for sender, msg, timestamp in messages:
        time_obj = datetime.fromisoformat(timestamp)
        time_str = time_obj.strftime("%H:%M")
        if sender == current_user:
            st.markdown(f"<div style='text-align: right; margin-bottom: 1rem;'><div style='display: inline-block; background-color: #0A2F6C; color: white; padding: 0.75rem; border-radius: 8px; max-width: 70%;'><div>{msg}</div><div style='font-size: 0.75rem; opacity: 0.7; margin-top: 0.25rem;'>{time_str}</div></div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: left; margin-bottom: 1rem;'><div style='display: inline-block; background-color: #F0F2F5; color: #1F2A3E; padding: 0.75rem; border-radius: 8px; max-width: 70%;'><div><strong>{sender}</strong></div><div>{msg}</div><div style='font-size: 0.75rem; opacity: 0.7; margin-top: 0.25rem;'>{time_str}</div></div></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        new_msg = st.text_input("Ваше сообщение:", key=f"msg_{patient_id}", label_visibility="collapsed")
    with col2:
        if st.button("Отправить", key=f"send_{patient_id}", use_container_width=True):
            if new_msg.strip():
                add_message(patient_id, st.session_state.get('user_name', 'Врач'), new_msg)
                st.rerun()

def render_footer():
    st.markdown('<div class="app-footer">Цифровая история назначений</div>', unsafe_allow_html=True)

# ========================== АНАЛИТИКА ПРЕПАРАТОВ ==========================
def drug_analytics_dashboard():
    render_breadcrumb(["Врач", "Аналитика", "Препараты"])
    
    st.markdown('<div class="card"><div class="card-header">Аналитика лекарственных препаратов</div>', unsafe_allow_html=True)
    
    prescriptions = get_all_prescriptions()
    if not prescriptions:
        st.info("Нет данных для анализа")
        return
    
    df = pd.DataFrame(prescriptions, columns=["Препарат", "Дозировка", "Регулярность", "Дата_начала"])
    
    st.subheader("Основные показатели")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Всего назначений", len(df))
    with col2:
        st.metric("Уникальных препаратов", df["Препарат"].nunique())
    with col3:
        st.metric("Пациентов", len(get_all_patients()))
    with col4:
        st.metric("Дозировок", df["Дозировка"].nunique())
    
    st.divider()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Топ препаратов", "Распределение по дозировке", "Частота назначения", "Анализ по группам", "Статистика"])
    
    with tab1:
        st.subheader("Топ 15 назначенных препаратов")
        top_drugs = df["Препарат"].value_counts().head(15)
        fig = px.bar(
            x=top_drugs.values,
            y=top_drugs.index,
            orientation='h',
            color=top_drugs.values,
            color_continuous_scale='Blues',
            labels={'x': 'Количество назначений', 'y': 'Препарат'},
            title="Самые часто назначаемые препараты"
        )
        fig.update_layout(height=500, showlegend=False, hovermode='y unified')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("**Статистика:**")
        st.write(f"- Самый часто назначаемый препарат: **{top_drugs.index[0]}** ({top_drugs.values[0]} раз)")
        st.write(f"- Средняя популярность препарата: **{top_drugs.mean():.1f}** назначений")
    
    with tab2:
        st.subheader("Распределение по дозировке")
        dosage_counts = df["Дозировка"].value_counts().head(10)
        fig = go.Figure(data=[
            go.Pie(labels=dosage_counts.index, values=dosage_counts.values, 
                   marker=dict(colors=px.colors.sequential.Blues_r))
        ])
        fig.update_layout(title="Распределение дозировок в назначениях", height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Частота назначения")
        freq_counts = df["Регулярность"].value_counts()
        colors_map = {"1 раз в день": "#0A2F6C", "2 раза в день": "#1E3A8A", "3 раза в день": "#3B82F6"}
        fig = go.Figure(data=[
            go.Bar(
                x=freq_counts.index,
                y=freq_counts.values,
                marker_color=[colors_map.get(f, "#6B7280") for f in freq_counts.index]
            )
        ])
        fig.update_layout(
            title="Распределение по частоте приема",
            xaxis_title="Частота приема",
            yaxis_title="Количество",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("**Анализ:**")
        for freq, count in freq_counts.items():
            percentage = (count / len(df)) * 100
            st.write(f"- **{freq}**: {count} назначений ({percentage:.1f}%)")
    
    with tab4:
        st.subheader("Анализ по группам препаратов")
        drug_groups = {
            "Кардиологические": ["Энап", "Метопролол", "Амлодипин", "Варфарин", "Конкор", "Норваск", "Кордарон", "Дигоксин"],
            "Эндокринологические": ["Метформин", "Глюкофаж"],
            "Гастроэнтерологические": ["Омепразол"],
            "Анальгетики": ["Диклофенак", "Ибупрофен", "Парацетамол", "Аспирин"],
            "Другие": []
        }
        
        group_counts = {}
        for drug in df["Препарат"].unique():
            found = False
            for group, drugs in drug_groups.items():
                if drug in drugs:
                    group_counts[group] = group_counts.get(group, 0) + len(df[df["Препарат"] == drug])
                    found = True
                    break
            if not found:
                group_counts["Другие"] = group_counts.get("Другие", 0) + len(df[df["Препарат"] == drug])
        
        fig = px.pie(
            values=list(group_counts.values()),
            names=list(group_counts.keys()),
            title="Распределение препаратов по группам",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("**Статистика по группам:**")
        for group, count in sorted(group_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(df)) * 100
            st.write(f"- **{group}**: {count} назначений ({percentage:.1f}%)")
    
    with tab5:
        st.subheader("Статистический анализ")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Препараты с наибольшей дозировкой:**")
            max_dosage = df.groupby("Препарат")["Дозировка"].first().sort_values(ascending=False).head(5)
            for drug, dose in max_dosage.items():
                st.write(f"- {drug}: {dose}")
        
        with col2:
            st.markdown("**Распределение начальных дат назначений:**")
            df["Месяц"] = pd.to_datetime(df["Дата_начала"]).dt.to_period("M")
            monthly_counts = df.groupby("Месяц").size()
            st.write(f"- Начало диапазона: {df['Дата_начала'].min()}")
            st.write(f"- Конец диапазона: {df['Дата_начала'].max()}")
            st.write(f"- Среднее по месяцам: {len(df) / len(monthly_counts):.0f} назначений")
        
        st.divider()
        
        st.markdown("**Временная динамика назначений:**")
        monthly_df = df.copy()
        monthly_df["Месяц"] = pd.to_datetime(monthly_df["Дата_начала"]).dt.to_period("M").astype(str)
        timeline = monthly_df.groupby("Месяц").size().reset_index(name="Количество")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline["Месяц"],
            y=timeline["Количество"],
            mode='lines+markers',
            name='Назначения',
            line=dict(color='#0A2F6C', width=3),
            marker=dict(size=10)
        ))
        fig.update_layout(
            title="Динамика назначений по месяцам",
            xaxis_title="Месяц",
            yaxis_title="Количество назначений",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== СТРАНИЦА ВРАЧА ==========================
def doctor_dashboard():
    st.markdown('<div class="app-header"><div class="logo">Цифровая история назначений</div></div>', unsafe_allow_html=True)
    render_top_bar(st.session_state.get('user_name'), st.session_state.get('role'))
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Пациенты", "Ранее выписанные", "Отсроченное обслуживание", "Наличие ЛП", "Аналитика"])
    
    with tab1:
        render_breadcrumb(["Врач", "Пациенты"])
        st.markdown('<div class="card"><div class="card-header">Список пациентов</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_name = st.text_input("Поиск по ФИ", placeholder="Иванов")
        with col2:
            birth_filter = st.text_input("Дата рождения (ГГГГ-ММ-ДД)", placeholder="1980-05-15")
        with col3:
            location_filter = st.text_input("Местоположение", placeholder="Москва")
        with col4:
            patient_id_filter = st.text_input("ID пациента", placeholder="1")
        
        patients = get_all_patients(search_name, birth_filter, location_filter, patient_id_filter)
        
        if not patients:
            st.info("Пациенты не найдены")
        else:
            cols_header = st.columns([0.5, 1, 1, 1.2, 2, 1, 0.8])
            for col, header in zip(cols_header, ["ID", "Фамилия", "Имя", "Дата рожд", "Местоположение", "Препараты", "Действия"]):
                col.markdown(f"**{header}**")
            
            st.divider()
            
            for pid, last_name, first_name, birth_date, policy, location in patients:
                _, prescs = get_patient_by_id(pid)
                drugs = ", ".join([p[1] for p in prescs]) if prescs else "Нет"
                
                cols = st.columns([0.5, 1, 1, 1.2, 2, 1, 0.8])
                cols[0].write(str(pid))
                cols[1].write(last_name)
                cols[2].write(first_name)
                cols[3].write(birth_date)
                cols[4].write(location)
                cols[5].write(drugs if len(drugs) < 30 else drugs[:27] + "...")
                
                if cols[6].button("Ред.", key=f"edit_{pid}"):
                    st.session_state['edit_patient_id'] = pid
                    st.session_state['page'] = 'doctor_edit'
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        render_breadcrumb(["Врач", "Ранее выписанные рецепты"])
        st.markdown('<div class="card"><div class="card-header">История рецептов</div>', unsafe_allow_html=True)
        st.info("Здесь отображаются ранее выписанные рецепты")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        render_breadcrumb(["Врач", "Отсроченное обслуживание"])
        st.markdown('<div class="card"><div class="card-header">Рецепты на отсроченном обслуживании</div>', unsafe_allow_html=True)
        st.info("Рецепты, которые пациент может получить позже")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        render_breadcrumb(["Врач", "Наличие ЛП"])
        st.markdown('<div class="card"><div class="card-header">Проверка наличия в аптеках</div>', unsafe_allow_html=True)
        drug_name = st.text_input("Введите название препарата")
        if drug_name:
            st.info(f"Поиск наличия препарата: {drug_name}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        drug_analytics_dashboard()
    
    render_footer()

def doctor_edit_patient():
    pid = st.session_state.get('edit_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_dashboard'
        st.rerun()
    
    patient, prescs = get_patient_by_id(pid)
    render_breadcrumb(["Врач", "Пациенты", f"Редактирование: {patient[1]} {patient[2]}"])
    
    st.markdown(f'<div class="card"><div class="card-header">Редактирование: {patient[1]} {patient[2]}</div>', unsafe_allow_html=True)
    render_top_bar(st.session_state.get('user_name'), st.session_state.get('role'))
    
    col1, col2 = st.columns(2)
    with col1:
        new_last = st.text_input("Фамилия", value=patient[1])
    with col2:
        new_first = st.text_input("Имя", value=patient[2])
    
    new_birth = st.date_input("Дата рождения", value=datetime.strptime(patient[3], "%Y-%m-%d").date())
    new_location = st.text_input("Местоположение", value=patient[5] or "")
    new_policy = st.text_input("Полис", value=patient[4] or "")
    
    st.divider()
    st.subheader("Препараты")
    
    if 'edit_prescriptions_list' not in st.session_state or st.session_state.get('edit_patient_id_prev') != pid:
        st.session_state['edit_prescriptions_list'] = [[p[1], p[2], p[3]] for p in prescs]
        st.session_state['edit_patient_id_prev'] = pid
    
    items = st.session_state['edit_prescriptions_list']
    
    for idx, item in enumerate(items):
        col1, col2, col3, col4 = st.columns([2.5, 1, 1.5, 0.5])
        drug = col1.text_input(f"Препарат", value=item[0], key=f"drug_edit_{idx}")
        dose = col2.text_input(f"мг", value=item[1], key=f"dose_edit_{idx}")
        reg = col3.text_input(f"Регулярность", value=item[2], key=f"reg_edit_{idx}")
        if col4.button("Удал.", key=f"del_edit_{idx}"):
            items.pop(idx)
            st.rerun()
        items[idx] = [drug, dose, reg]
    
    if st.button("+ Добавить препарат"):
        items.append(["", "", ""])
        st.rerun()
    
    st.divider()
    st.subheader("Чат")
    render_chat_panel(pid, st.session_state.get('user_name'))
    
    st.divider()
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        if st.button("Сохранить"):
            valid = [(d[0], d[1], d[2]) for d in items if d[0].strip()]
            save_patient(pid, new_last, new_first, new_birth.isoformat(), new_policy, new_location, valid)
            st.success("Сохранено")
            if 'edit_prescriptions_list' in st.session_state:
                del st.session_state['edit_prescriptions_list']
            st.session_state['page'] = 'doctor_dashboard'
            st.rerun()
    
    with col2:
        if st.button("Назад"):
            st.session_state['page'] = 'doctor_dashboard'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()

# ========================== СТРАНИЦА ПАЦИЕНТА ==========================
def patient_dashboard():
    st.markdown('<div class="app-header"><div class="logo">Цифровая история назначений</div></div>', unsafe_allow_html=True)
    render_top_bar(st.session_state.get('user_name'), st.session_state.get('role'))
    
    render_breadcrumb(["Пациент", "Главная"])
    
    pid = 1
    patient, prescs = get_patient_by_id(pid)
    
    st.markdown(f'<div class="card"><div class="card-header">Добро пожаловать, {patient[1]} {patient[2]}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ID", patient[0])
    with col2:
        st.metric("Рецепты", len(prescs))
    with col3:
        st.metric("Полис", patient[4] if patient[4] else "-")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    
    st.markdown('<div class="card"><div class="card-header">Мои назначения</div>', unsafe_allow_html=True)
    
    if not prescs:
        st.info("Нет рецептов")
    else:
        for p in prescs:
            with st.expander(f"{p[1]} {p[2]} | {p[3]}"):
                st.write(f"**Дозировка:** {p[2]}")
                st.write(f"**Частота:** {p[3]}")
                st.write(f"**Период:** {p[4]} – {p[5]}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()

# ========================== ВХОД ==========================
def login_page():
    st.markdown('<h1 class="login-header">Цифровая история назначений</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("Вход в систему")
        
        username = st.text_input("Логин", placeholder="врач1 или пациент1")
        password = st.text_input("Пароль", type="password", placeholder="пароль")
        
        # Selectbox для роли, стилизованный как поля ввода
        role = st.selectbox(
            "Роль",
            options=["doctor", "patient"],
            format_func=lambda x: "Врач" if x == "doctor" else "Пациент"
        )
        
        if st.button("Войти", use_container_width=True):
            if username and password:
                st.session_state['authenticated'] = True
                st.session_state['role'] = role
                st.session_state['user_name'] = username
                st.session_state['page'] = 'doctor_dashboard' if role == 'doctor' else 'patient_dashboard'
                st.rerun()
            else:
                st.error("Введите логин и пароль")
        
        st.caption("Тестовые учетные данные: любые логин/пароль")

# ========================== МАРШРУТИЗАЦИЯ ==========================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['page'] = 'login'

if not st.session_state.authenticated:
    login_page()
else:
    role = st.session_state.get('role')
    page = st.session_state.get('page', 'doctor_dashboard')
    
    if role == 'doctor':
        if page == 'doctor_edit':
            doctor_edit_patient()
        else:
            doctor_dashboard()
    else:
        patient_dashboard()
