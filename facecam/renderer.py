"""Рендер 3D-модели головы, повёрнутой по позе настоящей головы.

Модель НЕ анимируется: ни мимики, ни блендшейпов, ни скелета — только жёсткий
поворот. Вся выразительность приходит из настоящего видео (глаза и рот), так что
рендеру остаётся простая задача: показать голову под нужным углом.

Проекция ОРТОГРАФИЧЕСКАЯ и настроена прямо в пикселях кадра: левый верхний угол
(0,0), правый нижний (W,H). Так положение и размер модели задаются той же
системой координат, в которой лежат точки лица от MediaPipe, и совмещение с
вырезкой глаз/рта becomes тривиальным. Перспектива смотрелась бы чуть живее на
резких поворотах, но ценой нелинейного совмещения — на этом этапе не стоит того.

Контекст standalone (EGL/GLX без окна), поэтому работает и без X-сессии.
"""
import numpy as np
import moderngl
import trimesh

MODEL = "models/Suzanne.gltf"

# Y модели вверх, Y изображения вниз
_FLIP_Y = np.diag([1.0, -1.0, 1.0]).astype("f4")

VERT = """
#version 330
uniform mat4 mvp;
uniform mat3 nrm;
in vec3 in_vert;
in vec3 in_norm;
in vec2 in_uv;
out vec3 v_norm;
out vec2 v_uv;
void main() {
    gl_Position = mvp * vec4(in_vert, 1.0);
    v_norm = normalize(nrm * in_norm);
    v_uv = in_uv;
}
"""

FRAG = """
#version 330
uniform sampler2D tex;
uniform vec3 light;
uniform float ambient;
in vec3 v_norm;
in vec2 v_uv;
out vec4 f_color;
void main() {
    float d = max(dot(normalize(v_norm), normalize(light)), 0.0);
    vec3 base = texture(tex, v_uv).rgb;
    f_color = vec4(base * (ambient + (1.0 - ambient) * d), 1.0);
}
"""


def _ortho(w, h, near=-1000.0, far=1000.0):
    """Пиксели кадра -> NDC. Y вниз, как в изображении."""
    m = np.identity(4, dtype="f4")
    m[0, 0] = 2.0 / w
    m[1, 1] = -2.0 / h
    m[2, 2] = -2.0 / (far - near)
    m[0, 3] = -1.0
    m[1, 3] = 1.0
    m[2, 3] = -(far + near) / (far - near)
    return m


def _rotation(yaw, pitch, roll):
    """Поворот из углов в градусах. Порядок Y->X->Z (рыскание, тангаж, крен)."""
    y, p, r = np.radians([yaw, pitch, roll])
    cy, sy = np.cos(y), np.sin(y)
    cp, sp = np.cos(p), np.sin(p)
    cr, sr = np.cos(r), np.sin(r)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], "f4")
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], "f4")
    Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]], "f4")
    return Ry @ Rx @ Rz


class Renderer:
    def __init__(self, width, height, model=MODEL, ambient=0.55):
        self.w, self.h = width, height
        self.ambient = ambient
        self.ctx = moderngl.create_standalone_context(require=330)
        self.ctx.enable(moderngl.DEPTH_TEST)

        mesh = trimesh.load(model, force="mesh")
        # Приводим к единичному размеру с центром в нуле, чтобы масштаб потом
        # задавался одним числом в пикселях независимо от того, какая модель.
        v = np.asarray(mesh.vertices, "f4")
        v -= (v.max(0) + v.min(0)) / 2.0
        # Нормируем по ВЫСОТЕ, чтобы size означал высоту модели в пикселях
        # независимо от модели. У Suzanne габарит по X больше (уши), и нормировка
        # по максимальной оси давала неожиданно мелкую голову.
        # Запоминаем нормировку: по ней же приводятся точки привязки (якоря),
        # которые записаны в координатах ИСХОДНОЙ модели.
        self._nc = (np.asarray(mesh.vertices, "f4").max(0) +
                    np.asarray(mesh.vertices, "f4").min(0)) / 2.0
        self._ns = (v[:, 1].max() - v[:, 1].min()) / 2.0
        v /= self._ns
        # ширина модели в долях её высоты — нужна для оценки занимаемой области
        self.aspect = float((v[:, 0].max() - v[:, 0].min()) /
                            (v[:, 1].max() - v[:, 1].min()))

        n = np.asarray(mesh.vertex_normals, "f4")
        uv = np.asarray(mesh.visual.uv, "f4")
        uv[:, 1] = 1.0 - uv[:, 1]            # glTF считает V сверху вниз

        data = np.hstack([v, n, uv]).astype("f4")
        self._vbo = self.ctx.buffer(data.tobytes())
        self._ibo = self.ctx.buffer(np.asarray(mesh.faces, "i4").tobytes())

        self.prog = self.ctx.program(vertex_shader=VERT, fragment_shader=FRAG)
        self.vao = self.ctx.vertex_array(
            self.prog, [(self._vbo, "3f 3f 2f", "in_vert", "in_norm", "in_uv")],
            self._ibo)

        img = mesh.visual.material.baseColorTexture.convert("RGB")
        self.tex = self.ctx.texture(img.size, 3, img.tobytes())
        self.tex.build_mipmaps()
        self.tex.anisotropy = 4.0

        self.fbo = self.ctx.simple_framebuffer((width, height), components=4)
        self.prog["ambient"].value = ambient
        self.prog["light"].value = (0.3, -0.7, 1.0)   # свет спереди-сверху

    def normalize(self, pt):
        """Точка из координат исходной модели -> в нормированные."""
        return (np.asarray(pt, "f4") - self._nc) / self._ns

    def fit_by_eyes(self, pose, a_model, b_model, a_px, b_px,
                    signs=(1, 1, 1), margin=1.0, max_size=4000.0):
        """Подбирает center и size так, чтобы глаза МОДЕЛИ легли на глаза
        человека. Это и есть суть эффекта: настоящие глаза должны попасть в
        глазницы модели, а не жить рядом с ними.

        Возвращает (center, size). Вращение берётся из позы, поэтому при
        повороте головы межглазное расстояние модели сокращается ровно так же,
        как настоящее, и размер не скачет.
        """
        R = _FLIP_Y @ _rotation(signs[0] * pose.yaw,
                                signs[1] * pose.pitch,
                                signs[2] * pose.roll)
        A = R @ self.normalize(a_model)
        B = R @ self.normalize(b_model)

        d_model = (A - B)[:2]
        d_real = np.asarray(a_px, "f4") - np.asarray(b_px, "f4")
        nm = float(np.linalg.norm(d_model))
        if nm < 1e-3:                      # голова почти в профиль — якоря слиплись
            return None, None
        size = min(2.0 * float(np.linalg.norm(d_real)) / nm * margin, max_size)

        mid_model = ((A + B) / 2.0)[:2] * (size / 2.0)
        mid_px = (np.asarray(a_px, "f4") + np.asarray(b_px, "f4")) / 2.0
        return tuple(mid_px - mid_model), size

    def render(self, pose, center, size, flip_yaw=1, flip_pitch=1, flip_roll=1):
        """Возвращает (rgb HxWx3, alpha HxW) — модель и её силуэт.

        center — (x, y) в пикселях, size — размер модели в пикселях.
        Знаки поворотов вынесены наружу: соглашение осей у трекера и у модели
        совпасть само не обязано, подбирается один раз глазами.
        """
        R = _rotation(flip_yaw * pose.yaw, flip_pitch * pose.pitch,
                      flip_roll * pose.roll)

        # Y изображения смотрит вниз, Y модели — вверх. Без этого разворота
        # модель встаёт на голову; раньше это случайно компенсировалось тем,
        # что OpenGL отдаёт буфер снизу вверх, но положение при этом зеркалилось.
        RF = _FLIP_Y @ R
        model = np.identity(4, dtype="f4")
        model[:3, :3] = RF * (size / 2.0)
        model[0, 3], model[1, 3] = center

        mvp = _ortho(self.w, self.h) @ model

        self.fbo.use()
        self.fbo.clear(0.0, 0.0, 0.0, 0.0)
        self.tex.use(0)
        self.prog["tex"].value = 0
        self.prog["mvp"].write(np.ascontiguousarray(mvp.T, "f4"))
        self.prog["nrm"].write(np.ascontiguousarray(RF.T, "f4"))
        self.vao.render()

        buf = np.frombuffer(self.fbo.read(components=4), np.uint8)
        # OpenGL отдаёт строки снизу вверх — приводим к порядку изображения.
        img = np.ascontiguousarray(buf.reshape(self.h, self.w, 4)[::-1])
        return img[:, :, :3], img[:, :, 3]
