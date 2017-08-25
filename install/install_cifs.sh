#!/bin/bash 

sudo apt-get install cifs-utils

# interactive mount
# sudo mkdir -p /xchip/cga_home/gsaksena
# sudo mount -t cifs -o username=gsaksena,uid=`id -u $USER`,gid=`id -g $USER` //thunder/xchip_cga_home/gsaksena /xchip/cga_home/gsaksena
# interactive unmount
# sudo umount /xchip/cga_home/gsaksena
#
# automated mount
# edit fstab... see https://askubuntu.com/questions/334422/mounted-cifs-share-but-no-write-permissions
