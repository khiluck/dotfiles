#!/bin/bash
TEMPASS=$(< /dev/urandom tr -dc a-zA-Z0-9 | head -c12)
echo $TEMPASS | xclip -r -l 1 
echo $TEMPASS | xclip -selection clipboard
TEMPASS=""
