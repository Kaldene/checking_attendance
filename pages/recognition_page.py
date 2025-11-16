# pages/recognition_page.py
import streamlit as st
import datetime
import time
from pathlib import Path
import logging
import cv2
import numpy as np

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def recognition_page():
    """Страница для запуска распознавания лиц"""
    st.header("🎥 Распознавание студентов")

    logger.info("=== СТРАНИЦА РАСПОЗНАВАНИЯ ЗАПУЩЕНА ===")

    # Инициализация состояния камеры
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False
    if 'camera_capture' not in st.session_state:
        st.session_state.camera_capture = None
    if 'selected_camera_index' not in st.session_state:
        st.session_state.selected_camera_index = 0
    if 'face_cascade' not in st.session_state:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        st.session_state.face_cascade = cv2.CascadeClassifier(cascade_path)
    if 'frame_count' not in st.session_state:
        st.session_state.frame_count = 0
    if 'capturing_faces' not in st.session_state:
        st.session_state.capturing_faces = False
    if 'saved_faces_count' not in st.session_state:
        st.session_state.saved_faces_count = 0
    if 'last_save_time' not in st.session_state:
        st.session_state.last_save_time = 0

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

    # ВЫБОР КАМЕРЫ
    camera_options = {
        "Камера 0 (по умолчанию)": 0,
        "Камера 1": 1,
        "Камера 2": 2,
        "Внешняя USB камера": 3
    }

    selected_camera = st.selectbox(
        "Выберите камеру:",
        options=list(camera_options.keys()),
        index=st.session_state.selected_camera_index
    )

    st.session_state.selected_camera_index = camera_options[selected_camera]

    # Кнопки управления камерой
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📷 Запустить камеру", type="primary"):
            logger.info("Нажата кнопка 'Запустить камеру'")
            try:
                # Освобождаем старую камеру если есть
                if st.session_state.camera_capture is not None:
                    st.session_state.camera_capture.release()

                # Запускаем выбранную камеру
                st.session_state.camera_capture = cv2.VideoCapture(st.session_state.selected_camera_index)
                st.session_state.camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                st.session_state.camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

                if st.session_state.camera_capture.isOpened():
                    st.session_state.camera_active = True
                    st.session_state.frame_count = 0
                    st.success(f"Камера {st.session_state.selected_camera_index} запущена!")
                    logger.info(f"Камера {st.session_state.selected_camera_index} успешно запущена")
                else:
                    st.error(f"Не удалось открыть камеру {st.session_state.selected_camera_index}")
                    logger.error("Камера не доступна")
            except Exception as e:
                logger.error(f"Ошибка запуска камеры: {e}")
                st.error(f"Ошибка запуска камеры: {e}")

    with col2:
        if st.button("⏹️ Остановить камеру"):
            logger.info("Нажата кнопка 'Остановить камеру'")
            try:
                if st.session_state.camera_capture is not None:
                    st.session_state.camera_capture.release()
                    st.session_state.camera_capture = None
                st.session_state.camera_active = False
                st.info("Камера остановлена")
                logger.info("Камера остановлена")
            except Exception as e:
                logger.error(f"Ошибка остановки камеры: {e}")
                st.error(f"Ошибка остановки камеры: {e}")

    with col3:
        if st.button("💾 Начать захват лиц", type="secondary"):
            if st.session_state.camera_active:
                st.session_state.capturing_faces = True
                st.session_state.saved_faces_count = 0
                st.session_state.last_save_time = 0
                # Очищаем папку
                from core.photo_manager import PhotoManager
                PhotoManager.clear_temp_folder()
                st.success("Захват лиц запущен!")
                logger.info("Захват лиц запущен")
            else:
                st.warning("Сначала запустите камеру")

    with col4:
        if st.button("🚀 Распознать"):
            logger.info("Нажата кнопка 'Распознать'")
            try:
                # Останавливаем захват
                st.session_state.capturing_faces = False

                # Останавливаем видео для показа результатов
                was_active = st.session_state.camera_active
                st.session_state.camera_active = False

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
                            st.info(
                                "💡 Видео остановлено для отображения результатов. Нажмите 'Запустить камеру' чтобы продолжить.")
                            logger.info(f"Успешно распознано: {[r['name'] for r in results]}")
                        else:
                            st.warning("Не удалось распознать ни одного студента")
                            logger.warning("Не распознано ни одного студента")

                    except Exception as e:
                        logger.error(f"Ошибка в функции match: {e}")
                        st.error(f"Ошибка распознавания: {e}")
                        # Возвращаем видео если была ошибка
                        if was_active:
                            st.session_state.camera_active = True

            except Exception as e:
                logger.error(f"Ошибка при распознавании: {e}")
                st.error(f"Ошибка при распознавании: {e}")

    # Отображение видео с камеры в реальном времени с рамками вокруг лиц
    if st.session_state.camera_active and st.session_state.camera_capture is not None:
        st.subheader(f"📹 Видео с камеры (Камера {st.session_state.selected_camera_index})")

        # Создаем placeholder для видео
        video_placeholder = st.empty()

        # Показываем несколько кадров
        for _ in range(15):  # 15 кадров (~0.5 секунды)
            if not st.session_state.camera_active:
                break

            try:
                # Читаем один кадр
                ret, frame = st.session_state.camera_capture.read()

                if ret:
                    # Определяем лица на кадре
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = st.session_state.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(50, 50)
                    )

                    # Если включен режим захвата лиц - сохраняем их
                    current_time = time.time()
                    if st.session_state.capturing_faces and len(faces) > 0:
                        # Сохраняем каждые 2 секунды
                        if current_time - st.session_state.last_save_time >= 2.0:
                            for (x, y, w, h) in faces:
                                face_roi = frame[y:y + h, x:x + w]
                                # Увеличиваем контраст
                                face_roi = cv2.convertScaleAbs(face_roi, alpha=1.2, beta=10)

                                file_path = TEMP_FACES_DIR / f"face_{st.session_state.saved_faces_count}.jpg"
                                success = cv2.imwrite(str(file_path), face_roi)

                                if success:
                                    st.session_state.saved_faces_count += 1
                                    logger.info(f"Сохранено лицо: {file_path}")

                            st.session_state.last_save_time = current_time

                    # Рисуем прямоугольники вокруг лиц
                    for (x, y, w, h) in faces:
                        # Красная рамка если захват активен, зеленая если нет
                        color = (0, 0, 255) if st.session_state.capturing_faces else (0, 255, 0)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                        label = "CAPTURING" if st.session_state.capturing_faces else "DETECTED"
                        cv2.putText(frame, label, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                    # Добавляем информацию о количестве лиц
                    info_text = f"Faces: {len(faces)} | Saved: {st.session_state.saved_faces_count}"
                    cv2.putText(frame, info_text, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    # Конвертируем BGR в RGB для правильного отображения в Streamlit
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    video_placeholder.image(frame_rgb, channels="RGB", width="stretch")

                    # Увеличиваем счетчик кадров
                    st.session_state.frame_count += 1

                    # Небольшая задержка между кадрами
                    time.sleep(0.033)  # ~30 FPS
                else:
                    st.error("Не удалось прочитать кадр с камеры")
                    st.session_state.camera_active = False
                    break

            except Exception as e:
                logger.error(f"Ошибка при отображении видео: {e}")
                st.error(f"Ошибка отображения видео: {e}")
                st.session_state.camera_active = False
                break

        # После показа кадров - обновляем страницу
        if st.session_state.camera_active:
            st.rerun()

    elif st.session_state.camera_capture is not None and not st.session_state.camera_active:
        st.info("📹 Камера в режиме ожидания. Нажмите 'Запустить камеру' для продолжения. Не забудьте включить 'Начать захват лиц '")

    # Кнопки очистки
    col5, col6 = st.columns(2)

    with col5:
        if st.button("🧹 Очистить результаты"):
            if selected_group in st.session_state.recognition_results:
                del st.session_state.recognition_results[selected_group]
                st.session_state.recognition_time = None
                st.success("Результаты очищены!")
                st.rerun()

    with col6:
        if st.button("🗑️ Очистить сохраненные лица"):
            from core.photo_manager import PhotoManager
            PhotoManager.clear_temp_folder()
            st.session_state.saved_faces_count = 0
            st.success("Сохраненные лица очищены!")
            st.rerun()

    # Отображение статуса
    st.subheader("📊 Статус системы")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.camera_active:
            st.success(f"✅ Камера активна (Камера {st.session_state.selected_camera_index})")
        else:
            st.error("❌ Камера остановлена")

    with col2:
        if st.session_state.capturing_faces:
            st.info("🔴 Захват лиц активен")
        else:
            st.info("⚪ Захват лиц выключен")

    with col3:
        st.metric("Сохранено лиц", st.session_state.saved_faces_count)

    # Отображение результатов распознавания
    if selected_group in st.session_state.recognition_results:
        st.markdown("---")
        st.subheader("📋 Результаты распознавания")

        try:
            from core.photo_manager import PhotoManager
            all_students = PhotoManager.get_students(selected_group)
            recognized_students = st.session_state.recognition_results[selected_group]

            def normalize_name(name):
                return name.lower().strip().replace(' ', '_').replace('-', '_')

            st.write(f"**Группа:** {selected_group}")
            if st.session_state.recognition_time:
                st.write(f"**Время проверки:** {st.session_state.recognition_time.strftime('%Y-%m-%d %H:%M:%S')}")

            total_students = len(all_students)
            present_count = len(recognized_students)
            absent_count = total_students - present_count

            # Метрики
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("Всего студентов", total_students)
            with metric_col2:
                st.metric("✅ Присутствуют", present_count,
                          delta=f"{(present_count / total_students * 100):.0f}%" if total_students > 0 else "0%")
            with metric_col3:
                st.metric("❌ Отсутствуют", absent_count)

            st.markdown("---")

            # Разделяем студентов на присутствующих и отсутствующих
            present_students = []
            absent_students = []

            for student in all_students:
                student_normalized = normalize_name(student["name"])
                is_present = False
                confidence = ""

                for recognized in recognized_students:
                    if normalize_name(recognized["name"]) == student_normalized:
                        is_present = True
                        confidence = recognized['confidence']
                        break

                if is_present:
                    present_students.append({
                        'name': student['name'],
                        'confidence': confidence
                    })
                else:
                    absent_students.append({
                        'name': student['name']
                    })

            # ПРИСУТСТВУЮЩИЕ И ОТСУТСТВУЮЩИЕ в двух колонках
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"✅ Присутствуют ({len(present_students)})")
                if present_students:
                    present_students.sort(key=lambda x: x['name'])
                    for idx, student in enumerate(present_students, 1):
                        st.success(f"**{idx}. {student['name']}**  \n🎯 Уверенность: {student['confidence']}%")
                else:
                    st.info("Нет присутствующих студентов")

            with col2:
                st.subheader(f"❌ Отсутствуют ({len(absent_students)})")
                if absent_students:
                    absent_students.sort(key=lambda x: x['name'])
                    for idx, student in enumerate(absent_students, 1):
                        st.error(f"**{idx}. {student['name']}**")
                else:
                    st.success("Все студенты присутствуют!")

            # Кнопка экспорта отчета
            st.markdown("---")
            if st.button("📄 Экспорт отчета", use_container_width=True):
                # Формируем текстовый отчет
                report = f"Отчет о посещаемости\n"
                report += f"Группа: {selected_group}\n"
                report += f"Дата: {st.session_state.recognition_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                report += f"=" * 50 + "\n\n"

                report += f"ПРИСУТСТВУЮТ ({len(present_students)}):\n"
                for idx, student in enumerate(present_students, 1):
                    report += f"{idx}. {student['name']} (уверенность: {student['confidence']}%)\n"

                report += f"\nОТСУТСТВУЮТ ({len(absent_students)}):\n"
                for idx, student in enumerate(absent_students, 1):
                    report += f"{idx}. {student['name']}\n"

                st.download_button(
                    label="💾 Скачать отчет",
                    data=report,
                    file_name=f"attendance_{selected_group}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Ошибка при отображении результатов: {e}")
            import traceback
            st.error(f"Подробности: {traceback.format_exc()}")

    # Показываем последние сохраненные лица
    with st.expander("📷 Последние сохраненные лица"):
        temp_faces = list(TEMP_FACES_DIR.glob("face_*.jpg"))
        if temp_faces:
            recent_faces = sorted(temp_faces)[-6:]
            cols = st.columns(3)
            for idx, face_path in enumerate(recent_faces):
                with cols[idx % 3]:
                    st.image(str(face_path), caption=f"Лицо {idx + 1}", width=150)
        else:
            st.info("Нет сохраненных лиц")

    # ДИАГНОСТИКА
    with st.expander("🔧 Диагностика системы"):
        st.subheader("Проверка компонентов")

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

        st.write(f"**Кадров отображено:** {st.session_state.frame_count}")
        st.write(f"**Сохранено лиц:** {st.session_state.saved_faces_count}")
        st.write(f"**Захват активен:** {st.session_state.capturing_faces}")

        # Проверяем файлы в папке
        temp_files = list(TEMP_FACES_DIR.glob("face_*.jpg"))
        st.write(f"**Файлов в TEMP_FACES_DIR:** {len(temp_files)}")
        if temp_files:
            st.write("Последние файлы:")
            for f in sorted(temp_files)[-3:]:
                st.write(f" - {f.name}")