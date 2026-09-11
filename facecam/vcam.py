"""Вывод кадров в виртуальную камеру (v4l2loopback).

Тонкая обёртка над pyvirtualcam. Вынесена отдельно, потому что это единственное
место, которое знает про устройство вывода: если завтра pyvirtualcam отвалится
об ABI нового Python, замена ffmpeg-трубой затронет только этот файл.
"""
import subprocess
import numpy as np

DEVICE = "/dev/video10"


class VCam:
    """Пишет BGR-кадры (как их отдаёт OpenCV) в v4l2loopback."""

    def __init__(self, width, height, fps=30, device=DEVICE):
        import pyvirtualcam
        self._cam = pyvirtualcam.Camera(
            width=width, height=height, fps=fps, device=device,
            fmt=pyvirtualcam.PixelFormat.BGR)
        self.device = self._cam.device

    def send(self, bgr):
        self._cam.send(bgr)
        # Не даём писать быстрее заявленного fps: иначе потребитель захлебнётся,
        # а v4l2loopback начнёт копить задержку.
        self._cam.sleep_until_next_frame()

    def close(self):
        self._cam.close()

    def __enter__(self):  return self
    def __exit__(self, *a):  self.close()


def ensure_module(video_nr=10, label="facecam"):
    """Загружает v4l2loopback, если его ещё нет. Требует sudo.

    exclusive_caps=1 обязателен: без него устройство объявляет разом OUTPUT и
    CAPTURE, и Chromium (а значит и Teams на Electron) такую камеру игнорирует.
    """
    import os
    if os.path.exists(f"/dev/video{video_nr}"):
        return
    subprocess.run(
        ["sudo", "modprobe", "v4l2loopback", "devices=1",
         f"video_nr={video_nr}", f"card_label={label}", "exclusive_caps=1"],
        check=True)
    # udev назначает группу video не мгновенно — без этого возможна гонка,
    # когда устройство уже есть, а прав на него ещё нет.
    subprocess.run(["sudo", "udevadm", "settle"], check=False)
