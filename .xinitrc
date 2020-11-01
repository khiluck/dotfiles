# turn off beep
xset -b

# set keyboard repeat rate
xset r rate 200 20

# toggle keyboard layouts
setxkbmap us,ru,ua -option "grp:win_space_toggle"

setxkbmap -model thinkpad -layout us -option caps:escape
xset m 5 1

# turn off display energy save mode
xset -dpms
xset s off

# set wallpaper
[ -f ~/Pictures/desktop ] && feh --bg-scale ~/Pictures/desktop


xrandr --output eDP --set TearFree on

exec dwm
