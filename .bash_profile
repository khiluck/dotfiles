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
export BROWSER="firefox"


# start dwm
if [[ "$(tty)" = "/dev/tty1" ]]; then
	pgrep dwm || startx
fi

#if systemctl -q is-active graphical.target && [[ ! $DISPLAY && $XDG_VTNR -eq 1 ]]; then
#	exec startx
#fi
