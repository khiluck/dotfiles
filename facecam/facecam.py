#!/usr/bin/env python
"""facecam — виртуальная камера: 3D-модель + настоящие глаза и рот.

Режимы:
  passthrough  видео как есть, без обработки (проверка тракта)
  track        то же + разметка лица поверх (видно, что трекер жив)
  avatar       рабочий режим: 3D-модель + настоящие глаза и рот
"""
import argparse, os, signal, sys, time
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))

from tracker import Tracker
from vcam import VCam, ensure_module
import regions


def install_signals():
    """Сделать процесс останавливаемым сигналом.

    Запуск в фоне через `&` из НЕинтерактивного шелла (а именно так facecam
    стартует из webcamtoggle по хоткею) приводит к тому, что SIGINT и SIGQUIT
    наследуются как SIG_IGN — этого требует POSIX, — а Python такое наследование
    сохраняет. Проверено на живом процессе: SIGINT висел в SigIgn из
    /proc/<pid>/status, и `pkill -2` не убивал facecam вообще, из-за чего
    /dev/video0 оставалась занятой после выключения.

    Поэтому SIGINT переустанавливаем явно, а SIGTERM обрабатываем сами, чтобы
    отработал блок finally и камера с виртуальным устройством закрылись.
    """
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt))


def open_camera(device, w, h):
    cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    if not cap.isOpened():
        sys.exit(f"не открылась камера {device}")
    return cap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["passthrough", "track", "avatar"])
    ap.add_argument("--model",
                    default=os.path.join(HERE, "models", "Suzanne.gltf"))
    ap.add_argument("--anchors", default=None,
                    help="по умолчанию <модель>.anchors.json рядом с моделью")
    ap.add_argument("--margin", type=float, default=None,
                    help="размер модели сверх совмещения по глазам "
                         "(по умолчанию берётся из файла якорей модели)")
    ap.add_argument("--dilate-eyes", type=int, default=None,
                    help="расширение вырезки глаз, px (можно отрицательное)")
    ap.add_argument("--dilate-lips", type=int, default=None,
                    help="расширение вырезки губ, px (0 — ровно по кайме губ)")
    ap.add_argument("--feather", type=int, default=None,
                    help="радиус растушёвки края вырезки, px "
                         "(по умолчанию из compose.FEATHER)")
    ap.add_argument("--zoom-eyes", type=float, default=None,
                    help="увеличение вырезки глаз относительно их центра")
    ap.add_argument("--lift-lips", type=float, default=None,
                    help="поднять рот к глазам, в долях расстояния глаза-рот "
                         "(0 — оставить на месте, 0.25 — на четверть пути)")
    ap.add_argument("--background", default="real",
                    help="real | blur[:N] | R,G,B | #rrggbb | путь к картинке")
    ap.add_argument("--bg-blur", type=int, default=0,
                    help="размыть картинку фона на N px — так она меньше "
                         "спорит с головой и больше похожа на настоящий задник")
    ap.add_argument("--no-clip", action="store_true",
                    help="не обрезать вырезку силуэтом модели")
    ap.add_argument("--device", default="/dev/video0")
    ap.add_argument("--out", default="/dev/video10")
    ap.add_argument("--size", default="640x480")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--seconds", type=float, default=0, help="0 = бесконечно")
    ap.add_argument("--mirror", action="store_true", default=True,
                    help="зеркалить, как в webcamtoggle")
    a = ap.parse_args()

    install_signals()

    w, h = (int(x) for x in a.size.split("x"))
    ensure_module(int(a.out.rsplit("video", 1)[1]))

    cap = open_camera(a.device, w, h)
    track = Tracker() if a.mode in ("track", "avatar") else None

    rend = anchors = None
    if a.mode == "avatar":
        from renderer import Renderer
        from compose import compose, load_anchors
        rend = Renderer(w, h, a.model)
        anchors = load_anchors(a.anchors or
                               a.model.rsplit(".", 1)[0] + ".anchors.json")
        from background import Background
        bg = Background(a.background, w, h, blur=a.bg_blur)

        from compose import DILATE, ZOOM
        dilate = dict(DILATE)
        zoom = dict(ZOOM)
        if a.zoom_eyes is not None:
            zoom["left_eye"] = zoom["right_eye"] = a.zoom_eyes

        from compose import LIFT
        lift = dict(LIFT)
        if a.lift_lips is not None:
            lift["lips"] = a.lift_lips
        if a.dilate_eyes is not None:
            dilate["left_eye"] = dilate["right_eye"] = a.dilate_eyes
        if a.dilate_lips is not None:
            dilate["lips"] = a.dilate_lips

    n, lost, t0 = 0, 0, time.time()
    try:
        with VCam(w, h, a.fps, a.out) as out:
            print(f"пишу в {out.device}  ({w}x{h} @ {a.fps})  Ctrl-C для выхода")
            while True:
                ok, bgr = cap.read()
                if not ok:
                    break
                if a.mirror:
                    bgr = cv2.flip(bgr, 1)

                if track is not None:
                    face = track(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB),
                                 (time.time() - t0) * 1000)
                    if face is None and a.mode == "avatar" and bg.kind != "real":
                        # Лицо потеряно. Ни в коем случае не отдавать сырой кадр:
                        # смысл режима в том, чтобы настоящего лица не было видно,
                        # а потеря трекинга на секунду выдала бы и лицо, и комнату.
                        bgr = bg(bgr)
                        lost += 1
                    if face is not None:
                        if a.mode == "avatar":
                            bgr = compose(bgr, face, rend, anchors,
                                          base=None if bg.kind == "real"
                                               else bg(bgr),
                                          clip=not a.no_clip,
                                          margin=a.margin, dilate=dilate,
                                          zoom=zoom, lift=lift,
                                          **({} if a.feather is None
                                             else {'feather': a.feather}))
                        else:
                            cv2.polylines(bgr, face.polygons(regions.KEEP_REAL),
                                          True, (0, 255, 0), 1)
                            cv2.putText(bgr, str(face.pose), (8, 20),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (0, 255, 255), 1)

                out.send(bgr)
                n += 1
                if a.seconds and time.time() - t0 >= a.seconds:
                    break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()

    dt = time.time() - t0
    print(f"отдано {n} кадров за {dt:.1f} с -> {n/max(dt,1e-9):.1f} fps")
    if lost:
        print(f"лицо не найдено в {lost} кадрах ({100*lost/max(n,1):.1f}%) — "
              f"в них отдавался только фон")


if __name__ == "__main__":
    main()
