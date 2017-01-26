#!/usr/bin/env bash

#start vm that had previously been created then stopped

instance_name=$1

gcloud compute instances start $instance_name
