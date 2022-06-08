#!/bin/sh
# Get user selection via dmenu from emoji file.
chosen=$(ls $HOME/Games/sega/ | dmenu -i -l 30)

# Exit if none chosen.
[ -z "$chosen" ] && exit

$(which retroarch) --libretro /usr/lib/libretro/genesis_plus_gx_libretro.so $HOME/Games/sega/"$chosen"
