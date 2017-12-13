#!/usr/bin/env python

'''
cl = cromwell latest
cd `cl` from somehwhere under the task to get to the most recent execution output directory
Note that this needs to be set to have executable permissions to work.

'''

import os
import sys
import json
import subprocess

inputs_json_path = sys.argv[1]
output_json_path = sys.argv[2]
data_output_dir = sys.argv[3]


def execute_str(cmd_str):

    p = subprocess.Popen(cmd_str,shell=True,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    (stdout,stderr) = p.communicate()
    return_code = p.returncode
    err = return_code!=0
    stdout_str = str(stdout)
    stderr_str = str(stderr)

    return (err,stdout_str,stderr_str)


if not os.path.exists(data_output_dir):
    os.makedirs(data_output_dir)

fid = open(inputs_json_path)
inputs = json.load(fid)
outputs = {}
print (inputs)
for arg in inputs:
    input_value = inputs[arg]
    #print (arg)
    #print (input_value)

    is_file = input_value.startswith('/') or input_value.startswith('gs://') or input_value.startswith('http') or input_value.startswith('test')

    if not is_file:
        outputs[arg] = input_value
        continue

    arg_subdir = arg
    arg_dir = os.path.join(data_output_dir, arg_subdir)
    arg_fn = os.path.basename(input_value)
    arg_path = os.path.join(arg_dir, arg_fn)
    arg_subpath = os.path.join(arg_subdir, arg_fn)
    arg_partial_path = arg_path + '.partial'

    outputs[arg] = arg_path

    if os.path.exists(arg_path):
        print ('already exists: %s  at %s'%(arg_subpath, arg_path))
        continue
    elif not os.path.exists(arg_dir):
        os.mkdir(arg_dir)
        # go on to actually put the file there
    if input_value.startswith('gs://'):
        # check first whether on the cloud, if not then abort
        rc = subprocess.call('curl "http://metadata.google.internal/computeMetadata/v1/instance/machine-type" -H "Metadata-Flavor: Google"', shell=True)
        if rc != 0:
            raise Exception('Due to potential egress charges, localization of gs:// files is only supported from GCE instances.')

        print ('localizing %s from bucket %s'%(arg, input_value))
        (err, stdout_str, stderr_str) = execute_str('grep -c ^processor /proc/cpuinfo')
        num_cores = stdout_str.rstrip()
        print ('using %s cores'%num_cores)
        # todo get rid of check_hashes=never once compiled crcmod is installed to gce vm image.
        subprocess.check_call('gsutil -m -o "GSUtil:parallel_thread_count=6" -o "GSUtil:parallel_process_count=%s" -o "GSUtil:check_hashes=never" -o "GSUtil:sliced_object_download_threshold=200M" -o "GSUtil:sliced_object_download_component_size=50M" -o "GSUtil:sliced_object_download_max_components=4" cp %s %s'%(num_cores, input_value, arg_partial_path),shell=True)
        os.rename(arg_partial_path, arg_path)


    elif input_value.startswith('http'):
        print ('downloading %s from %s'%(arg, input_value))
        subprocess.check_call('curl %s > %s'%(input_value,arg_partial_path),shell=True)
        os.rename(arg_partial_path, arg_path)


    else:
        #assume it is a local path.
        # check that it exists
        if not os.path.exists(input_value):
            raise Exception('could not find arg %s: %s'%(arg,input_value))

        # get the real path.
        input_value_real_path = os.path.realpath(input_value)
        # make hard link for speed, which errors if not on the same volume
        print('hard linking %s from %s' % (arg, input_value))

        os.link(input_value_real_path, arg_path)

fid.close()
fid = open(output_json_path,'w')
json.dump(outputs,fid, indent=2, sort_keys=True)
fid.close()
