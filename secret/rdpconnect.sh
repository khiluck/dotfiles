#!/bin/bash

clear

# Read command output line by line into array ${lines [@]}
readarray -t lines < <(sort -k1 ~/secret/rdp.list | grep "^[^#;]" | sed -e "s/[[:space:]]\+/ /g")

# Prompt the user to select one of the lines.
echo "Please select server:"
echo "(Ctrl+C for exit)"
echo ""
select choice in "${lines[@]}"; do
  [[ -n $choice ]] || { echo "Invalid choice. Please try again." >&2; continue; }
  break # valid choice was made; exit prompt.
done

# Split the chosen line into ID and serial number.
read -r SN IP USERNAME PASSWORD unused <<<"$choice"

clear

# If PORT variable is not empty, connect using -p option
echo "Connecting to IP: [$IP];"
#$(which xfreerdp) /u:$USERNAME /p:$PASSWORD /v:$IP /f /scale:140 /scale-desktop:140 /sound:sys:pulse /network:auto /fonts /cert:ignore +auto-reconnect +heartbeat +aero -z 
#$(which xfreerdp) /u:$USERNAME /p:$PASSWORD /v:$IP /f /smart-sizing:1366x768 /sound:sys:pulse /network:auto /fonts /cert:ignore +auto-reconnect +heartbeat +aero -z 
$(which xfreerdp) /u:$USERNAME /p:$PASSWORD /v:$IP /drive:Downloads,/home/aex/Downloads /f /smart-sizing:1424x771 /sound:sys:pulse /network:auto /fonts /cert:ignore +auto-reconnect +heartbeat +aero -z 
