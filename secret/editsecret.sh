#!/bin/bash

# DECRYPT FILE
gpg --batch --yes -d -o $HOME/secret/rdp.list $HOME/secret/rdp.list.gpg

$(which vim) $HOME/secret/rdp.list

# ENCRYPT FILE
gpg --batch --yes -e -r $USER$USER $HOME/secret/rdp.list && rm -f $HOME/secret/rdp.list
