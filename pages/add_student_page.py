# pages/add_student_page.py
import streamlit as st
import os
from core.students import add_student
from core.photo_manager import PhotoManager
from config.settings import GROUPS


def add_student_form():
    """Форма для добавления нового студента."""
    st.header("➕ Добавить студента")

    with st.form("add_student"):
        name = st.text_input("Имя студента *", placeholder="Иван Иванов")
        group = st.selectbox("Группа *", GROUPS)
        photo = st.file_uploader("Фото студента *", type=["jpg", "jpeg", "png"])

        submitted = st.form_submit_button("Сохранить")

        if submitted:
            if not name or not photo:
                st.error("Заполните все поля и загрузите фото.")
            else:
                try:
                    # Сохраняем фото через PhotoManager
                    photo_path = PhotoManager.save_student_photo(group, name, photo.getvalue())

                    # Добавляем студента в базу
                    if add_student(name, group, photo_path):
                        st.success(f"Студент **{name}** добавлен в группу **{group}**!")
                        st.image(photo.getvalue(), width=200, caption="Загруженное фото")
                    else:
                        st.error("Ошибка при добавлении студента")
                except Exception as e:
                    st.error(f"Ошибка: {e}")