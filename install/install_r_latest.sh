#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y --force-yes r-base r-base-dev

sudo Rscript -e "install.packages('optparse', repos='http://cran.us.r-project.org')"
sudo Rscript -e "install.packages('data.table', repos='http://cran.us.r-project.org')"
# may depend on samtools being installed
sudo Rscript -e "source('http://bioconductor.org/biocLite.R'); biocLite(c('GenomicRanges','DNAcopy','Rsamtools'))"
