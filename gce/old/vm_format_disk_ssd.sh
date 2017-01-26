#!/usr/bin/env bash

#formats first attached disk, attaches it as /opt, and makes a docker storage directory there with a symlink pointing to it from /var/lib.
#if there are multiple attached disks, make sure the right one is formatted!

node_disk_name=google-local-ssd-0
mount_name=opt

ls /dev/disk/by-id
# format and mount the persistant disk
sudo mkfs.ext4 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/$node_disk_name
sudo mkdir -p /$mount_name
sudo mount -o discard,defaults /dev/disk/by-id/$node_disk_name /$mount_name
echo "/dev/disk/by-id/$node_disk_name /$mount_name ext4 discard,defaults 1 1" | sudo tee -a /etc/fstab
sudo chmod a+w /$mount_name


#put bulky docker images on the external disk
sudo mkdir -p /opt/docker
sudo ln -s  /opt/docker /var/lib/docker

df -h

#lastline
