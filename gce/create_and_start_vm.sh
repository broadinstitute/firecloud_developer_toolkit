#!/usr/bin/env bash


#creates bare vm with unitialized disk to go with it.
#example usage:
#create_and_start_vm.sh myinstance1 n1-standard-2 20


instance_name=$1 #lower case or dashes
mtype=$2  # eg n1-standard-2 (2 cores with 3.75GB/core)  or n1-highmem-8 (8 core with 7.5GB/core).  see https://cloud.google.com/compute/pricing for more options
disk_size=$3 # holds the docker images, docker disks, and whatever you put on /opt.  In GB.  eg 20

#TODO check that instance name is legal before proceeding
#TODO fix things so that errors don't cause junk resources to be left behind
#TODO print the project that the vm is being created in, as a reminder


# set these to disk images
base_image=pcawg-test-image
image_project=broad-cga-gsaksena-rebc
# default project can be looked up via 'gcloud compute project-info describe'
aux_image=${base_image}-aux

disk_name=${instance_name}-aux

gcloud compute disks create $disk_name --size $disk_size --type pd-standard --image $aux_image --image-project $image_project

gcloud compute instances create $instance_name --machine-type $mtype --image $base_image --image-project $image_project --disk name=$disk_name,mode=rw

gcloud compute instances set-disk-auto-delete $instance_name --auto-delete --disk $disk_name

echo
echo "expanding aux disk to requested size"
gcloud compute ssh $instance_name --command "sudo resize2fs /dev/disk/by-id/google-persistent-disk-1"
