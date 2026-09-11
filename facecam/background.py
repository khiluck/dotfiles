"""Фон, на который кладётся модель.

Раньше фоном служил сам кадр с камеры, и реальная комната оставалась видна.
Теперь настоящее видео даёт ТОЛЬКО глаза и рот, а всё остальное синтетическое.

Виды фона:
  real          настоящий кадр (прежнее поведение, для сравнения)
  blur[:N]      настоящий кадр, сильно размытый — комната угадывается, лица нет
  R,G,B         однотонная заливка, например 30,40,60
  #rrggbb       то же в шестнадцатеричном виде
  путь/к/img    картинка, вписанная в кадр с обрезкой

Картинка вписывается по принципу "cover": масштабируется так, чтобы накрыть
кадр целиком, лишнее обрезается по центру. Простое растягивание до 640x480
искажало бы пропорции — снимки обычно 16:9, а кадр 4:3, и пальмы поехали бы.
"""
import cv2
import numpy as np


class Background:
    def __init__(self, spec, width, height, blur=0):
        self.spec = spec
        self.w, self.h = width, height
        self._static = None          # заранее посчитанный кадр, если фон не зависит от видео
        self._blur = 0
        self._down = 6               # во сколько раз уменьшать перед размытием

        if spec == "real":
            self.kind = "real"
        elif spec.startswith("blur"):
            self.kind = "blur"
            _, _, n = spec.partition(":")
            self._blur = int(n) if n else 45
            self._blur |= 1                      # ядро размытия обязано быть нечётным
        else:
            self.kind = "static"
            self._static = self._make_static(spec, width, height)
            if blur:
                k = int(blur) | 1
                self._static = cv2.GaussianBlur(self._static, (k, k), 0)

    @staticmethod
    def _make_static(spec, w, h):
        if spec.startswith("#") and len(spec) == 7:
            r, g, b = (int(spec[i:i + 2], 16) for i in (1, 3, 5))
        elif "," in spec:
            r, g, b = (int(x) for x in spec.split(","))
        else:
            img = cv2.imread(spec, cv2.IMREAD_COLOR)
            if img is None:
                raise SystemExit(f"не читается картинка фона: {spec}")
            return Background._cover(img, w, h)
        return np.full((h, w, 3), (b, g, r), np.uint8)      # OpenCV хранит BGR

    @staticmethod
    def _cover(img, w, h):
        """Вписать с обрезкой: накрыть кадр целиком, лишнее срезать по центру."""
        ih, iw = img.shape[:2]
        s = max(w / iw, h / ih)
        rw, rh = max(int(round(iw * s)), w), max(int(round(ih * s)), h)
        img = cv2.resize(img, (rw, rh), interpolation=cv2.INTER_AREA)
        x, y = (rw - w) // 2, (rh - h) // 2
        return img[y:y + h, x:x + w].copy()

    def __call__(self, bgr):
        if self.kind == "real":
            return bgr.copy()
        if self.kind == "blur":
            # Гауссово ядро 61x61 по полному кадру стоило ~6 мс и роняло частоту
            # с 30 до 25 fps. Уменьшаем кадр, размываем маленьким ядром и
            # растягиваем обратно: для сильного размытия результат неотличим,
            # а цена падает на порядок.
            k = max(3, (self._blur // self._down) | 1)
            small = cv2.resize(bgr, None, fx=1.0 / self._down, fy=1.0 / self._down,
                               interpolation=cv2.INTER_AREA)
            small = cv2.GaussianBlur(small, (k, k), 0)
            return cv2.resize(small, (self.w, self.h), interpolation=cv2.INTER_LINEAR)
        return self._static.copy()
