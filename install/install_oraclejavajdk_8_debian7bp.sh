#!/usr/bin/env bash
#install oracle java 8 jdk

#install java 8 debian 7 bp
echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | sudo tee /etc/apt/sources.list.d/webupd8team-java.list
echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | sudo tee -a /etc/apt/sources.list.d/webupd8team-java.list
#accept java license
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886
sudo apt-get update
sudo apt-get install -y oracle-java8-installer
sudo rm -rf /var/cache/oracle-jdk8-installer
java -version

echo 'export JAVA_HOME=/usr/lib/jvm/java-8-oracle' >> ~/.bashrc

