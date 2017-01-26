#!/usr/bin/env bash


#creates bare vm with unitialized disk to go with it.
#example usage:
#create_and_start_vm.sh myinstance1 n1-standard-2 20

#todo change the boot disk to append -base

instance_name=$1 #lower case or dashes
mtype=$2  # eg n1-standard-2 (2 cores with 3.75GB/core)  or n1-highmem-8 (8 core with 7.5GB/core).  see https://cloud.google.com/compute/pricing for more options
disk_size=$3 # holds the docker images, docker disks, and whatever you put on /opt.  In GB.  eg 20

disk_name=${instance_name}-aux

gcloud compute disks create $disk_name --size $disk_size --type pd-standard --image firecloud-deb7bp-2016-09-07-aux --image-project broad-gsaksena

gcloud compute instances create $instance_name  --zone us-central1-f --machine-type $mtype --image firecloud-deb7bp-2016-09-07 --image-project broad-gsaksena --disk name=$disk_name,mode=rw  --local-ssd interface=scsi

gcloud compute instances set-disk-auto-delete $instance_name --auto-delete --disk $disk_name

echo
echo You need to run the following command on the vm if you asked for something different than the default 20GB on /opt
echo     sudo resize2fs /dev/disk/by-id/google-persistent-disk-1
echo
echo You need to run the following command on the vm if you want to access Firecloud
echo      gcloud init
echo
