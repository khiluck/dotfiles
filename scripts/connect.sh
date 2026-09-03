#!/bin/bash
export TERM=xterm
# clear только если запущены в терминале (хоткеем из dwm терминала нет)
[[ -t 1 ]] && clear


namearray=() 
iparray=()
while IFS=' ' read -r connectionname ipaddress
do
	namearray+=("$connectionname")
	iparray+=("$ipaddress")
done < <(sort -k1 ~/Work/secret/ip.list | grep "^[^#;]" | sed -e "s/[[:space:]]\+/ /g")


if [[ -f $(which dmenu 2>/dev/null) ]]; then 
	choice=$(printf "%s\n" "${namearray[@]}" | dmenu -i -l 15 -p "ssh:" | sed "s/ .*//")
else
	echo "Please select server:"
	echo "(Ctrl+c for exit)"
	echo ""
	select choice in "${namearray[@]}"; do
		[[ -n $choice ]] || { echo "Invalid choice. Please try again." >&2; continue; }
		break # valid choice was made; exit prompt.
	done
fi

# Escape в меню — просто выходим, ничего не открывая
[[ -z $choice ]] && exit 0


for ((a=0; a < ${#namearray[*]}; a++))
do
	if [[ "${namearray[$a]}" = "${choice}" ]]; then
		read -r IP PORT unused <<<"${iparray[$a]}"
	fi
done


[[ -z $IP ]] && { echo "No IP found for [$choice]" >&2; exit 1; }

# Если терминала нет (запуск хоткеем из dwm) — открываем ssh в новом окне st,
# чтобы меню не висело поверх пустого полноэкранного терминала.
if [[ ! -t 1 ]]; then
	[[ -z $PORT ]] || exec st -e ssh -lroot "$IP" -p "$PORT"
	exec st -e ssh -X -lroot "$IP"
fi

# If PORT variable is not empty, connect using -p option
[[ -z $PORT ]] || { echo "Connecting to IP: [$IP]; Port: [$PORT]"; exec ssh -lroot "$IP" -p "$PORT"; }
echo "Connecting to IP: [$IP];"
exec ssh -X -lroot "$IP"
