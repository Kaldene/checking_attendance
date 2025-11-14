# core/photo_manager.py
import shutil
from pathlib import Path
from config.settings import PHOTOS_DIR, TEMP_FACES_DIR, SUPPORTED_EXT

class PhotoManager:
    @staticmethod
    def get_group_folder(group_name: str) -> Path:
        return PHOTOS_DIR / group_name

    @staticmethod
    def save_student_photo(group: str, full_name: str, image_bytes: bytes) -> str:
        folder = PhotoManager.get_group_folder(group)
        folder.mkdir(parents=True, exist_ok=True)
        safe_name = full_name.strip().replace(" ", "_")
        file_path = folder / f"{safe_name}.jpg"

        with open(file_path, "wb") as f:
            f.write(image_bytes)
        print(f"Фото сохранено: {file_path}")
        return str(file_path)

    @staticmethod
    def get_students(group: str) -> list[dict]:
        folder = PhotoManager.get_group_folder(group)
        students = []

        if not folder.exists():
            print(f"Папка не найдена: {folder}")
            return students

        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXT:
                name = file_path.stem.replace("_", " ").title()
                students.append({"name": name, "path": str(file_path)})
        print(f"Загружено {len(students)} студентов из {group}")
        return students

    @staticmethod
    def clear_temp_folder():
        if TEMP_FACES_DIR.exists():
            for item in TEMP_FACES_DIR.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print(f"Очищено: {TEMP_FACES_DIR}")
        else:
            TEMP_FACES_DIR.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    PhotoManager.clear_temp_folder()