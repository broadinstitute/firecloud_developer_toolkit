#!/usr/bin/env bash

instance_name=$1
cp args

gcloud compute copy-files [LOCAL_FILE_PATH] [INSTANCE_NAME]:~/