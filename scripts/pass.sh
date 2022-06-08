#!/bin/bash
# generate password
newpass()
{
PASSOK=0
while [ $PASSOK -ne 1 ]; do
    TEMPASS=$(< /dev/urandom tr -dc a-hj-km-np-zA-HJ-KM-NP-Z2-9@\#$%_?^\! | head -c8)
    PASSOK=1
    # verify that there is at least one lower case letter
    [ "${TEMPASS}" = "${TEMPASS^^}" ] && { PASSOK=0; } # echo "No lower case letter"; }
    [ "${TEMPASS}" = "${TEMPASS,,}" ] && { PASSOK=0; } # echo "No upper case letter"; }
    [ "${TEMPASS//[^0-9]/}" ] || { PASSOK=0; } # echo "No number"; }
    [ "${TEMPASS//[^@\#$%_?^\!]/}" ] || { PASSOK=0; } # echo "No special symbol!"; }
done
echo $TEMPASS
}


TEMPASS=$(newpass)
echo $TEMPASS | xclip -r -l 1 
echo $TEMPASS | xclip -selection clipboard
TEMPASS=""
