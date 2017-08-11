#!/usr/bin/env bash

if [ -z "$FDT_BIN_ROOT" ]; then
    echo "FDT_BIN_ROOT not set, please source fdtsetroot"
    exit 2
fi

cd $FDT_BIN_ROOT
# don't know how to get latest version right off the bat, so just grab some hopefully recent version
# based on this page: https://cloud.google.com/sdk/downloads
wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-166.0.0-linux-x86_64.tar.gz
if [ -d google-cloud-sdk ]; then
    rm -r google-cloud-sdk
fi
tar xf google-cloud-sdk-166.0.0-linux-x86_64.tar.gz
rm google-cloud-sdk-166.0.0-linux-x86_64.tar.gz
# export CLOUDSDK_PYTHON=<non-system version of Python2.7, if needed>
# update environment variables
./google-cloud-sdk/install.sh -q --additional-components alpha beta
# bump to latest version
./google-cloud-sdk/bin/gcloud components update -q
