#!/bin/bash
pacmd load-module module-null-sink sink_name=recording sink_properties=device.description=recording
pacmd load-module module-combine-sink sink_name=combined sink_properties=device.description=combined slaves=recording,alsa_output.usb-Creative_Technology_Ltd_Sound_Blaster_Play__3_00204429-00.analog-stereo
pacmd load-module module-loopback source=alsa_input.usb-Creative_Technology_Ltd_Sound_Blaster_Play__3_00204429-00.analog-stereo sink=recording latency_msec=1
# Check in pavucontrol, on Playback tab and change sink to combined. Hint: the application won't appear there unless it is producing sound
pacmd set-default-sink combined
