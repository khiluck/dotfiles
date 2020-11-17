xrandr --auto

# turn off beep
xset -b

# set keyboard repeat rate
xset r rate 200 20

# toggle keyboard layouts
setxkbmap -model thinkpad -layout us,ru -option "grp:win_space_toggle"
#setxkbmap -model thinkpad -layout us,ru,ua -option "grp:win_space_toggle"
#setxkbmap -model thinkpad -layout us -option caps:escape
xset m 5 1

# turn off display energy save mode
#xset -dpms
xset s off

xrandr --output eDP --set TearFree on

~/scripts/dwm_status &

# add transparency
xcompmgr &

# set default brightness
echo "70" | sudo tee /sys/class/backlight/amdgpu_bl0/brightness

# set wallpaper
[ -f ~/Pictures/desktop.jpg ] && feh --bg-scale ~/Pictures/desktop.jpg

# check logitech mouse on startup, if connected - disable touchpad
#[ -n $(lsusb | grep -i "unifying receiver") ]] && synclient TouchpadOff=1 || synclient TouchpadOff=0


#autolock
xss-lock -- /usr/local/bin/slock &


exec dwm
