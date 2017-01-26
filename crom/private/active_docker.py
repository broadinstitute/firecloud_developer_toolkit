#!/usr/bin/env python

'''
ad = active docker
Note that this needs to be set to have executable permissions to work.

'''

import os
import subprocess

def execute_str(cmd_str):

    p = subprocess.Popen(cmd_str,shell=True,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    (stdout,stderr) = p.communicate()
    return_code = p.returncode
    err = return_code!=0
    stdout_str = str(stdout)
    stderr_str = str(stderr)

    return (err,stdout_str,stderr_str)

cmd_str = 'docker ps'
(err,stdout_str,stderr_str) = execute_str(cmd_str)

outlines = stdout_str.split('\n')
if len(outlines)<3:
        raise Exception('no docker containers running')
if len(outlines)>3:
    raise Exception('multiple docker containers running')

last_line = outlines[1].split()
print (last_line[-1])

