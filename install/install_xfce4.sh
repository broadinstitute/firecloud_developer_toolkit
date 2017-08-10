#!/bin/bash

sudo apt-get update
sudo apt-get install xrdp
sudo apt-get install xfce4
sudo apt-get install xfce4-terminal

echo xfce4-session >~/.xsession

# sudo nano /etc/xrdp/startwm.sh   <edit last line to say "startxfce4">

sudo service xrdp restart

# set a known password, eg via
# sudo passwd -d <myusername>
# passwd

#update keyboard layout??
#  apt-get install console-data
#
#  see /etc/xrdp
#  note xrdp-genkeymap is in /usr/local/bin
#  setxkbmap -model pc104 -layout us -variant dvorak
#  xrdp-genkeymap km-0409.ini

