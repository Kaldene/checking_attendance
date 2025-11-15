# pages/students_page.py
import streamlit as st
import os
from core.students import load_students, delete_student
from config.settings import GROUPS

def show_students():
    """Отобразить список студентов с возможностью фильтрации и удаления."""
    st.header("👥 Список студентов")
    students = load_students()

    if not students:
        st.info("Пока нет зарегистрированных студентов.")
        return

    # Фильтр по группам
    selected_group = st.selectbox("Фильтр по группе", ["Все"] + GROUPS)

    filtered_students = [
        s for s in students
        if selected_group == "Все" or s.get("group") == selected_group
    ]

    st.write(f"**Найдено студентов: {len(filtered_students)}**")

    # Отображение студентов
    for idx, student in enumerate(filtered_students):
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.write(f"**{student['name']}**")
            st.caption(f"Группа: {student['group']}")

        with col2:
            if os.path.exists(student['photo']):
                st.image(student['photo'], width=80)
            else:
                st.write("Фото отсутствует")

        with col3:
            # Кнопка удаления
            if st.button("Удалить", key=f"delete_{idx}"):
                if delete_student(student):
                    st.success(f"Студент {student['name']} удалён!")
                    st.rerun()