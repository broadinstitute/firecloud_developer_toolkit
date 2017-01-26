#!/usr/bin/env bash
#set timezone

echo "America/Los_Angeles" | sudo tee /etc/timezone; dpkg-reconfigure --frontend noninteractive tzdata
