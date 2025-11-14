# core/face_matcher/__init__.py
from .core import match
from .settings import DEEFACE_VERIFY_FACENET512

__all__ = ["match", "DEEFACE_VERIFY_FACENET512"]