#!/bin/bash
clear
#gpg --batch --yes -d -o $HOME/secret/rdp.list $HOME/secret/rdp.list.gpg || exit 1

namearray=()
iparray=()
while IFS=' ' read -r connectionname ipaddress
do
    namearray+=("$connectionname")
    iparray+=("$ipaddress")
done < <(sort -k1 ~/Work/secret/rdp.list | grep "^[^#;]" | sed -e "s/[[:space:]]\+/ /g")

# CLEAN file
#rm -f $HOME/secret/rdp.list


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
$(which xfreerdp3) /u:$USERNAME /v:$IP /p:$PASSWORD /drive:Downloads,/home/aex/Downloads /f /smart-sizing:1920x1080 /cert:ignore -smartcard +auto-reconnect +aero -themes +fonts -decorations /bpp:16 /gfx:avc444 /sound:sys:pulse,format:1,quality:high /mic:format:1,quality:high -window-drag -menu-anims +multitransport /network:auto /video -floatbar > /dev/null


