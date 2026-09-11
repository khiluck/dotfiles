"""Контуры лица: превращаем рёбра MediaPipe в замкнутые многоугольники.

MediaPipe отдаёт контур как НЕУПОРЯДОЧЕННЫЙ набор рёбер (пар индексов), а для
вырезания нужен обход по кругу — иначе cv2.fillPoly нарисует звезду вместо
области. Поэтому рёбра сшиваем в циклы сами.

Важно: у губ контуров ДВА (внешний и внутренний, 40 точек на двоих), поэтому
каждая область — это СПИСОК циклов, а не один цикл. При заливке маски
закрашиваются все циклы области; для губ внутренний лежит внутри внешнего и
объединение даёт ровно то, что нужно.

Индексы точек нарочно не хардкодим — берём из самой библиотеки, чтобы они не
разъехались при обновлении mediapipe.
"""
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarksConnections as _C


def _loops(connections):
    """Сшивает рёбра в замкнутые обходы. Возвращает список циклов."""
    adj = {}
    for c in connections:
        adj.setdefault(c.start, []).append(c.end)
        adj.setdefault(c.end, []).append(c.start)

    seen, out = set(), []
    for start in sorted(adj):
        if start in seen:
            continue
        loop, prev, cur = [start], None, start
        seen.add(start)
        while True:
            nxt = next((n for n in adj[cur] if n != prev), None)
            if nxt is None or nxt == start:
                break
            loop.append(nxt)
            seen.add(nxt)
            prev, cur = cur, nxt
        out.append(loop)
    return out


# Области, которые остаются «настоящими» — глаза и рот.
# Брови держим отдельно: возможно, их тоже захочется оставить живыми.
REGIONS = {
    "left_eye":   _loops(_C.FACE_LANDMARKS_LEFT_EYE),
    "right_eye":  _loops(_C.FACE_LANDMARKS_RIGHT_EYE),
    "lips":       _loops(_C.FACE_LANDMARKS_LIPS),
    "left_brow":  _loops(_C.FACE_LANDMARKS_LEFT_EYEBROW),
    "right_brow": _loops(_C.FACE_LANDMARKS_RIGHT_EYEBROW),
    "face_oval":  _loops(_C.FACE_LANDMARKS_FACE_OVAL),
}

# Что именно подмешиваем из реального видео поверх 3D-модели.
# Брови сюда не входят — их поведение решим, когда увидим картинку.
KEEP_REAL = ("left_eye", "right_eye", "lips")
