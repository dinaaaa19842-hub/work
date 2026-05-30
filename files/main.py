import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import hashlib
import qrcode
import calendar as cal
from io import BytesIO
import base64
import random
import numpy as np

# ========================== НАСТРОЙКА СТРАНИЦЫ ==========================
st.set_page_config(page_title="Цифровая история назначений", page_icon="💊", layout="wide", initial_sidebar_state="expanded")

# ========================== CSS СТИЛЬ ==========================
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
    
    .search-container {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #DCE5F0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .search-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #0A2F6C;
        margin-bottom: 0.3rem;
    }
    
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
    
    .breadcrumb { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; font-size: 0.9rem; color: #6B7280; }
    .breadcrumb span { color: #0A2F6C; font-weight: 600; }
    
    .user-info { font-size: 0.9rem; color: #4B5563; text-align: right; }
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
    }
    .app-footer {
        margin-top: 2rem;
        padding: 1rem 0;
        border-top: 1px solid #DCE5F0;
        font-size: 0.85rem;
        color: #6B7280;
    }
    
    .chat-message-user {
        text-align: right;
        margin-bottom: 1rem;
    }
    .chat-message-user div {
        display: inline-block;
        background-color: #0A2F6C;
        color: white;
        padding: 0.75rem;
        border-radius: 12px 12px 4px 12px;
        max-width: 70%;
    }
    .chat-message-assistant {
        text-align: left;
        margin-bottom: 1rem;
    }
    .chat-message-assistant div {
        display: inline-block;
        background-color: #F0F2F5;
        color: #1F2A3E;
        padding: 0.75rem;
        border-radius: 12px 12px 12px 4px;
        max-width: 70%;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0A2F6C;
    }
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stButton button {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stButton button {
        background-color: #1E3A8A !important;
        border: none;
        text-align: left;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #2E4A8E !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] .stMarkdown h2 {
        color: #FFFFFF !important;
    }
    
    .calendar-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    
    .calendar-header {
        background-color: #0A2F6C;
        color: white;
        padding: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    .calendar-day-header {
        background-color: #E6EDF6;
        color: #0A2F6C;
        padding: 8px;
        text-align: center;
        font-weight: 600;
        border: 1px solid #DCE5F0;
    }
    
    .calendar-day {
        border: 1px solid #DCE5F0;
        padding: 8px;
        text-align: center;
        height: 60px;
        vertical-align: top;
    }
    
    .calendar-day-active {
        background-color: #0A2F6C;
        color: white;
        font-weight: bold;
    }
    
    .history-item {
        background-color: #F0F4FA;
        border-left: 4px solid #0A2F6C;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
    
    .polypharmacy-risk-low {
        background-color: #D4EDDA;
        border-left: 4px solid #28A745;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
    
    .polypharmacy-risk-medium {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
    
    .polypharmacy-risk-high {
        background-color: #F8D7DA;
        border-left: 4px solid #DC3545;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
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
    c.execute("DROP TABLE IF EXISTS drug_interactions")
    
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
    
    c.execute('''CREATE TABLE drug_interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  drug1 TEXT,
                  drug2 TEXT,
                  severity TEXT,
                  description TEXT)''')
    
    conn.commit()
    
    # Тестовые данные
    first_names_m = ["Иван", "Петр", "Сергей", "Александр", "Виктор", "Дмитрий", "Павел", "Андрей", "Владимир", "Николай"]
    first_names_f = ["Анна", "Мария", "Елена", "Ольга", "Юлия", "Наталья", "Татьяна", "Галина", "Валентина", "Светлана"]
    last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Волков", "Морозов", "Орлов", "Павлов", "Соколов"]
    locations = ["Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск"]
    
    drugs_list = [
        ("Энап", "5 мг"), ("Аспирин Кардио", "100 мг"), ("Метформин", "500 мг"), 
        ("Амлодипин", "5 мг"), ("Метопролол", "50 мг"), ("Аторвастатин", "20 мг"),
        ("Омепразол", "20 мг"), ("Варфарин", "2.5 мг"), ("Глюкофаж", "1000 мг"),
    ]
    
    # Добавляем взаимодействия препаратов
    interactions = [
        ("Варфарин", "Аспирин Кардио", "high", "Увеличивает риск кровотечения"),
        ("Метформин", "Омепразол", "medium", "Может влиять на всасывание"),
        ("Амлодипин", "Метопролол", "medium", "Усиленное снижение давления"),
        ("Энап", "Амлодипин", "medium", "Синергический эффект"),
    ]
    
    for drug1, drug2, severity, desc in interactions:
        c.execute("INSERT INTO drug_interactions (drug1, drug2, severity, description) VALUES (?,?,?,?)",
                 (drug1, drug2, severity, desc))
    
    for i in range(30):
        gender = "M" if i % 2 == 0 else "F"
        first_name = first_names_m[i % len(first_names_m)] if gender == "M" else first_names_f[i % len(first_names_f)]
        last_name = last_names[i % len(last_names)]
        birth_year = 1950 + i
        birth_date = f"{birth_year:04d}-{(i % 12) + 1:02d}-15"
        policy = f"{1000000000 + i}"
        location = locations[i % len(locations)]
        
        c.execute('''INSERT INTO patients (last_name, first_name, birth_date, policy, location, created_at) 
                    VALUES (?,?,?,?,?,?)''',
                 (last_name, first_name, birth_date, policy, location, datetime.now().isoformat()))
        
        pid = c.lastrowid
        num_drugs = random.randint(2, 6)
        selected_drugs = random.sample(drugs_list, min(num_drugs, len(drugs_list)))
        
        for drug_name, dosage in selected_drugs:
            regularity = random.choice(["1 раз в день", "2 раза в день", "3 раза в день"])
            start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
            
            c.execute('''INSERT INTO prescriptions 
                       (patient_id, drug_name, dosage, regularity, start_date, end_date)
                       VALUES (?,?,?,?,?,?)''',
                     (pid, drug_name, dosage, regularity, start_date, end_date))
            
            presc_id = c.lastrowid
            for day_offset in range(360):
                if random.random() < 0.75:
                    intake_date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
                    c.execute("INSERT INTO intake_log (prescription_id, intake_date) VALUES (?,?)",
                             (presc_id, intake_date))
    
    conn.commit()
    conn.close()

if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state['db_initialized'] = True

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
        c.execute("SELECT id, drug_name, dosage, regularity, start_date, end_date FROM prescriptions WHERE patient_id=? ORDER BY start_date DESC", (pid,))
        prescs = c.fetchall()
        conn.close()
        return patient, prescs
    
    conn.close()
    return None, []

def get_prescription_history(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT DISTINCT p.id, p.drug_name, p.dosage, p.regularity, p.start_date, p.end_date 
                 FROM prescriptions p WHERE p.patient_id=? ORDER BY p.start_date DESC""", (patient_id,))
    prescs = c.fetchall()
    conn.close()
    return prescs

def get_intake_dates_for_prescription(prescription_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT intake_date FROM intake_log WHERE prescription_id=? ORDER BY intake_date DESC", (prescription_id,))
    dates = [row[0] for row in c.fetchall()]
    conn.close()
    return dates

def get_drug_interactions(drug1, drug2):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT severity, description FROM drug_interactions 
                 WHERE (drug1=? AND drug2=?) OR (drug1=? AND drug2=?)""", 
             (drug1, drug2, drug2, drug1))
    result = c.fetchone()
    conn.close()
    return result

def add_new_patient(last_name, first_name, birth_date, policy, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO patients (last_name, first_name, birth_date, policy, location, created_at) VALUES (?,?,?,?,?,?)",
             (last_name, first_name, birth_date, policy, location, datetime.now().isoformat()))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

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

def get_all_prescriptions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT drug_name, dosage, regularity, start_date FROM prescriptions")
    data = c.fetchall()
    conn.close()
    return data

def analyze_polypharmacy(patient_id):
    """Анализ полипрагмазии пациента"""
    _, prescriptions = get_patient_by_id(patient_id)
    patient, _ = get_patient_by_id(patient_id)
    
    # Вычисляем возраст
    birth_date = datetime.strptime(patient[3], "%Y-%m-%d").date()
    age = (date.today() - birth_date).days // 365
    
    num_drugs = len(prescriptions)
    
    # Определяем риск
    if age >= 65:
        thresholds = {'low': 2, 'medium': 4, 'high': 7, 'critical': 10}
    else:
        thresholds = {'low': 3, 'medium': 5, 'high': 8, 'critical': 11}
    
    if num_drugs >= thresholds['critical']:
        risk_level = 'critical'
    elif num_drugs >= thresholds['high']:
        risk_level = 'high'
    elif num_drugs >= thresholds['medium']:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    # Проверяем взаимодействия
    interactions = []
    for i, presc1 in enumerate(prescriptions):
        for presc2 in prescriptions[i+1:]:
            result = get_drug_interactions(presc1[1], presc2[1])
            if result:
                interactions.append({
                    'drug1': presc1[1],
                    'drug2': presc2[1],
                    'severity': result[0],
                    'description': result[1]
                })
    
    return {
        'num_drugs': num_drugs,
        'age': age,
        'risk_level': risk_level,
        'interactions': interactions
    }

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
    st.markdown(f"<div class='user-info'>Добро пожаловать, <strong>{username}</strong> ({role.upper()})</div>", unsafe_allow_html=True)

def render_footer():
    st.markdown('<div class="app-footer">Цифровая история назначений | Версия 3.0</div>', unsafe_allow_html=True)

# ========================== СТРАНИЦА ЧАТА ==========================
def doctor_chat_page():
    pid = st.session_state.get('chat_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_dashboard'
        st.rerun()
    
    patient, _ = get_patient_by_id(pid)
    full_name = f"{patient[1]} {patient[2]}"
    
    render_breadcrumb([f"Чат с {full_name}"])
    
    st.markdown(f'<div class="card"><div class="card-header">Чат с пациентом {full_name}</div>', unsafe_allow_html=True)
    
    messages = get_messages(pid)
    if not messages:
        st.info("Нет сообщений")
    
    for sender, msg, timestamp in messages:
        time_obj = datetime.fromisoformat(timestamp)
        time_str = time_obj.strftime("%H:%M")
        if sender == st.session_state.get('user_name'):
            st.markdown(f"""
            <div class="chat-message-user">
                <div>
                    <div>{msg}</div>
                    <div style="font-size: 0.7rem; opacity: 0.7; margin-top: 0.25rem;">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message-assistant">
                <div>
                    <div><strong>{sender}</strong><br>{msg}</div>
                    <div style="font-size: 0.7rem; opacity: 0.7; margin-top: 0.25rem;">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        new_msg = st.text_area("Сообщение:", key="chat_input", height=80, label_visibility="collapsed", placeholder="Напишите сообщение...")
    with col2:
        if st.button("Отправить", use_container_width=True):
            if new_msg.strip():
                add_message(pid, st.session_state.get('user_name', 'Врач'), new_msg)
                st.rerun()
    
    st.divider()
    if st.button("Вернуться на страницу пациентов"):
        st.session_state['page'] = 'doctor_dashboard'
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()

# ========================== ИСТОРИЯ ПРЕПАРАТОВ ==========================
def patient_prescription_history():
    pid = st.session_state.get('history_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_edit'
        st.rerun()
    
    patient, _ = get_patient_by_id(pid)
    full_name = f"{patient[1]} {patient[2]}"
    
    st.markdown(f'<div class="card"><div class="card-header">История препаратов пациента: {full_name}</div>', unsafe_allow_html=True)
    
    if st.button("Вернуться к редактированию"):
        st.session_state['page'] = 'doctor_edit'
        st.rerun()
    
    st.divider()
    
    all_prescriptions = get_prescription_history(pid)
    
    if not all_prescriptions:
        st.info("История препаратов отсутствует")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.subheader("Полная история назначений")
    
    for idx, presc in enumerate(all_prescriptions):
        presc_id, drug_name, dosage, regularity, start_date, end_date = presc
        is_active = datetime.strptime(end_date, "%Y-%m-%d").date() >= date.today()
        status = "Активный" if is_active else "Завершен"
        status_color = "#28A745" if is_active else "#DC3545"
        
        st.markdown(f"""
        <div class="history-item">
            <strong>{drug_name}</strong> ({dosage})<br>
            Частота: {regularity}<br>
            Период: {start_date} - {end_date}<br>
            <span style="color: {status_color}; font-weight: bold;">Статус: {status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("История приема")
    
    selected_drug_idx = st.selectbox(
        "Выберите препарат для просмотра приема:",
        range(len(all_prescriptions)),
        format_func=lambda i: f"{all_prescriptions[i][1]} ({all_prescriptions[i][2]})"
    )
    
    selected_prescription = all_prescriptions[selected_drug_idx]
    presc_id = selected_prescription[0]
    drug_name = selected_prescription[1]
    
    st.subheader(f"История приема: {drug_name}")
    
    # Выбор месяца и года
    col1, col2 = st.columns(2)
    with col1:
        month_num = st.selectbox(
            "Месяц:",
            range(1, 13),
            format_func=lambda x: ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"][x-1]
        )
    with col2:
        selected_year = st.selectbox("Год:", range(date.today().year - 1, date.today().year + 1))
    
    # Получаем даты приема
    intake_dates = get_intake_dates_for_prescription(presc_id)
    intake_dates_set = set(intake_dates)
    
    # Отображение календаря
    calendar_data = cal.monthcalendar(selected_year, month_num)
    month_name = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"][month_num - 1]
    
    st.markdown(f"<h4 style='text-align: center; color: #0A2F6C;'>{month_name} {selected_year}</h4>", unsafe_allow_html=True)
    
    # HTML таблица календаря
    html_calendar = '<table class="calendar-table"><tr>'
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    
    for day in days:
        html_calendar += f'<td class="calendar-day-header">{day}</td>'
    html_calendar += '</tr><tr>'
    
    day_count = 0
    for week in calendar_data:
        for day in week:
            if day == 0:
                html_calendar += '<td class="calendar-day"></td>'
            else:
                date_str = f"{selected_year:04d}-{month_num:02d}-{day:02d}"
                is_taken = date_str in intake_dates_set
                bg_color = '#0A2F6C' if is_taken else '#FFFFFF'
                text_color = 'white' if is_taken else '#1F2A3E'
                font_weight = 'bold' if is_taken else 'normal'
                
                html_calendar += f'<td class="calendar-day" style="background-color: {bg_color}; color: {text_color}; font-weight: {font_weight};">{day}</td>'
            
            day_count += 1
            if day_count % 7 == 0:
                html_calendar += '</tr><tr>'
    
    html_calendar += '</tr></table>'
    st.markdown(html_calendar, unsafe_allow_html=True)
    
    st.divider()
    
    # История приемов
    st.subheader("История приема препарата")
    
    recent_intakes = intake_dates[:30]
    
    if recent_intakes:
        intake_df = pd.DataFrame({
            'Дата приема': recent_intakes,
            'Препарат': [drug_name] * len(recent_intakes),
            'Статус': ['Принято'] * len(recent_intakes)
        })
        st.dataframe(intake_df, use_container_width=True, hide_index=True)
    else:
        st.info("Нет записей о приеме препарата")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== ДОБАВЛЕНИЕ ПАЦИЕНТА ==========================
def add_patient_page():
    render_breadcrumb(["Добавить пациента"])
    
    st.markdown('<div class="card"><div class="card-header">Добавить нового пациента</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        last_name = st.text_input("Фамилия", placeholder="Иванов")
    with col2:
        first_name = st.text_input("Имя", placeholder="Иван")
    
    birth_date = st.date_input("Дата рождения")
    
    col1, col2 = st.columns(2)
    with col1:
        policy = st.text_input("Номер полиса", placeholder="1234567890")
    with col2:
        location = st.text_input("Местоположение", placeholder="Москва")
    
    st.divider()
    st.subheader("Препараты (опционально)")
    
    if 'new_patient_prescriptions_list' not in st.session_state:
        st.session_state['new_patient_prescriptions_list'] = []
    
    items = st.session_state['new_patient_prescriptions_list']
    
    if items:
        for idx, item in enumerate(items):
            col1, col2, col3, col4 = st.columns([2.5, 1, 1.5, 0.5])
            drug = col1.text_input(f"Препарат", value=item[0], key=f"new_drug_{idx}")
            dose = col2.text_input(f"мг", value=item[1], key=f"new_dose_{idx}")
            reg = col3.text_input(f"Регулярность", value=item[2], key=f"new_reg_{idx}")
            if col4.button("Удал.", key=f"del_new_{idx}"):
                items.pop(idx)
                st.rerun()
            items[idx] = [drug, dose, reg]
    
    if st.button("+ Добавить препарат", key="add_new_drug"):
        items.append(["", "", ""])
        st.rerun()
    
    st.divider()
    
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        if st.button("Добавить пациента", use_container_width=True, key="submit_new_patient"):
            if last_name and first_name and policy:
                pid = add_new_patient(last_name, first_name, birth_date.isoformat(), policy, location)
                
                if items:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    for drug in items:
                        if drug[0].strip():
                            c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage, regularity, start_date, end_date) VALUES (?,?,?,?,?,?)",
                                     (pid, drug[0], drug[1], drug[2], date.today().isoformat(), (date.today() + timedelta(days=30)).isoformat()))
                    conn.commit()
                    conn.close()
                
                st.success(f"Пациент {first_name} {last_name} успешно добавлен!")
                if 'new_patient_prescriptions_list' in st.session_state:
                    del st.session_state['new_patient_prescriptions_list']
                st.session_state['page'] = 'doctor_dashboard'
                st.rerun()
            else:
                st.error("Пожалуйста, заполните обязательные поля (Фамилия, Имя, Полис)")
    
    with col2:
        if st.button("Отмена", use_container_width=True, key="cancel_new_patient"):
            if 'new_patient_prescriptions_list' in st.session_state:
                del st.session_state['new_patient_prescriptions_list']
            st.session_state['page'] = 'doctor_dashboard'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== РЕДАКТИРОВАНИЕ ПАЦИЕНТА ==========================
def doctor_edit_patient():
    pid = st.session_state.get('edit_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_dashboard'
        st.rerun()
    
    patient, prescs = get_patient_by_id(pid)
    render_breadcrumb([f"Редактирование: {patient[1]} {patient[2]}"])
    
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
    st.subheader("Текущие назначения")
    
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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("История препаратов", use_container_width=True):
            st.session_state['history_patient_id'] = pid
            st.session_state['page'] = 'prescription_history'
            st.rerun()
    
    with col2:
        if st.button("Чат", use_container_width=True):
            st.session_state['chat_patient_id'] = pid
            st.session_state['page'] = 'doctor_chat'
            st.rerun()
    
    with col3:
        if st.button("Анализ", use_container_width=True):
            st.session_state['analysis_patient_id'] = pid
            st.session_state['page'] = 'polypharmacy_analysis'
            st.rerun()
    
    st.divider()
    
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        if st.button("Сохранить", use_container_width=True):
            valid = [(d[0], d[1], d[2]) for d in items if d[0].strip()]
            save_patient(pid, new_last, new_first, new_birth.isoformat(), new_policy, new_location, valid)
            st.success("Изменения сохранены")
            if 'edit_prescriptions_list' in st.session_state:
                del st.session_state['edit_prescriptions_list']
            st.session_state['page'] = 'doctor_dashboard'
            st.rerun()
    
    with col2:
        if st.button("Отмена", use_container_width=True):
            st.session_state['page'] = 'doctor_dashboard'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()

# ========================== АНАЛИЗ ПОЛИПРАГМАЗИИ ==========================
def polypharmacy_analysis():
    pid = st.session_state.get('analysis_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_dashboard'
        st.rerun()
    
    patient, prescriptions = get_patient_by_id(pid)
    full_name = f"{patient[1]} {patient[2]}"
    
    render_breadcrumb([f"Анализ полипрагмазии: {full_name}"])
    
    st.markdown(f'<div class="card"><div class="card-header">Анализ полипрагмазии пациента: {full_name}</div>', unsafe_allow_html=True)
    
    if st.button("Вернуться к редактированию"):
        st.session_state['page'] = 'doctor_edit'
        st.rerun()
    
    st.divider()
    
    # Анализ полипрагмазии
    analysis = analyze_polypharmacy(pid)
    
    num_drugs = analysis['num_drugs']
    age = analysis['age']
    risk_level = analysis['risk_level']
    interactions = analysis['interactions']
    
    # Определение цвета и описания риска
    risk_colors = {
        'low': ('#D4EDDA', '#28A745'),
        'medium': ('#FFF3CD', '#FFC107'),
        'high': ('#F8D7DA', '#DC3545'),
        'critical': ('#F8D7DA', '#DC3545')
    }
    
    risk_labels = {
        'low': 'Низкий риск',
        'medium': 'Средний риск',
        'high': 'Высокий риск',
        'critical': 'Критический риск'
    }
    
    bg_color, border_color = risk_colors.get(risk_level, ('#F0F4FA', '#0A2F6C'))
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; border-left: 4px solid {border_color}; padding: 1rem; margin-bottom: 1rem; border-radius: 4px;">
        <strong>Возраст:</strong> {age} лет<br>
        <strong>Количество препаратов:</strong> {num_drugs}<br>
        <strong style="color: {border_color};">Уровень риска: {risk_labels[risk_level]}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Список препаратов
    st.subheader("Назначенные препараты")
    for presc in prescriptions:
        st.markdown(f"**{presc[1]}** ({presc[2]}) - {presc[3]}")
    
    st.divider()
    
    # Анализ взаимодействий
    if interactions:
        st.subheader("Выявленные взаимодействия")
        for interaction in interactions:
            severity_color = {
                'low': '#D4EDDA',
                'medium': '#FFF3CD',
                'high': '#F8D7DA'
            }.get(interaction['severity'], '#F0F4FA')
            
            severity_label = {
                'low': 'Слабое взаимодействие',
                'medium': 'Среднее взаимодействие',
                'high': 'Сильное взаимодействие'
            }.get(interaction['severity'], 'Неизвестное')
            
            st.markdown(f"""
            <div style="background-color: {severity_color}; border-left: 4px solid; padding: 1rem; margin-bottom: 1rem; border-radius: 4px;">
                <strong>{interaction['drug1']}</strong> + <strong>{interaction['drug2']}</strong><br>
                <strong>Тип:</strong> {severity_label}<br>
                <strong>Описание:</strong> {interaction['description']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Значительных взаимодействий между препаратами не выявлено")
    
    st.divider()
    
    # Графики анализа
    st.subheader("Графический анализ")
    
    # График 1: Распределение препаратов по частоте
    freqs = {}
    for presc in prescriptions:
        freq = presc[3]
        freqs[freq] = freqs.get(freq, 0) + 1
    
    if freqs:
        fig1 = px.bar(
            x=list(freqs.keys()),
            y=list(freqs.values()),
            labels={'x': 'Частота приема', 'y': 'Количество препаратов'},
            title="Распределение препаратов по частоте приема"
        )
        fig1.update_traces(marker_color='#0A2F6C')
        st.plotly_chart(fig1, use_container_width=True)
    
    # График 2: Риск по возрастным группам
    age_groups = {
        'Молодые (до 40)': 0,
        'Средний возраст (40-65)': 0,
        'Пожилые (65+)': 0
    }
    
    if age < 40:
        age_groups['Молодые (до 40)'] = num_drugs
    elif age < 65:
        age_groups['Средний возраст (40-65)'] = num_drugs
    else:
        age_groups['Пожилые (65+)'] = num_drugs
    
    fig2 = px.pie(
        values=[v for v in age_groups.values() if v > 0],
        names=[k for k, v in age_groups.items() if v > 0],
        title="Позиционирование по возрастной группе"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    # Рекомендации
    st.subheader("Рекомендации")
    
    recommendations = []
    
    if risk_level in ['high', 'critical']:
        recommendations.append("Рассмотрите возможность уменьшения количества препаратов")
        recommendations.append("Обратитесь к клиническому фармакологу для оптимизации терапии")
    
    if age >= 65 and num_drugs >= 5:
        recommendations.append("Для пожилого пациента количество препаратов выше рекомендуемого")
        recommendations.append("Проведите переоценку необходимости каждого препарата")
    
    if interactions:
        recommendations.append("Обратите внимание на выявленные взаимодействия")
        recommendations.append("Рассмотрите замену одного из взаимодействующих препаратов")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
    else:
        st.info("Специальных рекомендаций не требуется")
    
    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()

# ========================== СТРАНИЦА ПАЦИЕНТОВ ==========================
def doctor_patients_page():
    st.markdown('<div class="card"><div class="card-header">Список пациентов</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<h4 style="margin: 0 0 1rem 0;">Поиск по параметрам</h4>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col_search, col_add = st.columns([1.2, 1.2, 1.2, 1.2, 0.8, 1.2])
    
    with col1:
        st.markdown('<label class="search-label">Поиск по ФИО</label>', unsafe_allow_html=True)
        search_name = st.text_input("", placeholder="ФИО", key="search_fio", label_visibility="collapsed")
    
    with col2:
        st.markdown('<label class="search-label">Дата рождения</label>', unsafe_allow_html=True)
        birth_filter = st.text_input("", placeholder="ГГГГ-ММ-ДД", key="search_birth", label_visibility="collapsed")
    
    with col3:
        st.markdown('<label class="search-label">Местоположение</label>', unsafe_allow_html=True)
        location_filter = st.text_input("", placeholder="Город", key="search_location", label_visibility="collapsed")
    
    with col4:
        st.markdown('<label class="search-label">ID пациента</label>', unsafe_allow_html=True)
        patient_id_filter = st.text_input("", placeholder="№", key="search_id", label_visibility="collapsed")
    
    with col_search:
        st.markdown('<label class="search-label" style="opacity: 0;">.</label>', unsafe_allow_html=True)
        search_button = st.button("Поиск", use_container_width=True, key="search_btn")
    
    with col_add:
        st.markdown('<label class="search-label" style="opacity: 0;">.</label>', unsafe_allow_html=True)
        add_button = st.button("Добавить", use_container_width=True, key="add_btn")
    
    if add_button:
        st.session_state['page'] = 'add_patient'
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if search_button:
        patients = get_all_patients(search_name, birth_filter, location_filter, patient_id_filter)
    else:
        patients = get_all_patients()
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    if not patients:
        st.info("Пациенты не найдены")
    else:
        st.divider()
        
        cols_header = st.columns([0.5, 1.2, 1.2, 1.2, 1.5, 0.8, 0.8, 0.8])
        for col, header in zip(cols_header, ["ID", "Фамилия", "Имя", "Дата рожд", "Местоположение", "Препараты", "Чат", "Действия"]):
            col.markdown(f"**{header}**")
        st.divider()
        
        for pid, last_name, first_name, birth_date, policy, location in patients:
            _, prescs = get_patient_by_id(pid)
            drugs = ", ".join([p[1] for p in prescs]) if prescs else "Нет"
            
            cols = st.columns([0.5, 1.2, 1.2, 1.2, 1.5, 0.8, 0.8, 0.8])
            cols[0].write(str(pid))
            cols[1].write(last_name)
            cols[2].write(first_name)
            cols[3].write(birth_date)
            cols[4].write(location)
            cols[5].write(drugs if len(drugs) < 30 else drugs[:27] + "...")
            
            if cols[6].button("Чат", key=f"chat_{pid}", use_container_width=True):
                st.session_state['chat_patient_id'] = pid
                st.session_state['page'] = 'doctor_chat'
                st.rerun()
            
            if cols[7].button("Ред.", key=f"edit_{pid}", use_container_width=True):
                st.session_state['edit_patient_id'] = pid
                st.session_state['page'] = 'doctor_edit'
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== АНАЛИТИКА ==========================
def drug_analytics_dashboard():
    render_breadcrumb(["Аналитика"])
    
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Топ препаратов", "По дозировке", "Частота приема", "По группам", "Статистика"])
    
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
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.write(f"Самый назначаемый: **{top_drugs.index[0]}** ({top_drugs.values[0]} назначений)")
        st.write(f"Средняя популярность: **{top_drugs.mean():.1f}** назначений")
    
    with tab2:
        st.subheader("Распределение по дозировке")
        dosage_counts = df["Дозировка"].value_counts().head(10)
        fig = px.pie(labels=dosage_counts.index, values=dosage_counts.values, 
                    title="Распределение дозировок")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Частота приема")
        freq_counts = df["Регулярность"].value_counts()
        fig = px.bar(
            x=freq_counts.index,
            y=freq_counts.values,
            labels={'x': 'Частота приема', 'y': 'Количество'},
            title="Распределение по частоте приема"
        )
        fig.update_traces(marker_color='#0A2F6C')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Анализ по группам")
        drug_groups = {
            "Кардиологические": ["Энап", "Метопролол", "Амлодипин", "Варфарин"],
            "Эндокринологические": ["Метформин", "Глюкофаж"],
            "Гастроэнтерологические": ["Омепразол"],
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
        
        fig = px.pie(values=list(group_counts.values()), names=list(group_counts.keys()),
                    title="Препараты по фармакологическим группам")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("Статистический анализ")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Препараты с наибольшей дозировкой:**")
            max_dosage = df.groupby("Препарат")["Дозировка"].first().sort_values(ascending=False).head(5)
            for drug, dose in max_dosage.items():
                st.write(f"- {drug}: {dose}")
        
        with col2:
            st.write("**Диапазон дат назначений:**")
            st.write(f"- Начало: {df['Дата_начала'].min()}")
            st.write(f"- Конец: {df['Дата_начала'].max()}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== НАЛИЧИЕ ЛП ==========================
def drug_availability_page():
    render_breadcrumb(["Наличие лекарственных препаратов"])
    
    st.markdown('<div class="card"><div class="card-header">Проверка наличия лекарственных препаратов</div>', unsafe_allow_html=True)
    
    drug_name = st.text_input("Введите название препарата")
    
    if drug_name:
        # Получаем всех препаратов из БД
        all_prescriptions = get_all_prescriptions()
        df = pd.DataFrame(all_prescriptions, columns=["Препарат", "Дозировка", "Регулярность", "Дата"])
        
        # Фильтруем по названию
        matching_drugs = df[df["Препарат"].str.contains(drug_name, case=False, na=False)]
        
        if not matching_drugs.empty:
            st.subheader(f"Результаты по '{drug_name}':")
            
            # Подсчет назначений по дозировкам
            dosage_counts = matching_drugs["Дозировка"].value_counts()
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Количество назначений по дозировкам:**")
                for dosage, count in dosage_counts.items():
                    st.write(f"- {dosage}: {count} назначений")
            
            with col2:
                fig = px.pie(values=dosage_counts.values, names=dosage_counts.index,
                            title=f"Распределение препарата '{drug_name}' по дозировкам")
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Таблица подробных данных
            st.write("**Подробная информация:**")
            st.dataframe(matching_drugs, use_container_width=True, hide_index=True)
        else:
            st.info(f"Препарат '{drug_name}' не найден в системе")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== СТРАНИЦА ВРАЧА ==========================
def doctor_dashboard():
    st.markdown('<div class="app-header"><div class="logo">Цифровая история назначений</div></div>', unsafe_allow_html=True)
    render_top_bar(st.session_state.get('user_name'), st.session_state.get('role'))

    if 'doctor_selected_tab' not in st.session_state:
        st.session_state.doctor_selected_tab = "Пациенты"

    with st.sidebar:
        st.markdown("## Навигация")
        
        for tab in ["Пациенты", "Отсроченное обслуживание", "Наличие ЛП", "Аналитика"]:
            if st.button(tab, key=f"sidebar_{tab}", use_container_width=True):
                st.session_state.doctor_selected_tab = tab
                st.rerun()
        
        st.markdown("---")
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        if st.button("Выход", key="logout_btn", use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state.clear()
            st.rerun()

    selected_tab = st.session_state.doctor_selected_tab
    render_breadcrumb([selected_tab])

    if selected_tab == "Пациенты":
        doctor_patients_page()
    elif selected_tab == "Отсроченное обслуживание":
        st.markdown('<div class="card"><div class="card-header">Рецепты на отсроченном обслуживании</div>', unsafe_allow_html=True)
        st.info("Рецепты, которые пациент может получить позже")
        st.markdown('</div>', unsafe_allow_html=True)
    elif selected_tab == "Наличие ЛП":
        drug_availability_page()
    elif selected_tab == "Аналитика":
        drug_analytics_dashboard()

    render_footer()

# ========================== ВХОД ==========================
def login_page():
    st.markdown('<h1 style="text-align: center; color: #0A2F6C; margin-bottom: 3rem;">Цифровая история назначений</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("Вход в систему")
        
        username = st.text_input("Логин", placeholder="врач1")
        password = st.text_input("Пароль", type="password", placeholder="пароль")
        
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
        elif page == 'doctor_chat':
            doctor_chat_page()
        elif page == 'add_patient':
            add_patient_page()
        elif page == 'prescription_history':
            patient_prescription_history()
        elif page == 'polypharmacy_analysis':
            polypharmacy_analysis()
        else:
            doctor_dashboard()
    else:
        st.markdown('<h1>Доступ как пациент</h1>', unsafe_allow_html=True)
