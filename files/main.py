import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import sqlite3
import hashlib
import os

# ========================== НАСТРОЙКА СТРАНИЦЫ ==========================
st.set_page_config(
    page_title="Цифровая история назначений",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================== ЦВЕТА И CSS ==========================
st.markdown("""
<style>
    /* Общий фон */
    .stApp, .stApp > header, .stApp > div {
        background-color: #F7F9FC !important;
    }
    /* Все тексты тёмные */
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, label, .stTextInput label, .stSelectbox label, .stNumberInput label, .stCheckbox label, .stRadio label, .stDateInput label, .stCaption {
        color: #1F2A3E !important;
        background-color: transparent;
    }
    /* Заголовки */
    h1, h2, h3, h4, h5, h6 {
        color: #1F2A3E !important;
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
    /* Поля ввода */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input, .stTextArea textarea, .stDateInput input {
        background-color: #FFFFFF !important;
        color: #1F2A3E !important;
        border: 1px solid #D1D9E8 !important;
        border-radius: 8px !important;
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
</style>
""", unsafe_allow_html=True)

# ========================== БАЗА ДАННЫХ ==========================
DB_NAME = "patients.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Таблица пациентов
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  last_name TEXT,
                  first_name TEXT,
                  birth_date TEXT,
                  policy TEXT,
                  location TEXT)''')
    # Таблица назначенных препаратов
    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  patient_id INTEGER,
                  drug_name TEXT,
                  dosage_mg TEXT,
                  regularity TEXT,
                  FOREIGN KEY(patient_id) REFERENCES patients(id))''')
    conn.commit()
    # Добавим тестовых пациентов, если таблица пуста
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] == 0:
        test_patients = [
            ("Иванов", "Иван", "1980-05-15", "1234567890", "Москва"),
            ("Петрова", "Анна", "1992-08-22", "0987654321", "Санкт-Петербург"),
            ("Сидоров", "Петр", "1975-12-10", "1122334455", "Казань"),
        ]
        for p in test_patients:
            c.execute("INSERT INTO patients (last_name, first_name, birth_date, policy, location) VALUES (?,?,?,?,?)", p)
            patient_id = c.lastrowid
            if patient_id == 1:
                c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity) VALUES (?,?,?,?)", (patient_id, "Энап", "5", "1 раз в день"))
                c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity) VALUES (?,?,?,?)", (patient_id, "Аспирин Кардио", "100", "1 раз в день"))
            elif patient_id == 2:
                c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity) VALUES (?,?,?,?)", (patient_id, "Метформин", "500", "2 раза в день"))
            elif patient_id == 3:
                c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity) VALUES (?,?,?,?)", (patient_id, "Амлодипин", "5", "1 раз в день"))
        conn.commit()
    conn.close()

init_db()

def get_all_patients(search_query="", birth_date_filter=None, location_filter=""):
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
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_patient_by_id(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, last_name, first_name, birth_date, policy, location FROM patients WHERE id=?", (patient_id,))
    patient = c.fetchone()
    if patient:
        c.execute("SELECT id, drug_name, dosage_mg, regularity FROM prescriptions WHERE patient_id=?", (patient_id,))
        prescriptions = c.fetchall()
        conn.close()
        return patient, prescriptions
    conn.close()
    return None, []

def save_patient(patient_id, last_name, first_name, birth_date, policy, location, prescriptions_list):
    """
    prescriptions_list: список кортежей (drug_name, dosage_mg, regularity) для этого пациента
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Обновляем данные пациента
    c.execute("UPDATE patients SET last_name=?, first_name=?, birth_date=?, policy=?, location=? WHERE id=?",
              (last_name, first_name, birth_date, policy, location, patient_id))
    # Удаляем старые назначения и вставляем новые
    c.execute("DELETE FROM prescriptions WHERE patient_id=?", (patient_id,))
    for drug in prescriptions_list:
        c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity) VALUES (?,?,?,?)",
                  (patient_id, drug[0], drug[1], drug[2]))
    conn.commit()
    conn.close()

def add_new_patient(last_name, first_name, birth_date, policy, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO patients (last_name, first_name, birth_date, policy, location) VALUES (?,?,?,?,?)",
              (last_name, first_name, birth_date, policy, location))
    patient_id = c.lastrowid
    conn.commit()
    conn.close()
    return patient_id

# ========================== СТРАНИЦА ВРАЧА ==========================
def doctor_dashboard():
    st.markdown('<div class="logo-title">👨‍⚕️ Цифровая история назначений - Врач</div>', unsafe_allow_html=True)
    
    # Вкладки
    tab1, tab2 = st.tabs(["Пациенты", "Добавить пациента"])
    
    # ========== ВКЛАДКА ПАЦИЕНТЫ ==========
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Поиск и фильтрация пациентов")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("Поиск по фамилии/имени", placeholder="Введите фамилию...")
        with col2:
            birth_filter = st.text_input("Фильтр по дате рождения (ГГГГ-ММ-ДД)", placeholder="например 1980-05-15")
        with col3:
            location_filter = st.text_input("Фильтр по местоположению", placeholder="Город")
        
        patients = get_all_patients(search_name, birth_filter if birth_filter else None, location_filter)
        
        if not patients:
            st.info("Пациенты не найдены")
        else:
            # Таблица пациентов
            df = pd.DataFrame(patients, columns=["ID", "Фамилия", "Имя", "Дата рождения", "Полис", "Местоположение"])
            # Добавляем колонку "Назначенные препараты" (выводим список названий)
            drug_list = []
            for pid in df["ID"]:
                _, presc = get_patient_by_id(pid)
                drug_names = ", ".join([p[1] for p in presc])
                drug_list.append(drug_names if drug_names else "Нет")
            df["Назначенные препараты"] = drug_list
            
            # Выбираем колонки для отображения
            display_df = df[["ID", "Фамилия", "Имя", "Дата рождения", "Местоположение", "Назначенные препараты"]]
            st.dataframe(display_df, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### ✏️ Редактирование карточки пациента")
            # Выбор пациента для редактирования
            patient_options = {f"{row['ID']} - {row['Фамилия']} {row['Имя']}": row['ID'] for _, row in df.iterrows()}
            selected_label = st.selectbox("Выберите пациента для редактирования", list(patient_options.keys()))
            selected_id = patient_options[selected_label]
            
            # Загружаем данные
            patient, prescriptions = get_patient_by_id(selected_id)
            if patient:
                st.session_state['edit_patient_id'] = selected_id
                st.session_state['edit_patient_data'] = patient
                st.session_state['edit_prescriptions'] = prescriptions
                edit_patient_form()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ВКЛАДКА ДОБАВИТЬ ПАЦИЕНТА ==========
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ➕ Добавление нового пациента")
        with st.form("new_patient_form"):
            last_name = st.text_input("Фамилия")
            first_name = st.text_input("Имя")
            birth_date = st.date_input("Дата рождения", value=date(1980,1,1))
            policy = st.text_input("Полис (необязательно)")
            location = st.text_input("Местоположение (город)")
            submitted = st.form_submit_button("Добавить пациента")
            if submitted:
                if last_name and first_name:
                    pid = add_new_patient(last_name, first_name, birth_date.isoformat(), policy, location)
                    st.success(f"Пациент {last_name} {first_name} добавлен с ID {pid}")
                    st.rerun()
                else:
                    st.error("Фамилия и имя обязательны")
        st.markdown('</div>', unsafe_allow_html=True)

def edit_patient_form():
    """Форма редактирования карточки пациента и препаратов"""
    patient_id = st.session_state['edit_patient_id']
    patient = st.session_state['edit_patient_data']
    # patient: (id, last_name, first_name, birth_date, policy, location)
    _, last_name, first_name, birth_date_str, policy, location = patient
    
    st.markdown(f"### Редактирование: {last_name} {first_name} (ID: {patient_id})")
    
    with st.form(key="edit_patient_form"):
        new_last_name = st.text_input("Фамилия", value=last_name)
        new_first_name = st.text_input("Имя", value=first_name)
        new_birth_date = st.date_input("Дата рождения", value=datetime.strptime(birth_date_str, "%Y-%m-%d").date())
        new_policy = st.text_input("Полис", value=policy if policy else "")
        new_location = st.text_input("Местоположение", value=location if location else "")
        
        st.markdown("#### 💊 Назначенные препараты")
        # Получаем текущий список препаратов из session_state
        prescriptions = st.session_state.get('edit_prescriptions', [])
        # prescriptions: список кортежей (id, drug_name, dosage_mg, regularity)
        presc_list = []
        for i, p in enumerate(prescriptions):
            col1, col2, col3, col4 = st.columns([3,2,2,1])
            with col1:
                drug_name = st.text_input(f"Препарат {i+1}", value=p[1], key=f"drug_name_{i}")
            with col2:
                dosage = st.text_input(f"Дозировка (мг)", value=p[2], key=f"dosage_{i}")
            with col3:
                regularity = st.text_input(f"Регулярность", value=p[3], key=f"reg_{i}")
            with col4:
                if st.form_submit_button("Удалить", key=f"del_{i}"):
                    # Удаляем этот препарат (через session_state, потом сохраним)
                    prescriptions.pop(i)
                    st.rerun()
            presc_list.append((drug_name, dosage, regularity))
        
        # Кнопка добавления нового препарата
        if st.form_submit_button("➕ Добавить препарат"):
            prescriptions.append((0, "", "", ""))  # временная заглушка
            st.rerun()
        
        # Сохранение
        if st.form_submit_button("💾 Сохранить изменения"):
            # Собираем список валидных препаратов (не пустые)
            valid_prescs = [(d[0], d[1], d[2]) for d in presc_list if d[0].strip()]
            save_patient(patient_id, new_last_name, new_first_name, new_birth_date.isoformat(), new_policy, new_location, valid_prescs)
            st.success("Данные пациента сохранены")
            # Обновляем session_state
            st.session_state['edit_patient_data'] = (patient_id, new_last_name, new_first_name, new_birth_date.isoformat(), new_policy, new_location)
            st.session_state['edit_prescriptions'] = valid_prescs
            st.rerun()

# ========================== СТРАНИЦА ПАЦИЕНТА (минимальная) ==========================
def patient_dashboard():
    st.markdown('<div class="logo-title">👤 Цифровая история назначений - Пациент</div>', unsafe_allow_html=True)
    # Здесь можно разместить информацию о пациенте, но пока оставим простую заглушку
    st.info("Здесь будут отображаться ваши назначения и история. Функционал в разработке.")

# ========================== ВХОД ==========================
def login_page():
    st.markdown('<div class="logo-title">Цифровая история назначений</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Вход в систему")
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        role = st.selectbox("Роль", ["doctor", "patient"])   # фармацевт пока убрали
        if st.button("Войти", use_container_width=True):
            # Для демо любой логин/пароль
            st.session_state['authenticated'] = True
            st.session_state['role'] = role
            st.rerun()
        st.caption("Любые логин и пароль. Выберите роль doctor или patient.")
        st.markdown('</div>', unsafe_allow_html=True)

# ========================== МАРШРУТИЗАЦИЯ ==========================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state.authenticated:
    login_page()
else:
    if st.session_state.get('role') == 'doctor':
        doctor_dashboard()
    else:
        patient_dashboard()
