# face_matcher/core.py
from deepface import DeepFace
from config.settings import TEMP_FACES_DIR, FACE_THRESHOLD, SUPPORTED_EXT
from settings import DEEFACE_VERIFY_FACENET512
from core.photo_manager import PhotoManager
from typing import List, Dict

"""
Ядро распознавания.
"""

def match(group: str) -> List[Dict[str, str]]:
    print(f"\n[FaceMatcher] Распознавание: {group}")

    students = PhotoManager.get_students(group)
    if not students:
        print("Нет студентов")
        return []

    temp_faces = [
        f for f in TEMP_FACES_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in PhotoManager.SUPPORTED_EXT
    ]
    if not temp_faces:
        print("Нет фото с камеры")
        return []

    print(f"Студентов: {len(students)} | Кадров: {len(temp_faces)}")

    results = []
    seen = set()

    for student in students:
        name = student["name"]
        if name in seen:
            continue

        best_dist = float('inf')
        for face_path in temp_faces:
            try:
                result = DeepFace.verify(
                    img1_path=student["path"],
                    img2_path=str(face_path),
                    **DEEFACE_VERIFY_FACENET512
                )
                dist = result.get("distance", float('inf'))
                if result.get("verified", False) and dist < best_dist:
                    best_dist = dist
            except Exception as e:
                print(f"DeepFace error: {e}")

        if best_dist < FACE_THRESHOLD:
            conf = round((1 - best_dist) * 100, 1)
            results.append({"name": name, "confidence": conf})
            seen.add(name)
            print(f"Найден: {name} ({conf}%)")

    return results