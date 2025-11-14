# core/camera_detector.py
import cv2
import time
from pathlib import Path
from config.settings import TEMP_FACES_DIR, CAPTURE_DURATION, SAVE_INTERVAL, CAMERA_INDEX
from core.photo_manager import PhotoManager

#========================
# переделать логику камеры
#=======================
class CameraDetector:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise RuntimeError("Не удалось загрузить haarcascade_frontalface_default.xml")

    def capture_faces(self) -> bool:
        PhotoManager.clear_temp_folder()

        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            print("Не удалось открыть камеру")
            return False

        start_time = time.time()
        saved_count = 0
        last_save = 0

        print("Съёмка начата... (8 сек)")
        while time.time() - start_time < CAPTURE_DURATION:
            ret, frame = cap.read()
            if not ret:
                print("Ошибка чтения кадра")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            current_time = time.time()
            for (x, y, w, h) in faces:
                if current_time - last_save >= SAVE_INTERVAL:
                    face_roi = frame[y:y+h, x:x+w]
                    file_path = TEMP_FACES_DIR / f"face_{saved_count}.jpg"
                    cv2.imwrite(str(file_path), face_roi)
                    saved_count += 1
                    last_save = current_time
                    print(f"Сохранено: {file_path.name}")

            time.sleep(0.05)

        cap.release()
        print(f"Съёмка завершена. Сохранено лиц: {saved_count}")
        return saved_count > 0
