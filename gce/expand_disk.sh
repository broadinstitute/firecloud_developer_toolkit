#!/usr/bin/env bash

# change the amount of disk space available under /opt
# VM does not need to be shut down to run this


instance_name=$1
new_disk_size=$2  #in GB, eg 30

disk_name=${instance_name}-aux

gcloud compute disks resize $disk_name --size $new_disk_size

gcloud compute ssh $instance_name --command 'sudo resize2fs /dev/disk/by-id/google-persistent-disk-1'


