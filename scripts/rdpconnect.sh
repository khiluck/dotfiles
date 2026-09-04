#!/bin/bash
# Терминал ли это: [[ -t 1 ]] тут не годится, dwm наследует stdout от startx
# (/dev/tty1), а эмулятор терминала даёт pty (/dev/pts/N).
case "$(tty 2>/dev/null)" in
	/dev/pts/*) clear ;;
esac
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
    choice=$(printf "%s\n" "${namearray[@]}" | dmenu -i -l 15 -p "rdp:" | sed "s/ .*//")
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
                read -r IP USERNAME PASSWORD unused <<<"${iparray[$a]}"
        fi
done


[[ -z $IP ]] && { echo "No IP found for [$choice]" >&2; exit 1; }

echo "Connecting to IP: [$IP];"
#$(which xfreerdp) /u:$USERNAME /p:$PASSWORD /v:$IP /drive:Downloads,/home/aex/Downloads /f /smart-sizing:1600x850 /sound:sys:pulse /network:auto /fonts /cert:ignore +auto-reconnect +heartbeat +aero -z -window-drag -menu-anims -themes +fonts -decorations +compression /audio-mode:0 /mic:format:1 /sound:latency:50 -floatbar
#$(which xfreerdp) /u:$USERNAME /p:$PASSWORD /v:$IP /drive:Downloads,/home/aex/Downloads /f /sound:sys:pulse /network:auto /fonts /cert:ignore +auto-reconnect +heartbeat +aero -z -window-drag -menu-anims -themes +fonts -decorations +compression /audio-mode:0 /mic:format:1 /sound:latency:50 -floatbar
$(which xfreerdp3) /u:$USERNAME /v:$IP /p:$PASSWORD /drive:Downloads,/home/aex/Downloads /smart-sizing /w:1914 /h:1043 /scale-desktop:120 /cert:ignore +auto-reconnect +heartbeat +multitransport /gfx:AVC444,AVC420 -themes -wallpaper -window-drag -menu-anims +fonts -decorations +compression /sound:sys:pulse,quality:dynamic /mic:format:1 > /dev/null


