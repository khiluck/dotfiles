systemctl --user import-environment DISPLAY

#xrandr --dpi 133
xrandr --auto
for out in $(xrandr | awk '/ connected/{print $1}'); do
  xrandr --output "$out" --set TearFree on
done


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
#~/scripts/extmon

# Scroll speed
#imwheel &

~/scripts/dwm_status &

# add transparency
xcompmgr &

# Notifications
dunst &


# set default brightness
#echo "70" | sudo tee /sys/class/backlight/amdgpu_bl0/brightness

# set wallpaper
feh --bg-scale $(find ~/Pictures/wallpapers/*.jpg -type f | shuf -n 1)
#~/scripts/setbg &

# check logitech mouse on startup, if connected - disable touchpad
#[ -n $(lsusb | grep -i "unifying receiver") ]] && synclient TouchpadOff=1 || synclient TouchpadOff=0


# clipmenu
clipmenud &


# settings dpi
echo "Xft.dpi: 133" | xrdb -override -


#autolock
#xss-lock -n 'setxkbmap us' -- /usr/local/bin/slock &
xss-lock -- /usr/bin/slock &

# 1280x720 = 720p X220
hash fswebcam && fswebcam -q --no-banner -r 1280x720 ~/Pictures/login-photos/$(date +%Y-%m-%dT%H).jpg &


#set de layout
setxkbmap de

exec dbus-launch dwm
