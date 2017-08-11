#!/bin/bash

sudo apt-get update && sudo apt-get install -y openconnect

# to connect, run somethnig like:
# sudo openconnect  --authgroup=Duo-Split-Tunnel-VPN vpn.broadinstitute.org
