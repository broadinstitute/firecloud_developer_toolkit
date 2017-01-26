#!/usr/bin/env bash

# assumes python2.7 and git are already installed

#install main version of firecloud-cli
cd /tmp
git clone https://github.com/broadinstitute/firecloud-cli
cd firecloud-cli
./install.sh
echo 'export PATH=~/.firecloud-cli/ubin:$PATH' >> ~/.bashrc
cd /tmp
rm -rf firecloud-cli
#sh -c 'firecloud -h'
