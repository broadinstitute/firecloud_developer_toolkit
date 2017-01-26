#!/usr/bin/env bash



#//Install Oracle Java 7

  echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections && \
  sudo add-apt-repository -y ppa:webupd8team/java && \
  sudo apt-get update && \
  sudo apt-get install -y oracle-java7-installer && \
  sudo rm -rf /var/cache/oracle-jdk7-installer


#//  rm -rf /var/lib/apt/lists/* && \

#// Define commonly used JAVA_HOME variable
# export JAVA_HOME /usr/lib/jvm/java-7-oracle

sudo apt-get install oracle-java7-set-default

