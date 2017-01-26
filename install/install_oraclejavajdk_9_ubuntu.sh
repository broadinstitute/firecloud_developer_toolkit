#!/usr/bin/env bash


echo oracle-java9-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java9-installer

# set env variables to make this version of java the default
sudo apt-get install oracle-java9-set-default
