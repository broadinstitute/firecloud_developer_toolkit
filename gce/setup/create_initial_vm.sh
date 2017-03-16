#!/usr/bin/env bash

instance_name="$1" #lower case or dashes
mtype="$2"  # eg n1-standard-2 (2 cores with 3.75GB/core)  or n1-highmem-8 (8 core with 6.5GB/core).  see https://cloud.google.com/compute/pricing for more options
disk_size="$3" # holds the docker images, docker disks, and whatever you put on /opt.  In GB.  eg 20


#create and start a new VM based on a system image
# a second disk is created with the given disk_size, and mounted as /opt
# warning - if your ssh key is not set up first, this will leave a partially set up vm behind

disk_name=${instance_name}-aux


gcloud compute disks create $disk_name --size $disk_size --type pd-standard
gcloud compute instances create $instance_name --machine-type $mtype --image backports-debian-7-wheezy-v20160531 --image-project debian-cloud --disk name=$disk_name,mode=rw
gcloud compute instances set-disk-auto-delete $instance_name --auto-delete --disk $disk_name #uncomment for secondary disk to outlive vm deletion

#format the second disk and mount it to /opt
echo
echo "formating and mounting aux disk"
gcloud compute ssh $instance_name --command 'node_disk_name=google-persistent-disk-1;mount_name=opt;ls /dev/disk/by-id;sudo mkfs.ext4 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/$node_disk_name;sudo mkdir -p /$mount_name;sudo mount -o discard,defaults /dev/disk/by-id/$node_disk_name /$mount_name;echo "/dev/disk/by-id/$node_disk_name /$mount_name ext4 discard,defaults 1 1" | sudo tee -a /etc/fstab;sudo chmod a+w /$mount_name'

#move home of (future) docker images to /opt/docker_private
echo
echo "placing symlink to move docker storage to aux disk"
gcloud compute ssh $instance_name --command 'sudo mkdir -p /opt/docker_private;sudo ln -s  /opt/docker_private /var/lib/docker'
