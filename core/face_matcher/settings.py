#face_matcher/settings.py
from config.settings import FACE_MODEL, DISTANCE_METRIC

DEEFACE_VERIFY_FACENET512 ={
    "model_name": FACE_MODEL,
    "distance_metric": DISTANCE_METRIC,
    "enforce_detection": False,
    "detector_backend": "opencv",
    "align": True,
    "normalization": "base"
}