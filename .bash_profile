#
# ~/.bash_profile
#

[[ -f ~/.bashrc ]] && . ~/.bashrc

# default editor
export EDITOR="vim"

# Add script folder to PATH variable
export PATH=$PATH:~/scripts

# default terminal
export TERMINAL="st"

# default browser
export BROWSER="chromium"

sleep 1
# start dwm
if [[ "$(tty)" = "/dev/tty1" ]]; then
	pgrep dwm || startx
fi

#if systemctl -q is-active graphical.target && [[ ! $DISPLAY && $XDG_VTNR -eq 1 ]]; then
#	exec startx
#fi

echo Wait for 3 sec and shutdown...
sleep 3 && shutdown -P now
