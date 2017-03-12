#!/usr/bin/env bash


instance_name=$1

# enables keepalive pings
gcloud compute ssh  $instance_name -- -o ServerAliveInterval=30

