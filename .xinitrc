xrandr --auto

# turn off beep
xset -b

# set keyboard repeat rate
xset r rate 200 20

# toggle keyboard layouts
#setxkbmap -model thinkpad -layout us,ru -option "grp:win_space_toggle"
xset m 5 1

# turn off display energy save mode
#xset -dpms
xset s off

#xrandr --output eDP --set TearFree on
~/scripts/extmon



~/scripts/dwm_status &

# add transparency
xcompmgr &

# set default brightness
echo "70" | sudo tee /sys/class/backlight/amdgpu_bl0/brightness

# set wallpaper
feh --bg-scale $(find ~/Pictures/*.jpg -type f | shuf -n 1)

# check logitech mouse on startup, if connected - disable touchpad
#[ -n $(lsusb | grep -i "unifying receiver") ]] && synclient TouchpadOff=1 || synclient TouchpadOff=0


#autolock
xss-lock -- /usr/local/bin/slock &


exec dwm
