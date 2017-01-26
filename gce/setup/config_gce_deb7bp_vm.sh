#!/bin/bash


#todo add vim, emacs
#todo add compiled crcmod


sudo date


#install docker for debian 7bp
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

# add user to the docker group
sudo gpasswd -a ${USER} docker

sudo service docker start
# sudo docker run hello-world


#python 2.7 is installed with docker, but needs some additional packages
python -V
sudo apt-get install -y python-pip
sudo pip install virtualenv six


sudo apt-get install -y unzip
sudo apt-get install tree



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


#set timezone
echo "America/New_York" | sudo tee /etc/timezone; sudo dpkg-reconfigure --frontend noninteractive tzdata


#install Firecloud specific stuff

sudo pip install fissfc


#install main version of firecloud-cli
cd
git clone https://github.com/broadinstitute/firecloud-cli
cd firecloud-cli
./install.sh
echo 'export PATH=~/.firecloud-cli/ubin:$PATH' >> ~/.bashrc
cd
rm -rf firecloud-cli
sh -c 'firecloud -h'


#install latest released version of cromwell and the now decoupled wdltool
sudo mkdir /cromwell
curl -L `curl -s https://api.github.com/repos/broadinstitute/cromwell/releases | grep browser_download_url | head -1 | cut -f 4 -d '"'` > cromwell.tmp.jar
sudo mv cromwell.tmp.jar /cromwell/cromwell.jar
curl -L `curl -s https://api.github.com/repos/broadinstitute/wdltool/releases | grep browser_download_url | head -1 | cut -f 4 -d '"'` > wdltool.tmp.jar
sudo mv wdltool.tmp.jar /cromwell/wdltool.jar

java -jar /cromwell/cromwell.jar
java -jar /cromwell/wdltool.jar

#attach to your google account
#gcloud init

#attach to docker account
#docker login


