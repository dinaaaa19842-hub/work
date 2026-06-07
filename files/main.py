import streamlit as at
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import hashlib
import calendar as cal
from io import BytesIO
import base64
import random
import numpy as np
import qrcode # <--- ДОБАВЛЕНО для генерации QR-кода

# ========================== НАСТРОЙКА СТРАНИЦЫ ==========================
st.set_page_config(page_title="Цифровая история назначений", page_icon=None, layout="wide", initial_sidebar_state="expanded")

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

    /* Patient zone styles */
    .patient-drug-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F4FA 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #DCE5F0;
        box-shadow: 0 2px 8px rgba(10,47,108,0.07);
    }
    .patient-drug-card .drug-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0A2F6C;
        margin-bottom: 0.3rem;
    }
    .patient-drug-card .drug-detail {
        font-size: 0.88rem;
        color: #4B5563;
        margin-bottom: 0.15rem;
    }
    .patient-drug-card .drug-contraindication {
        font-size: 0.85rem;
        color: #DC3545;
        background: #FFF0F0;
        border-radius: 4px;
        padding: 0.3rem 0.6rem;
        margin-top: 0.4rem;
        display: inline-block;
    }
    .patient-metric-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid #DCE5F0;
        box-shadow: 0 1px 4px rgba(10,47,108,0.06);
    }
    .patient-metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0A2F6C;
    }
    .patient-metric-label {
        font-size: 0.82rem;
        color: #6B7280;
        margin-top: 0.2rem;
    }
    .reminder-card {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        border-radius: 6px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.7rem;
    }
    .reminder-card.done {
        background: #F0FFF4;
        border-left-color: #22C55E;
        opacity: 0.75;
    }
    .pharmacy-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
        border: 1px solid #DCE5F0;
    }

    /* AI Chat styles */
    .ai-chat-container {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #DCE5F0;
        box-shadow: 0 2px 8px rgba(10,47,108,0.08);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 600px;
    }
    .ai-chat-header {
        background: linear-gradient(135deg, #0A2F6C 0%, #1E3A8A 100%);
        color: white;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .ai-chat-header .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    .ai-chat-header .info {
        flex: 1;
    }
    .ai-chat-header .name {
        font-weight: 700;
        font-size: 0.95rem;
    }
    .ai-chat-header .status {
        font-size: 0.75rem;
        opacity: 0.8;
    }
    .ai-chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
        background: #FAFBFC;
    }
    .ai-message {
        margin-bottom: 1rem;
        display: flex;
        gap: 0.8rem;
    }
    .ai-message .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #0A2F6C;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .ai-message .bubble {
        background: #E8EEF7;
        color: #1F2A3E;
        padding: 0.8rem 1rem;
        border-radius: 12px 12px 12px 4px;
        max-width: 70%;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .ai-message .bubble a {
        color: #0A2F6C;
        text-decoration: underline;
    }
    .user-message {
        margin-bottom: 1rem;
        display: flex;
        justify-content: flex-end;
        gap: 0.8rem;
    }
    .user-message .bubble {
        background: #0A2F6C;
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 12px 12px 4px 12px;
        max-width: 70%;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .thinking-indicator {
        display: flex;
        gap: 0.3rem;
        align-items: center;
    }
    .thinking-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #0A2F6C;
        animation: bounce 1.4s infinite;
    }
    .thinking-dot:nth-child(2) { animation-delay: 0.2s; }
    .thinking-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-8px); }
    }
    .ai-chat-input {
        border-top: 1px solid #DCE5F0;
        padding: 1rem 1.5rem;
        background: #FFFFFF;
    }
    .message-actions {
        display: flex;
        gap: 0.4rem;
        margin-top: 0.4rem;
        justify-content: flex-end;
        font-size: 0.75rem;
    }
    .message-actions button {
        background: #E8EEF7;
        border: none;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        cursor: pointer;
        color: #0A2F6C;
    }
    .message-actions button:hover {
        background: #DCE5F0;
    }

</style>
""", unsafe_allow_html=True)

# ========================== БД ==========================
import os
import tempfile

# Streamlit Cloud: используем /tmp для записи БД
_TMP_DIR = tempfile.gettempdir()
DB_NAME = os.path.join(_TMP_DIR, "clinic.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("DROP TABLE IF EXISTS patients")
    c.execute("DROP TABLE IF EXISTS prescriptions")
    c.execute("DROP TABLE IF EXISTS messages")
    c.execute("DROP TABLE IF EXISTS intake_log")
    c.execute("DROP TABLE IF EXISTS drug_interactions")
    c.execute("DROP TABLE IF EXISTS wellbeing_log")
    
    c.execute('''CREATE TABLE patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  last_name TEXT, first_name TEXT,
                  birth_date TEXT, policy TEXT, location TEXT,
                  created_at TEXT,
                  contraindications TEXT)''')
    
    c.execute('''CREATE TABLE prescriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  patient_id INTEGER, 
                  drug_name TEXT,
                  dosage TEXT, 
                  regularity TEXT, 
                  start_date TEXT, 
                  end_date TEXT,
                  indication TEXT,
                  instructions TEXT,
                  food_relation TEXT,
                  special_notes TEXT,
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

    c.execute('''CREATE TABLE wellbeing_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  patient_id INTEGER,
                  log_date TEXT,
                  score INTEGER,
                  note TEXT,
                  FOREIGN KEY(patient_id) REFERENCES patients(id))''')
    
    conn.commit()
    
    first_names_m = ["Иван", "Петр", "Сергей", "Александр", "Виктор", "Дмитрий", "Павел", "Андрей", "Владимир", "Николай"]
    first_names_f = ["Анна", "Мария", "Елена", "Ольга", "Юлия", "Наталья", "Татьяна", "Галина", "Валентина", "Светлана"]
    last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Волков", "Морозов", "Орлов", "Павлов", "Соколов"]
    locations = ["Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск"]
    
    drugs_data = [
        ("Энап", "5 мг", "1 раз в день", "Снижение АД", "Принимать утром натощак", "До еды", "При сухом кашле — сообщить врачу"),
        ("Аспирин Кардио", "100 мг", "1 раз в день", "Профилактика тромбозов", "Принимать после еды", "После еды", "Не принимать при язве желудка"),
        ("Метформин", "500 мг", "2 раза в день", "Сахарный диабет 2 типа", "Принимать во время еды", "Во время еды", "Контроль функции почек"),
        ("Амлодипин", "5 мг", "1 раз в день", "Гипертония, стенокардия", "Принимать в одно время суток", "Независимо от еды", "Возможны отёки лодыжек"),
        ("Метопролол", "50 мг", "2 раза в день", "Гипертония, аритмия", "Принимать утром и вечером", "Во время еды", "Не прекращать резко"),
        ("Аторвастатин", "20 мг", "1 раз в день", "Высокий холестерин", "Принимать вечером", "Независимо от еды", "Сообщить о мышечных болях"),
        ("Омепразол", "20 мг", "1 раз в день", "Защита желудка", "Принимать за 30 мин до завтрака", "До еды", "Курс до 4 недель"),
        ("Варфарин", "2.5 мг", "1 раз в день", "Профилактика тромбоэмболии", "Принимать в одно время", "Независимо от еды", "Регулярный контроль МНО"),
        ("Глюкофаж", "1000 мг", "2 раза в день", "Сахарный диабет 2 типа", "Принимать во время еды", "Во время еды", "Контроль уровня глюкозы"),
    ]
    
    contraindications_list = [
        "Аллергия на сульфаниламиды",
        "Непереносимость лактозы",
        "Почечная недостаточность",
        "",
        "Бронхиальная астма",
        "",
        "Аллергия на пенициллин",
        "",
        "Печёночная недостаточность",
        "",
    ]
    
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
        contraindications = contraindications_list[i % len(contraindications_list)]
        
        c.execute('''INSERT INTO patients (last_name, first_name, birth_date, policy, location, created_at, contraindications) 
                    VALUES (?,?,?,?,?,?,?)''',
                 (last_name, first_name, birth_date, policy, location, datetime.now().isoformat(), contraindications))
        
        pid = c.lastrowid
        num_drugs = random.randint(2, 6)
        selected_drugs = random.sample(drugs_data, min(num_drugs, len(drugs_data)))
        
        for drug_entry in selected_drugs:
            drug_name, dosage, regularity, indication, instructions, food_relation, special_notes = drug_entry
            start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
            
            c.execute('''INSERT INTO prescriptions 
                       (patient_id, drug_name, dosage, regularity, start_date, end_date,
                        indication, instructions, food_relation, special_notes)
                       VALUES (?,?,?,?,?,?,?,?,?,?)''',
                     (pid, drug_name, dosage, regularity, start_date, end_date,
                      indication, instructions, food_relation, special_notes))
            
            presc_id = c.lastrowid
            for day_offset in range(360):
                if random.random() < 0.75:
                    intake_date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
                    c.execute("INSERT INTO intake_log (prescription_id, intake_date) VALUES (?,?)",
                             (presc_id, intake_date))
        
        # Генерируем данные самочувствия
        base_score = random.randint(5, 8)
        for day_offset in range(90):
            log_date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            # Постепенное улучшение с небольшими колебаниями
            trend = min(day_offset * 0.02, 1.5)
            score = max(1, min(10, int(base_score + trend + random.randint(-1, 1))))
            c.execute("INSERT INTO wellbeing_log (patient_id, log_date, score) VALUES (?,?,?)",
                     (pid, log_date, score))
    
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
    
    c.execute("SELECT id, last_name, first_name, birth_date, policy, location, contraindications FROM patients WHERE id=?", (pid,))
    patient = c.fetchone()
    
    if patient:
        c.execute("""SELECT id, drug_name, dosage, regularity, start_date, end_date,
                            indication, instructions, food_relation, special_notes
                     FROM prescriptions WHERE patient_id=? ORDER BY start_date DESC""", (pid,))
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

def get_all_intake_for_patient(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT il.intake_date, p.drug_name, p.dosage, p.regularity
                 FROM intake_log il
                 JOIN prescriptions p ON il.prescription_id = p.id
                 WHERE p.patient_id = ?
                 ORDER BY il.intake_date DESC""", (patient_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_wellbeing_log(patient_id, days=90):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    c.execute("""SELECT log_date, score FROM wellbeing_log
                 WHERE patient_id=? AND log_date >= ?
                 ORDER BY log_date ASC""", (patient_id, cutoff))
    rows = c.fetchall()
    conn.close()
    return rows

def get_drug_interactions(drug1, drug2):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT severity, description FROM drug_interactions 
                 WHERE (drug1=? AND drug2=?) OR (drug1=? AND drug2=?)""", 
             (drug1, drug2, drug2, drug1))
    result = c.fetchone()
    conn.close()
    return result

def add_new_patient(last_name, first_name, birth_date, policy, location, contraindications=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO patients (last_name, first_name, birth_date, policy, location, created_at, contraindications) VALUES (?,?,?,?,?,?,?)",
             (last_name, first_name, birth_date, policy, location, datetime.now().isoformat(), contraindications))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def save_patient(pid, last_name, first_name, birth_date, policy, location, prescriptions_list, contraindications=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("UPDATE patients SET last_name=?, first_name=?, birth_date=?, policy=?, location=?, contraindications=? WHERE id=?",
             (last_name, first_name, birth_date, policy, location, contraindications, pid))
    
    c.execute("DELETE FROM prescriptions WHERE patient_id=?", (pid,))
    
    for drug in prescriptions_list:
        c.execute("""INSERT INTO prescriptions 
                     (patient_id, drug_name, dosage, regularity, start_date, end_date,
                      indication, instructions, food_relation, special_notes)
                     VALUES (?,?,?,?,?,?,?,?,?,?)""",
                 (pid, drug[0], drug[1], drug[2], "2026-05-01", "2026-06-01",
                  drug[3] if len(drug) > 3 else "",
                  drug[4] if len(drug) > 4 else "",
                  drug[5] if len(drug) > 5 else "",
                  drug[6] if len(drug) > 6 else ""))
    
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
    c.execute("""SELECT p.drug_name, p.dosage, p.regularity, p.start_date, 
                        pat.location, pat.birth_date, p.end_date
                 FROM prescriptions p
                 JOIN patients pat ON p.patient_id = pat.id""")
    data = c.fetchall()
    conn.close()
    return data

def get_all_patients_full():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, last_name, first_name, birth_date, policy, location, contraindications FROM patients")
    rows = c.fetchall()
    conn.close()
    return rows

def get_intake_adherence_all():
    """Получить данные приверженности по всем пациентам"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT p.patient_id, p.drug_name,
               COUNT(il.id) as taken_count,
               p.start_date, p.end_date, p.regularity
        FROM prescriptions p
        LEFT JOIN intake_log il ON p.id = il.prescription_id
        GROUP BY p.id
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def analyze_polypharmacy(patient_id):
    _, prescriptions = get_patient_by_id(patient_id)
    patient, _ = get_patient_by_id(patient_id)
    
    birth_date = datetime.strptime(patient[3], "%Y-%m-%d").date()
    age = (date.today() - birth_date).days // 365
    
    num_drugs = len(prescriptions)
    
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
    
    intake_dates = get_intake_dates_for_prescription(presc_id)
    intake_dates_set = set(intake_dates)
    
    calendar_data = cal.monthcalendar(selected_year, month_num)
    month_name = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"][month_num - 1]
    
    st.markdown(f"<h4 style='text-align: center; color: #0A2F6C;'>{month_name} {selected_year}</h4>", unsafe_allow_html=True)
    
    html_calendar = '<table class="calendar-table"><tr>'
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    
    for day in days:
        html_calendar += f'<td class="calendar-day-header">{day}<td>'
    html_calendar += '<tr><tr>'
    
    day_count = 0
    for week in calendar_data:
        for day in week:
            if day == 0:
                html_calendar += '<td class="calendar-day"><td>'
            else:
                date_str = f"{selected_year:04d}-{month_num:02d}-{day:02d}"
                is_taken = date_str in intake_dates_set
                bg_color = '#0A2F6C' if is_taken else '#FFFFFF'
                text_color = 'white' if is_taken else '#1F2A3E'
                font_weight = 'bold' if is_taken else 'normal'
                
                html_calendar += f'<td class="calendar-day" style="background-color: {bg_color}; color: {text_color}; font-weight: {font_weight};">{day}</td>'
            
            day_count += 1
            if day_count % 7 == 0:
                html_calendar += '<tr><tr>'
    
    html_calendar += '</table>'
    st.markdown(html_calendar, unsafe_allow_html=True)
    
    st.divider()
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
    
    # Противопоказания
    contraindications = st.text_area(
        "Противопоказания и аллергии пациента",
        placeholder="Например: аллергия на пенициллин, непереносимость лактозы...",
        height=80
    )
    
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
                pid = add_new_patient(last_name, first_name, birth_date.isoformat(), policy, location, contraindications)
                
                if items:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    for drug in items:
                        if drug[0].strip():
                            c.execute("""INSERT INTO prescriptions 
                                         (patient_id, drug_name, dosage, regularity, start_date, end_date,
                                          indication, instructions, food_relation, special_notes)
                                         VALUES (?,?,?,?,?,?,?,?,?,?)""",
                                     (pid, drug[0], drug[1], drug[2], date.today().isoformat(),
                                      (date.today() + timedelta(days=30)).isoformat(), "", "", "", ""))
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
    
    # Противопоказания
    new_contraindications = st.text_area(
        "Противопоказания и аллергии",
        value=patient[6] or "",
        placeholder="Например: аллергия на пенициллин, непереносимость лактозы...",
        height=80
    )
    
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
    
    col1, col2, col3, col4 = st.columns(4)
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
    
    with col4:
        if st.button(" Дашборд", use_container_width=True):
            st.session_state['dashboard_patient_id'] = pid
            st.session_state['page'] = 'patient_dashboard_doctor'
            st.rerun()
    
    st.divider()
    
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        if st.button("Сохранить", use_container_width=True):
            valid = [(d[0], d[1], d[2]) for d in items if d[0].strip()]
            save_patient(pid, new_last, new_first, new_birth.isoformat(), new_policy, new_location, valid, new_contraindications)
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
    
    analysis = analyze_polypharmacy(pid)
    num_drugs = analysis['num_drugs']
    age = analysis['age']
    risk_level = analysis['risk_level']
    interactions = analysis['interactions']
    
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
    
    st.subheader("Назначенные препараты")
    for presc in prescriptions:
        st.markdown(f"**{presc[1]}** ({presc[2]}) - {presc[3]}")
    
    st.divider()
    
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
    
    st.subheader("Графический анализ")
    
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

# ========================== ДАШБОРД ПАЦИЕНТА (для врача) ==========================
def patient_dashboard_doctor():
    pid = st.session_state.get('dashboard_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_dashboard'
        st.rerun()
    
    patient, prescriptions = get_patient_by_id(pid)
    full_name = f"{patient[1]} {patient[2]}"
    birth_date = datetime.strptime(patient[3], "%Y-%m-%d").date()
    age = (date.today() - birth_date).days // 365
    
    render_breadcrumb([f"Дашборд пациента: {full_name}"])
    
    st.markdown(f'<div class="card"><div class="card-header"> Аналитический дашборд: {full_name}, {age} лет</div>', unsafe_allow_html=True)
    
    if st.button("← Вернуться к редактированию"):
        st.session_state['page'] = 'doctor_edit'
        st.rerun()
    
    st.divider()
    
    # ---- Сводные метрики ----
    all_intake = get_all_intake_for_patient(pid)
    df_intake = pd.DataFrame(all_intake, columns=["date", "drug", "dosage", "regularity"]) if all_intake else pd.DataFrame(columns=["date","drug","dosage","regularity"])
    
    wellbeing = get_wellbeing_log(pid, 90)
    df_well = pd.DataFrame(wellbeing, columns=["date", "score"]) if wellbeing else pd.DataFrame(columns=["date","score"])
    
    num_drugs = len(prescriptions)
    
    # Приверженность за последние 30 дней
    if not df_intake.empty:
        last_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        recent = df_intake[df_intake["date"] >= last_30]
        expected = num_drugs * 30
        actual = len(recent)
        adherence_pct = min(100, int(actual / max(expected, 1) * 100))
    else:
        adherence_pct = 0
    
    avg_wellbeing = round(df_well["score"].mean(), 1) if not df_well.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="patient-metric-card">
            <div class="patient-metric-value">{num_drugs}</div>
            <div class="patient-metric-label">Активных препаратов</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        adh_color = "#22C55E" if adherence_pct >= 80 else ("#F59E0B" if adherence_pct >= 50 else "#EF4444")
        st.markdown(f"""
        <div class="patient-metric-card">
            <div class="patient-metric-value" style="color:{adh_color};">{adherence_pct}%</div>
            <div class="patient-metric-label">Приверженность (30 дней)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        well_color = "#22C55E" if avg_wellbeing >= 7 else ("#F59E0B" if avg_wellbeing >= 5 else "#EF4444")
        st.markdown(f"""
        <div class="patient-metric-card">
            <div class="patient-metric-value" style="color:{well_color};">{avg_wellbeing}/10</div>
            <div class="patient-metric-label">Среднее самочувствие</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        total_intakes = len(df_intake)
        st.markdown(f"""
        <div class="patient-metric-card">
            <div class="patient-metric-value">{total_intakes}</div>
            <div class="patient-metric-label">Всего приёмов за историю</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---- Вкладки дашборда ----
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Самочувствие", " Приверженность", " Расписание приёмов", " Сравнение препаратов", " Сводка"
    ])
    
    with tab1:
        st.subheader("Динамика самочувствия (90 дней)")
        st.caption("График показывает оценку самочувствия пациента от 1 (очень плохо) до 10 (отлично)")
        
        if not df_well.empty:
            df_well["date"] = pd.to_datetime(df_well["date"])
            df_well_sorted = df_well.sort_values("date")
            
            # Скользящее среднее
            df_well_sorted["ma7"] = df_well_sorted["score"].rolling(7, min_periods=1).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_well_sorted["date"],
                y=df_well_sorted["score"],
                mode="markers",
                name="Ежедневная оценка",
                marker=dict(color="#93C5FD", size=5, opacity=0.6),
            ))
            fig.add_trace(go.Scatter(
                x=df_well_sorted["date"],
                y=df_well_sorted["ma7"],
                mode="lines",
                name="Скользящее среднее (7 дней)",
                line=dict(color="#0A2F6C", width=3),
            ))
            fig.add_hrect(y0=7, y1=10, fillcolor="#D4EDDA", opacity=0.15, line_width=0, annotation_text="Хорошо", annotation_position="top left")
            fig.add_hrect(y0=4, y1=7, fillcolor="#FFF3CD", opacity=0.15, line_width=0, annotation_text="Умеренно", annotation_position="top left")
            fig.add_hrect(y0=0, y1=4, fillcolor="#F8D7DA", opacity=0.15, line_width=0, annotation_text="Плохо", annotation_position="top left")
            
            fig.update_layout(
                yaxis=dict(range=[0, 10.5], title="Оценка самочувствия (1-10)", tickvals=list(range(0, 11))),
                xaxis_title="Дата",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                height=400,
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Недельная сводка
            df_well_sorted["week"] = df_well_sorted["date"].dt.isocalendar().week
            weekly = df_well_sorted.groupby("week")["score"].mean().reset_index()
            weekly.columns = ["Неделя", "Среднее самочувствие"]
            
            col1, col2 = st.columns(2)
            with col1:
                trend = "⬆ Улучшение" if len(df_well_sorted) > 14 and df_well_sorted["score"].iloc[-7:].mean() > df_well_sorted["score"].iloc[:7].mean() else " Стабильно"
                st.info(f"**Тренд за период:** {trend}")
                st.write(f"**Минимальная оценка:** {df_well_sorted['score'].min()}/10")
                st.write(f"**Максимальная оценка:** {df_well_sorted['score'].max()}/10")
                st.write(f"**Дней с оценкой ≥ 7:** {(df_well_sorted['score'] >= 7).sum()} из {len(df_well_sorted)}")
            with col2:
                fig_hist = px.histogram(
                    df_well_sorted, x="score", nbins=10,
                    title="Распределение оценок самочувствия",
                    labels={"score": "Оценка", "count": "Дней"},
                    color_discrete_sequence=["#0A2F6C"]
                )
                st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Нет данных о самочувствии")
    
    with tab2:
        st.subheader("Приверженность к лечению по препаратам")
        st.caption("Показывает, как регулярно пациент принимает каждый препарат. 100% = каждый день без пропусков")
        
        if not df_intake.empty and prescriptions:
            adherence_data = []
            for presc in prescriptions:
                presc_id = presc[0]
                drug_name = presc[1]
                reg = presc[3]
                start = presc[4]
                end = presc[5]
                
                intake_dates = get_intake_dates_for_prescription(presc_id)
                
                # Ожидаемые приёмы в зависимости от регулярности
                times_per_day = 1
                if "2 раза" in reg:
                    times_per_day = 2
                elif "3 раза" in reg:
                    times_per_day = 3
                
                try:
                    s = datetime.strptime(start, "%Y-%m-%d")
                    e = min(datetime.strptime(end, "%Y-%m-%d"), datetime.now())
                    days_prescribed = max(1, (e - s).days)
                    expected_intakes = days_prescribed * times_per_day
                    actual_intakes = len(intake_dates)
                    adh = min(100, round(actual_intakes / expected_intakes * 100, 1))
                except:
                    adh = 0
                
                # Последние 7 дней
                last_7_dates = set([(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)])
                taken_7 = len([d for d in intake_dates if d in last_7_dates])
                
                adherence_data.append({
                    "drug": drug_name,
                    "adherence": adh,
                    "total": len(intake_dates),
                    "last_7": taken_7
                })
            
            df_adh = pd.DataFrame(adherence_data)
            
            # Горизонтальный бар-чарт
            colors = ["#22C55E" if a >= 80 else "#F59E0B" if a >= 50 else "#EF4444" for a in df_adh["adherence"]]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_adh["adherence"],
                y=df_adh["drug"],
                orientation="h",
                marker_color=colors,
                text=[f"{a}%" for a in df_adh["adherence"]],
                textposition="outside"
            ))
            fig.add_vline(x=80, line_dash="dash", line_color="#22C55E", annotation_text="Целевой уровень 80%")
            fig.update_layout(
                xaxis=dict(range=[0, 115], title="Приверженность (%)"),
                yaxis_title="",
                height=max(250, len(df_adh) * 50),
                showlegend=False,
                title="Приверженность к приёму по каждому препарату"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Тепловая карта приёмов за последние 30 дней
            st.subheader("Тепловая карта приёмов (последние 30 дней)")
            st.caption("Зелёный = принят, белый = пропущен")
            
            date_range = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
            heatmap_data = []
            drug_names = []
            
            for presc in prescriptions:
                intake_set = set(get_intake_dates_for_prescription(presc[0]))
                row = [1 if d in intake_set else 0 for d in date_range]
                heatmap_data.append(row)
                drug_names.append(presc[1])
            
            if heatmap_data:
                fig_heat = go.Figure(data=go.Heatmap(
                    z=heatmap_data,
                    x=[d[5:] for d in date_range], # только MM-DD
                    y=drug_names,
                    colorscale=[[0, "#F8D7DA"], [1, "#0A2F6C"]],
                    showscale=False,
                    hovertemplate="Дата: %{x}<br>Препарат: %{y}<br>%{z}<extra></extra>",
                ))
                fig_heat.update_layout(height=max(200, len(drug_names) * 40 + 100), xaxis_title="Дата (MM-DD)")
                st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Нет данных о приёмах")
    
    with tab3:
        st.subheader("Расписание ежедневных приёмов")
        st.caption("Когда и сколько раз в день пациент принимает препараты")
        
        schedule = {
            "Утро (06:00-12:00)": [],
            "День (12:00-18:00)": [],
            "Вечер (18:00-22:00)": [],
            "Ночь (22:00-06:00)": []
        }
        
        for presc in prescriptions:
            drug = presc[1]
            reg = presc[3]
            dosage = presc[2]
            
            if "утром" in str(presc[7]).lower() or "1 раз" in reg:
                schedule["Утро (06:00-12:00)"].append(f"{drug} {dosage}")
            if "вечером" in str(presc[7]).lower() or "2 раза" in reg:
                schedule["Вечер (18:00-22:00)"].append(f"{drug} {dosage}")
            if "3 раза" in reg:
                schedule["День (12:00-18:00)"].append(f"{drug} {dosage}")
        
        cols = st.columns(4)
        icons = {"Утро (06:00-12:00)": "", "День (12:00-18:00)": "", "Вечер (18:00-22:00)": "", "Ночь (22:00-06:00)": ""}
        
        for col, (time_slot, drugs) in zip(cols, schedule.items()):
            with col:
                st.markdown(f"**{icons[time_slot]} {time_slot}**")
                if drugs:
                    for d in drugs:
                        st.markdown(f"""
                        <div style="background:#EFF6FF;border-radius:6px;padding:0.5rem 0.8rem;margin-bottom:0.4rem;font-size:0.85rem;border-left:3px solid #3B82F6;">
                             {d}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#9CA3AF;font-size:0.85rem;'>Нет приёмов</span>", unsafe_allow_html=True)
        
        st.divider()
        
        # График нагрузки по дням недели
        if not df_intake.empty:
            df_intake["date"] = pd.to_datetime(df_intake["date"])
            df_intake["weekday"] = df_intake["date"].dt.day_name()
            
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            day_names_ru = {"Monday":"Понедельник","Tuesday":"Вторник","Wednesday":"Среда",
                           "Thursday":"Четверг","Friday":"Пятница","Saturday":"Суббота","Sunday":"Воскресенье"}
            
            weekly_counts = df_intake.groupby("weekday").size().reindex(day_order, fill_value=0)
            weekly_counts.index = [day_names_ru[d] for d in weekly_counts.index]
            
            fig_week = px.bar(
                x=weekly_counts.index,
                y=weekly_counts.values,
                title="Приёмы по дням недели (всего за историю)",
                labels={"x": "День недели", "y": "Количество приёмов"},
                color=weekly_counts.values,
                color_continuous_scale="Blues"
            )
            fig_week.update_layout(showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_week, use_container_width=True)
    
    with tab4:
        st.subheader("Сравнение препаратов")
        st.caption("Насколько регулярно принимается каждый препарат и как давно назначен")
        
        if prescriptions:
            drug_stats = []
            for presc in prescriptions:
                intake_dates_p = get_intake_dates_for_prescription(presc[0])
                
                try:
                    s = datetime.strptime(presc[4], "%Y-%m-%d")
                    e = min(datetime.strptime(presc[5], "%Y-%m-%d"), datetime.now())
                    days = max(1, (e - s).days)
                except:
                    days = 1
                
                adh = min(100, round(len(intake_dates_p) / max(days, 1) * 100, 1))
                
                drug_stats.append({
                    "Препарат": presc[1],
                    "Дозировка": presc[2],
                    "Регулярность": presc[3],
                    "Дней назначен": days,
                    "Всего приёмов": len(intake_dates_p),
                    "Приверженность %": adh,
                    "Показание": presc[6] if len(presc) > 6 else ""
                })
            
            df_stats = pd.DataFrame(drug_stats)
            
            # Пузырьковая диаграмма
            fig_bubble = px.scatter(
                df_stats,
                x="Дней назначен",
                y="Приверженность %",
                size="Всего приёмов",
                color="Препарат",
                hover_data=["Дозировка", "Регулярность", "Показание"],
                title="Препараты: длительность назначения vs приверженность",
                size_max=50,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_bubble.add_hline(y=80, line_dash="dash", line_color="#22C55E", annotation_text="Целевой уровень 80%")
            fig_bubble.update_layout(height=450)
            st.plotly_chart(fig_bubble, use_container_width=True)
            
            st.write("**Детальная статистика по препаратам:**")
            st.dataframe(
                df_stats[["Препарат","Дозировка","Регулярность","Дней назначен","Всего приёмов","Приверженность %"]],
                use_container_width=True,
                hide_index=True
            )
    
    with tab5:
        st.subheader("Общая сводка пациента")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            ** Пациент:** {full_name} 
            ** Возраст:** {age} лет 
            ** Город:** {patient[5] or '—'} 
            ** Полис:** {patient[4] or '—'} 
            """)
            
            if patient[6]:
                st.markdown(f"""
                <div style="background:#FFF0F0;border-left:3px solid #EF4444;padding:0.8rem;border-radius:4px;margin-top:0.5rem;">
                     <strong>Противопоказания:</strong> {patient[6]}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Радарная диаграмма здоровья
            categories = ["Приверженность", "Самочувствие", "Регулярность", "Стабильность", "Активность"]
            
            adh_norm = adherence_pct / 10
            well_norm = avg_wellbeing
            reg_norm = 8.5 # условно
            stab_norm = 7.0
            act_norm = 6.5
            
            values = [adh_norm, well_norm, reg_norm, stab_norm, act_norm]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(10,47,108,0.15)',
                line=dict(color='#0A2F6C', width=2),
                name="Пациент"
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[8, 8, 8, 8, 8, 8],
                theta=categories + [categories[0]],
                line=dict(color='#22C55E', dash='dash', width=1),
                name="Целевой уровень",
                mode="lines"
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                showlegend=True,
                title="Профиль здоровья пациента",
                height=350
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        st.divider()
        
        # Временная шкала назначений
        st.subheader("Временная шкала активных назначений")
        
        if prescriptions:
            gantt_data = []
            for presc in prescriptions:
                gantt_data.append(dict(
                    Task=presc[1],
                    Start=presc[4],
                    Finish=presc[5],
                    Dosage=presc[2]
                ))
            
            df_gantt = pd.DataFrame(gantt_data)
            
            fig_gantt = px.timeline(
                df_gantt,
                x_start="Start",
                x_end="Finish",
                y="Task",
                title="Период назначения каждого препарата",
                color="Task",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hover_data=["Dosage"]
            )
            fig_gantt.update_yaxes(autorange="reversed")
            fig_gantt.add_vline(x=datetime.now(), line_dash="dash", line_color="#EF4444", annotation_text="Сегодня")
            fig_gantt.update_layout(showlegend=False, height=max(250, len(prescriptions) * 40 + 100))
            st.plotly_chart(fig_gantt, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()

# ========================== СТРАНИЦА ПАЦИЕНТОВ ==========================
def doctor_patients_page():
    st.markdown('<div class="card"><div class="card-header">Список пациентов</div>', unsafe_allow_html=True)

    col_title, col_add_btn = st.columns([3, 1])
    with col_title:
        st.markdown('<h4 style="margin: 0 0 1rem 0;">Поиск по параметрам</h4>', unsafe_allow_html=True)
    with col_add_btn:
        if st.button(" Добавить", use_container_width=True, key="add_patient_btn"):
            st.session_state['page'] = 'add_patient'
            st.rerun()

    col1, col2, col3, col4, col_search = st.columns([1.2, 1.2, 1.2, 1.2, 1.2])
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
        patient_id_filter = st.text_input("", placeholder="No", key="search_id", label_visibility="collapsed")
    with col_search:
        st.markdown('<label class="search-label" style="opacity: 0;">.</label>', unsafe_allow_html=True)
        search_button = st.button(" Поиск", use_container_width=True, key="search_btn")

    st.divider()

    if search_button:
        patients = get_all_patients(search_name, birth_filter, location_filter, patient_id_filter)
    else:
        patients = get_all_patients()

    if not patients:
        st.info("Пациенты не найдены")
    else:
        cols_header = st.columns([0.5, 1.2, 1.2, 1.2, 1.5, 0.8, 0.8, 0.8, 0.8])
        headers = ["ID", "Фамилия", "Имя", "Дата рожд", "Местоположение", "Препараты", "Чат", "Дашборд", "Действия"]
        for col, header in zip(cols_header, headers):
            col.markdown(f"**{header}**")
        st.divider()

        for pid, last_name, first_name, birth_date, policy, location in patients:
            _, prescs = get_patient_by_id(pid)
            drugs = ", ".join([p[1] for p in prescs]) if prescs else "Нет"
            drugs_short = drugs if len(drugs) < 30 else drugs[:27] + "..."

            cols = st.columns([0.5, 1.2, 1.2, 1.2, 1.5, 0.8, 0.8, 0.8, 0.8])
            cols[0].write(str(pid))
            cols[1].write(last_name)
            cols[2].write(first_name)
            cols[3].write(birth_date)
            cols[4].write(location)
            cols[5].write(drugs_short)

            if cols[6].button(" Чат", key=f"chat_{pid}", use_container_width=True):
                st.session_state['chat_patient_id'] = pid
                st.session_state['page'] = 'doctor_chat'
                st.rerun()

            if cols[7].button("", key=f"dash_{pid}", use_container_width=True):
                st.session_state['dashboard_patient_id'] = pid
                st.session_state['page'] = 'patient_dashboard_doctor'
                st.rerun()

            if cols[8].button(" Ред.", key=f"edit_{pid}", use_container_width=True):
                st.session_state['edit_patient_id'] = pid
                st.session_state['page'] = 'doctor_edit'
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== АНАЛИТИКА ВРАЧА (РАСШИРЕННАЯ) ==========================
def drug_analytics_dashboard():
    render_breadcrumb(["Аналитика"])
    
    st.markdown('<div class="card"><div class="card-header">Аналитика лекарственных препаратов</div>', unsafe_allow_html=True)
    
    prescriptions = get_all_prescriptions()
    if not prescriptions:
        st.info("Нет данных для анализа")
        return
    
    df = pd.DataFrame(prescriptions, columns=["Препарат", "Дозировка", "Регулярность", "Дата_начала", "Город", "Дата_рождения", "Дата_окончания"])
    
    # Вычисляем возраст
    def calc_age(birth_str):
        try:
            bd = datetime.strptime(birth_str, "%Y-%m-%d").date()
            return (date.today() - bd).days // 365
        except:
            return None
    
    df["Возраст"] = df["Дата_рождения"].apply(calc_age)
    df["Возрастная_группа"] = df["Возраст"].apply(
        lambda a: "До 40 лет" if a and a < 40 else ("40-65 лет" if a and a < 65 else "65+ лет")
    )
    
    all_patients = get_all_patients_full()
    
    # ---- Метрики верхнего уровня ----
    st.subheader(" Основные показатели")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Всего назначений", len(df), help="Общее число записей о назначениях")
    with col2:
        st.metric("Уникальных препаратов", df["Препарат"].nunique(), help="Разных наименований препаратов в системе")
    with col3:
        st.metric("Пациентов", len(all_patients), help="Зарегистрировано в системе")
    with col4:
        avg_per_patient = round(len(df) / max(len(all_patients), 1), 1)
        st.metric("Препаратов/пациент", avg_per_patient, help="Среднее число назначений на одного пациента")
    with col5:
        multi_drug = len([p for p in all_patients if len(get_patient_by_id(p[0])[1]) >= 5])
        st.metric("Полипрагмазия (5+)", multi_drug, help="Пациентов с 5 и более препаратами")
    
    st.divider()
    
    # ---- Вкладки ----
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        " Топ препаратов",
        " По возрасту",
        " По городам",
        "⏰ Частота приёма",
        " Тренды",
        " Полипрагмазия",
        " Статистика"
    ])
    
    with tab1:
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.subheader("Топ 10 назначенных препаратов")
            st.caption("Чем длиннее полоска — тем чаще врачи назначают этот препарат")
            top_drugs = df["Препарат"].value_counts().head(10).reset_index()
            top_drugs.columns = ["Препарат", "Назначений"]
            
            fig = px.bar(
                top_drugs,
                x="Назначений",
                y="Препарат",
                orientation="h",
                color="Назначений",
                color_continuous_scale="Blues",
                title="Самые часто назначаемые препараты",
                text="Назначений"
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(height=450, showlegend=False, coloraxis_showscale=False,
                              yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Доля в общем объёме")
            st.caption("Процент от всех назначений")
            top_pie = df["Препарат"].value_counts().head(6)
            others = df["Препарат"].value_counts().iloc[6:].sum()
            labels = list(top_pie.index) + (["Остальные"] if others > 0 else [])
            values = list(top_pie.values) + ([others] if others > 0 else [])
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels, values=values,
                hole=0.45,
                textinfo="label+percent"
            )])
            fig_pie.update_layout(
                title="Структура назначений",
                height=450,
                showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown(f"""
        <div style="background:#EFF6FF;border-left:4px solid #3B82F6;padding:1rem;border-radius:4px;">
             <strong>Вывод:</strong> Самый назначаемый препарат — <strong>{top_drugs.iloc[0]['Препарат']}</strong> 
            ({top_drugs.iloc[0]['Назначений']} назначений). 
            Первые 3 препарата составляют {round(top_drugs.head(3)['Назначений'].sum()/len(df)*100, 1)}% всех назначений.
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Назначения по возрастным группам")
        st.caption("Смотрите, каким возрастным группам чаще всего назначают конкретные препараты")
        
        age_drug = df.groupby(["Возрастная_группа", "Препарат"]).size().reset_index(name="Количество")
        
        fig_age = px.bar(
            age_drug,
            x="Препарат",
            y="Количество",
            color="Возрастная_группа",
            barmode="group",
            title="Назначения препаратов по возрастным группам",
            color_discrete_map={"До 40 лет": "#93C5FD", "40-65 лет": "#3B82F6", "65+ лет": "#0A2F6C"},
            labels={"Возрастная_группа": "Возрастная группа"}
        )
        fig_age.update_layout(height=450, xaxis_tickangle=-30)
        st.plotly_chart(fig_age, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            age_counts = df["Возрастная_группа"].value_counts().reset_index()
            age_counts.columns = ["Группа", "Назначений"]
            fig_age_pie = px.pie(
                age_counts, values="Назначений", names="Группа",
                title="Доля назначений по возрасту",
                color_discrete_map={"До 40 лет": "#93C5FD", "40-65 лет": "#3B82F6", "65+ лет": "#0A2F6C"}
            )
            st.plotly_chart(fig_age_pie, use_container_width=True)
        
        with col2:
            st.write("**Среднее количество препаратов по группе:**")
            
            # Считаем по пациентам
            patient_age_drugs = []
            for pat in all_patients:
                pat_age = calc_age(pat[3])
                if pat_age is None:
                    continue
                grp = "До 40 лет" if pat_age < 40 else ("40-65 лет" if pat_age < 65 else "65+ лет")
                _, pat_prescs = get_patient_by_id(pat[0])
                patient_age_drugs.append({"group": grp, "n_drugs": len(pat_prescs)})
            
            df_pad = pd.DataFrame(patient_age_drugs)
            if not df_pad.empty:
                avg_by_group = df_pad.groupby("group")["n_drugs"].mean().reset_index()
                avg_by_group.columns = ["Группа", "Среднее препаратов"]
                avg_by_group["Среднее препаратов"] = avg_by_group["Среднее препаратов"].round(1)
                
                fig_avg = px.bar(
                    avg_by_group, x="Группа", y="Среднее препаратов",
                    title="Среднее число препаратов на пациента",
                    color="Группа",
                    color_discrete_map={"До 40 лет": "#93C5FD", "40-65 лет": "#3B82F6", "65+ лет": "#0A2F6C"},
                    text="Среднее препаратов"
                )
                fig_avg.update_traces(textposition="outside")
                fig_avg.update_layout(showlegend=False)
                st.plotly_chart(fig_avg, use_container_width=True)
    
    with tab3:
        st.subheader("Назначения по городам")
        st.caption("Географическое распределение назначений")
        
        city_counts = df["Город"].value_counts().reset_index()
        city_counts.columns = ["Город", "Назначений"]
        
        col1, col2 = st.columns(2)
        with col1:
            fig_city = px.bar(
                city_counts, x="Город", y="Назначений",
                title="Количество назначений по городам",
                color="Назначений",
                color_continuous_scale="Blues",
                text="Назначений"
            )
            fig_city.update_traces(textposition="outside")
            fig_city.update_layout(coloraxis_showscale=False, showlegend=False)
            st.plotly_chart(fig_city, use_container_width=True)
        
        with col2:
            # Топ препараты по городам
            city_drug = df.groupby(["Город", "Препарат"]).size().reset_index(name="Кол-во")
            top_city_drug = city_drug.sort_values("Кол-во", ascending=False).groupby("Город").head(3)
            
            fig_city_drug = px.bar(
                top_city_drug,
                x="Город", y="Кол-во",
                color="Препарат",
                title="Топ препараты по городам (топ-3 для каждого)",
                barmode="stack"
            )
            fig_city_drug.update_layout(height=400)
            st.plotly_chart(fig_city_drug, use_container_width=True)
        
        st.subheader("Пациентов по городам")
        pat_city = {}
        for pat in all_patients:
            c_val = pat[5] or "Не указан"
            pat_city[c_val] = pat_city.get(c_val, 0) + 1
        
        df_pat_city = pd.DataFrame(list(pat_city.items()), columns=["Город", "Пациентов"])
        fig_pat = px.pie(df_pat_city, values="Пациентов", names="Город",
                         title="Распределение пациентов по городам",
                         hole=0.35)
        st.plotly_chart(fig_pat, use_container_width=True)
    
    with tab4:
        st.subheader("Частота приёма препаратов")
        st.caption("1 раз в день = удобнее для пациента, 3 раза в день = сложнее соблюдать режим")
        
        col1, col2 = st.columns(2)
        with col1:
            freq_counts = df["Регулярность"].value_counts().reset_index()
            freq_counts.columns = ["Режим", "Назначений"]
            
            colors_freq = ["#0A2F6C", "#3B82F6", "#93C5FD"]
            fig_freq = px.bar(
                freq_counts, x="Режим", y="Назначений",
                title="Распределение по частоте приёма",
                color="Режим",
                color_discrete_sequence=colors_freq,
                text="Назначений"
            )
            fig_freq.update_traces(textposition="outside")
            fig_freq.update_layout(showlegend=False)
            st.plotly_chart(fig_freq, use_container_width=True)
        
        with col2:
            # Какие препараты назначают 2-3 раза в день
            multi_dose = df[df["Регулярность"].str.contains("2 раза|3 раза", na=False)]
            if not multi_dose.empty:
                md_counts = multi_dose["Препарат"].value_counts().head(8).reset_index()
                md_counts.columns = ["Препарат", "Кол-во"]
                fig_md = px.bar(
                    md_counts, x="Препарат", y="Кол-во",
                    title="Препараты с многократным приёмом (2-3 раза/день)",
                    color_discrete_sequence=["#3B82F6"],
                    text="Кол-во"
                )
                fig_md.update_traces(textposition="outside")
                fig_md.update_layout(showlegend=False, xaxis_tickangle=-20)
                st.plotly_chart(fig_md, use_container_width=True)
            else:
                st.info("Нет препаратов с многократным приёмом")
        
        st.markdown(f"""
        <div style="background:#F0FFF4;border-left:4px solid #22C55E;padding:1rem;border-radius:4px;margin-top:1rem;">
             <strong>Вывод:</strong> {freq_counts.iloc[0]['Режим']} — наиболее популярный режим приёма 
            ({round(freq_counts.iloc[0]['Назначений']/len(df)*100, 1)}% назначений).
            Одноразовые режимы улучшают приверженность пациентов.
        </div>
        """, unsafe_allow_html=True)
    
    with tab5:
        st.subheader("Тренды назначений во времени")
        st.caption("Как менялось количество назначений — смотрите рост или снижение интереса к препаратам")
        
        df_trend = df.copy()
        df_trend["Дата_начала"] = pd.to_datetime(df_trend["Дата_начала"], errors='coerce')
        df_trend = df_trend.dropna(subset=["Дата_начала"])
        df_trend["Месяц"] = df_trend["Дата_начала"].dt.to_period("M").astype(str)
        
        monthly = df_trend.groupby("Месяц").size().reset_index(name="Назначений")
        monthly = monthly.sort_values("Месяц")
        
        if len(monthly) > 1:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=monthly["Месяц"],
                y=monthly["Назначений"],
                mode="lines+markers",
                line=dict(color="#0A2F6C", width=3),
                marker=dict(size=8, color="#3B82F6"),
                fill="tozeroy",
                fillcolor="rgba(59,130,246,0.1)",
                name="Назначений в месяц"
            ))
            fig_trend.update_layout(
                title="Динамика назначений по месяцам",
                xaxis_title="Месяц",
                yaxis_title="Количество назначений",
                height=350,
                hovermode="x unified"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Топ препараты по месяцам
        st.subheader("Популярность препаратов по месяцам")
        top5_drugs = df["Препарат"].value_counts().head(5).index.tolist()
        df_top5 = df_trend[df_trend["Препарат"].isin(top5_drugs)]
        monthly_drugs = df_top5.groupby(["Месяц", "Препарат"]).size().reset_index(name="Назначений")
        
        if not monthly_drugs.empty:
            fig_lines = px.line(
                monthly_drugs,
                x="Месяц", y="Назначений", color="Препарат",
                title="Топ-5 препаратов: динамика назначений",
                markers=True
            )
            fig_lines.update_layout(height=400, hovermode="x unified")
            st.plotly_chart(fig_lines, use_container_width=True)
    
    with tab6:
        st.subheader("Анализ полипрагмазии по всем пациентам")
        st.caption("Полипрагмазия — когда пациент принимает 5 и более препаратов одновременно. Это повышает риск нежелательных взаимодействий.")
        
        poly_stats = {"1-2 препарата": 0, "3-4 препарата": 0, "5-6 препаратов": 0, "7+ препаратов": 0}
        risk_by_age = {"До 40 лет": {"low": 0, "medium": 0, "high": 0}, 
                       "40-65 лет": {"low": 0, "medium": 0, "high": 0},
                       "65+ лет": {"low": 0, "medium": 0, "high": 0}}
        
        for pat in all_patients:
            _, pat_prescs = get_patient_by_id(pat[0])
            n = len(pat_prescs)
            pat_age = calc_age(pat[3]) or 50
            
            if n <= 2:
                poly_stats["1-2 препарата"] += 1
            elif n <= 4:
                poly_stats["3-4 препарата"] += 1
            elif n <= 6:
                poly_stats["5-6 препаратов"] += 1
            else:
                poly_stats["7+ препаратов"] += 1
            
            age_grp = "До 40 лет" if pat_age < 40 else ("40-65 лет" if pat_age < 65 else "65+ лет")
            risk = "high" if n >= 7 else ("medium" if n >= 4 else "low")
            risk_by_age[age_grp][risk] += 1
        
        col1, col2 = st.columns(2)
        with col1:
            df_poly = pd.DataFrame(list(poly_stats.items()), columns=["Группа", "Пациентов"])
            colors_poly = {"1-2 препарата": "#22C55E", "3-4 препарата": "#F59E0B", 
                          "5-6 препаратов": "#EF4444", "7+ препаратов": "#7C3AED"}
            
            fig_poly = px.bar(
                df_poly, x="Группа", y="Пациентов",
                title="Распределение пациентов по числу препаратов",
                color="Группа",
                color_discrete_map=colors_poly,
                text="Пациентов"
            )
            fig_poly.update_traces(textposition="outside")
            fig_poly.update_layout(showlegend=False)
            st.plotly_chart(fig_poly, use_container_width=True)
        
        with col2:
            # Риск по возрастным группам — stacked bar
            risk_df_rows = []
            for age_grp, risks in risk_by_age.items():
                for risk_lvl, cnt in risks.items():
                    risk_df_rows.append({"Возраст": age_grp, "Риск": risk_lvl, "Пациентов": cnt})
            
            df_risk = pd.DataFrame(risk_df_rows)
            risk_colors = {"low": "#22C55E", "medium": "#F59E0B", "high": "#EF4444"}
            risk_labels_map = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}
            df_risk["Уровень риска"] = df_risk["Риск"].map(risk_labels_map)
            
            fig_risk = px.bar(
                df_risk, x="Возраст", y="Пациентов",
                color="Уровень риска",
                title="Уровень риска полипрагмазии по возрастам",
                color_discrete_map={"Низкий": "#22C55E", "Средний": "#F59E0B", "Высокий": "#EF4444"},
                barmode="stack",
                text="Пациентов"
            )
            fig_risk.update_layout(height=400)
            st.plotly_chart(fig_risk, use_container_width=True)
        
        high_risk_count = sum(1 for pat in all_patients if len(get_patient_by_id(pat[0])[1]) >= 7)
        st.markdown(f"""
        <div style="background:#FFF0F0;border-left:4px solid #EF4444;padding:1rem;border-radius:4px;margin-top:1rem;">
             <strong>Внимание:</strong> {high_risk_count} пациентов принимают 7+ препаратов одновременно. 
            Рекомендуется консультация клинического фармаколога.
        </div>
        """, unsafe_allow_html=True)
    
    with tab7:
        st.subheader("Детальная статистика")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Топ препараты по городам:**")
            city_top = df.groupby(["Город", "Препарат"]).size().reset_index(name="Кол-во")
            city_top = city_top.sort_values("Кол-во", ascending=False).groupby("Город").head(1)
            for _, row in city_top.iterrows():
                st.write(f"- **{row['Город']}**: {row['Препарат']} ({row['Кол-во']} назначений)")
        
        with col2:
            st.write("**Сводка по дозировкам:**")
            dosage_top = df["Дозировка"].value_counts().head(5)
            for dosage, count in dosage_top.items():
                st.write(f"- {dosage}: {count} назначений")
        
        st.divider()
        
        st.write("**Полная таблица назначений (первые 50):**")
        display_df = df[["Препарат", "Дозировка", "Регулярность", "Город", "Возрастная_группа"]].head(50)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== НАЛИЧИЕ ЛП ==========================
def drug_availability_page():
    render_breadcrumb(["Наличие лекарственных препаратов"])
    
    st.markdown('<div class="card"><div class="card-header">Проверка наличия лекарственных препаратов</div>', unsafe_allow_html=True)
    
    drug_name = st.text_input("Введите название препарата")
    
    if drug_name:
        all_prescriptions = get_all_prescriptions()
        df = pd.DataFrame(all_prescriptions, columns=["Препарат", "Дозировка", "Регулярность", "Дата", "Город", "ДатаРожд", "ДатаКонца"])
        
        matching_drugs = df[df["Препарат"].str.contains(drug_name, case=False, na=False)]
        
        if not matching_drugs.empty:
            st.subheader(f"Результаты по '{drug_name}':")
            
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
            st.write("**Подробная информация:**")
            st.dataframe(matching_drugs[["Препарат","Дозировка","Регулярность","Город"]], use_container_width=True, hide_index=True)
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

# ========================== ИИ АССИСТЕНТ ПАЦИЕНТА ==========================
import requests
import json

def get_ai_response(conversation_history, patient_info):
    """Получить ответ от ИИ ассистента через Groq API"""

    system_prompt = f"""Ты - медицинский ассистент пациента с дипломом кандидата наук по медицине.

Информация о пациенте:
- Имя: {patient_info['name']}
- Возраст: {patient_info['age']}
- Назначенные препараты: {', '.join([p[1] for p in patient_info['prescriptions']])}
- Противопоказания: {patient_info['contraindications'] or 'Нет информации'}

ВАЖНЫЕ ПРАВИЛА:
1. Отвечай доброжелательно и профессионально на русском языке.
2. Помогай пациенту понимать назначенные ему препараты.
3. НЕ ставь диагнозы - это прерогатива врача.
4. НЕ рекомендуй препараты или их замены - говори "вам нужно обсудить с врачом".
5. НЕ давай лишних медицинских советов - напоминай о консультации врача.
6. Спрашивай о самочувствии и его изменениях.
7. В каждом ответе подчеркивай: если нужен совет о лечении - обсуди с врачом.
8. Отвечай развернуто, объясняй назначения простым языком.

Начни разговор с приветствия и предложи помощь."""

    # Получаем API-ключ: сначала из secrets, потом из переменной окружения
    api_key = ""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    if not api_key:
        import os
        api_key = os.environ.get("GROQ_API_KEY", "")

    if not api_key:
        return ("Для работы ИИ-ассистента укажите API-ключ Groq.\n\n"
                "Создайте файл .streamlit/secrets.toml:\n"
                'GROQ_API_KEY = "gsk_...ваш_ключ..."')

    # Формируем историю: system идёт отдельным сообщением для Groq
    messages = [{"role": "system", "content": system_prompt}] + [
        {"role": msg["role"], "content": msg["content"]}
        for msg in conversation_history
    ]

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.7
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        elif response.status_code == 401:
            return "Ошибка авторизации: неверный API-ключ Groq. Проверьте GROQ_API_KEY в secrets.toml."
        elif response.status_code == 429:
            return "Превышен лимит запросов Groq. Подождите немного и попробуйте снова."
        else:
            err = response.text[:300] if response.text else "нет деталей"
            return f"Ошибка сервера ({response.status_code}): {err}"
    except requests.exceptions.Timeout:
        return "Время ожидания истекло. Сервер не ответил за 30 секунд. Попробуйте ещё раз."
    except requests.exceptions.ConnectionError:
        return "Нет подключения к интернету. Проверьте сетевое соединение."
    except Exception as e:
        return f"Непредвиденная ошибка: {str(e)}"

def ai_assistant_chat(pid, patient_data):
    """Интерфейс чата с ИИ ассистентом"""

    if 'ai_chat_history' not in st.session_state:
        st.session_state['ai_chat_history'] = []
    if 'ai_greeting_sent' not in st.session_state:
        st.session_state['ai_greeting_sent'] = False

    chat_history = st.session_state['ai_chat_history']

    # Приветствие при первом входе — коротко
    if not st.session_state['ai_greeting_sent'] and len(chat_history) == 0:
        with st.spinner("Ассистент печатает..."):
            greeting = get_ai_response(
                [{"role": "user", "content": (
                    "Привет! Представься одним предложением и задай один вопрос о самочувствии. "
                    "Строго не более 2 предложений."
                )}],
                patient_data
            )
        chat_history.append({
            "role": "assistant",
            "content": greeting,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        st.session_state['ai_greeting_sent'] = True

    # ---- Шапка чата ----
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0A2F6C, #1E3A8A); color: white;
                    padding: 0.75rem 1.2rem; border-radius: 10px 10px 0 0;
                    display: flex; align-items: center; gap: 0.8rem;">
            <div style="width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,0.2);
                        display:flex;align-items:center;justify-content:center;
                        font-weight:700;font-size:0.8rem;color:white;">AI</div>
            <div>
                <div style="font-weight:700;font-size:0.9rem;">Медицинский Ассистент</div>
                <div style="font-size:0.72rem;opacity:0.8;">Отвечает на вопросы о препаратах</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ---- Сообщения через st.chat_message (встроенный Streamlit-компонент) ----
    chat_area = st.container(height=420, border=True)
    with chat_area:
        for msg in chat_history:
            if msg["role"] == "assistant":
                with st.chat_message("assistant", avatar="🏥"):
                    # Разбиваем длинный текст на абзацы
                    text = msg["content"]
                    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
                    for p in paragraphs:
                        st.markdown(p)
                    if msg.get("timestamp"):
                        st.caption(msg["timestamp"])
            else:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
                    if msg.get("timestamp"):
                        st.caption(msg["timestamp"])

    # ---- Поле ввода — фиксированное, не растягивается ----
    col_input, col_send, col_clear = st.columns([0.74, 0.16, 0.10])
    with col_input:
        user_input = st.text_input(
            "Вопрос",
            placeholder="Напишите вопрос о препаратах...",
            label_visibility="collapsed",
            key="ai_chat_input"
        )
    with col_send:
        send = st.button("Отправить", use_container_width=True, key="ai_send")
    with col_clear:
        if st.button("Сброс", use_container_width=True, key="ai_clear"):
            st.session_state['ai_chat_history'] = []
            st.session_state['ai_greeting_sent'] = False
            st.rerun()

    # ---- Обработка отправки ----
    if send and user_input.strip():
        chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M")
        })

        api_history = [{"role": m["role"], "content": m["content"]} for m in chat_history]

        # Жёсткое ограничение на длину ответа
        api_history[-1]["content"] += (
            "\n\n[ВАЖНО: отвечай строго не более 80 слов. "
            "Используй 2-3 коротких абзаца или маркированный список. "
            "Никаких длинных объяснений.]"
        )

        with st.spinner("Ассистент печатает..."):
            ai_response = get_ai_response(api_history, patient_data)

        chat_history.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().strftime("%H:%M")
        })

        st.rerun()


# ========================== АВТОРИЗОВАННАЯ ЗОНА ПАЦИЕНТА ==========================
def patient_dashboard():
    """Полноценная авторизованная зона пациента"""
    
    # Для демо берём первого пациента из БД
    patients = get_all_patients()
    if not patients:
        st.error("Нет пациентов в системе")
        return
    
    # Берём пациента по имени пользователя (демо: просто первый)
    pid = patients[0][0]
    patient, prescriptions = get_patient_by_id(pid)
    full_name = f"{patient[1]} {patient[2]}"
    birth_date = datetime.strptime(patient[3], "%Y-%m-%d").date()
    age = (date.today() - birth_date).days // 365
    
    # Шапка
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0A2F6C 0%, #1E3A8A 100%); 
                border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; color: white;">
        <div style="font-size: 0.85rem; opacity: 0.8; margin-bottom: 0.3rem;">Личный кабинет пациента</div>
        <div style="font-size: 1.5rem; font-weight: 700;">{full_name}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">{age} лет · Полис: {patient[4]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## Мой кабинет")
        
        for tab in ["Мои препараты", "Расписание", "Рекомендации", "Заказ в аптеке", "Самочувствие", " Ассистент"]:
            if st.button(tab, key=f"p_sidebar_{tab}", use_container_width=True):
                st.session_state['patient_tab'] = tab
                st.rerun()
        
        st.markdown("---")
        if st.button("Выход", key="p_logout", use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state.clear()
            st.rerun()
    
    patient_tab = st.session_state.get('patient_tab', 'Мои препараты')
    
    # ================================================================
    # ВКЛ 1: МОИ ПРЕПАРАТЫ
    # ================================================================
    if patient_tab == "Мои препараты":
        st.markdown('<div class="card"><div class="card-header"> Мои назначенные препараты</div>', unsafe_allow_html=True)
        
        if not prescriptions:
            st.info("Нет активных назначений")
        else:
            contraindications = patient[6] or ""
            
            for presc in prescriptions:
                drug_name = presc[1]
                dosage = presc[2]
                regularity = presc[3]
                start_date = presc[4]
                end_date = presc[5]
                indication = presc[6] if len(presc) > 6 else "—"
                instructions = presc[7] if len(presc) > 7 else "—"
                food_relation = presc[8] if len(presc) > 8 else "—"
                special_notes = presc[9] if len(presc) > 9 else "—"
                
                is_active = datetime.strptime(end_date, "%Y-%m-%d").date() >= date.today()
                status_badge = '<span style="background:#D4EDDA;color:#155724;padding:2px 8px;border-radius:10px;font-size:0.8rem;font-weight:600;">Активный</span>' if is_active else '<span style="background:#F8D7DA;color:#721c24;padding:2px 8px;border-radius:10px;font-size:0.8rem;font-weight:600;">Завершён</span>'
                
                contra_warning = ""
                if contraindications and any(word.lower() in drug_name.lower() for word in contraindications.split(",")):
                    contra_warning = f'<div class="drug-contraindication"> Возможное взаимодействие с вашими противопоказаниями: {contraindications}</div>'
                
                st.markdown(f"""
                <div class="patient-drug-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div class="drug-name"> {drug_name}</div>
                        {status_badge}
                    </div>
                    <div class="drug-detail"> <b>Дозировка:</b> {dosage}</div>
                    <div class="drug-detail"> <b>Режим приёма:</b> {regularity}</div>
                    <div class="drug-detail"> <b>Связь с едой:</b> {food_relation}</div>
                    <div class="drug-detail"> <b>Период:</b> {start_date} — {end_date}</div>
                    <div class="drug-detail">🩺 <b>Причина назначения:</b> {indication}</div>
                    <div class="drug-detail"> <b>Как принимать:</b> {instructions}</div>
                    <div class="drug-detail"> <b>Особые указания:</b> {special_notes}</div>
                    {contra_warning}
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f" Инструкция по применению: {drug_name}"):
                    st.markdown(f"""
                    **Название препарата:** {drug_name}
                    
                    **Дозировка:** {dosage}
                    
                    **Способ применения:** {instructions}
                    
                    **Частота приёма:** {regularity}
                    
                    **Связь с приёмом пищи:** {food_relation}
                    
                    **Показание (зачем назначен):** {indication}
                    
                    **Особые указания:** {special_notes}
                    
                    ---
                    *Для получения полной инструкции обратитесь к лечащему врачу или фармацевту.*
                    """)
            
            if contraindications:
                st.markdown(f"""
                <div style="background:#FFF0F0;border-left:4px solid #EF4444;padding:1rem;border-radius:6px;margin-top:1rem;">
                     <strong>Ваши противопоказания и аллергии:</strong><br>{contraindications}
                    <br><small>Сообщите об этом врачу при любом новом назначении.</small>
                </div>
                """, unsafe_allow_html=True)

            # ========== ДОБАВЛЕННЫЙ БЛОК: QR-КОД И КОД ДЛЯ ФАРМАЦЕВТА ==========
            today_str = date.today().isoformat()
            code_seed = f"{pid}_{today_str}"
            code_hash = hashlib.md5(code_seed.encode()).hexdigest()
            daily_code = code_hash[:6].upper() # Например, "A3F8B1"
            qr_data = f"PatientCode:{daily_code}" # Данные для QR

            # Генерация QR-изображения в base64
            try:
                qr = qrcode.QRCode(box_size=4, border=2)
                qr.add_data(qr_data)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="#0A2F6C", back_color="white")
                buffered = BytesIO()
                qr_img.save(buffered, format="PNG")
                qr_base64 = base64.b64encode(buffered.getvalue()).decode()
                qr_html = f'<img src="data:image/png;base64,{qr_base64}" style="width: 140px; height: 140px;">'
            except ImportError:
                qr_html = '<div style="color: #DC3545;"> Библиотека qrcode не установлена</div>'
            except Exception as e:
                qr_html = f'<div style="color: #DC3545;">Ошибка: {e}</div>'

            # Отображаем информационный блок с контрастной рамкой
            st.markdown(f"""
            <div style="background: #EFF6FF; border: 2px solid #0A2F6C; border-radius: 14px; 
                        padding: 1.2rem; margin: 1.5rem 0 0.5rem 0; text-align: center;
                        box-shadow: 0 2px 8px rgba(10,47,108,0.1);">
                <div style="font-size: 1.2rem; font-weight: 700; color: #0A2F6C; margin-bottom: 0.5rem;">
                     Получение препаратов в аптеке
                </div>
                <div style="margin: 0.8rem 0; font-size: 1rem; line-height: 1.4;">
                    Покажите QR‑код или назовите код 
                    <strong style="font-size: 1.3rem; background: #FFFFFF; padding: 0.2rem 0.8rem; 
                                 border-radius: 20px; letter-spacing: 1px;">{daily_code}</strong>
                    <br>фармацевту, чтобы получить ваши лекарства.
                </div>
                <div style="display: flex; justify-content: center; margin: 0.5rem 0;">
                    {qr_html}
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #4B5563;">
                     Код обновляется каждую ночь в 00:00<br>
                    Актуально на сегодня: <strong>{date.today().strftime('%d.%m.%Y')}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # ========== КОНЕЦ ДОБАВЛЕННОГО БЛОКА ==========
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ================================================================
    # ВКЛ 2: РАСПИСАНИЕ / НАПОМИНАНИЯ
    # ================================================================
    elif patient_tab == "Расписание":
        st.markdown('<div class="card"><div class="card-header">⏰ Расписание приёма и напоминания</div>', unsafe_allow_html=True)
        
        today_str = date.today().strftime("%d %B %Y")
        st.markdown(f"**Сегодня:** {today_str}")
        
        st.subheader("Сегодняшний план приёма")
        
        if prescriptions:
            time_slots = [
                (" Утро", "07:00", "#EFF6FF", "#3B82F6"),
                (" День", "13:00", "#F0FFF4", "#22C55E"),
                (" Вечер", "20:00", "#FFF7ED", "#F59E0B"),
            ]
            
            for slot_name, slot_time, bg, color in time_slots:
                slot_drugs = []
                for presc in prescriptions:
                    reg = presc[3]
                    instructions = presc[7] if len(presc) > 7 else ""
                    
                    is_morning = "утром" in str(instructions).lower() or "1 раз" in reg
                    is_evening = "вечером" in str(instructions).lower() or "2 раза" in reg
                    is_day = "3 раза" in reg
                    
                    if "Утро" in slot_name and is_morning:
                        slot_drugs.append(presc)
                    elif "Вечер" in slot_name and is_evening:
                        slot_drugs.append(presc)
                    elif "День" in slot_name and is_day:
                        slot_drugs.append(presc)
                
                if slot_drugs:
                    for presc in slot_drugs:
                        taken_key = f"taken_{presc[0]}_{slot_name}"
                        is_taken = st.session_state.get(taken_key, False)
                        
                        st.markdown(f"""
                        <div class="reminder-card {'done' if is_taken else ''}">
                            <strong>{slot_name} {slot_time}</strong> · {presc[1]} {presc[2]}
                            {'<span style="color:#22C55E;font-weight:700;"> Принято</span>' if is_taken else ''}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if not is_taken:
                            if st.button(f" Отметить приём: {presc[1]}", key=f"mark_{presc[0]}_{slot_name}"):
                                st.session_state[taken_key] = True
                                st.rerun()
        
        st.divider()
        
        st.subheader(" Настройка напоминаний")
        st.caption("Выберите удобный способ получения напоминаний")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            push = st.toggle("Push-уведомления", value=True)
            st.caption("Уведомления на устройство")
        with col2:
            sms = st.toggle("SMS", value=False)
            st.caption("Сообщения на телефон")
        with col3:
            email = st.toggle("E-mail", value=False)
            st.caption("На электронную почту")
        
        if push or sms or email:
            methods = []
            if push: methods.append("Push")
            if sms: methods.append("SMS")
            if email: methods.append("E-mail")
            st.success(f" Напоминания включены: {', '.join(methods)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ================================================================
    # ВКЛ 3: РЕКОМЕНДАЦИИ ОТ ВРАЧЕЙ
    # ================================================================
    elif patient_tab == "Рекомендации":
        st.markdown('<div class="card"><div class="card-header"> Рекомендации специалистов</div>', unsafe_allow_html=True)
        
        st.caption("Все рекомендации по поддержанию здоровья от разных специалистов — в одном окне")
        
        # Демонстрационные рекомендации
        recommendations_demo = [
            {
                "doctor": "Кардиолог",
                "icon": "",
                "date": "15 мая 2026",
                "color": "#EFF6FF",
                "border": "#3B82F6",
                "items": [
                    "Принимать Метопролол строго по расписанию, не пропускать дозы",
                    "Контролировать АД 2 раза в день (утром и вечером), записывать показания",
                    "Ограничить потребление соли до 5г в сутки",
                    "Ходьба 30 минут в день в умеренном темпе",
                    "Избегать физических нагрузок при АД выше 160/100"
                ]
            },
            {
                "doctor": "Эндокринолог",
                "icon": "",
                "date": "10 мая 2026",
                "color": "#F0FFF4",
                "border": "#22C55E",
                "items": [
                    "Принимать Метформин строго во время еды",
                    "Контролировать уровень глюкозы крови натощак ежедневно",
                    "Придерживаться диеты с ограничением простых углеводов",
                    "Следующий анализ HbA1c — через 3 месяца",
                    "При уровне глюкозы > 14 ммоль/л — срочно связаться с врачом"
                ]
            },
            {
                "doctor": "Терапевт",
                "icon": "🩺",
                "date": "1 мая 2026",
                "color": "#FFF7ED",
                "border": "#F59E0B",
                "items": [
                    "Аспирин Кардио принимать только после еды",
                    "Ежегодный анализ крови (общий + биохимия) — следующий в ноябре",
                    "Отказ от курения",
                    "Контроль веса: целевое значение ИМТ < 25",
                ]
            }
        ]
        
        for rec in recommendations_demo:
            with st.expander(f"{rec['icon']} {rec['doctor']} — {rec['date']}", expanded=True):
                st.markdown(f"""
                <div style="background:{rec['color']};border-left:4px solid {rec['border']};padding:1rem;border-radius:6px;">
                """, unsafe_allow_html=True)
                for item in rec["items"]:
                    st.markdown(f"• {item}")
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # Сообщения от врача
        st.subheader(" Сообщения от врача")
        messages = get_messages(pid)
        if messages:
            for sender, msg, timestamp in messages[-5:]:
                time_str = datetime.fromisoformat(timestamp).strftime("%d.%m %H:%M")
                st.markdown(f"""
                <div style="background:#F8FAFC;border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.6rem;border:1px solid #E2E8F0;">
                    <strong>{sender}</strong> <span style="color:#9CA3AF;font-size:0.8rem;">{time_str}</span><br>
                    {msg}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Нет сообщений от врача")
        
        # Написать врачу
        new_msg = st.text_area("Написать сообщение врачу:", placeholder="Ваш вопрос или сообщение...", height=80)
        if st.button("Отправить сообщение"):
            if new_msg.strip():
                add_message(pid, full_name, new_msg)
                st.success("Сообщение отправлено!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ================================================================
    # ВКЛ 4: ЗАКАЗ В АПТЕКЕ
    # ================================================================
    elif patient_tab == "Заказ в аптеке":
        st.markdown('<div class="card"><div class="card-header"> Заказ препаратов в аптеке</div>', unsafe_allow_html=True)
        
        st.caption("Заказывайте все назначенные препараты в один клик")
        
        if prescriptions:
            st.subheader("Мои назначенные препараты")
            
            total_items = []
            for presc in prescriptions:
                is_active = datetime.strptime(presc[5], "%Y-%m-%d").date() >= date.today()
                if is_active:
                    key = f"order_{presc[0]}"
                    selected = st.checkbox(f" {presc[1]} {presc[2]} — {presc[3]}", value=True, key=key)
                    if selected:
                        total_items.append(presc[1])
            
            st.divider()
            
            if st.button(" Заказать все отмеченные в один клик", use_container_width=True):
                if total_items:
                    st.success(f" Заказ оформлен: {', '.join(total_items)}")
                    st.balloons()
                else:
                    st.warning("Выберите хотя бы один препарат")
        
        st.divider()
        
        # Ближайшие аптеки
        st.subheader(" Ближайшие аптеки")
        
        pharmacies = [
            {"name": "Аптека 36.6", "address": "ул. Ленина, 15", "distance": "0.3 км", "status": "Открыто", "status_color": "#22C55E", "hours": "08:00 - 22:00"},
            {"name": "Горздрав", "address": "пр. Мира, 42", "distance": "0.7 км", "status": "Открыто", "status_color": "#22C55E", "hours": "09:00 - 21:00"},
            {"name": "Ригла", "address": "ул. Садовая, 8", "distance": "1.2 км", "status": "Закрыто", "status_color": "#EF4444", "hours": "10:00 - 20:00"},
            {"name": "Самсон-Фарма", "address": "ул. Победы, 31", "distance": "1.8 км", "status": "Открыто", "status_color": "#22C55E", "hours": "08:00 - 00:00"},
        ]
        
        for ph in pharmacies:
            st.markdown(f"""
            <div class="pharmacy-card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <strong>{ph['name']}</strong> &nbsp;
                        <span style="color:{ph['status_color']};font-size:0.8rem;font-weight:600;">{ph['status']}</span><br>
                        <span style="color:#6B7280;font-size:0.85rem;">{ph['address']}</span><br>
                        <span style="color:#9CA3AF;font-size:0.82rem;">⏰ {ph['hours']}</span>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.1rem;font-weight:700;color:#0A2F6C;">{ph['distance']}</div>
                        <div style="font-size:0.8rem;color:#9CA3AF;">от вас</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.button(f"Проверить наличие", key=f"check_{ph['name']}", use_container_width=True)
            with col2:
                st.button(f"Заказать здесь", key=f"order_ph_{ph['name']}", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ================================================================
    # ВКЛ 5: САМОЧУВСТВИЕ
    # ================================================================
    elif patient_tab == "Самочувствие":
        st.markdown('<div class="card"><div class="card-header"> Мое самочувствие</div>', unsafe_allow_html=True)
        
        st.subheader("Оценить самочувствие сегодня")
        
        today_well_key = f"today_wellbeing_{date.today().isoformat()}"
        
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            score = st.slider("Как вы себя чувствуете? (1 = очень плохо, 10 = отлично)", 1, 10, 7)
        with col2:
            emoji = "" if score >= 8 else "" if score >= 6 else "" if score >= 4 else ""
            st.markdown(f"<div style='font-size:3rem;text-align:center;padding-top:0.5rem;'>{emoji}</div>", unsafe_allow_html=True)
        
        note = st.text_area("Заметки (необязательно):", placeholder="Напишите, как прошёл день...", height=70)
        
        if st.button(" Сохранить оценку"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            today_str = date.today().isoformat()
            c.execute("DELETE FROM wellbeing_log WHERE patient_id=? AND log_date=?", (pid, today_str))
            c.execute("INSERT INTO wellbeing_log (patient_id, log_date, score, note) VALUES (?,?,?,?)",
                     (pid, today_str, score, note))
            conn.commit()
            conn.close()
            st.success(f"Оценка {score}/10 сохранена! {emoji}")
            st.rerun()
        
        st.divider()
        
        # История самочувствия
        wellbeing = get_wellbeing_log(pid, 30)
        if wellbeing:
            df_well = pd.DataFrame(wellbeing, columns=["date", "score"])
            df_well["date"] = pd.to_datetime(df_well["date"])
            df_well = df_well.sort_values("date")
            
            df_well["ma7"] = df_well["score"].rolling(7, min_periods=1).mean()
            
            fig = go.Figure()
            
            # Цветные зоны
            fig.add_hrect(y0=7, y1=10.5, fillcolor="#D4EDDA", opacity=0.2, line_width=0)
            fig.add_hrect(y0=4, y1=7, fillcolor="#FFF3CD", opacity=0.2, line_width=0)
            fig.add_hrect(y0=0, y1=4, fillcolor="#F8D7DA", opacity=0.2, line_width=0)
            
            fig.add_trace(go.Bar(
                x=df_well["date"],
                y=df_well["score"],
                name="Ежедневная оценка",
                marker_color=[
                    "#22C55E" if s >= 7 else "#F59E0B" if s >= 4 else "#EF4444"
                    for s in df_well["score"]
                ],
                opacity=0.7
            ))
            fig.add_trace(go.Scatter(
                x=df_well["date"],
                y=df_well["ma7"],
                name="Тренд (7 дней)",
                line=dict(color="#0A2F6C", width=3),
                mode="lines"
            ))
            
            fig.update_layout(
                title="Самочувствие за последние 30 дней",
                yaxis=dict(range=[0, 10.5], title="Оценка (1-10)",
                           tickvals=[1,2,3,4,5,6,7,8,9,10],
                           ticktext=["1 ","2","3","4 ","5","6","7 ","8","9","10 "]),
                xaxis_title="Дата",
                height=380,
                hovermode="x unified",
                legend=dict(orientation="h")
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Связь препараты — самочувствие
            st.subheader(" Как препараты влияют на самочувствие")
            st.caption("Примерный анализ: сравнение дней приёма и без приёма")
            
            if prescriptions:
                correlation_data = []
                for presc in prescriptions[:4]: # Берём первые 4 для наглядности
                    intake_dates_p = set(get_intake_dates_for_prescription(presc[0]))
                    
                    well_with = []
                    well_without = []
                    
                    for _, row in df_well.iterrows():
                        d_str = row["date"].strftime("%Y-%m-%d")
                        if d_str in intake_dates_p:
                            well_with.append(row["score"])
                        else:
                            well_without.append(row["score"])
                    
                    avg_with = round(sum(well_with)/len(well_with), 1) if well_with else 0
                    avg_without = round(sum(well_without)/len(well_without), 1) if well_without else 0
                    
                    correlation_data.append({
                        "Препарат": presc[1],
                        "При приёме": avg_with,
                        "Без приёма": avg_without
                    })
                
                df_corr = pd.DataFrame(correlation_data)
                
                fig_corr = go.Figure()
                fig_corr.add_trace(go.Bar(
                    x=df_corr["Препарат"], y=df_corr["При приёме"],
                    name="Самочувствие при приёме",
                    marker_color="#0A2F6C"
                ))
                fig_corr.add_trace(go.Bar(
                    x=df_corr["Препарат"], y=df_corr["Без приёма"],
                    name="Самочувствие без приёма",
                    marker_color="#93C5FD"
                ))
                fig_corr.update_layout(
                    barmode="group",
                    title="Среднее самочувствие: с препаратом vs без",
                    yaxis=dict(range=[0, 10], title="Средняя оценка"),
                    height=350,
                    legend=dict(orientation="h")
                )
                st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Нет данных о самочувствии. Начните отслеживать уже сегодня!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ================================================================
    # ВКЛ 6: ИИ АССИСТЕНТ
    # ================================================================
    elif patient_tab == " Ассистент":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Подготавливаем данные пациента для ассистента
        patient_info = {
            "name": full_name,
            "age": age,
            "prescriptions": prescriptions,
            "contraindications": patient[6] or "Нет информации"
        }
        
        # Вызываем чат с ассистентом
        ai_assistant_chat(pid, patient_info)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
                st.session_state['page'] = 'doctor_dashboard' if role == 'doctor' else 'patient_zone'
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
        elif page == 'patient_dashboard_doctor':
            patient_dashboard_doctor()
        else:
            doctor_dashboard()
    elif role == 'patient':
        patient_dashboard()
    else:
        st.markdown('<h1>Неизвестная роль</h1>', unsafe_allow_html=True)
