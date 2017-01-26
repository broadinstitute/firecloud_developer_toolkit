#!/usr/bin/env bash

instance_name=instance1assd
mtype=n1-highmem-2
disk_size=20
disk_name=${instance_name}-disk

# gcloud compute instances create $instance_name  --zone us-central1-f --machine-type $mtype --local-ssd interface=scsi  --image backports-debian-7-wheezy-v20160531 --image-project debian-cloud 


gcloud compute instances create $instance_name  --zone us-central1-f --machine-type $mtype --local-ssd interface=nvme   --image nvme-backports-debian-7-wheezy-v20151104 --image-project gce-nvme
