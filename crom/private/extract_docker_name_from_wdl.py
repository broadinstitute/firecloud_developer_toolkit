#!/usr/bin/env python

#Note - this parser could be made smarter.  It requires only one line in the wdl having the string 'docker', and only docker info on that line.
# if there is an error, silently returns empty string, to avoid spamming when running make

import sys

name_format = sys.argv[1]
wdl_path = sys.argv[2]

# hostname[:port]/username/reponame[:tag]

# 		docker : "broadinstitute/pcawg_tokens:1"


fid = open(wdl_path)
docker_line = None
for line in fid:
    if 'docker' in line:
        if docker_line:
            sys.exit(1)
            #raise Exception('multiple docker lines in wdl file')
        else:
            docker_line = line

if not docker_line:
    sys.exit(1)
    #raise Exception('could not fined docker line in wdl file')

delim_pos = docker_line.index(':')
docker_image_name = docker_line[delim_pos+1:].strip().strip('"')

dn1 = docker_image_name.split('/')
dn2 = dn1[-1].split(':')
docker_image_name_base = '/'.join(dn1[:-1]) + '/' + ':'.join(dn2[:-1])
docker_image_user_tag = dn2[-1]

if name_format == 'usertag':
    output = docker_image_user_tag
elif name_format == 'base':
    output = docker_image_name_base
else:
    sys.exit(1)

    #raise Exception('name_format must be usertag or base')

print output
