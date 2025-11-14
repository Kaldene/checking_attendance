# utils/menu.py
import streamlit as st


def show_menu():
    """Отобразить боковое меню навигации."""
    with st.sidebar:
        st.header("📋 Навигация")

        # Показываем уведомление о новых результатах
        if 'recognition_results' in st.session_state and st.session_state.recognition_results:
            st.sidebar.success("📊 Есть новые результаты распознавания!")

        page = st.radio(
            "Выберите раздел:",
            ["👥 Студенты", "➕ Добавить студента", "🎥 Распознавание"],
            key="main_menu"
        )
    return page


def show_user_info(username):
    """Отобразить информацию о пользователе и кнопку выхода."""
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 **Пользователь:** {username}")

    if st.sidebar.button("🚪 Выйти"):
        # Очищаем все данные сессии
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()