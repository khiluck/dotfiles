#!/bin/bash

export TERM=xterm

clear

# Read command output line by line into array ${lines [@]}
readarray -t lines < <(sort -k1 ~/secret/ip.list | grep "^[^#;]" | sed -e "s/[[:space:]]\+/ /g")

# Prompt the user to select one of the lines.
echo "Please select server:"
echo "(Ctrl+C for exit)"
echo ""
select choice in "${lines[@]}"; do
  [[ -n $choice ]] || { echo "Invalid choice. Please try again." >&2; continue; }
  break # valid choice was made; exit prompt.
done

# Split the chosen line into ID and serial number.
read -r SN IP PORT unused <<<"$choice"

clear

# If PORT variable is not empty, connect using -p option
[[ -z $PORT ]] || { echo "Connecting to IP: [$IP]; Port: [$PORT]"; $(which ssh) -lroot $IP -p $PORT; exit; }
echo "Connecting to IP: [$IP];"
$(which ssh) -X -lroot $IP
