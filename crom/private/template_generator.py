#!/usr/bin/env python

import sys
import os
import getpass
#Template generator for Firecloud WDL + Docker tasks


def usage():
    print("Template generator for gdac-firecloud tasks and workflows\n")
    print("Usage: template_generator.py (-t | -w) folder_name \n")
    print("Required Arguments:\n")
    print("\t-t:\t\tCreate a template task folder")
    print("\t-w:\t\tCreate a template workflow folder")
    print("\tfolder_name:\tName of template folder")

def generate_task_folder(methodname):

    ##Make a new folders
    os.mkdir(methodname)
    os.mkdir(os.path.join(methodname, "src"))
    #os.mkdir(os.path.join(methodname, "test_output"))
    #os.mkdir(os.path.join(methodname, "build"))

    ##Paths for contents
    readme_path = os.path.join(methodname, "README.%s.md"%methodname)
    makefile_path = os.path.join(methodname, "Makefile")
    dockerfile_fn = "docker.%s.txt"%methodname
    dockerfile_path = os.path.join(methodname, dockerfile_fn )
    taskdef_path = os.path.join(methodname, "taskdef.%s.wdl"%methodname)
    sourcefiles_path = os.path.join(methodname, "sourcefiles.%s.list"%methodname)
    inputtest_path = os.path.join(methodname, "inputtest.%s.json"%methodname)

    cmd_fn = "cmd.%s.sh"%methodname
    cmd_docker_path = os.path.join('/opt/src', cmd_fn )
    cmd_path = os.path.join(methodname, 'src', cmd_fn )

    hello_fn = "hello.py"
    hello_docker_path = os.path.join('/opt/src', hello_fn )
    hello_path = os.path.join(methodname, 'src', hello_fn )

    name_url = 'https://personal.broadinstitute.org/gsaksena/world.txt'


    username = getpass.getuser()
    templateargs = {'methodname':methodname, 'username':username, 'hello':hello_docker_path, 'cmd':cmd_docker_path,
                    'name_url':name_url}
###################################################
###################################################
##### README.method.md

    with open(readme_path, 'w') as fid:
        fid.write('''# README for {methodname}
'''.format(**templateargs))
###################################################
##### Makefile

    with open(makefile_path, 'w') as fid:
        fid.write(
'''include ../../Makefile.inc
FIRECLOUD_WDL_DOMAIN=${{USER}}
FIRECLOUD_WDL_METHOD_NAME=${{FOLDER}}
'''.format(**templateargs))
        
###################################################
##### docker.method.txt

    with open(dockerfile_path, 'w') as fid:
        fid.write(
'''FROM ubuntu:16.04
RUN apt-get update && apt-get install -y python sudo dstat

#copy contents of tasks/<taskname>/build/src on the build host into /opt/src on the docker
COPY src/ /opt/src/

WORKDIR /opt/src
'''.format(**templateargs))
        


###################################################
##### taskdef.method.wdl

    with open(taskdef_path, 'w') as fid:
        fid.write(
'''task {methodname} {{

    #Inputs and constants defined here
    String salutation_input_string
    File name_input_file

    String output_disk_gb
    String boot_disk_gb = "10"
    String ram_gb = "8"
    String cpu_cores = "2"

    command {{
python_cmd="
import subprocess
def run(cmd):
    subprocess.check_call(cmd,shell=True)

run('ln -sT `pwd` /opt/execution')
run('ln -sT `pwd`/../inputs /opt/inputs')
run('/opt/src/algutil/monitor_start.py')

# start task-specific calls
##########################

run('python /opt/src/hello.py \\"${{salutation_input_string}}\\"  \\"${{name_input_file}}\\"')

run('tar cvfz greeting.tar.gz greeting.txt')

#########################
# end task-specific calls
run('/opt/src/algutil/monitor_stop.py')
"
        echo "$python_cmd"
        python -c "$python_cmd"

    }}

    output {{
        File greeting_txt="greeting.txt"
        File greeting_tarball="greeting.tar.gz"
    }}

    runtime {{
        docker : "docker.io/{username}/{methodname}:1"
        memory: "${{ram_gb}}GB"
        cpu: "${{cpu_cores}}"
        disks: "local-disk ${{output_disk_gb}} HDD"
        bootDiskSizeGb: "${{boot_disk_gb}}"
        preemptible: 0
    }}


    meta {{
        author : "Your Name"
        email : "Your.Email@Address.com"
    }}

}}

workflow {methodname}_workflow {{
    call {methodname}
}}
'''.format(**templateargs))

###################################################
##### sourcefile.method.list



    with open(sourcefiles_path, 'w') as fid:
        fid.write(
'''src\tdest
src/*\tbuild/src/
../../algutil\tbuild/src/
'''.format(**templateargs))

####################################################
##### inputtest.method.json


    with open(inputtest_path, 'w') as fid:
        fid.write(
'''{{
    "{methodname}_workflow.{methodname}.salutation_input_string": "hello",
    "{methodname}_workflow.{methodname}.name_input_file": "{name_url}",
    "{methodname}_workflow.{methodname}.output_disk_gb": "10"
}}
'''.format(**templateargs))

###################################################
##### src/cmd.method.sh


#     with open(cmd_path, 'w') as fid:
#         fid.write(
# '''#!/bin/bash
# mkdir -p /opt
# ln -sT `pwd` /opt/outdir
# ln -sT `pwd`/../inputs /opt/indir
# /opt/src/algutil/monitor_start.py
#
#
# SALUTATION_INPUT_STRING="$1"
# INPUT_NAME_FILE="$2"
#
# python {hello} "$SALUTATION_INPUT_STRING" "$INPUT_NAME_FILE"
#
# METHOD_EXIT_CODE=$?
#
# tar cvfz greeting.tar.gz greeting.txt
#
# /opt/src/algutil/monitor_stop.py
# exit $METHOD_EXIT_CODE
# '''.format(**templateargs))

###################################################
##### src/hello.py

    with open(hello_path, 'w') as fid:
        fid.write(
'''import sys

salutation = sys.argv[1]
name_file = sys.argv[2]

infid = open(name_file)
name_contents = infid.read()
infid.close()
name = name_contents.strip()


outfid = open('greeting.txt','w')
outfid.write('%s %s\\n'%(salutation,name))
outfid.close()
'''.format(**templateargs))


###################################################
###################################################





def workflow_wdl_contents(workflow_name):
    contents = "workflow " + workflow_name + " {\n"
    contents += "\t#Sync tasks with 'make sync', then insert task calls and logic here.\n}\n"
    return contents

def generate_workflow_folder(foldername):
    os.mkdir(foldername)
    wdl_path = os.path.join(foldername, foldername + ".wdl")
    sync_path = os.path.join(foldername, "SYNC_TASKS")
    makefile_path = os.path.join(foldername, "Makefile")


    with open(wdl_path, 'w') as wf:
        wf.write(workflow_wdl_contents(foldername))

    with open(sync_path, 'w') as sf:
        pass ##Empty by default

    with open(makefile_path, 'w') as mf:
        mf.write(makefile_contents())

def main():
    if len(sys.argv) != 3:
        if len(sys.argv) != 1:
            print("Error: Invalid number of arguments")
        else:
            usage()
    elif not os.path.isdir(sys.argv[2]):
        if sys.argv[1] == "-t":
            generate_task_folder(sys.argv[2])
        elif sys.argv[1] == "-w":
            generate_workflow_folder(sys.argv[2])
        else:
            raise ValueError("Unrecognized argument {0}".format(sys.argv[1]))
    else:
        print("{0} already exists".format(sys.argv[2]))

if __name__ == '__main__':
    main()
