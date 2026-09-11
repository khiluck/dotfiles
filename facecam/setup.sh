#!/bin/bash
# Разворачивание facecam с нуля.
# Модель, фоны и картошка лежат в репозитории — интернет нужен только для venv.
set -e
cd "$(dirname "$0")"

echo "== виртуальное окружение =="
python -m venv venv
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r requirements.txt

echo "== модуль виртуальной камеры =="
if ! modinfo v4l2loopback >/dev/null 2>&1; then
    echo "  нет v4l2loopback — ставлю (нужен sudo)"
    sudo pacman -S --needed --noconfirm v4l2loopback-dkms
fi

echo
echo "Готово. Запуск:"
echo "  ./venv/bin/python facecam.py avatar --model models/Potato.glb \\"
echo "      --background assets/backgrounds/beach.jpg"
echo
echo "Затем выбрать камеру 'facecam' в Teams или браузере."
