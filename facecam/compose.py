"""Композит: фон, 3D-модель, настоящие глаза и рот.

Порядок слоёв снизу вверх:
  1. фон — однотонный, картинка или размытый кадр (background.py)
  2. 3D-модель, посаженная так, чтобы её глазницы легли на настоящие глаза
  3. вырезанные из живого кадра глаза и рот

Настоящий кадр служит ТОЛЬКО источником глаз и рта. Никуда больше его пиксели
попадать не должны — на этом держится весь смысл режима.
"""
import json

import cv2
import numpy as np

import regions


# Насколько расширить (+) или поджать (-) контур каждой области, px.
#
# ВАЖНО: эти числа скомпенсированы под FEATHER. Растушёвка почти не меняет
# геометрию (площадь по уровню 50% падает всего на 2-3%), но съедает
# НЕПРОЗРАЧНУЮ сердцевину: при FEATHER=6 у глаза в полную силу видно лишь 36%
# исходной площади, у губ 52%, остальное подмешано к модели и выглядит блёкло.
# Замер на реальном кадре, сколько нужно добавить, чтобы вернуть непрозрачную
# площадь:
#     растушёвка 2: +2 -> 107%
#     растушёвка 3: +2 ->  99%
#     растушёвка 4: +3 -> 110%   <- текущая пара
#     растушёвка 6: +3 ->  92%
# Взято +3 для глаз: непрозрачность возвращена ровно к исходной (93%).
# Для губ компенсация НЕ применяется — там ограничивает не растушёвка, а
# щетина: контур MediaPipe шире губ, и его приходится поджимать до -2.
# Поэтому меняя FEATHER, эти числа надо пересматривать: они ходят парой.
#
# Потолки, за которые лезть не стоит:
#   глаз  — от +7 в вырезку входит кожа века и она превращается в заплатку;
#           в минусе от -2 глаз подрезается по радужке.
#   губы  — от +3 сверху проступает тёмная полоска усов.
DILATE = {"left_eye": 3, "right_eye": 3, "lips": -2}

# Во сколько раз увеличить вырезку относительно её собственного центра.
# Аккуратный глаз объективно мал и на крупной модели читается точкой, поэтому
# глаза слегка укрупняем. Рот не трогаем: он и так выразительный, а увеличение
# рассинхронизировало бы его с положением на модели.
ZOOM = {"left_eye": 1.18, "right_eye": 1.18, "lips": 1.0}

# Подтянуть область к середине между глазами, в ДОЛЯХ расстояния глаза->область.
# 0 — оставить там, где она на лице; 0.25 — поднять рот на четверть пути к глазам.
# Доли, а не пиксели: иначе сдвиг поехал бы, стоит придвинуться к камере.
# Нужно потому, что модель сажается по глазам, а рот остаётся на своём месте в
# кадре: на высокой модели вроде арбуза он оказывается непривычно низко.
LIFT = {"lips": 0.22}

# Радиус растушёвки края вырезки, px. Осторожно с большими значениями: глаз
# мал, и ядро размытия, сопоставимое с ним, съедает не только край, но и сам
# глаз — маска перестаёт доходить до 255, и сквозь глаз просвечивает модель.
#
# Обратная сторона малых значений: размытие заодно пряталo фактуру по кайме
# губ (щетину, растущую вплотную к ним). Чем меньше растушёвка, тем эта
# зернистость заметнее, и поджатием губ её не убрать — она сидит на самой
# губе. 4 — компромисс: края ещё мягкие, но черты уже не размазаны.
FEATHER = 4


def load_anchors(path):
    """Точки привязки модели плюс её собственный масштаб по умолчанию.

    margin держим здесь, а не в ключах запуска: каждой модели нужен свой
    (картошке ~1.6, Suzanne 1.0), и помнить это руками бессмысленно.
    """
    d = json.load(open(path))
    return (np.array(d["eye_x_pos"], "f4"),
            np.array(d["eye_x_neg"], "f4"),
            float(d.get("margin", 1.0)))


def eye_centers(face):
    """Центры настоящих глаз в пикселях: (экранно левый, экранно правый)."""
    l = face.polygons(["left_eye"])[0].mean(0)
    r = face.polygons(["right_eye"])[0].mean(0)
    # Упорядочиваем по X, чтобы не зависеть от того, что MediaPipe считает
    # «левым» (у него — со стороны человека, а кадр ещё и зеркалим).
    return (l, r) if l[0] >= r[0] else (r, l)


def face_box(face):
    """Габарит лица по овалу: центр и размер в пикселях."""
    oval = face.polygons(["face_oval"])[0]
    x, y, w, h = cv2.boundingRect(oval)
    return (x + w / 2.0, y + h / 2.0), w, h


def _fill(mask, polys, off):
    """Заливает многоугольники ОБЪЕДИНЕНИЕМ.

    Именно по одному, а не одним вызовом со списком: fillPoly со списком
    контуров заливает по правилу чётности, и вложенный контур ВЫЧИТАЕТСЯ.
    У губ контура два (внешний и внутренний), поэтому одним вызовом в маске
    появлялась дырка ровно по отверстию рта — с закрытым ртом незаметная, а на
    открытом сквозь неё была видна модель вместо зубов.
    """
    for p in polys:
        cv2.fillPoly(mask, [p - off], 255)


def _disc(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (abs(r) * 2 + 1,) * 2)


def _morph(mask, d):
    if d == 0:
        return mask
    return cv2.dilate(mask, _disc(d)) if d > 0 else cv2.erode(mask, _disc(d))


def real_layer(face, bgr, roi, names=regions.KEEP_REAL,
               dilate=None, zoom=None, feather=FEATHER, offsets=None):
    """Слой настоящих глаз и рта: (картинка BGR в ROI, маска 0..1 в ROI).

    Каждая область обрабатывается в своей маленькой рамке — так и дешевле, и
    позволяет масштабировать области по отдельности вокруг их центров.
    """
    dilate = DILATE if dilate is None else dilate
    zoom = ZOOM if zoom is None else zoom
    offsets = offsets or {}
    if not isinstance(dilate, dict):
        dilate = {n: int(dilate) for n in names}

    x0, y0, x1, y1 = roi
    H, W = bgr.shape[:2]
    layer = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
    mask = np.zeros((y1 - y0, x1 - x0), np.uint8)

    for name in names:
        polys = face.polygons([name])
        pts = np.vstack(polys)
        d = int(dilate.get(name, 0))
        z = float(zoom.get(name, 1.0))
        # ВНИМАНИЕ: ниже `off` — это начало рамки, поэтому сдвиг зовём shift.
        shift = np.asarray(offsets.get(name, (0.0, 0.0)), np.float32)

        # Рамка вокруг области с запасом на поджатие/расширение и на увеличение.
        # numpy 2 убрал метод ndarray.ptp() — только функция
        span = max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1]))
        # запас ещё и на сдвиг, иначе смещённая область вылезет за рамку
        pad = (abs(d) + feather + 3 + int(span * max(z - 1.0, 0.0) / 2) + 2
               + int(np.abs(shift).max()) + 2)
        bx0 = max(int(pts[:, 0].min()) - pad, 0)
        by0 = max(int(pts[:, 1].min()) - pad, 0)
        bx1 = min(int(pts[:, 0].max()) + pad, W)
        by1 = min(int(pts[:, 1].max()) + pad, H)
        if bx1 <= bx0 or by1 <= by0:
            continue

        off = np.array([bx0, by0], np.int32)
        bw, bh = bx1 - bx0, by1 - by0

        part = np.zeros((bh, bw), np.uint8)
        _fill(part, polys, off)
        part = _morph(part, d)
        img = bgr[by0:by1, bx0:bx1]

        if abs(z - 1.0) > 1e-3 or np.abs(shift).max() > 0.5:
            c = pts.mean(0) - np.array([bx0, by0], np.float32)
            M = cv2.getRotationMatrix2D((float(c[0]), float(c[1])), 0.0, z)
            M[0, 2] += shift[0]
            M[1, 2] += shift[1]
            part = cv2.warpAffine(part, M, (bw, bh), flags=cv2.INTER_NEAREST)
            img = cv2.warpAffine(img, M, (bw, bh), flags=cv2.INTER_LINEAR)

        # Перенос в ROI по пересечению рамок.
        ix0, iy0 = max(bx0, x0), max(by0, y0)
        ix1, iy1 = min(bx1, x1), min(by1, y1)
        if ix1 <= ix0 or iy1 <= iy0:
            continue
        dst = (slice(iy0 - y0, iy1 - y0), slice(ix0 - x0, ix1 - x0))
        src = (slice(iy0 - by0, iy1 - by0), slice(ix0 - bx0, ix1 - bx0))

        sm = part[src]
        # Пиксели кладём ШИРЕ маски — на радиус растушёвки. Иначе в полосе,
        # где маска уже не 0, но ещё не 255, слой остаётся чёрным, это чёрное
        # подмешивается к модели и по краю вырезки идёт тёмная обводка.
        # Проверено: в полосе растушёвки было 53% чёрных пикселей.
        wide = cv2.dilate(part, _disc(feather + 1))[src] if feather else sm
        np.copyto(layer[dst], img[src], where=wide[:, :, None] > 0)
        np.maximum(mask[dst], sm, out=mask[dst])

    if feather:
        f = feather * 2 + 1
        mask = cv2.GaussianBlur(mask, (f, f), 0)
    return layer, mask


def real_mask(face, shape, names=regions.KEEP_REAL, dilate=None, feather=FEATHER,
              roi=None, zoom=None):
    """Только маска — для отладки и подбора значений."""
    if roi is None:
        roi = (0, 0, shape[1], shape[0])
    return real_layer(face, np.zeros((shape[0], shape[1], 3), np.uint8), roi,
                      names, dilate, zoom, feather)[1]


def _roi(bgr, face, center, size, aspect, pad):
    """Прямоугольник, за пределами которого кадр заведомо не меняется:
    габарит модели плюс габарит вырезаемых областей, с запасом pad."""
    h, w = bgr.shape[:2]
    hw = size * aspect / 2.0
    hh = size / 2.0
    x0, x1 = center[0] - hw, center[0] + hw
    y0, y1 = center[1] - hh, center[1] + hh

    pts = np.vstack(face.polygons(regions.KEEP_REAL))
    x0 = min(x0, pts[:, 0].min()); x1 = max(x1, pts[:, 0].max())
    y0 = min(y0, pts[:, 1].min()); y1 = max(y1, pts[:, 1].max())

    return (max(int(x0 - pad), 0), max(int(y0 - pad), 0),
            min(int(x1 + pad) + 1, w), min(int(y1 + pad) + 1, h))


def compose(bgr, face, renderer, anchors, *, base=None, clip=True,
            margin=None, dy=0.0, dx=0.0, lift=None,
            dilate=None, zoom=None, feather=FEATHER, signs=(1, 1, 1)):
    """Собирает итоговый кадр из трёх слоёв.

    Модель сажается по ЯКОРЯМ: её глаза совмещаются с настоящими. Посадка по
    габариту лица (первая версия) для этого эффекта не годилась — глазницы
    модели жили отдельно от настоящих глаз, и вместо «мои глаза на модели»
    получались два разных набора глаз рядом.

    base=None означает «фоном служит сам кадр» — прежнее поведение.
    clip=True обрезает вырезку силуэтом модели: без этого рот, не попавший на
    модель, повисает прямо на фоне сам по себе.
    """
    a_model, b_model, _ = anchors
    a_px, b_px = eye_centers(face)

    center, size = renderer.fit_by_eyes(face.pose, a_model, b_model, a_px, b_px,
                                        signs,
                                        anchors[2] if margin is None else margin)
    if center is None:
        # Голова почти в профиль, якоря слиплись. Отдаём фон, а НЕ настоящий
        # кадр: иначе при повороте головы в эфир уходит живое лицо.
        return bgr if base is None else base
    center = (center[0] + dx * size, center[1] + dy * size)

    # Сдвиг областей к середине между глазами (см. LIFT). Считается в долях
    # расстояния глаза->область, поэтому не зависит от того, близко ли ты к
    # камере.
    eye_mid = (np.asarray(a_px, "f4") + np.asarray(b_px, "f4")) / 2.0
    offsets = {}
    for nm, frac in (LIFT if lift is None else lift).items():
        if frac:
            c = np.vstack(face.polygons([nm])).mean(0)
            offsets[nm] = (eye_mid - c) * float(frac)

    rgb, alpha = renderer.render(face.pose, center, size, *signs)

    # Всё смешивание — только внутри ROI. Полнокадровая арифметика в float32
    # стоила ~27 мс на кадр и роняла частоту вдвое; модель занимает малую часть
    # кадра, поэтому считать остальное бессмысленно. Фон при этом кладётся на
    # весь кадр — он-то меняется целиком.
    dmax = max((dilate or DILATE).values()) if isinstance(dilate or DILATE, dict) \
        else int(dilate or 0)
    zmax = max((zoom or ZOOM).values())
    smax = max((abs(v).max() for v in offsets.values()), default=0.0)
    pad = feather + 4 + abs(dmax) + int(40 * max(zmax - 1.0, 0.0)) + int(smax) + 2
    x0, y0, x1, y1 = _roi(bgr, face, center, size, renderer.aspect, pad)

    out = bgr.copy() if base is None else base
    sub = out[y0:y1, x0:x1]
    model = cv2.cvtColor(rgb[y0:y1, x0:x1], cv2.COLOR_RGB2BGR)

    real, m8 = real_layer(face, bgr, (x0, y0, x1, y1),
                          dilate=dilate, zoom=zoom, feather=feather,
                          offsets=offsets)

    a = (alpha[y0:y1, x0:x1].astype(np.float32) / 255.0)[:, :, None]
    m = (m8.astype(np.float32) / 255.0)[:, :, None]
    if clip:
        m = m * a                            # вырезка живёт только на модели

    # Три слоя в один проход: фон * (1-a)(1-m) + модель * a(1-m) + живое * m
    km = a * (1.0 - m)
    np.copyto(sub, (real * m + model * km + sub * (1.0 - m - km)).astype(np.uint8))
    return out
