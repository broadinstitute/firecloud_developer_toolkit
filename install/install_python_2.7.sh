#!/usr/bin/env bash

sudo apt-get update && sudo apt-get install -y python python-dev python-pip
sudo pip install --upgrade pip
sudo pip install virtualenv six
sudo pip install 'requests[security]'
sudo pip install -U crcmod
