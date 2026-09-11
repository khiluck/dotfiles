#!/usr/bin/env python
"""Поиск точек привязки (якорей) для новой модели.

Якоря — это центры глаз модели в её собственных координатах. По ним facecam
сажает модель на лицо: её глазницы совмещаются с настоящими глазами. Без якорей
модель встанет мимо, и эффект развалится.

Способ 1 (авто, --color): если глаза модели выделены цветом в базовой текстуре,
находим вершины этого цвета и делим их по знаку X.

Способ 2 (вручную, --render): рендерим модель в трёх проекциях с сеткой
координат; смотришь, где глаза, и вписываешь числа в <модель>.anchors.json.

Примеры:
  tools/find_anchors.py models/Robot.gltf --color 240,224,144 --tol 60
  tools/find_anchors.py models/Robot.gltf --render /tmp/robot.png
"""
import argparse, json, sys
import numpy as np
import trimesh


def by_color(mesh, rgb, tol):
    v = np.asarray(mesh.vertices, float)
    uv = getattr(mesh.visual, "uv", None)
    if uv is None:
        sys.exit("у модели нет UV — цветом не найти, используй --render")
    tex = np.asarray(mesh.visual.material.baseColorTexture.convert("RGB"))
    h, w, _ = tex.shape
    px = np.clip((uv[:, 0] * (w - 1)).astype(int), 0, w - 1)
    py = np.clip(((1 - uv[:, 1]) * (h - 1)).astype(int), 0, h - 1)
    col = tex[py, px].astype(int)
    hit = np.abs(col - np.array(rgb)).max(1) <= tol
    if hit.sum() < 6:
        sys.exit(f"нашлось всего {hit.sum()} вершин такого цвета — поменяй цвет или --tol")
    ev = v[hit]
    pos, neg = ev[ev[:, 0] > 0], ev[ev[:, 0] < 0]
    if len(pos) < 3 or len(neg) < 3:
        sys.exit("вершины не разделились на две группы по X — глаза не нашлись")
    return pos.mean(0), neg.mean(0), hit.sum()


def render_views(mesh, out):
    """Три ортографические проекции с координатной сеткой — чтобы снять якоря на глаз."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    v = np.asarray(mesh.vertices, float)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (i, j, name) in zip(axes, [(0, 1, "спереди X-Y"),
                                       (2, 1, "сбоку Z-Y"),
                                       (0, 2, "сверху X-Z")]):
        ax.scatter(v[:, i], v[:, j], s=0.5, alpha=0.3)
        ax.set_title(name); ax.grid(True, alpha=0.4); ax.set_aspect("equal")
    fig.tight_layout(); fig.savefig(out, dpi=110)
    print(f"проекции: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--color", help="цвет глаз в текстуре, R,G,B")
    ap.add_argument("--tol", type=int, default=40)
    ap.add_argument("--render", metavar="PNG")
    ap.add_argument("--write", action="store_true", help="записать <модель>.anchors.json")
    a = ap.parse_args()

    mesh = trimesh.load(a.model, force="mesh")
    v = np.asarray(mesh.vertices, float)
    print(f"{a.model}: {len(v)} вершин, габарит {np.round(v.min(0),3)} .. {np.round(v.max(0),3)}")

    if a.render:
        render_views(mesh, a.render)
    if not a.color:
        return

    pos, neg, n = by_color(mesh, [int(x) for x in a.color.split(",")], a.tol)
    print(f"найдено {n} вершин цвета глаз")
    print(f"  eye_x_pos = {np.round(pos,4).tolist()}")
    print(f"  eye_x_neg = {np.round(neg,4).tolist()}")

    if a.write:
        p = a.model.rsplit(".", 1)[0] + ".anchors.json"
        json.dump({"model": a.model.rsplit("/", 1)[-1],
                   "eye_x_pos": np.round(pos, 4).tolist(),
                   "eye_x_neg": np.round(neg, 4).tolist(),
                   "found_by": f"цвет {a.color} tol={a.tol}"},
                  open(p, "w"), indent=2, ensure_ascii=False)
        print(f"записано: {p}")


if __name__ == "__main__":
    main()
