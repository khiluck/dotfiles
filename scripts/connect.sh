#!/bin/bash
export TERM=xterm
clear


namearray=() 
iparray=()
while IFS=' ' read -r connectionname ipaddress
do
	namearray+=("$connectionname")
	iparray+=("$ipaddress")
done < <(sort -k1 ~/secret/ip.list | grep "^[^#;]" | sed -e "s/[[:space:]]\+/ /g")


if [[ -f $(which dmenu 2>/dev/null) ]]; then 
	choice=$(printf "%s\n" "${namearray[@]}" | dmenu -i -l 30 | sed "s/ .*//")
else
	echo "Please select server:"
	echo "(Ctrl+c for exit)"
	echo ""
	select choice in "${namearray[@]}"; do
		[[ -n $choice ]] || { echo "Invalid choice. Please try again." >&2; continue; }
		break # valid choice was made; exit prompt.
	done
fi


for ((a=0; a < ${#namearray[*]}; a++))
do
	if [[ "${namearray[$a]}" = "${choice}" ]]; then
		read -r IP PORT unused <<<"${iparray[$a]}"
	fi
done


# If PORT variable is not empty, connect using -p option
[[ -z $PORT ]] || { echo "Connecting to IP: [$IP]; Port: [$PORT]"; $(which ssh) -lroot $IP -p $PORT; exit; }
echo "Connecting to IP: [$IP];"
$(which ssh) -X -lroot $IP
