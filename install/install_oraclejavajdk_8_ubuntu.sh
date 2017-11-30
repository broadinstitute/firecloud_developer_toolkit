#!/usr/bin/env bash

#install java 8 on ubuntu

# install package containing add-apt-repository
sudo apt-get install -y software-properties-common


echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install -y oracle-java8-installer

# set this version of Java as the default
sudo apt-get install -y oracle-java8-set-default
