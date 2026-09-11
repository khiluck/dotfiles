#!/usr/bin/env python
"""Генератор картошки.

Готовую модель картошки брать неоткуда: у случайных моделей из интернета мутная
лицензия, а картошка — это бугристый эллипсоид. Своя генерация решает разом и
лицензию (она наша), и главную проблему: у картошки нет глаз, поэтому точки
привязки надо не искать, а НАЗНАЧИТЬ. Здесь они назначаются сразу и осознанно.

Форма: сфера -> эллипсоид -> смещение вершин вдоль нормали суммой синусоид
разных частот. Синусоиды вместо настоящего шума Перлина — чтобы не тащить
зависимость; на глаз разница неразличима, а бугры получаются органичные.

Текстура рисуется тут же: базовый коричневый + пятна + тёмные глазки картофеля.
"""
import argparse, json
import numpy as np
import trimesh
from PIL import Image


def lumpy_sphere(subdiv=4, axes=(0.72, 1.0, 0.78), bumps=6, amp=0.13, seed=7):
    """Бугристый эллипсоид."""
    rng = np.random.default_rng(seed)
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    v = np.asarray(m.vertices, float)

    n = v / np.linalg.norm(v, axis=1, keepdims=True)
    disp = np.zeros(len(v))
    for _ in range(bumps):
        # случайное направление и частота -> одна "волна" по поверхности
        d = rng.normal(size=3); d /= np.linalg.norm(d)
        freq = rng.uniform(1.2, 3.4)
        phase = rng.uniform(0, 2 * np.pi)
        disp += rng.uniform(0.5, 1.0) * np.sin(freq * (n @ d) * np.pi + phase)
    disp = amp * disp / bumps * 3.0

    v = n * (1.0 + disp)[:, None] * np.array(axes)
    m.vertices = v
    return m


def spherical_uv(v):
    """Сферическая развёртка: картошке хватает, шва почти не видно на пятнах."""
    n = v / np.linalg.norm(v, axis=1, keepdims=True)
    u = 0.5 + np.arctan2(n[:, 0], n[:, 2]) / (2 * np.pi)
    w = 0.5 - np.arcsin(np.clip(n[:, 1], -1, 1)) / np.pi
    return np.column_stack([u, w]).astype(np.float32)


def potato_texture(size=512, seed=3):
    """Коричневая кожура с пятнами и тёмными глазками."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size

    base = np.zeros((size, size, 3), np.float32)
    base[..., 0], base[..., 1], base[..., 2] = 0.62, 0.46, 0.28   # RGB картошки

    # крупные разводы
    t = np.zeros((size, size), np.float32)
    for f, a in ((3, .5), (7, .3), (17, .2), (37, .12)):
        t += a * np.sin(2*np.pi*f*xx + rng.uniform(0, 6)) * \
                 np.sin(2*np.pi*f*yy + rng.uniform(0, 6))
    base *= (1.0 + 0.22 * t)[..., None]

    # глазки картофеля — тёмные точки
    for _ in range(70):
        cx, cy = rng.uniform(0, size, 2)
        r = rng.uniform(2.5, 6.0)
        d = np.hypot(np.arange(size)[None, :] - cx, np.arange(size)[:, None] - cy)
        base *= (1.0 - 0.55 * np.exp(-(d / r) ** 2))[..., None]

    return Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="models/Potato.glb")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--subdiv", type=int, default=4)
    # Оси эллипсоида X,Y,Z. Y — высота. Больше Y, чем X, — картошка стоя;
    # наоборот — лежачий блин, с которого всё начиналось.
    ap.add_argument("--axes", default="0.72,1.0,0.78",
                    help="полуоси эллипсоида X,Y,Z (Y — высота)")
    ap.add_argument("--amp", type=float, default=0.13,
                    help="высота бугров: 0 — гладкое яйцо, 0.2 — корявая")
    ap.add_argument("--bumps", type=int, default=6,
                    help="сколько волн задают бугристость")
    # Куда посадить глаза и рот. Картошка смотрит в +Z (как Suzanne).
    ap.add_argument("--eye-dx", type=float, default=0.30, help="разнос глаз по X")
    ap.add_argument("--eye-y",  type=float, default=0.17, help="высота глаз")
    a = ap.parse_args()

    m = lumpy_sphere(subdiv=a.subdiv, seed=a.seed, amp=a.amp, bumps=a.bumps,
                     axes=tuple(float(x) for x in a.axes.split(",")))
    v = np.asarray(m.vertices, float)
    uv = spherical_uv(v)
    tex = potato_texture(seed=a.seed)

    m.visual = trimesh.visual.TextureVisuals(
        uv=uv, material=trimesh.visual.material.PBRMaterial(
            baseColorTexture=tex, metallicFactor=0.0, roughnessFactor=0.95))
    m.export(a.out)
    print(f"{a.out}: {len(v)} вершин, {len(m.faces)} треугольников, "
          f"габарит {np.round(v.min(0),3)} .. {np.round(v.max(0),3)}")

    # Якоря кладём НА ПОВЕРХНОСТЬ: берём ближайшую вершину к желаемой точке,
    # чтобы глаз не оказался внутри картошки или в воздухе.
    def on_surface(x, y):
        want = np.array([x, y, 10.0])           # тянем вперёд, к лицевой стороне
        front = v[v[:, 2] > 0]
        i = np.argmin(np.linalg.norm(front[:, :2] - [x, y], axis=1)
                      - front[:, 2] * 0.001)
        return front[i]

    eye_pos = on_surface(+a.eye_dx, a.eye_y)
    eye_neg = on_surface(-a.eye_dx, a.eye_y)
    p = a.out.rsplit(".", 1)[0] + ".anchors.json"
    json.dump({"_comment": "У картошки глаз нет — точки привязки НАЗНАЧЕНЫ "
                           "генератором tools/make_potato.py, а не найдены.",
               "model": a.out.rsplit("/", 1)[-1],
               "eye_x_pos": [round(float(x), 4) for x in eye_pos],
               "eye_x_neg": [round(float(x), 4) for x in eye_neg],
               "margin": 1.35,
               "found_by": f"make_potato.py --axes {a.axes} --amp {a.amp} "
                           f"--seed {a.seed} --eye-dx {a.eye_dx} --eye-y {a.eye_y}"},
              open(p, "w"), indent=2, ensure_ascii=False)
    print(f"{p}: глаза {np.round(eye_pos,3)} и {np.round(eye_neg,3)}")


if __name__ == "__main__":
    main()
