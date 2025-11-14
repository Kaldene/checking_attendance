# app.py
import streamlit as st
import bcrypt
import json
import os
from datetime import datetime
from core.camera_detector import CameraDetector
from core.photo_manager import PhotoManager
from config.settings import GROUPS, PHOTOS_DIR

# пути
USERS_FILE = "data/users.json"
STUDENTS_FILE = "data/students.json"

#  инициализация
os.makedirs("data", exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)
for group in GROUPS:
    os.makedirs(os.path.join(PHOTOS_DIR, group), exist_ok=True)

if not os.path.exists(STUDENTS_FILE):
    with open(STUDENTS_FILE, "w") as f:
        json.dump([], f, indent=4)


#  работа с файлами
def load_students():
    with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_students(students):
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=4, ensure_ascii=False)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


# === АВТОРИЗАЦИЯ ===
def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False
    return bcrypt.checkpw(password.encode(), users[username].encode())


# старницы
def show_students():
    st.title("Список студентов")
    students = load_students()
    if not students:
        st.info("Пока нет зарегистрированных студентов.")
        return

    # фильтр по группам
    selected_group = st.selectbox("Фильтр по группе", ["Все"] + GROUPS)

    filtered_students = [
        s for s in students
        if selected_group == "Все" or s.get("group") == selected_group
    ]

    col1, col2 = st.columns(2)

    with col1:
        attendace_filter = st.selectbox(
            "📊 Статус посещения сегодня",
            ["Все", "Был сегодня", "Не был сегодня"]
        )

    # отображение студента
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
                st.session_state.delete_index = idx
                st.session_state.delete_student = student
                st.rerun()

    # подтверждение удаления
    if "delete_student" in st.session_state:
        student = st.session_state.delete_student
        st.warning(f"Удалить студента **{student['name']}**?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Да, удалить", type="primary"):
                # Удаляем фото
                if os.path.exists(student['photo']):
                    os.remove(student['photo'])
                    st.toast(f"Фото удалено: {student['photo']}")

                # удаляем из JSON
                students = load_students()
                students.remove(student)
                save_students(students)

                # очищаем состояние
                del st.session_state.delete_student
                del st.session_state.delete_index

                st.success(f"Студент **{student['name']}** удалён!")
                st.rerun()
        with col2:
            if st.button("Отмена"):
                del st.session_state.delete_student
                del st.session_state.delete_index
                st.rerun()

def add_student_form():
    st.title("Добавить студента")

    with st.form("add_student"):
        name = st.text_input("Имя студента *", placeholder="Иван Иванов")
        group = st.selectbox("Группа *", GROUPS)
        photo = st.file_uploader("Фото студента *", type=["jpg", "jpeg", "png"])

        submitted = st.form_submit_button("Сохранить")
        if submitted:
            if not name or not photo:
                st.error("Заполните все поля и загрузите фото.")
            else:
                group_dir = os.path.join(PHOTOS_DIR, group)
                os.makedirs(group_dir, exist_ok=True)
                photo_path = os.path.join(group_dir, f"{name}_{photo.name}")

                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())

                students = load_students()
                students.append({
                    "name": name,
                    "group": group,
                    "photo": photo_path,
                    "added_at": datetime.now().isoformat(),
                    "attendance": []  #
                })
                save_students(students)

                st.success(f"Студент **{name}** добавлен!")
                st.image(photo_path, width=200)


def recognition_page():
    st.title("Распознавание лиц")
    st.write("Нажмите кнопку, чтобы запустить камеру и проверить присутствие.")

    if st.button("Начать распознавание", type="primary"):
        with st.spinner("Запуск камеры..."):
            detector = CameraDetector()
            result = detector.run_detection()

            if result:
                st.success(f"Распознан: **{result['name']}**")
                st.image(result['frame'], channels="BGR", width=400)
            else:
                st.warning("Лицо не распознано или не найдено в базе.")


# === МЕНЮ ===
def show_menu():
    with st.sidebar:
        st.title("Меню")
        page = st.radio(
            "Перейти",
            ["Студенты", "Добавить студента", "Распознавание"],
            key="main_menu"
        )
    return page


# авторизация
def login_section():
    st.title("Авторизация")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Вход")
        with st.form("login_form"):
            username = st.text_input("Логин")
            password = st.text_input("Пароль", type="password")
            if st.form_submit_button("Войти"):
                if login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Добро пожаловать, **{username}**!")
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль.")

    with col2:
        st.subheader("Регистрация")
        with st.form("register_form"):
            new_user = st.text_input("Новый логин")
            new_pwd = st.text_input("Пароль", type="password")
            confirm_pwd = st.text_input("Подтвердите пароль", type="password")
            if st.form_submit_button("Зарегистрироваться"):
                if new_pwd != confirm_pwd:
                    st.error("Пароли не совпадают.")
                elif register_user(new_user, new_pwd):
                    st.success("Регистрация успешна! Войдите.")
                else:
                    st.warning("Пользователь уже существует.")


# основная система
def main_system():
    st.header(f"Привет, **{st.session_state.username}**!")

    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    # меню
    page = show_menu()

    #  Отображаем страницу
    if page == "Студенты":
        show_students()
    elif page == "Добавить студента":
        add_student_form()
    elif page == "Распознавание":
        recognition_page()

# запуск
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.logged_in:
    main_system()
else:
    login_section()