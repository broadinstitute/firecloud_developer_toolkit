#!/usr/bin/env bash

#stops vm if running, then deletes it.
#attached disks will be destroyed too, assuming they are marked for autodeletion or are SSD

instance_name=$1

gcloud compute instances delete $instance_name
