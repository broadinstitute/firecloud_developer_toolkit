#!/bin/bash
# Installs Stackdriver monitoring and logging drivers to node.
# The parent project also needs to be set up for things to work.
# access via something like: https://app.google.stackdriver.com/?project=broad-cga-gsaksena-rebc 

cd /tmp

curl -O "https://repo.stackdriver.com/stack-install.sh"
sudo bash stack-install.sh --write-gcm

curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sudo bash install-logging-agent.sh
