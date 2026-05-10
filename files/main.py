import streamlit as st
import pandas as pd
import plotly.express as px
import qrcode
from io import BytesIO
from datetime import datetime, date
import hashlib
import random
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ========================== НАСТРОЙКА СТРАНИЦЫ ==========================
st.set_page_config(
    page_title="Цифровая история назначений",
    page_icon=":medical_symbol:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Принудительно белый фон везде */
    .stApp, .stApp > header, .stApp > div {
        background-color: #FFFFFF !important;
    }
    /* Все тексты и метки — чёрные */
    body, .stMarkdown, label, .stTextInput label, .stSelectbox label, .stNumberInput label, .stTextArea label, .stDateInput label, .stCheckbox label, .stCaption, .stAlert {
        color: #111827 !important;
    }
    /* Поля ввода — белые, текст чёрный */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input, .stTextArea textarea, .stDateInput input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
    }
    /* Выпадающие списки */
    .stSelectbox div[data-baseweb="select"] ul {
        background-color: #FFFFFF !important;
        color: #111827 !important;
    }
    /* Кнопки — синий фон, белый текст */
    .stButton button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 500 !important;
    }
    .stButton button:hover {
        background-color: #2563EB !important;
    }
    /* Карточки и прочие блоки (не меняйте, если всё устраивает) */
    .card, .metric-card {
        background-color: #F9FAFB !important;
        color: #111827 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========================== CSS ДЛЯ ПРОФЕССИОНАЛЬНОГО ВИДА ==========================
st.markdown("""
<style>
    /* Общий фон и шрифт */
    .stApp {
        background-color: #FFFFFF;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
    }
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        border-bottom: 1px solid #E5E7EB;
        background-color: #FFFFFF;
    }
    .logo-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
        text-decoration: none;
        margin-left: 0;
    }
    .user-info {
        font-size: 0.9rem;
        color: #4B5563;
    }
    /* Карточки */
    .card {
        background-color: #F9FAFB;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    .metric-card {
        background-color: #F9FAFB;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6B7280;
    }
    /* Таблицы */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th {
        background-color: #F3F4F6;
        color: #111827;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
    }
    td {
        padding: 0.75rem;
        border-bottom: 1px solid #E5E7EB;
        color: #111827;
    }
    /* Предупреждения */
    .alert-warning {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 8px;
        color: #92400E;
        margin: 1rem 0;
    }
    .alert-danger {
        background-color: #FEE2E2;
        border-left: 4px solid #EF4444;
        padding: 1rem;
        border-radius: 8px;
        color: #991B1B;
        margin: 1rem 0;
    }
    .alert-success {
        background-color: #D1FAE5;
        border-left: 4px solid #22C55E;
        padding: 1rem;
        border-radius: 8px;
        color: #065F46;
        margin: 1rem 0;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-low {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .status-medium {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .status-high {
        background-color: #FEE2E2;
        color: #991B1B;
    }
</style>
""", unsafe_allow_html=True)

# ========================== БАЗА ДАННЫХ ==========================
DB_PATH = os.path.join(os.path.dirname(__file__), "prescriptions.db")
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    full_name = Column(String)

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    birth_date = Column(Date)
    policy_number = Column(String, unique=True)
    allergies = Column(Text)

class Prescription(Base):
    __tablename__ = 'prescriptions'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String, default='active')
    qr_token = Column(String, unique=True)

class PrescriptionItem(Base):
    __tablename__ = 'prescription_items'
    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey('prescriptions.id'))
    drug_name = Column(String)
    dosage = Column(String)
    quantity = Column(Integer)
    is_dispensed = Column(Boolean, default=False)

class Interaction(Base):
    __tablename__ = 'interactions'
    id = Column(Integer, primary_key=True)
    drug1 = Column(String)
    drug2 = Column(String)
    severity = Column(String)
    description = Column(String)

Base.metadata.create_all(engine)

def init_db():
    session = SessionLocal()
    if session.query(User).count() == 0:
        users = [
            User(username="doctor", password="doctor", role="doctor", full_name="Анна Петрова"),
            User(username="pharmacist", password="pharm", role="pharmacist", full_name="Иван Смирнов"),
            User(username="patient", password="patient", role="patient", full_name="Пётр Сидоров")
        ]
        session.add_all(users)
        session.commit()
    if session.query(Patient).count() == 0:
        patient = Patient(first_name="Пётр", last_name="Сидоров", birth_date=date(1965,5,20), policy_number="1234567890", allergies="Пенициллин")
        session.add(patient)
        session.commit()
    if session.query(Interaction).count() == 0:
        interactions = [
            Interaction(drug1="Аспирин", drug2="Варфарин", severity="high", description="Повышенный риск кровотечения"),
            Interaction(drug1="Ибупрофен", drug2="Аспирин", severity="medium", description="Риск желудочно-кишечного кровотечения"),
        ]
        session.add_all(interactions)
        session.commit()
    session.close()

init_db()

# ========================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def authenticate(username, password):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username, User.password == password).first()
    session.close()
    return user

def check_interactions(drug_names):
    session = SessionLocal()
    warnings = []
    for i, d1 in enumerate(drug_names):
        for d2 in drug_names[i+1:]:
            rule = session.query(Interaction).filter(
                ((Interaction.drug1 == d1) & (Interaction.drug2 == d2)) |
                ((Interaction.drug1 == d2) & (Interaction.drug2 == d1))
            ).first()
            if rule:
                warnings.append(f"{d1} + {d2}: {rule.description} (уровень {rule.severity})")
    session.close()
    return warnings

def get_active_prescriptions(patient_id):
    session = SessionLocal()
    prescs = session.query(Prescription).filter(Prescription.patient_id == patient_id, Prescription.status.in_(['active', 'partially_dispensed'])).all()
    drugs = []
    for p in prescs:
        items = session.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == p.id, PrescriptionItem.is_dispensed == False).all()
        drugs.extend([i.drug_name for i in items])
    session.close()
    return list(set(drugs))

def evaluate_polypharmacy(patient_id, new_drugs):
    active = get_active_prescriptions(patient_id)
    total = len(active) + len(new_drugs)
    return total >= 5, total

def generate_qr_token(prescription_id):
    secret = "secret_key_123"
    token = hashlib.sha256(f"{prescription_id}{secret}".encode()).hexdigest()[:16]
    return token

def generate_qr_image(token):
    img = qrcode.make(f"http://localhost:8501?rx={token}")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return buffered

# ========================== СТРАНИЦЫ ==========================
def login_page():
    st.markdown('<div class="logo-title">Цифровая история назначений</div>', unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("Вход в систему")
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        if st.button("Войти", use_container_width=True):
            user = authenticate(username, password)
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user'] = user
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
        st.caption("Тестовые учётные записи: doctor/doctor, pharmacist/pharm, patient/patient")

def main_app():
    # Шапка с названием и пользователем
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown('<div class="logo-title">Цифровая история назначений</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="user-info" style="text-align: right;">{st.session_state.user.full_name} ({st.session_state.user.role})</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Боковое меню
    with st.sidebar:
        st.markdown("## Навигация")
        if st.session_state.user.role == "doctor":
            menu = st.radio("", ["Создать рецепт", "Активные пациенты"])
        elif st.session_state.user.role == "pharmacist":
            menu = st.radio("", ["Проверить рецепт", "Очередь"])
        else:
            menu = st.radio("", ["Мои рецепты", "История"])
        if st.button("Выйти"):
            for key in ['authenticated', 'user']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Рендер страниц
    if st.session_state.user.role == "doctor":
        if menu == "Создать рецепт":
            doctor_create_prescription()
        else:
            doctor_patients()
    elif st.session_state.user.role == "pharmacist":
        if menu == "Проверить рецепт":
            pharmacist_check()
        else:
            pharmacist_queue()
    else:
        if menu == "Мои рецепты":
            patient_active()
        else:
            patient_history()

def doctor_create_prescription():
    st.header("Новый рецепт")
    session = SessionLocal()
    patients = session.query(Patient).all()
    patient_options = {f"{p.last_name} {p.first_name}": p.id for p in patients}
    selected = st.selectbox("Пациент", list(patient_options.keys()))
    patient_id = patient_options[selected]

    if "drugs" not in st.session_state:
        st.session_state.drugs = [{"name":"","dosage":"","quantity":1}]
    def add_drug():
        st.session_state.drugs.append({"name":"","dosage":"","quantity":1})
    def remove_drug(i):
        st.session_state.drugs.pop(i)

    st.subheader("Препараты")
    for i, drug in enumerate(st.session_state.drugs):
        cols = st.columns([3,2,1,0.5])
        drug["name"] = cols[0].text_input("Название", drug["name"], key=f"name_{i}")
        drug["dosage"] = cols[1].text_input("Дозировка", drug["dosage"], key=f"dose_{i}")
        drug["quantity"] = cols[2].number_input("Кол-во", min_value=1, value=drug["quantity"], key=f"qty_{i}")
        if cols[3].button("Удалить", key=f"del_{i}"):
            remove_drug(i)
            st.rerun()
    st.button("Добавить препарат", on_click=add_drug)

    drug_names = [d["name"] for d in st.session_state.drugs if d["name"]]
    if drug_names:
        warnings = check_interactions(drug_names)
        for w in warnings:
            st.markdown(f'<div class="alert-danger">{w}</div>', unsafe_allow_html=True)
        poly, total = evaluate_polypharmacy(patient_id, drug_names)
        if poly:
            st.markdown(f'<div class="alert-warning">Полипрагмазия: {total} активных препаратов. Рекомендуется пересмотр терапии.</div>', unsafe_allow_html=True)

    if st.button("Сохранить рецепт", type="primary"):
        if not drug_names:
            st.error("Добавьте хотя бы один препарат")
        else:
            new_pres = Prescription(patient_id=patient_id, doctor_id=st.session_state.user.id, status='active')
            session.add(new_pres)
            session.flush()
            for d in st.session_state.drugs:
                if d["name"]:
                    item = PrescriptionItem(prescription_id=new_pres.id, drug_name=d["name"], dosage=d["dosage"], quantity=d["quantity"])
                    session.add(item)
            token = generate_qr_token(new_pres.id)
            new_pres.qr_token = token
            session.commit()
            st.success("Рецепт сохранён")
            qr_img = generate_qr_image(token)
            st.image(qr_img, width=200)
            st.session_state.drugs = [{"name":"","dosage":"","quantity":1}]
            st.rerun()
    session.close()

def doctor_patients():
    st.header("Активные пациенты")
    session = SessionLocal()
    patients = session.query(Patient).all()
    for p in patients:
        with st.expander(f"{p.last_name} {p.first_name}"):
            st.write(f"Дата рождения: {p.birth_date}")
            st.write(f"Аллергии: {p.allergies or 'Нет'}")
            active = get_active_prescriptions(p.id)
            if active:
                st.write("Активные назначения:", ", ".join(active))
            else:
                st.write("Нет активных назначений")
    session.close()

def pharmacist_queue():
    st.header("Очередь рецептов")
    session = SessionLocal()
    prescriptions = session.query(Prescription).filter(Prescription.status.in_(['active', 'partially_dispensed'])).all()
    if not prescriptions:
        st.info("Нет рецептов в очереди")
    for p in prescriptions:
        patient = session.query(Patient).get(p.patient_id)
        st.markdown(f'<div class="card">Рецепт #{p.id} - Пациент: {patient.last_name} {patient.first_name} - Статус: {p.status}</div>', unsafe_allow_html=True)
    session.close()

def pharmacist_check():
    st.header("Проверка рецепта")
    rx_id = st.text_input("Введите номер рецепта")
    if st.button("Найти"):
        session = SessionLocal()
        pres = session.query(Prescription).filter(Prescription.id == int(rx_id)).first() if rx_id.isdigit() else None
        if pres:
            patient = session.query(Patient).get(pres.patient_id)
            st.markdown(f'<div class="card"><strong>Пациент:</strong> {patient.last_name} {patient.first_name}<br><strong>Статус:</strong> {pres.status}</div>', unsafe_allow_html=True)
            items = session.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == pres.id).all()
            for item in items:
                col1, col2, col3 = st.columns([3,1,1])
                col1.write(f"{item.drug_name} {item.dosage}")
                col2.write(f"Кол-во: {item.quantity}")
                if not item.is_dispensed:
                    if col3.button(f"Отпустить {item.id}", key=item.id):
                        item.is_dispensed = True
                        session.commit()
                        st.rerun()
                else:
                    col3.write("Отпущен")
            all_dispensed = all(i.is_dispensed for i in items)
            if all_dispensed and len(items)>0:
                pres.status = 'dispensed'
                session.commit()
                st.success("Рецепт полностью отпущен")
        else:
            st.error("Рецепт не найден")
        session.close()

def patient_active():
    st.header("Мои активные рецепты")
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.last_name == "Сидоров").first()  # упрощённо
    if patient:
        prescriptions = session.query(Prescription).filter(Prescription.patient_id == patient.id, Prescription.status.in_(['active', 'partially_dispensed'])).all()
        for p in prescriptions:
            with st.expander(f"Рецепт от {p.created_at.strftime('%d.%m.%Y')}"):
                items = session.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == p.id).all()
                for item in items:
                    st.write(f"{item.drug_name} {item.dosage} - {item.quantity} шт. - {'Отпущен' if item.is_dispensed else 'Не отпущен'}")
                if p.qr_token:
                    qr_img = generate_qr_image(p.qr_token)
                    st.image(qr_img, width=150)
    session.close()

def patient_history():
    st.header("История назначений")
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.last_name == "Сидоров").first()
    if patient:
        prescriptions = session.query(Prescription).filter(Prescription.patient_id == patient.id).order_by(Prescription.created_at).all()
        data = []
        for p in prescriptions:
            items = session.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == p.id).all()
            data.append({
                "Дата": p.created_at.strftime("%Y-%m-%d"),
                "Препараты": ", ".join([i.drug_name for i in items]),
                "Статус": p.status
            })
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        # График
        monthly = {}
        for p in prescriptions:
            month = p.created_at.strftime("%Y-%m")
            cnt = session.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == p.id).count()
            monthly[month] = monthly.get(month, 0) + cnt
        if monthly:
            df_plot = pd.DataFrame(list(monthly.items()), columns=["Месяц", "Кол-во"])
            fig = px.bar(df_plot, x="Месяц", y="Кол-во", title="Динамика назначений", color_discrete_sequence=["#3B82F6"])
            st.plotly_chart(fig, use_container_width=True)
    session.close()

# ========================== ГЛАВНЫЙ ПОТОК ==========================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user'] = None

if not st.session_state.authenticated:
    login_page()
else:
    main_app()
