# config/settings.py
"""
Центральный конфигурационный файл.
Содержит пути, настройки и константы.
"""

from pathlib import Path

#основные пути
BASE_DIR = Path(__file__).parent.parent          # attendance-system/
DATA_DIR = BASE_DIR / "data"
PHOTOS_DIR = DATA_DIR / "photos"                 # Фото студентов: data/photos/ГР-1/
TEMP_FACES_DIR = PHOTOS_DIR / "temp_faces" # Временные скриншоты: data/temp_faces/
DATABASE_DIR = BASE_DIR / "database" # базы данных attendance-system/batabase/

# автоматически создаем папки
for directory in [DATA_DIR, PHOTOS_DIR, TEMP_FACES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# камера
CAMERA_INDEX = 0
CAPTURE_DURATION = 8      # секунд съёмки
SAVE_INTERVAL = 0.5       # интервал между кадрами (сек)

#распознавание лиц
FACE_THRESHOLD = 0.68
FACE_MODEL = "Facenet512"
DISTANCE_METRIC = "cosine"   # ← Исправлено: строка, не кортеж

# настройки приложения
ADMIN_PASSWORD = "admin"
GROUPS = ["ГР-1", "ГР-2", "ГР-3", "ГР-4"]
SUPPORTED_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}

__all__ = [
    "BASE_DIR", "DATA_DIR", "PHOTOS_DIR", "TEMP_FACES_DIR",
    "CAMERA_INDEX", "CAPTURE_DURATION", "SAVE_INTERVAL",
    "FACE_THRESHOLD", "FACE_MODEL", "DISTANCE_METRIC",
    "ADMIN_PASSWORD", "GROUPS", "SUPPORTED_EXT"
]