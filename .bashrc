# if not running interactively, do not do anything
[[ $- == *i* ]] || return

# Set PATH
if test -d "$HOME/scripts"
then
	PATH="$HOME/scripts:$PATH"
fi

# Python PATH
PATH="$PATH:/home/aex/.local/bin"

# set aliases

# alias mount office share
#alias share='sudo mount -t cifs -o username=guest,password=guest,uid=1000 //192.168.0.100/share /mnt/share/'

alias sudo='sudo '
alias vi='vim'
# fix remote ssh connections
alias ssh='TERM=xterm ssh'

alias c='~/secret/connect.sh'
alias r='~/secret/rdpconnect.sh'

# add color output
alias ls='ls --color=auto -l --time-style long-iso'
alias ll='ls --color=auto -la --time-style long-iso'
alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias ip='ip -c'
alias pacman='pacman --color auto'
alias pactree='pactree --color'
alias yay='sudo -u aurbuilder yay'
alias vdir='vdir --color=auto'
alias watch='watch --color'
man() {
	env \
		LESS_TERMCAP_mb=$(printf "\e[1;31m") \
		LESS_TERMCAP_md=$(printf "\e[1;31m") \
		LESS_TERMCAP_me=$(printf "\e[0m") \
		LESS_TERMCAP_se=$(printf "\e[0m") \
		LESS_TERMCAP_so=$(printf "\e[1;44;33m") \
		LESS_TERMCAP_ue=$(printf "\e[0m") \
		LESS_TERMCAP_us=$(printf "\e[1;32m") \
			man "$@"
}
export LS_COLORS="di=0;34:fi=0;94:ln=1;94:or=1;31:ex=0;33:*.jpg=0;32:*.jpeg=0;32:*.gif=0;32:*.bmp=0;32:*.png=0;32:*.svg=0;32:*.mpg=0;32:*.mpeg=0;32:*.mkv=0;32:*.webm=0;32:*.mp4=0;32:*.wmv=0;32:*.flc=0;32:*.avi=0;32:"


# automatic ls on cd
#cd()
#{
#	builtin cd "$@" && ll
#}


# define prompt
clrreset='\e[0m'
clrwhite='\e[1;37m'
clrgreen='\e[1;32m'
clrred='\e[1;31m'
clrcyan='\e[1;36m'
clrpurple='\e[1;35m'
PS1="\[$clrcyan\]\u\[$clrwhite\]@\[$clrpurple\]\w\`if [ \$? = 0 ]; then echo -e '\[$clrgreen\]'; else echo -e '\[$clrred\]'; fi\`\\$ \[$clrreset\]"


# generate password
newpass()
{
PASSOK=0
while [ $PASSOK -ne 1 ]; do
    TEMPASS=$(< /dev/urandom tr -dc a-hj-km-np-zA-HJ-KM-NP-Z2-9@\#$%_?^\! | head -c8)
    PASSOK=1
    # verify that there is at least one lower case letter
    [ "${TEMPASS}" = "${TEMPASS^^}" ] && { PASSOK=0; } # echo "No lower case letter"; }
    [ "${TEMPASS}" = "${TEMPASS,,}" ] && { PASSOK=0; } # echo "No upper case letter"; }
    [ "${TEMPASS//[^0-9]/}" ] || { PASSOK=0; } # echo "No number"; }
    [ "${TEMPASS//[^@\#$%_?^\!]/}" ] || { PASSOK=0; } # echo "No special symbol!"; }
done
echo $TEMPASS
}

pass()
{
	# generate password if no parameter was passed
	[ $# -eq 0 ] &&	{ TEMPASS=$(newpass); echo $TEMPASS; echo $TEMPASS | xclip -r -l 1; echo $TEMPASS | xclip -selection clipboard; } || 
{ TEMPASS=""; for i in $(eval echo {1..$1}); do echo $(newpass); done; }
}

# rdp connection
rdp()
{
	# to get out of connection use Ctrl+Alt+Enter
	# first parameter - server, second - username@domain, third - password
	#xfreerdp /u:$2 /p:$3 /v:$1 /drive:Downloads,/home/aex/Downloads /f /smart-sizing:1600x850 /sound:sys:pulse /network:auto /fonts /cert:ignore +auto-reconnect +heartbeat +aero -z -window-drag -menu-anims -themes +fonts -decorations +compression /audio-mode:0 /mic:format:1 /sound:latency:50 -floatbar
	xfreerdp /u:$2 /p:$3 /v:$1 /drive:Downloads,/home/aex/Downloads /f /sound:sys:pulse /network:auto /fonts /cert:ignore +auto-reconnect +heartbeat +aero -z -window-drag -menu-anims -themes +fonts -decorations +compression /audio-mode:0 /mic:format:1 /sound:latency:50 -floatbar

}

# youtube music download
dl(){
	 youtube-dl -f bestaudio $1

}

# copy using rsync
rcp(){
	rsync --info=progress2 $1 $2
}

# search using find 
f(){
	find / -name "$1" 2>/dev/null
}

# update all
update(){
	sudo pacman -Syu
	yay -Syu
}


# radio
radio(){
#	mplayer -prefer-ipv4 http://us4.internet-radio.com:8258/stream
	mplayer -prefer-ipv4 http://airspectrum.cdnstream1.com:8018/1606_192
}

eval "$(mcfly init bash)"

knock(){
	nmap -Pn --host-timeout 100 --max-retries 0 -p $1 $2
}
