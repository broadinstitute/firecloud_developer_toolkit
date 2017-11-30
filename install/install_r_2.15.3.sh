#!/bin/bash

#install R-2.15.3 by compiling from source

sudo apt-get update && apt-get install -y tk-dev gcc gfortran texlive-latex-base libreadline-dev xorg-dev libxml2-dev libcurl4-gnutls-dev 

sudo apt-get install -y sqlite3 wget

sudo cd /usr/local \
&& mkdir R \
&& cd R \
&& wget  https://cran.r-project.org/src/base/R-2/R-2.15.3.tar.gz  \
&& tar zxvf R-2.15.3.tar.gz \
&& cd R-2.15.3/ \
&& ./configure \
&& make \
&& make check \
&& make install

