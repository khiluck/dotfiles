#!/bin/bash
TEMPASS=$(< /dev/urandom tr -dc a-hj-km-np-zA-HJ-KM-NP-Z2-9@\#$%_?^\! | head -c12)
echo $TEMPASS | xclip -r -l 1 
echo $TEMPASS | xclip -selection clipboard
TEMPASS=""
