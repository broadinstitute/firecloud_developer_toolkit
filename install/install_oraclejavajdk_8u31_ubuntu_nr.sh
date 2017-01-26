#!/usr/bin/env bash

if [ -z "$FDT_BIN_ROOT" ]; then
    echo "FDT_BIN_ROOT not set, please source fdtsetroot"
    exit 2
fi


mkdir -p $FDT_BIN_ROOT
cd $FDT_BIN_ROOT/java8
curl -kLOH "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u31-b13/server-jre-8u31-linux-x64.tar.gz
tar xvf  server-jre-8u31-linux-x64.tar.gz
rm server-jre-8u31-linux-x64.tar.gz

# call using explicit path to Java
# export JAVA_HOME=$FDT_BIN_ROOT/java8/jdk1.8.0_31
# $JAVA_HOME/jre/bin/java -jar x.jar ...
