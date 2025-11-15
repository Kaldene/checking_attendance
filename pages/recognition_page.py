# pages/recognition_page.py
import streamlit as st
import datetime
import time
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def recognition_page():
    """Страница для запуска распознавания лиц"""
    st.header("🎥 Распознавание студентов")

    logger.info("=== СТРАНИЦА РАСПОЗНАВАНИЯ ЗАПУЩЕНА ===")

    # Инициализация детектора в session state
    if 'camera_detector' not in st.session_state:
        logger.info("Инициализация CameraDetector...")
        try:
            from core.camera_detector import CameraDetector
            st.session_state.camera_detector = CameraDetector()
            logger.info("CameraDetector инициализирован успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации CameraDetector: {e}")
            st.error(f"Ошибка инициализации камеры: {e}")
            return

    # Инициализация результатов распознавания
    if 'recognition_results' not in st.session_state:
        st.session_state.recognition_results = {}
        st.session_state.recognition_time = None
        logger.info("Инициализированы recognition_results")

    try:
        from config.settings import GROUPS, TEMP_FACES_DIR
        logger.info(f"GROUPS загружены: {GROUPS}")
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
        st.error(f"Ошибка загрузки настроек: {e}")
        return

    # Выбор группы для распознавания
    selected_group = st.selectbox("Выберите группу для распознавания:", GROUPS)
    logger.info(f"Выбрана группа: {selected_group}")

    # Кнопки управления
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚀 Запустить камеру", type="primary"):
            logger.info("Нажата кнопка 'Запустить камеру'")
            try:
                if st.session_state.camera_detector.start_capture():
                    st.success("Камера запущена! Обнаруженные лица сохраняются...")
                    logger.info("Камера успешно запущена")
                else:
                    st.warning("Камера уже запущена")
                    logger.info("Камера уже была запущена")
            except Exception as e:
                logger.error(f"Ошибка запуска камеры: {e}")
                st.error(f"Ошибка запуска камеры: {e}")

    with col2:
        if st.button("⏹️ Остановить камеру"):
            logger.info("Нажата кнопка 'Остановить камеру'")
            try:
                st.session_state.camera_detector.stop_capture()
                st.info("Камера остановлена")
                logger.info("Камера остановлена")
            except Exception as e:
                logger.error(f"Ошибка остановки камеры: {e}")
                st.error(f"Ошибка остановки камеры: {e}")

    with col3:
        if st.button("🔍 Распознать лица"):
            logger.info("Нажата кнопка 'Распознать лица'")
            try:
                status = st.session_state.camera_detector.get_status()
                logger.info(f"Статус камеры: {status}")

                if status["saved_count"] > 0:
                    logger.info(f"Найдено сохраненных лиц: {status['saved_count']}")
                    with st.spinner("Идет распознавание..."):
                        try:
                            from core.face_matcher import match
                            logger.info("Импорт face_matcher выполнен успешно")

                            results = match(selected_group)
                            logger.info(f"Результаты распознавания: {len(results)} студентов")

                            st.session_state.recognition_results[selected_group] = results
                            st.session_state.recognition_time = datetime.datetime.now()

                            if results:
                                st.success(f"Распознавание завершено! Найдено {len(results)} студентов")
                                logger.info(f"Успешно распознано: {[r['name'] for r in results]}")
                            else:
                                st.warning("Не удалось распознать ни одного студента")
                                logger.warning("Не распознано ни одного студента")

                        except Exception as e:
                            logger.error(f"Ошибка в функции match: {e}")
                            st.error(f"Ошибка распознавания: {e}")
                else:
                    st.warning("Сначала запустите камеру и сохраните лица")
                    logger.warning("Нет сохраненных лиц для распознавания")

            except Exception as e:
                logger.error(f"Ошибка при распознавании: {e}")
                st.error(f"Ошибка при распознавании: {e}")

    # Кнопки очистки и экспорта
    col5 = st.columns(1)

    with col5:
        if st.button("🧹 Очистить результаты"):
            if selected_group in st.session_state.recognition_results:
                del st.session_state.recognition_results[selected_group]
                st.session_state.recognition_time = None
                st.success("Результаты очищены!")
                st.rerun()

    # ДИАГНОСТИКА: Проверка всех компонентов
    with st.expander("🔧 Диагностика системы"):
        st.subheader("Проверка компонентов")

        # Проверка импортов
        components = {
            "CameraDetector": "core.camera_detector",
            "Face Matcher": "core.face_matcher",
            "PhotoManager": "core.photo_manager",
            "Settings": "config.settings"
        }

        for name, module in components.items():
            try:
                if module == "core.camera_detector":
                    from core.camera_detector import CameraDetector
                elif module == "core.face_matcher":
                    from core.face_matcher import match
                elif module == "core.photo_manager":
                    from core.photo_manager import PhotoManager
                elif module == "config.settings":
                    from config.settings import GROUPS, TEMP_FACES_DIR

                st.success(f"✅ {name} - OK")
            except Exception as e:
                st.error(f"❌ {name} - Ошибка: {e}")

        # Проверка временной директории
        try:
            temp_files = list(TEMP_FACES_DIR.glob("*"))
            st.write(f"Файлов в TEMP_FACES_DIR: {len(temp_files)}")
            for f in temp_files[-5:]:
                st.write(f" - {f.name}")
        except Exception as e:
            st.error(f"Ошибка доступа к TEMP_FACES_DIR: {e}")

    # Отображение статуса
    st.subheader("📊 Статус системы")
    try:
        status = st.session_state.camera_detector.get_status()

        if status["is_running"]:
            st.success("✅ Камера активна - обнаружение лиц в реальном времени")
        else:
            st.error("❌ Камера остановлена")

        st.metric("Сохранено лиц", status["saved_count"])
        logger.info(f"Статус отображен: running={status['is_running']}, saved={status['saved_count']}")

    except Exception as e:
        st.error(f"Ошибка получения статуса: {e}")
        logger.error(f"Ошибка получения статуса камеры: {e}")

    # Отображение результатов распознавания
    if selected_group in st.session_state.recognition_results:
        st.subheader("📋 Результаты распознавания")

        try:
            from core.photo_manager import PhotoManager
            all_students = PhotoManager.get_students(selected_group)
            recognized_students = st.session_state.recognition_results[selected_group]

            # ДИАГНОСТИКА
            st.write("🔍 Диагностика:")
            st.write(f"- Всего студентов в группе: {len(all_students)}")
            st.write(f"- Распознано системой: {len(recognized_students)}")

            if all_students:
                st.write("- Все студенты:", [s['name'] for s in all_students])
            if recognized_students:
                st.write("- Распознанные:", [s['name'] for s in recognized_students])

            # Нормализуем имена для сравнения
            def normalize_name(name):
                return name.lower().strip().replace(' ', '_').replace('-', '_')

            recognized_names = {normalize_name(student["name"]) for student in recognized_students}

            st.write(f"**Группа:** {selected_group}")
            if st.session_state.recognition_time:
                st.write(f"**Время проверки:** {st.session_state.recognition_time.strftime('%Y-%m-%d %H:%M:%S')}")

            total_students = len(all_students)
            present_count = len(recognized_students)
            absent_count = total_students - present_count

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего студентов", total_students)
            with col2:
                st.metric("Присутствуют", present_count)
            with col3:
                st.metric("Отсутствуют", absent_count)

            st.subheader("👥 Список студентов")
            all_students.sort(key=lambda x: x["name"])

            # Заголовки таблицы
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write("**ФИО студента**")
            with col2:
                st.write("**Статус**")
            with col3:
                st.write("**Уверенность**")

            # Отображаем всех студентов
            for student in all_students:
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.write(student["name"])

                with col2:
                    student_normalized = normalize_name(student["name"])
                    is_present = any(normalize_name(recognized["name"]) == student_normalized
                                     for recognized in recognized_students)

                    if is_present:
                        st.success("✅ Был")
                    else:
                        st.error("❌ Не был")

                with col3:
                    # Находим уверенность для этого студента
                    confidence = ""
                    student_normalized = normalize_name(student["name"])
                    for recognized in recognized_students:
                        if normalize_name(recognized["name"]) == student_normalized:
                            confidence = f"{recognized['confidence']}%"
                            break
                    st.write(confidence)

            # Показываем детали распознанных студентов
            if recognized_students:
                st.subheader("✅ Детали распознавания")
                for student in recognized_students:
                    st.write(f"- **{student['name']}** (уверенность: {student['confidence']}%)")

        except Exception as e:
            st.error(f"Ошибка при отображении результатов: {e}")
            import traceback
            st.error(f"Подробности: {traceback.format_exc()}")

    # Показываем последние сохраненные лица
    temp_faces = list(TEMP_FACES_DIR.glob("face_*.jpg"))
    if temp_faces:
        st.subheader("📷 Последние сохраненные лица")
        recent_faces = sorted(temp_faces)[-6:]
        cols = st.columns(3)
        for idx, face_path in enumerate(recent_faces):
            with cols[idx % 3]:
                st.image(str(face_path), caption=f"Лицо {idx + 1}", width=150)