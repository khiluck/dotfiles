"""Этап 1: проверка трекинга на живом видео, без окон и без 3D.

Гоняет камеру N секунд, меряет реальный fps и складывает отладочные кадры:
показывает, что именно будет вырезано из настоящего видео (глаза и рот).
"""
import argparse, time, sys
import cv2, numpy as np

from tracker import Tracker
import regions


def mask_of(face, shape, names, feather=0):
    """Альфа-маска вырезаемых областей. feather — радиус размытия краёв в px."""
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, face.polygons(names), 255)
    if feather:
        k = feather * 2 + 1
        m = cv2.GaussianBlur(m, (k, k), 0)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="/dev/video0")
    ap.add_argument("--size", default="640x480")
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--outdir", default="/tmp/facecam-probe")
    ap.add_argument("--feather", type=int, default=6)
    a = ap.parse_args()

    w, h = (int(x) for x in a.size.split("x"))
    import os; os.makedirs(a.outdir, exist_ok=True)

    cap = cv2.VideoCapture(a.device, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    if not cap.isOpened():
        sys.exit(f"не открылась камера {a.device}")

    n = hit = 0
    t_track = 0.0
    t0 = time.time()
    saved = []

    with Tracker() as track:
        while time.time() - t0 < a.seconds:
            ok, bgr = cap.read()
            if not ok:
                break
            n += 1
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

            t = time.perf_counter()
            face = track(rgb, (time.time() - t0) * 1000)
            t_track += time.perf_counter() - t

            if face is None:
                continue
            hit += 1

            # отладочные кадры — три штуки за прогон, в начале/середине/конце
            if hit in (1, 15, 40):
                m = mask_of(face, bgr.shape, regions.KEEP_REAL, a.feather)
                cut = cv2.bitwise_and(bgr, bgr, mask=m)          # что останется настоящим
                ann = bgr.copy()
                cv2.polylines(ann, face.polygons(regions.KEEP_REAL), True, (0, 255, 0), 1)
                cv2.polylines(ann, face.polygons(["face_oval"]),     True, (255, 0, 0), 1)
                cv2.putText(ann, str(face.pose), (8, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                p = f"{a.outdir}/{hit:03d}"
                cv2.imwrite(p + "-ann.png", ann)
                cv2.imwrite(p + "-cut.png", cut)
                saved += [p + "-ann.png", p + "-cut.png"]
                print(f"  кадр {hit:3}: {face.pose}")

    cap.release()
    dt = time.time() - t0
    print(f"\nкадров: {n} за {dt:.1f} с  ->  {n/dt:.1f} fps сквозных")
    print(f"лицо найдено: {hit}/{n} ({100*hit/max(n,1):.0f}%)")
    print(f"трекинг: {1000*t_track/max(n,1):.1f} мс/кадр  (потолок {max(n,1)/max(t_track,1e-9):.0f} fps)")
    print("отладочные кадры:"); [print("  ", s) for s in saved]


if __name__ == "__main__":
    main()
