"""Трекер лица: кадр -> поза головы + многоугольники глаз/рта.

Работает в режиме VIDEO (а не IMAGE): MediaPipe тогда сглаживает результат
между кадрами и не теряет лицо на моргании. Взамен требует монотонные
временные метки в миллисекундах.
"""
import math
import numpy as np
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions, vision

import regions

MODEL = "assets/face_landmarker.task"


class Pose:
    """Поворот головы в градусах. Это всё, что нужно 3D-модели:
    мимику мы не анимируем — глаза и рот приходят настоящие."""
    __slots__ = ("yaw", "pitch", "roll", "matrix")

    def __init__(self, matrix):
        self.matrix = matrix
        R = matrix[:3, :3]
        self.yaw   = math.degrees(math.atan2(R[0, 2], R[2, 2]))
        self.pitch = math.degrees(math.asin(max(-1.0, min(1.0, -R[1, 2]))))
        self.roll  = math.degrees(math.atan2(R[1, 0], R[1, 1]))

    def __repr__(self):
        return f"yaw={self.yaw:+6.1f} pitch={self.pitch:+6.1f} roll={self.roll:+6.1f}"


class Face:
    """Результат по одному кадру."""
    def __init__(self, pose, points):
        self.pose = pose
        self.points = points          # (478, 2) в пикселях кадра

    def polygons(self, names):
        """Многоугольники названных областей, в пикселях, готовые для fillPoly."""
        out = []
        for name in names:
            for loop in regions.REGIONS[name]:
                out.append(self.points[loop].astype(np.int32))
        return out


class Tracker:
    def __init__(self, model=MODEL, num_faces=1):
        opts = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model),
            running_mode=vision.RunningMode.VIDEO,
            output_facial_transformation_matrixes=True,
            output_face_blendshapes=False,   # мимика не нужна: глаза и рот настоящие
            num_faces=num_faces)
        self._lm = vision.FaceLandmarker.create_from_options(opts)

    def __call__(self, rgb, ts_ms):
        """rgb — кадр HxWx3 (RGB). Возвращает Face или None, если лица нет."""
        res = self._lm.detect_for_video(
            Image(image_format=ImageFormat.SRGB, data=rgb), int(ts_ms))
        if not res.face_landmarks:
            return None

        h, w = rgb.shape[:2]
        pts = np.array([[p.x * w, p.y * h] for p in res.face_landmarks[0]],
                       dtype=np.float32)
        return Face(Pose(np.array(res.facial_transformation_matrixes[0])), pts)

    def close(self):
        self._lm.close()

    def __enter__(self):  return self
    def __exit__(self, *a):  self.close()
