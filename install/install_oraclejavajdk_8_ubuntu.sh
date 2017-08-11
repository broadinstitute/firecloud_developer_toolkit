#!/usr/bin/env bash

#install java 8 on ubuntu

echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer

# set this version of Java as the default
sudo apt-get install oracle-java8-set-default
