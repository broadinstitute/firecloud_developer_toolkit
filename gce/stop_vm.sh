#!/usr/bin/env bash

#stop vm, can be restarted later
#charges stop accruing for CPU time, but still accrue for the disk space

instance_name=$1

gcloud compute instances stop $instance_name
