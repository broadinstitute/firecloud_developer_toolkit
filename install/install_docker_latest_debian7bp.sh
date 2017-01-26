#!/usr/bin/env bash

#install docker for debian 7bp
#note - you probably don't want the docker images living on the boot disk, for better robustness against accidental
# disk filling.  Accomplish this via something like the following before installing docker:
# sudo mkdir -p /opt/docker;sudo ln -s  /opt/docker /var/lib/docker
# this may have been done already when the VM was created.

echo "deb http://http.debian.net/debian wheezy-backports main" | sudo tee /etc/apt/sources.list.d/backports.list
sudo apt-get update
sudo apt-get purge "lxc-docker*"
sudo apt-get purge "docker.io*"
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D


echo  "deb https://apt.dockerproject.org/repo debian-wheezy main" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys F76221572C52609D

sudo apt-get update
sudo apt-cache policy docker-engine
sudo apt-get update
sudo apt-get install -y docker-engine

# add user to the docker group (takes effect after next login)
sudo gpasswd -a ${USER} docker
echo "docker group becomes effective after next login"

sudo service docker start
# sudo docker run hello-world #test code
