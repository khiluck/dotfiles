#!/bin/bash
clear
gpg --batch --yes -d -o $HOME/secret/rdp.list $HOME/secret/rdp.list.gpg || exit 1

namearray=()
iparray=()
while IFS=' ' read -r connectionname ipaddress
do
    namearray+=("$connectionname")
    iparray+=("$ipaddress")
done < <(sort -k1 ~/secret/rdp.list | grep "^[^#;]" | sed -e "s/[[:space:]]\+/ /g")

# CLEAN file
rm -f $HOME/secret/rdp.list


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
                read -r IP USERNAME PASSWORD unused <<<"${iparray[$a]}"
        fi
done


# If PORT variable is not empty, connect using -p option
echo "Connecting to IP: [$IP];"
$(which xfreerdp) /u:$USERNAME /p:$PASSWORD /v:$IP /drive:Downloads,/home/aex/Downloads /f /smart-sizing:1600x900 /sound:sys:pulse /network:auto /fonts /cert:ignore +auto-reconnect +heartbeat +aero -z -window-drag -menu-anims -themes +fonts -decorations +compression /audio-mode:0 /mic:format:1 /sound:latency:50 -floatbar



