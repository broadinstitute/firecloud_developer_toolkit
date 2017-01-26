#!/usr/bin/env python


import sys
import subprocess
def execute_str(cmd_str):

    p = subprocess.Popen(cmd_str,shell=True,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    (stdout,stderr) = p.communicate()
    return_code = p.returncode
    err = return_code!=0
    stdout_str = str(stdout)
    stderr_str = str(stderr)

    return (err,stdout_str,stderr_str)


vm_name = sys.argv[1]
from_files = sys.argv[2:-1]
to_location = sys.argv[-1]



cmd_str = 'gcloud compute instances describe %s'%vm_name
(err,stdout_str,stderr_str) = execute_str(cmd_str)
if err:
    raise Exception(stderr_str)

stdout_list = stdout_str.split('\n')

for line in stdout_list:
    line_list = line.split()
    if len(line_list)<2:
        continue

    if 'natIP:' == line_list[0]:
        natIP = line_list[1]
    elif 'status:' == line_list[0]:
        status = line_list[1]

if status != 'RUNNING':
    raise Exception('vm status is %s'%status)

input_files = ' '.join(from_files)
cmd_str = 'rsync -av --exclude ".*" -e "ssh -i $HOME/.ssh/google_compute_engine"  %s $USER@%s:%s'%(input_files, natIP, to_location)
subprocess.check_call(cmd_str,shell=True)
