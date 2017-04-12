#!/usr/bin/env bash

#stop vm, can be restarted later
#charges stop accruing for CPU time, but still accrue for the disk space
# omit the instance name to shut down the node you are currently on.

instance_name="$1"

if [ -z "$instance_name" ]; then 
    sudo shutdown -h now
else
    gcloud compute instances stop $instance_name
fi
