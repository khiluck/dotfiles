#!/bin/bash
set -euo pipefail

# Сводит в одно виртуальное устройство "recording" системный звук (то, что
# играет в колонках) и микрофон — из него потом пишет ffmpeg (см. screencast).
#
# Устройства берём ПО УМОЛЧАНИЮ, а не по жёсткому имени: так запись работает и
# со встроенным звуком ноутбука, и с внешней USB-картой (Sound Blaster), и не
# ломается, если карту отключить. Раньше имена были прописаны руками, и без той
# конкретной USB-карты запись просто не стартовала.

SPEAKER_SINK="$(pactl get-default-sink)"
MIC_SOURCE="$(pactl get-default-source)"

# Если микрофон по умолчанию — это monitor какого-то выхода (т.е. не настоящий
# вход, а «системный звук»), второй loopback дал бы двойной системный звук.
# В этом случае микрофон не подмешиваем.
mic_is_monitor=0
case "$MIC_SOURCE" in
	*.monitor) mic_is_monitor=1 ;;
esac

# Чистим возможные старые модули, чтобы не плодить дубликаты
pactl list short modules | awk '/module-(loopback|null-sink|combine-sink)/{print $1}' | xargs -r -n1 pactl unload-module

# 1) Виртуальный выход для записи
pactl load-module module-null-sink sink_name=recording sink_properties=device.description=recording >/dev/null

# 2) Системный звук → в запись (берём monitor реального выхода)
pactl load-module module-loopback source="${SPEAKER_SINK}.monitor" sink=recording latency_msec=60 >/dev/null

# 3) Микрофон → в запись
if [ "$mic_is_monitor" = 0 ]; then
	pactl load-module module-loopback source="$MIC_SOURCE" sink=recording latency_msec=60 >/dev/null
else
	echo "⚠️  Источник по умолчанию — monitor ($MIC_SOURCE), микрофон не подмешан." >&2
fi

# 4) (опционально) Самопрослушка микрофона в колонки — если нужно слышать себя
# pactl load-module module-loopback source="$MIC_SOURCE" sink="$SPEAKER_SINK" latency_msec=120 >/dev/null

# По умолчанию вывод оставляем реальным колонкам (НЕ combined)
pactl set-default-sink "$SPEAKER_SINK"

echo "🎧 ${SPEAKER_SINK}.monitor + 🎤 $MIC_SOURCE → [recording]; latency ≈ 60 ms. Готово."
