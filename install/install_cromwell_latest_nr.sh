#!/usr/bin/env bash
#install latest released version of cromwell and the now decoupled wdltool


if [ -z "$FDT_BIN_ROOT" ]; then
    echo "FDT_BIN_ROOT not set, please source fdtsetroot"
    exit 2
fi

sudo mkdir -p $FDT_BIN_ROOT
cd /tmp
curl -L `curl -s https://api.github.com/repos/broadinstitute/cromwell/releases | grep browser_download_url | head -1 | cut -f 4 -d '"'` > cromwell.tmp.jar
sudo mv cromwell.tmp.jar $FDT_BIN_ROOT/cromwell.jar
curl -L `curl -s https://api.github.com/repos/broadinstitute/wdltool/releases | grep browser_download_url | head -1 | cut -f 4 -d '"'` > wdltool.tmp.jar
sudo mv wdltool.tmp.jar $FDT_BIN_ROOT/wdltool.jar

unset install_root
