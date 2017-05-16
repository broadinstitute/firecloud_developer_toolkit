#!/bin/bash

sudo apt-get install ruby
sudo gem install rmate

# establish tunnel - run on local machine
#ssh -f -N -i $HOME/.ssh/google_compute_engine -R 52698:127.0.0.1:52698 <gce_node_username@gce_node_ipaddress> 
# start server app on local machine via vscode, textmate, etc
# 
# on remote node, 
# alias open="rmate -p 52698"
