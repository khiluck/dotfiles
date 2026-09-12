#!/usr/bin/env python
"""Генератор ананаса: тело с чешуёй и зелёный хохолок сверху.

Чешуйки настоящего ананаса сидят на пересечении двух ВСТРЕЧНЫХ спиралей, и
числа спиралей — соседние числа Фибоначчи (8 и 13). Отсюда характерная
ромбическая сетка. Мы задаём её одной формулой и по ней же считаем И рельеф,
И текстуру — тогда бугры и рисунок совпадают точно, а не «примерно».

Сетка — поверхность вращения с ЯВНЫМ швом (кольцо замыкается дублем вершин).
Икосфера, как у картошки, тут не годится: на ней шов рвал бы узор.

Нормали считаем сами, численным дифференцированием по (u,t). Если доверить их
trimesh, на шве получится светлая полоса: дублирующие вершины видят только свою
сторону и получают разные нормали.
"""
import argparse, json, math
import numpy as np
import trimesh
from PIL import Image
from scipy.interpolate import PchipInterpolator

TAU = 2 * math.pi

# Числа спиралей. Целые по u — иначе узор не сойдётся на шве.
N1, N2 = 8, 13
# Наклон спиралей по высоте: подобран так, чтобы ромбы были近 квадратными.
K1, K2 = 13.0, 8.0


# Силуэт ананаса задан контрольными точками, а не формулой: формулы дают либо
# шар, либо бочку-банку, а тут нужен свой профиль — округлый низ, полная
# середина и сужение к макушке, где сидит хохолок. Гладко интерполируем PCHIP:
# он не даёт выбросов между точками, а нормали считаются численно и требуют
# гладкости.
_PT = np.array([0.00, 0.06, 0.16, 0.30, 0.45, 0.62, 0.80, 0.92, 1.00])
_PR = np.array([0.26, 0.58, 0.83, 0.96, 1.00, 0.98, 0.90, 0.78, 0.62])
_PROFILE = PchipInterpolator(_PT, _PR)


def profile(t):
    """Радиус тела по высоте t in [0,1]."""
    return _PROFILE(np.clip(t, 0.0, 1.0))


def scales(u, t, sharp=1.7):
    """Ромбическая сетка чешуек: 1 в центре чешуйки, 0 в желобке.

    sharp заостряет: чем больше, тем уже бугорок и шире желобок между ними.
    На 1.0 получается мягкая волна, на 1.7 — читаемая чешуя.
    """
    a = N1 * u + K1 * t
    b = N2 * u - K2 * t
    ca = (0.5 + 0.5 * np.cos(TAU * a)) ** sharp
    cb = (0.5 + 0.5 * np.cos(TAU * b)) ** sharp
    return ca * cb


def eye_dist(u, t):
    """Расстояние до центра ближайшей чешуйки в координатах решётки —
    по нему рисуем тёмный «глазок» и коричневый хохолок на каждой чешуйке."""
    a = N1 * u + K1 * t
    b = N2 * u - K2 * t
    da = (a + 0.5) % 1.0 - 0.5
    db = (b + 0.5) % 1.0 - 0.5
    return np.sqrt(da * da + db * db)


def _cell_hash(a, b):
    """Псевдослучайное число на чешуйку — чтобы они не были близнецами.

    Целочисленный хэш, а не sin(): синусный хэш даёт видимую регулярную
    структуру — на текстуре проступали прямоугольные пятна крупнее самих
    чешуек.
    """
    ia = np.floor(a + 0.5).astype(np.int64)
    ib = np.floor(b + 0.5).astype(np.int64)
    h = (ia * np.int64(73856093)) ^ (ib * np.int64(19349663))
    h = (h ^ (h >> 13)) * np.int64(1274126177)
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def texture(size=1024, crown=128, sharp=0.9, bright=1.0):
    """Текстура тела + полоса для листьев хохолка.

    Рисуется ПО ТОЙ ЖЕ формуле, что и рельеф, поэтому тёмные «глазки» садятся
    ровно на вершины бугорков, а не рядом. В этом весь смысл — если рисовать
    текстуру отдельно, чешуя расползается.

    Снизу к телу подклеена полоса (crown строк) с зелёным градиентом: листьям
    нужен свой цвет, а лезть в текстуру тела нельзя. Развёртка тела при этом
    сжимается по вертикали, см. body_v().
    """
    W, Hb = size, size
    H = Hb + crown
    img = np.zeros((H, W, 3), np.float32)

    uu = (np.arange(W) + 0.5) / W
    tt = (np.arange(Hb) + 0.5) / Hb
    U, T = np.meshgrid(uu, tt, indexing="xy")

    # У ТЕКСТУРЫ заострение меньше, чем у рельефа: на текстуре широкая светлая
    # грань чешуйки и тонкий тёмный желобок, иначе поверхность читается
    # оливковой — тёмные желобки занимают её большую часть.
    s = scales(U, T, sharp)

    # Базовый цвет: снизу теплее и краснее, к макушке желтее и зеленее —
    # как у настоящего, он дозревает снизу вверх.
    low = np.array([0.68, 0.45, 0.14]) * bright
    high = np.array([0.92, 0.76, 0.26]) * bright
    base = low + (high - low) * T[..., None]

    # Гребень чешуйки светлее, желобок темнее.
    crest = np.clip(base * 1.25 + 0.10, 0, 1)
    # Дно желобка: чем выше, тем меньше «грязи» в общем тоне.
    groove = base * (0.62 + 0.14 * (bright - 1.0) / 0.25)
    col = groove + (crest - groove) * s[..., None]

    # Каждая чешуйка чуть своего оттенка.
    a = N1 * U + K1 * T
    b = N2 * U - K2 * T
    col *= (0.88 + 0.24 * _cell_hash(a, b))[..., None]

    # Тёмный «глазок» в центре чешуйки и короткий бурый хохолок на нём.
    d = eye_dist(U, T)
    eye = np.clip(1.0 - d / 0.13, 0, 1) ** 1.6
    col = col * (1.0 - 0.72 * eye[..., None]) +           np.array([0.16, 0.10, 0.05]) * (0.72 * eye)[..., None]
    bristle = np.clip(1.0 - d / 0.07, 0, 1)
    col = col * (1.0 - bristle[..., None]) +           np.array([0.34, 0.26, 0.12]) * bristle[..., None]

    img[:Hb] = col

    # Полоса для листьев. Оттенок меняется ВДОЛЬ полосы (по u), а каждый лист
    # берёт из неё свой случайный кусочек (leaf(u0=...)) — значит, и свой цвет.
    # У настоящего ананаса листья разного возраста: наружные тёмные и грубые,
    # внутренние молодые, салатовые, а кончики подсыхают в рыжину.
    g = np.linspace(0.0, 1.0, crown)[:, None, None]      # вдоль листа

    # Плавная псевдослучайная смесь: несколько синусоид разной частоты, чтобы
    # соседние куски полосы отличались, но внутри одного листа цвет не прыгал.
    mix = (0.5 + 0.44 * np.sin(TAU * uu * 3.0 + 1.3)
               + 0.20 * np.sin(TAU * uu * 7.0 + 0.4)
               + 0.11 * np.sin(TAU * uu * 13.0 + 2.1))
    mix = np.clip(mix, 0.0, 1.0)[None, :, None]

    dark = np.array([0.06, 0.21, 0.05])                  # старый тёмный лист
    lime = np.array([0.60, 0.88, 0.31])                  # молодой салатовый
    tipc = dark + (lime - dark) * mix                    # цвет у кончика
    basec = tipc * 0.48                                  # у основания темнее
    leaf = basec + (tipc - basec) * g

    # Подсохшие кончики у части листьев — чуть рыжины на последней четверти.
    dry = np.clip((g - 0.78) / 0.22, 0, 1) * np.clip(1.0 - mix * 1.6, 0, 1)
    leaf = leaf * (1.0 - dry) + np.array([0.62, 0.45, 0.16]) * dry

    # продольные жилки
    vein = 0.5 + 0.5 * np.cos(TAU * uu * 46.0)
    leaf = leaf * (0.86 + 0.14 * vein)[None, :, None]
    img[Hb:] = leaf

    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), Hb / H


def body_pos(u, t, amp, height, radius, sharp=1.7):
    """Точка поверхности тела. u — вокруг оси (0..1), t — снизу вверх (0..1)."""
    ang = TAU * u
    r = profile(t) * radius
    # Рельеф наружу по радиусу — этого достаточно, поверхность почти цилиндр.
    r = r * (1.0 + amp * scales(u, t, sharp))
    y = (t - 0.5) * height
    return np.stack([r * np.sin(ang), y, r * np.cos(ang)], axis=-1)


def body(nu=160, nv=120, amp=0.065, height=2.0, radius=0.72, sharp=1.7):
    """Сетка вращения со швом + честные нормали."""
    u = np.linspace(0.0, 1.0, nu + 1)          # nu+1: последний столбец — шов
    t = np.linspace(0.0, 1.0, nv + 1)
    U, T = np.meshgrid(u, t, indexing="ij")
    P = body_pos(U, T, amp, height, radius, sharp)

    # Нормали численно: центральные разности по u и t. На шве работает верно,
    # потому что формула периодична по u.
    e = 1e-3
    du = body_pos(U + e, T, amp, height, radius, sharp) \
       - body_pos(U - e, T, amp, height, radius, sharp)
    dt = body_pos(U, np.clip(T + e, 0, 1), amp, height, radius, sharp) \
       - body_pos(U, np.clip(T - e, 0, 1), amp, height, radius, sharp)
    N = np.cross(du, dt)
    n = np.linalg.norm(N, axis=-1, keepdims=True)
    N = np.divide(N, np.where(n < 1e-12, 1.0, n))

    verts = P.reshape(-1, 3)
    norms = N.reshape(-1, 3)
    uvs = np.stack([U, T], axis=-1).reshape(-1, 2)

    idx = lambda i, j: i * (nv + 1) + j
    faces = []
    for i in range(nu):
        for j in range(nv):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            faces += [[a, b, c], [a, c, d]]

    # Крышки. Профиль не сходится в точку ни снизу, ни сверху (низ плоский,
    # сверху сидит хохолок), поэтому без них модель просвечивает насквозь —
    # на наклонённом кадре видно нутро.
    verts = list(verts); norms = list(norms); uvs = list(uvs)
    for j, ny in ((0, -1.0), (nv, 1.0)):
        c = len(verts)
        verts.append([0.0, (j / nv - 0.5) * height, 0.0])
        norms.append([0.0, ny, 0.0])
        # t чуть внутрь диапазона тела: ровно на t=1 крышка попадала на первую
        # строку зелёной полосы и макушка зеленела.
        uvs.append([0.5, min(j / nv, 0.985)])
        for i in range(nu):
            a, b = idx(i, j), idx(i + 1, j)
            faces.append([c, a, b] if ny < 0 else [c, b, a])

    return (np.array(verts, "f4"), np.array(faces, np.int64),
            np.array(norms, "f4"), np.array(uvs, "f4"))


def leaf(base, azim, tilt, length, width, curve, droop, keel, u0, du, body_frac,
         nseg=10):
    """Один лист хохолка: полоска из трёх рядов вершин (край-киль-край).

    Киль по центру нужен не для красоты: плоский лист при боковом свете
    выглядит бумажкой, а сложенный домиком даёт нормальную светотень.

    Развёртка вдоль листа идёт по зелёной полосе текстуры: у основания тёмный
    край полосы, у кончика светлый.
    """
    up = np.array([0.0, 1.0, 0.0])
    out = np.array([math.sin(azim), 0.0, math.cos(azim)])
    side = np.array([math.cos(azim), 0.0, -math.sin(azim)])

    d0 = up * math.cos(tilt) + out * math.sin(tilt)
    d0 /= np.linalg.norm(d0)

    s = np.linspace(0.0, 1.0, nseg + 1)
    # Ось листа: прямая + квадратичный отгиб наружу и вниз к кончику.
    axis = (base[None, :] + length * (d0[None, :] * s[:, None]
            + (out[None, :] * curve - up[None, :] * droop) * (s ** 2)[:, None]))
    # Ширина: сужается к острию.
    w = width * np.clip(1.0 - s, 0, 1) ** 0.55
    w[-1] = 0.0                                   # кончик — точка

    left = axis + side[None, :] * (w / 2)[:, None]
    right = axis - side[None, :] * (w / 2)[:, None]
    mid = axis + up[None, :] * (keel * w)[:, None]

    verts = np.concatenate([left, mid, right], axis=0)

    n = nseg + 1
    faces = []
    for i in range(nseg):
        for (A, B) in ((0, n), (n, 2 * n)):        # левая и правая половинки
            a, b = A + i, A + i + 1
            c, d = B + i + 1, B + i
            faces += [[a, b, c], [a, c, d]]

    # Развёртка: вдоль листа — по зелёной полосе (с учётом флипа v в рендере),
    # поперёк — узкий кусочек u, чтобы поймать пару продольных жилок.
    gv = (1.0 - body_frac) * (1.0 - s)
    uvs = np.concatenate([
        np.stack([np.full(n, u0), gv], 1),
        np.stack([np.full(n, u0 + du * 0.5), gv], 1),
        np.stack([np.full(n, u0 + du), gv], 1)])
    return verts, np.array(faces, np.int64), uvs


def _vnormals(v, f):
    """Нормали усреднением по смежным граням — для листьев, у тела они свои."""
    n = np.zeros_like(v, dtype="f8")
    tri = v[f]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    for k in range(3):
        np.add.at(n, f[:, k], fn)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    return (n / np.where(ln < 1e-12, 1.0, ln)).astype("f4")


def crown(top_y, top_r, rings, body_frac, seed=11, scale=1.0):
    """Хохолок: несколько колец листьев. К центру листья длиннее и прямее,
    по краю — короче и разложены в стороны, как у настоящего."""
    rng = np.random.default_rng(seed)
    V, F, UV = [], [], []
    for (count, rad, tilt, length, width, curve, droop) in rings:
        for k in range(count):
            # Золотой угол между листьями — иначе кольца встают частоколом.
            az = (k / count) * TAU + rng.uniform(-0.12, 0.12) + rad * 7.0
            jitter = rng.uniform(0.86, 1.14)
            base = np.array([math.sin(az) * top_r * rad, top_y - 0.02,
                             math.cos(az) * top_r * rad])
            v, f, uv = leaf(base, az,
                            tilt + rng.uniform(-0.08, 0.08),
                            length * jitter * scale,
                            width * scale,
                            curve, droop,
                            keel=0.22,
                            u0=rng.uniform(0.0, 0.94), du=0.05,
                            body_frac=body_frac)
            F.append(f + sum(len(x) for x in V))
            V.append(v); UV.append(uv)
    return np.vstack(V), np.vstack(F), np.vstack(UV)


# Кольца хохолка: (сколько листьев, радиус от оси, наклон, длина, ширина,
# отгиб наружу, провисание). К центру листья длиннее и прямее.
RINGS = [
    (17, 1.00, 0.95, 0.66, 0.22, 0.30, 0.26),   # наружное: короче, в стороны
    (14, 0.76, 0.72, 0.84, 0.21, 0.22, 0.16),
    (11, 0.52, 0.48, 1.00, 0.19, 0.13, 0.08),
    (7,  0.26, 0.22, 1.14, 0.16, 0.06, 0.03),   # центр: длинные, почти вверх
]


def build(nu=160, nv=120, amp=0.065, sharp=1.7, tex_sharp=0.9,
          size=1024, crown_rows=128, bright=1.0,
          crown_scale=1.0, seed=11, with_crown=True):
    """Тело + хохолок + текстура, с развёрткой, ужатой под полосу листьев."""
    tex, body_frac = texture(size, crown_rows, tex_sharp, bright)
    v, f, n, uv = body(nu, nv, amp, sharp=sharp)
    uv = uv.copy()
    # Рендер переворачивает v (renderer.py: uv[:,1] = 1 - uv[:,1]), поэтому
    # пишем уже перевёрнутое. Без этого полоса листьев оказывалась на дне
    # ананаса: проверено на первом же рендере.
    uv[:, 1] = 1.0 - uv[:, 1] * body_frac

    if with_crown:
        top_y = v[:, 1].max()
        top_r = float(profile(1.0)) * 0.72
        cv_, cf, cuv = crown(top_y, top_r, RINGS, body_frac,
                             seed=seed, scale=crown_scale)
        cn = _vnormals(cv_, cf)
        f = np.vstack([f, cf + len(v)])
        v = np.vstack([v, cv_.astype("f4")])
        n = np.vstack([n, cn])
        uv = np.vstack([uv, cuv.astype("f4")])

    return v, f, n, uv, tex, body_frac


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="models/Pineapple.glb")
    ap.add_argument("--amp", type=float, default=0.065, help="высота чешуек")
    ap.add_argument("--sharp", type=float, default=1.7, help="заострение чешуек")
    ap.add_argument("--tex-sharp", type=float, default=0.9,
                    help="ширина светлой грани чешуйки на текстуре")
    ap.add_argument("--bright", type=float, default=1.2,
                    help="яркость кожуры: >1 светлее и золотистее")
    ap.add_argument("--nu", type=int, default=160)
    ap.add_argument("--nv", type=int, default=120)
    ap.add_argument("--crown-scale", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=11)
    # Лицо. eye-y — доля высоты ТЕЛА (без хохолка): 1.0 у самой макушки тела.
    ap.add_argument("--eye-dx", type=float, default=0.30)
    ap.add_argument("--eye-y", type=float, default=0.74)
    # Умолчания должны совпадать с тем, что лежит в models/*.anchors.json:
    # иначе перегенерация без ключей молча даёт другую модель.
    ap.add_argument("--margin", type=float, default=0.95)
    ap.add_argument("--lift-lips", type=float, default=0.48)
    a = ap.parse_args()

    v, f, n, uv, tex, frac = build(a.nu, a.nv, a.amp, a.sharp, a.tex_sharp,
                                   bright=a.bright,
                                   crown_scale=a.crown_scale, seed=a.seed)
    # Центруем: рендер нормирует по высоте, а якоря пишем уже в этих координатах.
    v = v - (v.max(0) + v.min(0)) / 2.0
    print(f"{len(v)} вершин, {len(f)} треугольников, "
          f"габарит {np.round(v.min(0),2)} .. {np.round(v.max(0),2)}")

    m = trimesh.Trimesh(vertices=v, faces=f, vertex_normals=n, process=False)
    m.visual = trimesh.visual.TextureVisuals(
        uv=uv, material=trimesh.visual.material.PBRMaterial(
            baseColorTexture=tex.convert("RGB"),
            metallicFactor=0.0, roughnessFactor=0.85))
    m.export(a.out)

    # Якоря ставим на ТЕЛЕ, а не где попало: берём только вершины сетки тела
    # (они идут первыми) и тянемся к лицевой стороне, +Z.
    nbody = (a.nu + 1) * (a.nv + 1)
    bv = v[:nbody]
    y_lo, y_hi = bv[:, 1].min(), bv[:, 1].max()
    hh = (y_hi - y_lo) / 2.0
    want_y = y_lo + (y_hi - y_lo) * a.eye_y
    front = bv[bv[:, 2] > 0]

    def on_surface(x, y):
        return front[np.argmin(np.linalg.norm(front[:, :2] - [x, y], axis=1)
                               - front[:, 2] * 0.001)]

    ep = on_surface(+a.eye_dx * hh, want_y)
    en = on_surface(-a.eye_dx * hh, want_y)
    p = a.out.rsplit(".", 1)[0] + ".anchors.json"
    json.dump({"_comment": "Ананас сгенерирован tools/make_pineapple.py. "
                           "Глаз у ананаса нет — якоря назначены.",
               "model": a.out.rsplit("/", 1)[-1],
               "eye_x_pos": [round(float(x), 4) for x in ep],
               "eye_x_neg": [round(float(x), 4) for x in en],
               "margin": a.margin,
               "lift_lips": a.lift_lips,
               "found_by": f"make_pineapple.py --eye-dx {a.eye_dx} "
                           f"--eye-y {a.eye_y} --lift-lips {a.lift_lips}"},
              open(p, "w"), indent=2, ensure_ascii=False)
    print(f"{a.out} и {p}: глаза {np.round(ep,3)} / {np.round(en,3)}")


if __name__ == "__main__":
    main()
