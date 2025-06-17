#!/bin/bash

# Устройства (замените при необходимости)
MIC_SOURCE="alsa_input.usb-Creative_Technology_Ltd_Sound_Blaster_Play__3_00204429-00.analog-stereo"
SPEAKER_SINK="alsa_output.usb-Creative_Technology_Ltd_Sound_Blaster_Play__3_00204429-00.analog-stereo"

# Удаляем любые loopback-модули, где микрофон направлен в динамики
pactl list modules short | grep "module-loopback" | grep "$MIC_SOURCE" | grep "$SPEAKER_SINK" | cut -f1 | while read -r id; do
  pactl unload-module "$id" && echo "❌ Удалён loopback микрофона в динамики (эхо)"
done

# Загружаем null sink (виртуальный выход для записи)
pactl load-module module-null-sink sink_name=recording sink_properties=device.description=recording

# Объединяем null-sink и реальные динамики в combined sink
pactl load-module module-combine-sink sink_name=combined sink_properties=device.description=combined slaves=recording,$SPEAKER_SINK

# Микрофон → recording (для записи)
pactl load-module module-loopback source=$MIC_SOURCE sink=recording latency_msec=1

# Микрофон → динамики (для прослушивания). Чтоб слышать самого себя
#pactl load-module module-loopback source=$MIC_SOURCE sink=$SPEAKER_SINK latency_msec=1

# Устанавливаем combined как устройство вывода по умолчанию
pactl set-default-sink combined

echo "🎤 Скрипт выполнен. Микрофон пишется и слышен. Используется PipeWire (через pactl)."
