#!/bin/bash

sudo apt-get update
sudo apt-get install libxss1 libappindicator1 libindicator7
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb
sudo apt-get install -f
