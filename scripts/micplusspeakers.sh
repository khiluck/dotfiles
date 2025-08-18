#!/bin/bash
set -euo pipefail

# 👉 Подставь свои точные имена (pactl list short sources/sinks)
MIC_SOURCE="alsa_input.usb-Creative_Technology_Ltd_Sound_Blaster_Play__3_00204429-00.analog-stereo"
SPEAKER_SINK="alsa_output.usb-Creative_Technology_Ltd_Sound_Blaster_Play__3_00204429-00.analog-stereo"

# Чистим возможные старые модули, чтобы не плодить дубликаты
pactl list short modules | awk '/module-(loopback|null-sink|combine-sink)/{print $1}' | xargs -r -n1 pactl unload-module

# 1) Виртуальный выход для записи
pactl load-module module-null-sink sink_name=recording sink_properties=device.description=recording >/dev/null

# 2) Системный звук → в запись (берём monitor реального выхода)
pactl load-module module-loopback source="${SPEAKER_SINK}.monitor" sink=recording latency_msec=60 >/dev/null

# 3) Микрофон → в запись
pactl load-module module-loopback source="$MIC_SOURCE" sink=recording latency_msec=60 >/dev/null

# 4) (опционально) Самопрослушка микрофона в колонки — если нужно слышать себя
# pactl load-module module-loopback source="$MIC_SOURCE" sink="$SPEAKER_SINK" latency_msec=120 >/dev/null

# По умолчанию вывод оставляем реальным колонкам (НЕ combined)
pactl set-default-sink "$SPEAKER_SINK"

echo "🎧 ${SPEAKER_SINK}.monitor + 🎤 $MIC_SOURCE → [recording]; latency ≈ 60 ms. Готово."

