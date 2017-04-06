# firecloud_developer_toolkit

The Firecloud Developer Toolkit (FDT) is broken up into several sections which may be used together or independently.
* gce - wrappers around gsutil, used to create and manage standalone Google Compute Engine VMs
* install - installation scripts for commonly used 3rd-party software for Ubuntu/Debian
* crom - wrappers around Docker and Cromwell to streamline the creation and testing of Firecloud modules. Currently only single-task workflows are fully supported.
* algutil - utilities intended to run inside the Docker container of a Firecloud module.


The currently supported approach for debugging docker containers for Firecloud is to do all of the heavy lifting with a Google VM (GCE instance), ie building docker containers and using Cromwell to run them.  To make code edits, the simplest setup is to run an editor right on the VM, though you may have a better experience if you edit a local copy of the code, and push it to the VM via GitHub, rsync, or by using the deployment features of your local editor. While it is possible to configure your local Mac/Windows machine or a local Ubuntu VM to work at a reasonable level, the setup steps are different and not yet documented, and in any case your local machine will likely have more limited CPU/RAM/disk/network options than GCE instances.


## How do I get set up with running Google VMs?


## Once I'm set up, how do I create and interact with Google VMs?


## How do I use the crom framework to develop a Firecloud task?

FireCloud algorithms are encapsulated in Docker containers and run by the Cromwell execution engine.  The 'crom' framework
wraps common Docker and Cromwell commands needed to test your algorithm outside of Firecloud.  It assumes your tasks follow a certain directory structure and file naming convention, as set up by the createnewrepo and createnewtask scripts.  Once you have your task set up, including your source code, dockerfile, WDL, and input arguments, you can build the docker and run it within Cromwell.  You can monitor the code as it runs within Cromwell by examining the output files or attaching a bash shell to the running Docker container. After Cromwell finishes, you can "wake the container back up" by spinning up bash prompt in a new container, with the input and output files from the previous run already mounted.

While you are developing, you will have two different git repos on your development node: 1) FDT (this repo) for utilities, and 2) a task repo to hold your algorithms.  While many of the utilites are embedded in Makefiles that live in the task repo, they are intended to be called via wrappers that live in FDT, and certain functionality like creating a new task and running Cromwell depends on utilities that live in FDT.

The utilities rely on several environment variables being set correctly.  These variables are set for you by the scripts, and all start with 'FDT_'.  `cd <fdt_root> && . fdtsetroot -s` as previously mentioned, both adds a pointer to the FDT repo to your current environment variables, as well as modifies .bashrc so that future shells will already be set up.  `. createnewrepo <path_to_new_task_repo>` and `. setrepodir [<path_to_existing_task_repo>]` creates a pointer to the task repo but leaves the algdir blank.  `. createnewtask <taskname>` and `. setalgdir [<fpath_to_task_dir>]` set the algdir, which is your current working task.  This current working task is the implicit target of most of the crom tools, such as build and runcromwell. The pointers to the task repo and current task are _not_ stored in .bashrc, so you will need to run the `setalgdir` command each time you power up the VM or create a new shell.

This framework currently assumes 1) you have sudo privileges that do not require a password re-prompt, 2) you are in the docker group,  3) you will be using the /opt directory for your development work, and 4) you are using a Linux rather than a BSD/Mac system.  These assumptions are consistent with the Google VM setup described above.

#### preliminary

You should make sure key utilities are up to date, to avoid encountering odd bugs that noone cares about.   
```
cd $FDT_ROOT && git pull  #update FDT, assuming the environment variables were set
sudo update_gsutil_latest_nr.sh
install_cromwell_25_nr.sh  #Check Firecloud to ensure the version matches
install_fissfc_latest.sh
install_firecloudcli_latest_nr.sh
```

#### Create repo
To start with, create a new task repo:
```
. createnewrepo <path_to_new_task_repo>
```

This creates a directory structure with 'tasks' and 'workflows' directory.  Algorithms with their own dockerfile will live under the tasks directory, along with WDL representing a single task workflow.  Algorithms that are single-task workflows that piggy-back off of other dockers, or workflows that chain together multiple dockers, should live in the workflows directory.

Makefiles will be added to this repo.  Normally you will not need to mess with them, except as described later.

A basic .gitignore is created at the root of the task repo, so that artifacts from building and running are not checked into Git.  You may want to add to this file depending on the languages and editors you use, to avoid compiler outputs and editor backup files.

You may want to add your own README.md and LICENSE files.

This command does _not_ create an actual git repo or attach it to GitHub.  If you want your new repo to live on GitHub, perhaps the most straightforward way to do this is
* Create a new empty public or private repo on GitHub
* cd to the local directory you want to be parent to your repo
* `git clone <https://.../mynewrepo.git>` 
* `. createnewrepo /full/path/to/mynewrepo`
You can also initialize and attach your repo to GitHub later, but the steps are different.

#### Create task

Tasks require certain files to be present that follow a certain naming convention.  To make this easier, the `createnewtask` script generates a hello-world task that follows these conventions, giving you a starting point.

```
. createnewtask <taskname>
```

If the taskname is 'testtask', this creates the following files:

src/hello.py
* Accepts a string and a file input.
* Emits a file result.
```
import sys

salutation = sys.argv[1]
name_file = sys.argv[2]

infid = open(name_file)
name_contents = infid.read()
infid.close()
name = name_contents.strip()


outfid = open('greeting.txt','w')
outfid.write('%s %s\n'%(salutation,name))
outfid.close()
```

sourcefiles.testtask.list 
* TSV table to tell the build process to pull files from elsewhere in the repository to the tasks/testtask/build directory.
* The docker.testtask.txt file will also be copied to the build directory, but does not need to be listed here.
```
src    dest
src/*  build/src/
../../algutil   build/src/
```


docker.testtask.txt
* Starts from a recent stable Ubuntu image.
* Installs Python and the dstat monitoring tool, useful for tuning the VM size.  
* Installs sudo so you can paste in other installation commands with less editing.  
* Copies tasks/testtask/build/src directory to live under /opt/src in the docker.
```
FROM ubuntu:16.04
RUN apt-get update && apt-get install -y python sudo dstat

#copy contents of tasks/<taskname>/build/src on the build host into /opt/src on the docker
COPY src/ /opt/src/

WORKDIR /opt/src
```

taskdef.testtask.wdl
* Single task workflow WDL
* Accepts file and string inputs, generates file outputs.
* Accepts an input for the output disk size, explicitly hard-codes other VM parameters.
* A non-preemptible VM is chosen.
* The docker repo name, location, and version used when pushing it is specified in the runtime block:  "docker.io/<user>/testtask:1" = Dockerhub, <user> repo name, and 1 = version tag.

* Glue code is all in Python, for better readability and exception handling than bash (at least when things are more complicated/realistic than this example)
* Note that double quotes are avoided or escaped in the Python code, so they don't terminate the python_cmd variable definition. Braces used for Python dictionaries also need escaping, otherwise they are interpreted as WDL variable substitution.
* The glue code drops symlinks to /opt/inputs and /opt/execution, which are useful for manual debug.
* monitor_start.py and monitor_stop.py drop several log files that can be useful for debugging crashes or sizing the VM.

```
task testtask {

    #Inputs and constants defined here
    String salutation_input_string
    File name_input_file

    String output_disk_gb
    String boot_disk_gb = "10"
    String ram_gb = "8"
    String cpu_cores = "2"

    command {
python_cmd="
import subprocess
def run(cmd):
    subprocess.check_call(cmd,shell=True)

run('ln -sT `pwd` /opt/execution')
run('ln -sT `pwd`/../inputs /opt/inputs')
run('/opt/src/algutil/monitor_start.py')

# start task-specific calls
##########################

run('python /opt/src/hello.py \"${salutation_input_string}\"  \"${name_input_file}\"')

run('tar cvfz greeting.tar.gz greeting.txt')

#########################
# end task-specific calls
run('/opt/src/algutil/monitor_stop.py')
"
        echo "$python_cmd"
        python -c "$python_cmd"

    }

    output {
        File greeting_txt="greeting.txt"
        File greeting_tarball="greeting.tar.gz"
    }

    runtime {
        docker : "docker.io/<user>/testtask:1"
        memory: "${ram_gb}GB"
        cpu: "${cpu_cores}"
        disks: "local-disk ${output_disk_gb} HDD"
        bootDiskSizeGb: "${boot_disk_gb}"
        preemptible: 0
    }


    meta {
        author : "Your Name"
        email : "Your.Email@Address.com"
    }

}

workflow testtask_workflow {
    call testtask
}
```


inputtest.testtask.json 
* input arguments for running Cromwell on the local node
* file args can be absolute paths, http links, or gs:// links.
```
{
    "testtask_workflow.testtask.salutation_input_string": "hello",
    "testtask_workflow.testtask.name_input_file": "https://personal.broadinstitute.org/gsaksena/world.txt",
    "testtask_workflow.testtask.output_disk_gb": "10"
}
```

Makefile 
* Contains values used when pushing the WDL to Firecloud
* namespace = username on this node, method name = directory name under tasks.
```
include ../../Makefile.inc
FIRECLOUD_WDL_DOMAIN=${USER}
FIRECLOUD_WDL_METHOD_NAME=${FOLDER}
```

README.testtask.md 
* Minimalist readme file for your task.
```
# README for testtask
```

###### Simple task
If you have a script that runs elsewhere and you would like to dockerize it, follow these steps:

* run `. createnewtask <taskname>` as described above.
* Import your source code
    * Either ignore or get rid of src/hello.py
    * If you have an independent script or set of scripts, copy them all into the <taskname>/src directory.
    * If you have common code that you want to pull into multiple docker images
        * put just the code that is specific to this task under the <taskname>/src directory.
        * create a directory outside of this task, eg <reponame>/common, and copy the common code there.
* Update the sourcefiles.<taskname>.list file
    * If you have an independent script, ie all of your code lives under <taskname>/src, then you can leave this file alone.
    * If you want to pull in files from elsewhere in the repo into the build, add source-destination pairs to this file.  Everything under a source directory will be recursively copied.  If the destination is a directory, be sure to terminate it with a slash.

* Update the docker file: docker.testtask.txt
    * Add whatever other languages or packages you need.
    * Refer to the ```install``` directory under FDT for common installation recipes.
    * Refer to dockerfile best practices to avoid common pitfalls.

* Update the WDL: taskdef.testtask.wdl.
    Test the WDL syntax via `validatewdl`.  Blank output means OK.

    Inputs
    * Modify the inputs to match your task
    * Note that all input files will be in separate directories.  Add code here to symlink indexs to live in the same directory as the file they index, eg for BAMs and VCFs.
    * Untar reference file bundles if needed.  
        * You probably want to put them into a subdirectory of the output directory - putting them anywhere else, eg /tmp, will bloat the boot disk and cause mysterious VM lockups if it fills. An issue has been filed to request Firecloud stores the whole docker image, not just the execution and inputs directories, on the output disk.
    * For aggregation parameters (eg when running on a sample_set with a sample-level annotation), parse the representation passed in from Firecloud.

    Outputs
    * Ok to leave outputs blank initially - run things locally first, then see the exact outputs to fill in.

    Command
    * Update the commandline to run your algorithm
    * Be extremely careful that a failure anywhere in your command, or in the input/output processing, causes a non-zero exit code to be returned from the comamnd block.  You can do this by using Python for the whole command block or by setting bash flags such as `set -euo pipefail`.
    * All outputs should be written to the CWD or one of its subdirectories.  Any files written elsewhere will bloat the boot disk (see discussion under reference files, above).
    
    Update the Docker repo information
        * These edits are not as important when running locally, before pushing to Dockerhub.
        * Dockerhub = docker.io, Google container registry = us.gcr.io. 
            *Google's seems more reliable than Dockerhub's, but someone had trouble making private containers work due to FC service account issues, and the pricing is a bit different.
        * update the repo name testtask, if you want.  This repo needs to have already been created.
        * update the version number, if you want. (Note that there is active work related to setting this version number.)
    
    Update the VM specs
    * Irrelevant for running on local Cromwell
    * On Firecloud, memory and cpu requests rounded up to nearest pre-defined VM type (see https://cloud.google.com/compute/pricing)
    * The boot disk can stay at 10GB, unless your algorithm must write to someplace outside the output directory.
    * The output disk must be sized to hold all input files, intermediate files, and output files.
    * See best-practices for how to set the preemptible flag

    Update meta tags
    * Fill in contact info of the maintainer

* Update the test inputs: inputtest.testtask.json
    * This file is only used locally, not on Firecloud.
    * After significant WDL changes, you may want to use `createinputtest` to create a inputtest.tesktask.json.template file, to get all of the naming correct.
    * Files are passed in as JSON strings.  Currently they must start with /, http, or gs://. 'tests/' will also likely be supported soon, to allow test data to be referenced via a relative path.
    * You may create multiple test input files to test multiple cases. For ease of use, the file names should be distinguished by adding characters somewhere in the middle of the standard name.

* Update the Makefile
    * edit to update the namespace and method name to push the WDL to in Firecloud
    * These edits are not needed when running locally.

* Update the Readme
    * This info will be visible within GitHub as well as Firecloud.  It is for documentation only.

###### Workflow

###### Best practices

Workflows
* WDL workflows vs atomic tasks
* WDL-based scatter gather vs Pipette-based scatter-gather.

WDL
* use of strings vs floats or ints
* propagating root filename to outputs? add to template?
* handling variable outputs - tarballs vs globbing
* handling numerous outputs - tarballs vs many explicit values
* handling multiple files referenced by .html output file
* handling short output values, eg a number or path
* bash vs python
* returning error codes reliably
* dynamically sizing output disk
* preemptible flag

Dockerfiles
<link to official best practices>
* apt-get install should be on same line as apt-get update, to avoid cryptic build failures in the future.
* do not include CMD or EXEC lines, they make debug awkward

#### Run task


#### Debug task

--
todo#

adding tests/ as acceptable file prefix

if [[ "$(uname)" == "Darwin" ]]; then
<mac specific workaround/error msg>
else
<existing linux code>
fi





