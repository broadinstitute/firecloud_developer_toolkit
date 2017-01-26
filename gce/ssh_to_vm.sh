#!/usr/bin/env bash


instance_name=$1

gcloud compute ssh $instance_name

#note that this connection times out after it is idle about an hour
#if you want to run something for a long time, run in the background or use screen.