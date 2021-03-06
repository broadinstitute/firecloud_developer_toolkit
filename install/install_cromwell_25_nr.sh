#!/usr/bin/env bash
#install latest released version of cromwell and the now decoupled wdltool


if [ -z "$FDT_BIN_ROOT" ]; then
    echo "FDT_BIN_ROOT not set, please source fdtsetroot"
    exit 2
fi

mkdir -p $FDT_BIN_ROOT
cd /tmp
curl -L https://github.com/broadinstitute/cromwell/releases/download/25/cromwell-25.jar > cromwell.tmp.jar
mv cromwell.tmp.jar $FDT_BIN_ROOT/cromwell.jar
curl -L https://github.com/broadinstitute/wdltool/releases/download/0.8/wdltool-0.8.jar > wdltool.tmp.jar
mv wdltool.tmp.jar $FDT_BIN_ROOT/wdltool.jar

