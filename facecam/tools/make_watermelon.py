#!/usr/bin/env python
"""Готовит арбуз из скачанного OBJ: разворот под наши оси + хвостик сверху.

Исходник (free3d, OBJ+MTL+jpg) сделан в Z-up и лежит длинной осью вдоль Y,
а facecam ждёт glTF с +Y вверх и лицом в +Z. Плюс у арбуза нет хвостика —
дорисовываем его геометрией.

Хвостик красится БЕЗ правки текстуры: все его вершины получают одну и ту же
UV-координату, указывающую в самый тёмный зелёный тексель самого арбуза. Так
не нужно ни расширять картинку, ни искать в ней свободное место, а объём
хвостику даёт обычное освещение по нормалям.
"""
import argparse, json, os
import numpy as np
import trimesh
from PIL import Image

SRC_DIR = ("/home/aex/Downloads/"
           "Watermelon_V1_L3.123c07613a36-e9b5-4ffe-b425-8f5010f1bc0a")
SRC_OBJ = "10211_Watermelon_v1-L3.obj"


def darkest_uv(img, sample=4):
    """UV самого тёмного зелёного текселя — им красим хвостик."""
    a = np.asarray(img.convert("RGB"), float)[::sample, ::sample]
    green = a[:, :, 1] - (a[:, :, 0] + a[:, :, 2]) / 2.0     # «зеленее прочего»
    score = green - a.sum(2) / 3.0 * 0.6                      # и потемнее
    iy, ix = np.unravel_index(np.argmax(score), score.shape)
    h, w = a.shape[:2]
    return np.array([(ix + 0.5) / w, (iy + 0.5) / h], np.float32), a[iy, ix]


def stem(base, up, length, r0, r1, bend, seg=14, ring=10):
    """Сужающийся слегка изогнутый хвостик. Возвращает (вершины, треугольники)."""
    # ось хвостика: от base вверх, с наклоном в сторону bend
    t = np.linspace(0, 1, seg)
    axis = base[None, :] + up[None, :] * (length * t)[:, None]
    axis += bend[None, :] * (t ** 2)[:, None] * length

    # два орта поперёк оси
    a = up / np.linalg.norm(up)
    tmp = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(a, tmp); e1 /= np.linalg.norm(e1)
    e2 = np.cross(a, e1)

    ang = np.linspace(0, 2 * np.pi, ring, endpoint=False)
    circ = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
    rad = r0 + (r1 - r0) * t

    verts = (axis[:, None, :] + circ[None, :, :] * rad[:, None, None]
             ).reshape(-1, 3)
    faces = []
    for i in range(seg - 1):
        for j in range(ring):
            a0 = i * ring + j
            a1 = i * ring + (j + 1) % ring
            b0 = a0 + ring
            b1 = a1 + ring
            faces += [[a0, b0, b1], [a0, b1, a1]]
    # крышка сверху
    top = len(verts)
    verts = np.vstack([verts, axis[-1]])
    for j in range(ring):
        faces.append([(seg - 1) * ring + j, top,
                      (seg - 1) * ring + (j + 1) % ring])
    return verts, np.array(faces, np.int64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(SRC_DIR, SRC_OBJ))
    ap.add_argument("--out", default="models/Watermelon.glb")
    ap.add_argument("--stem-len", type=float, default=0.20,
                    help="длина хвостика в долях высоты арбуза")
    ap.add_argument("--stem-r", type=float, default=0.045,
                    help="радиус основания хвостика в долях высоты")
    ap.add_argument("--stem-bend", type=float, default=0.06)
    ap.add_argument("--no-stem", action="store_true")
    ap.add_argument("--eye-dx", type=float, default=0.26)
    ap.add_argument("--eye-y", type=float, default=0.12)
    ap.add_argument("--margin", type=float, default=1.3)
    a = ap.parse_args()

    m = trimesh.load(a.src, force="mesh")
    v = np.asarray(m.vertices, float)
    uv = np.asarray(m.visual.uv, float)
    img = getattr(m.visual.material, "image", None) \
        or m.visual.material.baseColorTexture
    print(f"исходник: {len(v)} вершин, текстура {img.size}")

    # В исходнике Z — «вверх», длинная ось — Y. Нам нужно +Y вверх, лицо в +Z.
    # Ставим арбуз стоймя на длинную ось: она и становится вертикалью,
    # а бывшая вертикаль уходит в глубину кадра.
    v = v - (v.max(0) + v.min(0)) / 2.0
    print("после центровки, размеры XYZ:", np.round(v.max(0) - v.min(0), 2))

    faces = np.asarray(m.faces, np.int64)
    if not a.no_stem:
        h = v[:, 1].max() - v[:, 1].min()
        # ставим хвостик на самую верхнюю точку арбуза
        top_i = int(np.argmax(v[:, 1]))
        base = v[top_i] - np.array([0, h * 0.01, 0])
        sv, sf = stem(base, np.array([0.0, 1.0, 0.0]),
                      length=a.stem_len * h,
                      r0=a.stem_r * h, r1=a.stem_r * h * 0.45,
                      bend=np.array([a.stem_bend * h, 0.0, a.stem_bend * h * .4]))
        suv, col = darkest_uv(img)
        print(f"хвостик: {len(sv)} вершин, цвет из текстуры RGB={col.astype(int)}")
        faces = np.vstack([faces, sf + len(v)])
        v = np.vstack([v, sv])
        uv = np.vstack([uv, np.repeat(suv[None, :], len(sv), axis=0)])

    out = trimesh.Trimesh(vertices=v, faces=faces, process=False)
    out.visual = trimesh.visual.TextureVisuals(
        uv=uv, material=trimesh.visual.material.PBRMaterial(
            baseColorTexture=img.convert("RGB"),
            metallicFactor=0.0, roughnessFactor=0.85))
    out.export(a.out)
    print(f"{a.out}: {len(v)} вершин, {len(faces)} треугольников")

    # Якоря: тянем к поверхности с лицевой стороны (+Z)
    front = v[v[:, 2] > 0]
    def on_surface(x, y):
        return front[np.argmin(np.linalg.norm(front[:, :2] - [x, y], axis=1)
                               - front[:, 2] * 0.001)]
    hh = (v[:, 1].max() - v[:, 1].min()) / 2.0
    ep = on_surface(+a.eye_dx * hh, a.eye_y * hh)
    en = on_surface(-a.eye_dx * hh, a.eye_y * hh)
    p = a.out.rsplit(".", 1)[0] + ".anchors.json"
    json.dump({"_comment": "Арбуз: исходник free3d (OBJ), развёрнут и дополнен "
                           "хвостиком скриптом tools/make_watermelon.py. "
                           "Глаз у арбуза нет — якоря назначены.",
               "model": os.path.basename(a.out),
               "eye_x_pos": [round(float(x), 4) for x in ep],
               "eye_x_neg": [round(float(x), 4) for x in en],
               "margin": a.margin,
               "found_by": f"make_watermelon.py --eye-dx {a.eye_dx} "
                           f"--eye-y {a.eye_y}"},
              open(p, "w"), indent=2, ensure_ascii=False)
    print(f"{p}: глаза {np.round(ep,3)} и {np.round(en,3)}")


if __name__ == "__main__":
    main()
