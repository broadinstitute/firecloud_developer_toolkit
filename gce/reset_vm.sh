#!/usr/bin/env bash

#reboots vm

instance_name=$1

gcloud compute instances reset $instance_name
