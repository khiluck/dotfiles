# if not running interactively, do not do anything
[[ $- == *i* ]] || return

# Set PATH
if test -d "$HOME/scripts"
then
	PATH="$HOME/scripts:$PATH"
fi


# set aliases
alias sudo='sudo '
alias vi='vim'

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
pass()
{
	# generate password if no parameter was passed
	[ $# -eq 0 ] && { echo $(< /dev/urandom tr -dc a-zA-Z0-9 | head -c12); return 0; } | xclip -r -l 1
}


# rdp connection
rdp()
{
	# first parameter - server, second - username@domain, third - password
	xfreerdp /u:$2 /p:$3 /v:$1 /f /sound:sys:pulse /network:auto /fonts /cert-tofu +auto-reconnect +heartbeat +aero -z

}


# fix remote ssh connections
alias ssh='TERM=xterm ssh -lroot'

