import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import hashlib
import qrcode
from io import BytesIO
import base64

# ========================== НАСТРОЙКА СТРАНИЦЫ ==========================
st.set_page_config(
    page_title="Цифровая история назначений",
    page_icon="circle",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================== CSS - ПРОФЕССИОНАЛЬНЫЙ ДИЗАЙН ==========================
st.markdown("""
<style>
    .stApp {
        background-color: #F7F9FC !important;
    }
    
    /* ОСНОВНЫЕ ЭЛЕМЕНТЫ */
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, label, .stCaption {
        color: #1F2A3E !important;
        background-color: transparent !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #1F2A3E !important;
        font-weight: 600;
    }
    
    /* КАРТОЧКИ */
    .card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #E8ECF0;
    }
    
    .card-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1F2A3E;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #3B82F6;
    }
    
    /* ИНПУТЫ */
    .stTextInput input, .stSelectbox div, .stNumberInput input, .stDateInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #1F2A3E !important;
        border: 1px solid #D1D9E8 !important;
        border-radius: 8px !important;
    }
    
    /* КНОПКИ */
    .stButton button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stButton button:hover {
        background-color: #2563EB !important;
    }
    
    .btn-danger {
        background-color: #EF4444 !important;
    }
    
    .btn-danger:hover {
        background-color: #DC2626 !important;
    }
    
    .btn-success {
        background-color: #22C55E !important;
    }
    
    .btn-success:hover {
        background-color: #16A34A !important;
    }
    
    /* ТАБЛИЦЫ */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    
    th {
        background-color: #F0F2F5;
        color: #1F2A3E;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #3B82F6;
    }
    
    td {
        padding: 1rem;
        border-bottom: 1px solid #E8ECF0;
        color: #1F2A3E;
    }
    
    /* ВКЛАДКИ */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF;
        border-bottom: 2px solid #E8ECF0;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #6B7280;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        color: #3B82F6 !important;
    }
    
    /* ХЛЕБНЫЕ КРОШКИ */
    .breadcrumb {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
        color: #6B7280;
    }
    
    .breadcrumb span {
        color: #3B82F6;
        font-weight: 600;
    }
    
    /* ТОП ПАНЕЛЬ */
    .top-bar {
        background-color: #FFFFFF;
        padding: 1rem;
        border-bottom: 1px solid #E8ECF0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .user-info {
        font-size: 0.9rem;
        color: #6B7280;
    }
    
    .user-info strong {
        color: #1F2A3E;
    }
</style>
""", unsafe_allow_html=True)

# ========================== БД ==========================
DB_NAME = "clinic.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Таблица пациентов
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  last_name TEXT, first_name TEXT,
                  birth_date TEXT, policy TEXT, location TEXT,
                  created_at TEXT)''')
    
    # Таблица рецептов
    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  patient_id INTEGER, 
                  drug_name TEXT,
                  dosage_mg TEXT, 
                  regularity TEXT, 
                  start_date TEXT, 
                  end_date TEXT,
                  status TEXT,
                  pharmacy_available TEXT,
                  FOREIGN KEY(patient_id) REFERENCES patients(id))''')
    
    # Таблица сообщений (чат)
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  patient_id INTEGER,
                  sender TEXT,
                  message TEXT,
                  timestamp TEXT,
                  FOREIGN KEY(patient_id) REFERENCES patients(id))''')
    
    # Таблица истории приёмов
    c.execute('''CREATE TABLE IF NOT EXISTS intake_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  prescription_id INTEGER, 
                  intake_date TEXT,
                  FOREIGN KEY(prescription_id) REFERENCES prescriptions(id))''')
    
    conn.commit()
    
    # Проверяем есть ли тестовые данные
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] == 0:
        # Добавляем тестовых пациентов
        test_patients = [
            ("Иванов", "Иван", "1980-05-15", "1234567890", "Москва"),
            ("Петрова", "Анна", "1992-08-22", "0987654321", "Санкт-Петербург"),
            ("Сидоров", "Пётр", "1975-12-10", "1122334455", "Казань"),
            ("Волкова", "Елена", "1988-03-30", "5544332211", "Москва"),
            ("Соколов", "Сергей", "1995-07-18", "9876543210", "Екатеринбург"),
        ]
        
        for p in test_patients:
            c.execute('''INSERT INTO patients 
                        (last_name, first_name, birth_date, policy, location, created_at) 
                        VALUES (?,?,?,?,?,?)''',
                     (p[0], p[1], p[2], p[3], p[4], datetime.now().isoformat()))
            pid = c.lastrowid
            
            # Добавляем рецепты
            if pid == 1:
                c.execute('''INSERT INTO prescriptions 
                           (patient_id, drug_name, dosage_mg, regularity, start_date, end_date, status, pharmacy_available)
                           VALUES (?,?,?,?,?,?,?,?)''',
                         (pid, "Энап", "5", "1 раз в день", "2026-05-01", "2026-06-01", "АКТИВНЫЙ", "Да"))
                c.execute('''INSERT INTO prescriptions 
                           (patient_id, drug_name, dosage_mg, regularity, start_date, end_date, status, pharmacy_available)
                           VALUES (?,?,?,?,?,?,?,?)''',
                         (pid, "Аспирин Кардио", "100", "1 раз в день", "2026-05-01", "2026-06-01", "АКТИВНЫЙ", "Да"))
            elif pid == 2:
                c.execute('''INSERT INTO prescriptions 
                           (patient_id, drug_name, dosage_mg, regularity, start_date, end_date, status, pharmacy_available)
                           VALUES (?,?,?,?,?,?,?,?)''',
                         (pid, "Метформин", "500", "2 раза в день", "2026-05-01", "2026-06-01", "АКТИВНЫЙ", "Да"))
    
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
    
    c.execute('''SELECT id, last_name, first_name, birth_date, policy, location 
                FROM patients WHERE id=?''', (pid,))
    patient = c.fetchone()
    
    if patient:
        c.execute('''SELECT id, drug_name, dosage_mg, regularity, start_date, end_date, status, pharmacy_available 
                    FROM prescriptions WHERE patient_id=?''', (pid,))
        prescs = c.fetchall()
        conn.close()
        return patient, prescs
    
    conn.close()
    return None, []

def save_patient(pid, last_name, first_name, birth_date, policy, location, prescriptions_list):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''UPDATE patients 
                SET last_name=?, first_name=?, birth_date=?, policy=?, location=? 
                WHERE id=?''',
             (last_name, first_name, birth_date, policy, location, pid))
    
    c.execute("DELETE FROM prescriptions WHERE patient_id=?", (pid,))
    
    for drug in prescriptions_list:
        c.execute('''INSERT INTO prescriptions 
                   (patient_id, drug_name, dosage_mg, regularity, start_date, end_date, status, pharmacy_available)
                   VALUES (?,?,?,?,?,?,?,?)''',
                 (pid, drug[0], drug[1], drug[2], "2026-05-01", "2026-06-01", "АКТИВНЫЙ", "Да"))
    
    conn.commit()
    conn.close()

def add_new_patient(last_name, first_name, birth_date, policy, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO patients 
                (last_name, first_name, birth_date, policy, location, created_at)
                VALUES (?,?,?,?,?,?)''',
             (last_name, first_name, birth_date, policy, location, datetime.now().isoformat()))
    
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def add_message(patient_id, sender, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO messages (patient_id, sender, message, timestamp)
                VALUES (?,?,?,?)''',
             (patient_id, sender, message, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_messages(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''SELECT sender, message, timestamp FROM messages 
                WHERE patient_id=? ORDER BY timestamp ASC''', (patient_id,))
    
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

# ========================== КОМПОНЕНТЫ UI ==========================
def render_breadcrumb(path):
    """Отображает хлебные крошки"""
    breadcrumb_html = '<div class="breadcrumb">'
    for i, item in enumerate(path):
        if i == len(path) - 1:
            breadcrumb_html += f'<span>{item}</span>'
        else:
            breadcrumb_html += f'<span>{item}</span> > '
    breadcrumb_html += '</div>'
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

def render_top_bar(username, role):
    """Отображает верхнюю панель с кнопкой выхода"""
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        st.markdown(f"""
        <div class="user-info">
            Добро пожаловать, <strong>{username}</strong> ({role.upper()})
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪 ВЫХОД", use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state.clear()
            st.rerun()

def render_chat_panel(patient_id, current_user):
    """Отображает чат в карточке"""
    st.subheader("💬 Онлайн-чат")
    
    messages = get_messages(patient_id)
    
    # Отображение сообщений
    for sender, msg, timestamp in messages:
        time_obj = datetime.fromisoformat(timestamp)
        time_str = time_obj.strftime("%H:%M")
        
        if sender == current_user:
            st.markdown(f"""
            <div style="text-align: right; margin-bottom: 1rem;">
                <div style="display: inline-block; background-color: #3B82F6; color: white; 
                           padding: 0.75rem; border-radius: 12px; max-width: 70%;">
                    <div>{msg}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; margin-top: 0.25rem;">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: left; margin-bottom: 1rem;">
                <div style="display: inline-block; background-color: #F0F2F5; color: #1F2A3E; 
                           padding: 0.75rem; border-radius: 12px; max-width: 70%;">
                    <div><strong>{sender}</strong></div>
                    <div>{msg}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; margin-top: 0.25rem;">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Поле ввода сообщения
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        new_msg = st.text_input("Ваше сообщение:", key=f"msg_{patient_id}", label_visibility="collapsed")
    with col2:
        if st.button("Отправить", key=f"send_{patient_id}", use_container_width=True):
            if new_msg.strip():
                add_message(patient_id, st.session_state.get('user_name', 'Врач'), new_msg)
                st.rerun()

# ========================== СТРАНИЦА ВРАЧА ==========================
def doctor_dashboard():
    """Главная страница врача"""
    
    st.markdown("# 👨‍⚕️ Дашборд врача")
    
    render_top_bar(st.session_state.get('user_name'), st.session_state.get('role'))
    st.divider()
    
    # Вкладки
    tab1, tab2, tab3, tab4 = st.tabs(["Пациенты", "Ранее выписанные рецепты", "Отсроченное обслуживание", "Наличие ЛП в аптеках"])
    
    # ========== ВКЛ 1: ПАЦИЕНТЫ ==========
    with tab1:
        render_breadcrumb(["Врач", "Пациенты"])
        
        st.markdown('<div class="card"><div class="card-header">Список пациентов</div>', unsafe_allow_html=True)
        
        # Фильтры
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_name = st.text_input("🔍 Поиск по ФИ", placeholder="Иванов или Иван")
        with col2:
            birth_filter = st.text_input("📅 Дата рождения (ГГГГ-ММ-ДД)", placeholder="1980-05-15")
        with col3:
            location_filter = st.text_input("📍 Местоположение", placeholder="Москва")
        with col4:
            patient_id_filter = st.text_input("🆔 ID пациента", placeholder="1")
        
        patients = get_all_patients(search_name, birth_filter, location_filter, patient_id_filter)
        
        if not patients:
            st.info("Пациенты не найдены")
        else:
            st.markdown("### Результаты поиска")
            
            # Таблица
            cols_header = st.columns([0.5, 1, 1, 1.2, 2, 1, 0.8])
            cols_header[0].markdown("**ID**")
            cols_header[1].markdown("**Фамилия**")
            cols_header[2].markdown("**Имя**")
            cols_header[3].markdown("**Дата рожд**")
            cols_header[4].markdown("**Местоположение**")
            cols_header[5].markdown("**Препараты**")
            cols_header[6].markdown("**Действия**")
            
            st.divider()
            
            for patient in patients:
                pid, last_name, first_name, birth_date, policy, location = patient
                _, prescs = get_patient_by_id(pid)
                drugs = ", ".join([p[1] for p in prescs]) if prescs else "Нет"
                
                cols = st.columns([0.5, 1, 1, 1.2, 2, 1, 0.8])
                cols[0].write(str(pid))
                cols[1].write(last_name)
                cols[2].write(first_name)
                cols[3].write(birth_date)
                cols[4].write(location)
                cols[5].write(drugs if len(drugs) < 30 else drugs[:27] + "...")
                
                if cols[6].button("✏️", key=f"edit_{pid}"):
                    st.session_state['edit_patient_id'] = pid
                    st.session_state['page'] = 'doctor_edit'
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ВКЛ 2: РАНЕЕ ВЫПИСАННЫЕ ==========
    with tab2:
        render_breadcrumb(["Врач", "Ранее выписанные рецепты"])
        
        st.markdown('<div class="card"><div class="card-header">История рецептов</div>', unsafe_allow_html=True)
        
        patients = get_all_patients()
        
        history_data = []
        for pid, last_name, first_name, _, _, _ in patients:
            _, prescs = get_patient_by_id(pid)
            for p in prescs:
                if p[6] == "ВЫПОЛНЕН":  # status
                    history_data.append({
                        "ID Пациента": pid,
                        "Пациент": f"{last_name} {first_name}",
                        "Препарат": p[1],
                        "Дозировка": p[2],
                        "Дата выписки": p[4],
                        "Дата окончания": p[5]
                    })
        
        if history_data:
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("История рецептов пуста")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ВКЛ 3: ОТСРОЧЕННОЕ ОБСЛУЖИВАНИЕ ==========
    with tab3:
        render_breadcrumb(["Врач", "Отсроченное обслуживание"])
        
        st.markdown('<div class="card"><div class="card-header">Рецепты на отсроченном обслуживании</div>', unsafe_allow_html=True)
        
        st.info("Это рецепты, которые пациент может получить позже. Система отправит уведомление о готовности.")
        
        st.markdown("""
        **Функциональность:**
        - Отправка запроса на продление срока действия рецепта
        - Уведомление пациента о возможности получения ЛС
        - Бронирование лекарственных средств
        - Построение маршрута до аптеки
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ВКЛ 4: НАЛИЧИЕ ЛП ==========
    with tab4:
        render_breadcrumb(["Врач", "Наличие ЛП в аптеках"])
        
        st.markdown('<div class="card"><div class="card-header">Проверка наличия лекарственных препаратов</div>', unsafe_allow_html=True)
        
        drug_name = st.text_input("Введите название препарата", placeholder="Энап")
        
        if drug_name:
            # Симуляция данных о наличии
            availability_data = {
                "Аптека": ["Аптека №1 на Петровке", "Аптека №5 на Арбате", "Фармация на Тверской"],
                "Адрес": ["ул. Петровка, 25", "ул. Арбат, 12", "ул. Тверская, 38"],
                "Наличие": ["В наличии (10 шт)", "В наличии (5 шт)", "Нет в наличии"],
                "Цена": ["180 руб", "190 руб", "-"],
                "Расстояние": ["1.2 км", "2.5 км", "3.8 км"]
            }
            
            df_availability = pd.DataFrame(availability_data)
            st.dataframe(df_availability, use_container_width=True, hide_index=True)
        else:
            st.write("Введите название препарата для проверки наличия")
        
        st.markdown('</div>', unsafe_allow_html=True)

def doctor_edit_patient():
    """Редактирование данных пациента"""
    
    pid = st.session_state.get('edit_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_dashboard'
        st.rerun()
    
    patient, prescs = get_patient_by_id(pid)
    
    render_breadcrumb(["Врач", "Пациенты", f"Редактирование: {patient[1]} {patient[2]}"])
    
    st.markdown(f'<div class="card"><div class="card-header">Редактирование карточки пациента: {patient[1]} {patient[2]}</div>', unsafe_allow_html=True)
    
    render_top_bar(st.session_state.get('user_name'), st.session_state.get('role'))
    
    # Основные данные
    col1, col2 = st.columns(2)
    with col1:
        new_last = st.text_input("Фамилия", value=patient[1])
    with col2:
        new_first = st.text_input("Имя", value=patient[2])
    
    col1, col2 = st.columns(2)
    with col1:
        new_birth = st.date_input("Дата рождения", value=datetime.strptime(patient[3], "%Y-%m-%d").date())
    with col2:
        new_location = st.text_input("Местоположение", value=patient[5] or "")
    
    new_policy = st.text_input("Полис (необязательно)", value=patient[4] or "")
    
    st.divider()
    
    st.subheader("💊 Назначенные препараты")
    
    # Инициализация список препаратов
    if 'edit_prescriptions_list' not in st.session_state or st.session_state.get('edit_patient_id_prev') != pid:
        st.session_state['edit_prescriptions_list'] = [[p[1], p[2], p[3]] for p in prescs]
        st.session_state['edit_patient_id_prev'] = pid
    
    items = st.session_state['edit_prescriptions_list']
    
    # Отображение препаратов
    for idx, item in enumerate(items):
        col1, col2, col3, col4 = st.columns([2.5, 1, 1.5, 0.5])
        
        drug = col1.text_input(f"Название препарата", value=item[0], key=f"drug_edit_{idx}")
        dose = col2.text_input(f"мг", value=item[1], key=f"dose_edit_{idx}")
        reg = col3.text_input(f"Регулярность", value=item[2], key=f"reg_edit_{idx}")
        
        if col4.button("🗑", key=f"del_edit_{idx}"):
            items.pop(idx)
            st.rerun()
        
        items[idx] = [drug, dose, reg]
    
    if st.button("➕ Добавить препарат"):
        items.append(["", "", ""])
        st.rerun()
    
    st.divider()
    
    st.subheader("💬 Чат с пациентом")
    render_chat_panel(pid, st.session_state.get('user_name'))
    
    st.divider()
    
    # Кнопки сохранения
    col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
    
    with col1:
        if st.button("💾 Сохранить изменения", use_container_width=True):
            valid = [(d[0], d[1], d[2]) for d in items if d[0].strip()]
            save_patient(pid, new_last, new_first, new_birth.isoformat(), new_policy, new_location, valid)
            st.success("✅ Данные сохранены")
            if 'edit_prescriptions_list' in st.session_state:
                del st.session_state['edit_prescriptions_list']
                del st.session_state['edit_patient_id_prev']
            st.session_state['page'] = 'doctor_dashboard'
            st.rerun()
    
    with col2:
        if st.button("← Назад", use_container_width=True):
            if 'edit_prescriptions_list' in st.session_state:
                del st.session_state['edit_prescriptions_list']
                del st.session_state['edit_patient_id_prev']
            st.session_state['page'] = 'doctor_dashboard'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== СТРАНИЦА ПАЦИЕНТА ==========================
def patient_dashboard():
    """Дашборд пациента"""
    
    st.markdown("# 👤 Мой медицинский кабинет")
    
    render_top_bar(st.session_state.get('user_name'), st.session_state.get('role'))
    st.divider()
    
    render_breadcrumb(["Пациент", "Главная"])
    
    # Используем первого пациента как текущего
    pid = 1
    patient, prescs = get_patient_by_id(pid)
    
    st.markdown(f'<div class="card"><div class="card-header">Добро пожаловать, {patient[1]} {patient[2]}</div>', unsafe_allow_html=True)
    
    # Общая информация
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ID пациента", patient[0])
    with col2:
        st.metric("Активные рецепты", get_prescribed_count(pid))
    with col3:
        st.metric("Полис", patient[4] if patient[4] else "Не указан")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Рецепты
    st.markdown('<div class="card"><div class="card-header">💊 Мои назначения</div>', unsafe_allow_html=True)
    
    if not prescs:
        st.info("У вас нет активных рецептов")
    else:
        for p in prescs:
            with st.expander(f"💊 {p[1]} {p[2]} мг | {p[3]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Дозировка:** {p[2]} мг")
                    st.write(f"**Частота приема:** {p[3]}")
                    st.write(f"**Период:** {p[4]} – {p[5]}")
                    st.write(f"**Статус:** {p[6]}")
                
                with col2:
                    st.write(f"**Наличие в аптеке:** {p[7]}")
                    
                    if st.button(f"📱 Сформировать QR-код", key=f"qr_{p[0]}"):
                        # Генерируем QR код
                        url = f"https://pharmacy.example.com/rx/{p[0]}"
                        img = qrcode.make(url)
                        buffer = BytesIO()
                        img.save(buffer, format="PNG")
                        buffer.seek(0)
                        st.image(buffer, width=200)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================== СТРАНИЦА ВХОДА ==========================
def login_page():
    """Страница входа"""
    
    st.markdown("# Цифровая история назначений")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.subheader("🔐 Вход в систему")
        
        username = st.text_input("Логин", placeholder="врач1 или пациент1")
        password = st.text_input("Пароль", type="password", placeholder="password")
        role = st.selectbox("Роль", ["doctor", "patient"], format_func=lambda x: "👨‍⚕️ Врач" if x == "doctor" else "👤 Пациент")
        
        if st.button("Войти", use_container_width=True):
            if username and password:
                st.session_state['authenticated'] = True
                st.session_state['role'] = role
                st.session_state['user_name'] = username
                st.session_state['page'] = 'doctor_dashboard' if role == 'doctor' else 'patient_dashboard'
                st.rerun()
            else:
                st.error("Пожалуйста, введите логин и пароль")
        
        st.caption("Тестовые учетные данные: любые логин/пароль")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ========================== ИНИЦИАЛИЗАЦИЯ И МАРШРУТИЗАЦИЯ ==========================
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
