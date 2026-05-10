import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="💊 MediScript Pro", page_icon="💊", layout="wide")

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================================

if "page" not in st.session_state:
    st.session_state.page = "role_selection"

# ============================================================================
# ДАННЫЕ
# ============================================================================

PATIENTS = [
    {"id": "PAT-00001", "name": "Иванов И.И.", "age": 65, "meds": 3},
    {"id": "PAT-00002", "name": "Петров П.П.", "age": 58, "meds": 2},
    {"id": "PAT-00003", "name": "Сидоров С.С.", "age": 72, "meds": 5},
]

# ============================================================================
# СТРАНИЦА 1: ВЫБОР РОЛИ
# ============================================================================

def page_role_selection():
    st.markdown("# 💊 MediScript Pro")
    st.markdown("## Выберите вашу роль")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👨‍⚕️ Врач")
        if st.button("Войти как врач", use_container_width=True):
            st.session_state.page = "doctor"
            st.rerun()
    
    with col2:
        st.markdown("### 💊 Фармацевт")
        if st.button("Войти как фармацевт", use_container_width=True):
            st.session_state.page = "pharmacist"
            st.rerun()
    
    with col3:
        st.markdown("### 🧑‍⚕️ Пациент")
        if st.button("Войти как пациент", use_container_width=True):
            st.session_state.page = "patient"
            st.rerun()

# ============================================================================
# СТРАНИЦА 2: ВРАЧ
# ============================================================================

def page_doctor():
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("## 👨‍⚕️ Дашборд врача")
    with col2:
        if st.button("Выход"):
            st.session_state.page = "role_selection"
            st.rerun()
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Пациентов", "20")
    with col2:
        st.metric("Рецептов", "12")
    with col3:
        st.metric("Высокого риска", "3")
    with col4:
        st.metric("В очереди", "5")
    
    st.divider()
    
    st.markdown("### 🔍 Поиск пациента")
    search = st.text_input("Введите ФИО или ID")
    
    if search:
        for patient in PATIENTS:
            if search.lower() in patient["name"].lower() or search in patient["id"]:
                st.write(f"✅ {patient['name']} ({patient['age']} л.) - {patient['id']}")

# ============================================================================
# СТРАНИЦА 3: ФАРМАЦЕВТ
# ============================================================================

def page_pharmacist():
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("## 💊 Дашборд фармацевта")
    with col2:
        if st.button("Выход", key="exit1"):
            st.session_state.page = "role_selection"
            st.rerun()
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("В очереди", "8")
    with col2:
        st.metric("Обработано", "23")
    with col3:
        st.metric("Требуют внимания", "2")
    with col4:
        st.metric("На складе", "156")

# ============================================================================
# СТРАНИЦА 4: ПАЦИЕНТ
# ============================================================================

def page_patient():
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("## 🧑‍⚕️ Мой кабинет")
    with col2:
        if st.button("Выход", key="exit2"):
            st.session_state.page = "role_selection"
            st.rerun()
    
    st.divider()
    
    st.markdown("### 👤 Моя информация")
    st.info("ФИО: Иванов И.И. | Возраст: 65 лет | ID: PAT-00001")
    
    st.markdown("### 💊 Мои активные лекарства")
    
    data = {
        "Препарат": ["Метопролол", "Амлодипин", "Омепразол"],
        "Доза": ["50 мг", "5 мг", "20 мг"],
        "Частота": ["1 раз в день", "1 раз в день", "1 раз в день"]
    }
    
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# ============================================================================
# МАРШРУТИЗАТОР
# ============================================================================

if st.session_state.page == "role_selection":
    page_role_selection()
elif st.session_state.page == "doctor":
    page_doctor()
elif st.session_state.page == "pharmacist":
    page_pharmacist()
elif st.session_state.page == "patient":
    page_patient()

# ============================================================================
# ФУТЕР
# ============================================================================

st.divider()
st.markdown("<div style='text-align: center; padding: 2rem; color: #666; font-size: 0.9rem;'><p>💊 Цифровая история лекарственных назначений</p><p>© 2026</p></div>", unsafe_allow_html=True)
