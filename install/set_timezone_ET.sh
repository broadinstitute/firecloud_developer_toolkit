#!/usr/bin/env bash
#set timezone
echo "America/New_York" | sudo tee /etc/timezone; sudo dpkg-reconfigure --frontend noninteractive tzdata
