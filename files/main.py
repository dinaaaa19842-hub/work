import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import sqlite3
import hashlib
import qrcode
from io import BytesIO
import base64

# ========================== НАСТРОЙКА СТРАНИЦЫ ==========================
st.set_page_config(page_title="Цифровая история назначений", page_icon="🏥", layout="wide")

# ========================== CSS ==========================
st.markdown("""
<style>
    .stApp, .stApp > header, .stApp > div { background-color: #F7F9FC !important; }
    html, body, .stMarkdown, label, .stTextInput label, .stSelectbox label, .stNumberInput label, .stCheckbox label, .stRadio label, .stDateInput label, .stCaption {
        color: #1F2A3E !important; background-color: transparent;
    }
    h1, h2, h3, h4, h5, h6 { color: #1F2A3E !important; }
    .card { background-color: #FFFFFF; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #E8ECF0; }
    .card-header { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #3B82F6; display: inline-block; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input, .stTextArea textarea, .stDateInput input {
        background-color: #FFFFFF !important; color: #1F2A3E !important; border: 1px solid #D1D9E8 !important; border-radius: 8px !important;
    }
    .stButton button {
        background-color: #3B82F6 !important; color: #FFFFFF !important; border-radius: 12px !important; border: none !important;
        padding: 0.25rem 1rem !important; font-weight: 500 !important; width: 100px; white-space: nowrap;
    }
    .stButton button:hover { background-color: #2563EB !important; }
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #F0F2F5; color: #1F2A3E; padding: 0.75rem; text-align: left; }
    td { padding: 0.75rem; border-bottom: 1px solid #E8ECF0; color: #1F2A3E; }
</style>
""", unsafe_allow_html=True)

# ========================== БАЗА ДАННЫХ ==========================
DB_NAME = "clinic.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, last_name TEXT, first_name TEXT,
                  birth_date TEXT, policy TEXT, location TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, drug_name TEXT,
                  dosage_mg TEXT, regularity TEXT, start_date TEXT, end_date TEXT,
                  FOREIGN KEY(patient_id) REFERENCES patients(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS intake_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, prescription_id INTEGER, intake_date TEXT,
                  FOREIGN KEY(prescription_id) REFERENCES prescriptions(id))''')
    conn.commit()
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] == 0:
        test_patients = [
            ("Иванов", "Иван", "1980-05-15", "1234567890", "Москва"),
            ("Петрова", "Анна", "1992-08-22", "0987654321", "Санкт-Петербург"),
            ("Сидоров", "Пётр", "1975-12-10", "1122334455", "Казань")
        ]
        for p in test_patients:
            c.execute("INSERT INTO patients (last_name, first_name, birth_date, policy, location) VALUES (?,?,?,?,?)", p)
            pid = c.lastrowid
            if pid == 1:
                c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity, start_date, end_date) VALUES (?,?,?,?,?,?)",
                          (pid, "Энап", "5", "1 раз в день", "2026-05-01", "2026-06-01"))
                c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity, start_date, end_date) VALUES (?,?,?,?,?,?)",
                          (pid, "Аспирин Кардио", "100", "1 раз в день", "2026-05-01", "2026-06-01"))
                for d in range(3, 12):
                    c.execute("INSERT INTO intake_log (prescription_id, intake_date) VALUES (?, ?)", (1, f"2026-05-{d:02d}"))
            elif pid == 2:
                c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity, start_date, end_date) VALUES (?,?,?,?,?,?)",
                          (pid, "Метформин", "500", "2 раза в день", "2026-05-01", "2026-06-01"))
            elif pid == 3:
                c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity, start_date, end_date) VALUES (?,?,?,?,?,?)",
                          (pid, "Амлодипин", "5", "1 раз в день", "2026-05-01", "2026-06-01"))
    conn.commit()
    conn.close()

init_db()

# ========================== ФУНКЦИИ ДЛЯ БД ==========================
def get_all_patients(search_query="", birth_date_filter="", location_filter=""):
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

def get_patient_by_id(pid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, last_name, first_name, birth_date, policy, location FROM patients WHERE id=?", (pid,))
    patient = c.fetchone()
    if patient:
        c.execute("SELECT id, drug_name, dosage_mg, regularity, start_date, end_date FROM prescriptions WHERE patient_id=?", (pid,))
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
        c.execute("INSERT INTO prescriptions (patient_id, drug_name, dosage_mg, regularity, start_date, end_date) VALUES (?,?,?,?,?,?)",
                  (pid, drug[0], drug[1], drug[2], "2026-05-01", "2026-06-01"))
    conn.commit()
    conn.close()

def add_new_patient(last_name, first_name, birth_date, policy, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO patients (last_name, first_name, birth_date, policy, location) VALUES (?,?,?,?,?)",
              (last_name, first_name, birth_date, policy, location))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def get_intake_dates(prescription_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT intake_date FROM intake_log WHERE prescription_id=?", (prescription_id,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def add_intake(prescription_id, intake_date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO intake_log (prescription_id, intake_date) VALUES (?,?)", (prescription_id, intake_date))
    conn.commit()
    conn.close()

def check_interactions(drug_names):
    interactions_db = {
        ("Энап", "Аспирин Кардио"): "Энап + Аспирин Кардио: возможно снижение антигипертензивного эффекта",
        ("Метформин", "Аспирин Кардио"): "Риск гипогликемии",
    }
    warnings = []
    for i, d1 in enumerate(drug_names):
        for d2 in drug_names[i+1:]:
            if (d1, d2) in interactions_db:
                warnings.append(interactions_db[(d1, d2)])
            elif (d2, d1) in interactions_db:
                warnings.append(interactions_db[(d2, d1)])
    return warnings

def polypharmacy_analysis(num_drugs):
    if num_drugs <= 4:
        return ("Низкий", "#10B981", "Продолжайте терапию")
    elif num_drugs <= 7:
        return ("Средний", "#F59E0B", "Рекомендуется пересмотреть часть препаратов")
    else:
        return ("Высокий", "#EF4444", "Требуется консультация клинического фармаколога")

def generate_qr_html(prescription_id, drug_name):
    secret = "clinic_secret_key"
    token = hashlib.sha256(f"{prescription_id}{drug_name}{secret}".encode()).hexdigest()[:16]
    url = f"https://pharmacy.example.com/rx/{token}"
    img = qrcode.make(url)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<img src="data:image/png;base64,{img_base64}" width="120">'

# ========================== СТРАНИЦЫ ВРАЧА ==========================
def doctor_patients_list():
    st.markdown('<div class="card"><div class="card-header">Список пациентов</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        search_name = st.text_input("Поиск по фамилии/имени", placeholder="Иванов")
    with col2:
        birth_filter = st.text_input("Фильтр по дате рождения (ГГГГ-ММ-ДД)", placeholder="1980-05-15")
    with col3:
        location_filter = st.text_input("Фильтр по местоположению", placeholder="Москва")
    patients = get_all_patients(search_name, birth_filter, location_filter)
    if not patients:
        st.info("Пациенты не найдены")
    else:
        df = pd.DataFrame(patients, columns=["ID","Фамилия","Имя","Дата_рожд","Полис","Местоположение"])
        df["Препараты"] = [", ".join([p[1] for p in get_patient_by_id(pid)[1]]) for pid in df["ID"]]
        display_df = df[["ID","Фамилия","Имя","Дата_рожд","Местоположение","Препараты"]]
        # Вставляем колонки для кнопок
        cols = st.columns([0.8, 1, 1, 1, 1.5, 1.5, 0.8, 0.8, 0.8])
        headers = ["ID", "Фамилия", "Имя", "Дата_рожд", "Местоположение", "Препараты", "Редакт", "График", "Аналитика"]
        for i, header in enumerate(headers):
            cols[i].write(f"**{header}**")
        for _, row in display_df.iterrows():
            cols2 = st.columns([0.8, 1, 1, 1, 1.5, 1.5, 0.8, 0.8, 0.8])
            cols2[0].write(row["ID"])
            cols2[1].write(row["Фамилия"])
            cols2[2].write(row["Имя"])
            cols2[3].write(row["Дата_рожд"])
            cols2[4].write(row["Местоположение"])
            cols2[5].write(row["Препараты"])
            pid = row["ID"]
            if cols2[6].button("✏️", key=f"edit_{pid}"):
                st.session_state['edit_patient_id'] = pid
                st.session_state['page'] = 'doctor_edit'
                st.rerun()
            if cols2[7].button("📈", key=f"graph_{pid}"):
                st.session_state['graph_patient_id'] = pid
                st.session_state['page'] = 'doctor_graph'
                st.rerun()
            if cols2[8].button("📊", key=f"analytics_{pid}"):
                st.session_state['analytics_patient_id'] = pid
                st.session_state['page'] = 'doctor_analytics'
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def doctor_edit_patient():
    pid = st.session_state.get('edit_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_patients'
        st.rerun()
    patient, prescs = get_patient_by_id(pid)
    st.markdown(f"<div class='card-header'>Редактирование: {patient[1]} {patient[2]}</div>", unsafe_allow_html=True)

    # Основные данные без формы
    new_last = st.text_input("Фамилия", value=patient[1])
    new_first = st.text_input("Имя", value=patient[2])
    new_birth = st.date_input("Дата рождения", value=datetime.strptime(patient[3], "%Y-%m-%d").date())
    new_policy = st.text_input("Полис", value=patient[4] or "")
    new_location = st.text_input("Местоположение", value=patient[5] or "")

    st.subheader("Препараты")
    # Инициализация session_state для списка препаратов
    if 'edit_prescriptions_list' not in st.session_state or st.session_state.get('edit_patient_id_prev') != pid:
        st.session_state['edit_prescriptions_list'] = [list(p[1:4]) for p in prescs]
        st.session_state['edit_patient_id_prev'] = pid

    items = st.session_state['edit_prescriptions_list']
    # Отображение строк препаратов
    for idx, item in enumerate(items):
        col1, col2, col3, col4 = st.columns([3, 1, 2, 0.5])
        drug = col1.text_input(f"Название {idx+1}", value=item[0], key=f"drug_edit_{idx}")
        dose = col2.text_input(f"мг", value=item[1], key=f"dose_edit_{idx}")
        reg = col3.text_input(f"Регулярность", value=item[2], key=f"reg_edit_{idx}")
        if col4.button("🗑", key=f"del_edit_{idx}"):
            items.pop(idx)
            st.rerun()
        items[idx] = [drug, dose, reg]

    if st.button("➕ Добавить препарат"):
        items.append(["", "", ""])
        st.rerun()

    # Сохранение
    if st.button("💾 Сохранить изменения"):
        valid = [(d[0], d[1], d[2]) for d in items if d[0].strip()]
        save_patient(pid, new_last, new_first, new_birth.isoformat(), new_policy, new_location, valid)
        st.success("Данные сохранены")
        # Убираем временные данные
        del st.session_state['edit_prescriptions_list']
        del st.session_state['edit_patient_id_prev']
        st.session_state['page'] = 'doctor_patients'
        st.rerun()

    if st.button("← Назад к списку пациентов"):
        if 'edit_prescriptions_list' in st.session_state:
            del st.session_state['edit_prescriptions_list']
            del st.session_state['edit_patient_id_prev']
        st.session_state['page'] = 'doctor_patients'
        st.rerun()

def doctor_patient_graph():
    pid = st.session_state.get('graph_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_patients'
        st.rerun()
    patient, prescs = get_patient_by_id(pid)
    st.markdown(f"<div class='card-header'>График приёма: {patient[1]} {patient[2]}</div>", unsafe_allow_html=True)
    for p in prescs:
        dates = get_intake_dates(p[0])
        if dates:
            df = pd.DataFrame({"date": pd.to_datetime(dates)})
            daily = df.groupby(df["date"].dt.date).size().reset_index(name="count")
            fig = px.line(daily, x="date", y="count", markers=True, title=f"Приём {p[1]} {p[2]} мг",
                          labels={"count": "Количество таблеток", "date": "Дата"})
            fig.update_traces(line=dict(color="#3B82F6", width=2), marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write(f"Нет данных о приёме для {p[1]}")
    if st.button("← Назад к списку пациентов"):
        st.session_state['page'] = 'doctor_patients'
        st.rerun()

def doctor_patient_analytics():
    pid = st.session_state.get('analytics_patient_id')
    if not pid:
        st.session_state['page'] = 'doctor_patients'
        st.rerun()
    patient, prescs = get_patient_by_id(pid)
    st.markdown(f"<div class='card-header'>Аналитика: {patient[1]} {patient[2]}</div>", unsafe_allow_html=True)
    drugs = [p[1] for p in prescs if p[1]]
    if not drugs:
        st.info("Нет назначений")
    else:
        warnings = check_interactions(drugs)
        if warnings:
            st.warning("Обнаружены взаимодействия:")
            for w in warnings:
                st.write(f"- {w}")
        else:
            st.success("Взаимодействий не найдено")
        level, color, rec = polypharmacy_analysis(len(drugs))
        st.metric("Количество препаратов", len(drugs))
        st.markdown(f"**Уровень полипрагмазии:** <span style='color:{color}'>{level}</span>", unsafe_allow_html=True)
        st.info(f"Рекомендация: {rec}")
    if st.button("← Назад к списку пациентов"):
        st.session_state['page'] = 'doctor_patients'
        st.rerun()

def doctor_dashboard():
    st.markdown('<div class="logo-title">👨‍⚕️ Цифровая история назначений - Врач</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Пациенты", "Добавить пациента"])
    with tab1:
        doctor_patients_list()
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ➕ Добавление нового пациента")
        with st.form("new_patient_form"):
            last_name = st.text_input("Фамилия")
            first_name = st.text_input("Имя")
            birth_date = st.date_input("Дата рождения", value=date(1980,1,1))
            policy = st.text_input("Полис (необязательно)")
            location = st.text_input("Местоположение")
            submitted = st.form_submit_button("Добавить пациента")
            if submitted:
                if last_name and first_name:
                    pid = add_new_patient(last_name, first_name, birth_date.isoformat(), policy, location)
                    st.success(f"Пациент {last_name} {first_name} добавлен (ID {pid})")
                    st.rerun()
                else:
                    st.error("Фамилия и имя обязательны")
        st.markdown('</div>', unsafe_allow_html=True)

# ========================== СТРАНИЦА ПАЦИЕНТА ==========================
def patient_dashboard():
    st.markdown('<div class="logo-title">👤 Цифровая история назначений - Пациент</div>', unsafe_allow_html=True)
    pid = 1
    patient, prescs = get_patient_by_id(pid)
    st.markdown(f"<div class='card-header'>Ваши назначения: {patient[1]} {patient[2]}</div>", unsafe_allow_html=True)
    for p in prescs:
        with st.expander(f"💊 {p[1]} {p[2]} мг | {p[3]}"):
            st.write(f"**Период:** {p[4]} – {p[5]}")
            qr_html = generate_qr_html(p[0], p[1])
            st.markdown(qr_html, unsafe_allow_html=True)
            if st.button(f"Отметить приём", key=f"take_{p[0]}"):
                add_intake(p[0], date.today().isoformat())
                st.success("Приём отмечен")
                st.rerun()
    st.markdown("<div class='card-header'>Календарь приёмов</div>", unsafe_allow_html=True)
    all_dates = []
    for p in prescs:
        all_dates.extend(get_intake_dates(p[0]))
    if all_dates:
        all_dates = sorted(set(all_dates))
        st.write("Дни с отметками:")
        cols = st.columns(10)
        for i, d in enumerate(all_dates):
            day = d.split("-")[-1]
            cols[i % 10].markdown(f"<div style='background:#3B82F6; color:white; text-align:center; border-radius:50%; padding:0.5rem;'>{day}</div>", unsafe_allow_html=True)
    else:
        st.info("Нет отметок")

# ========================== ВХОД ==========================
def login_page():
    st.markdown('<div class="logo-title">Цифровая история назначений</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Вход в систему")
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        role = st.selectbox("Роль", ["doctor", "patient"])
        if st.button("Войти", use_container_width=True):
            st.session_state['authenticated'] = True
            st.session_state['role'] = role
            st.rerun()
        st.caption("Любые логин/пароль")
        st.markdown('</div>', unsafe_allow_html=True)

# ========================== МАРШРУТИЗАЦИЯ ==========================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['page'] = 'doctor_patients'

if not st.session_state.authenticated:
    login_page()
else:
    role = st.session_state.get('role')
    page = st.session_state.get('page', 'doctor_patients')
    if role == 'doctor':
        if page == 'doctor_patients':
            doctor_dashboard()
        elif page == 'doctor_edit':
            doctor_edit_patient()
        elif page == 'doctor_graph':
            doctor_patient_graph()
        elif page == 'doctor_analytics':
            doctor_patient_analytics()
        else:
            doctor_dashboard()
    else:
        patient_dashboard()
