# firecloud_developer_toolkit

The Firecloud Developer Toolkit (FDT) is broken up into several sections which may be used together or independently.
* gce - wrappers around gsutil, used to create and manage standalone Google Compute Engine VMs
* install - installation scripts for commonly used 3rd-party software for Ubuntu/Debian
* crom - wrappers around Docker and Cromwell to streamline the creation and testing of Firecloud modules. Currently only single-task workflows are fully supported.
* algutil - utilities intended to run inside the Docker container of a Firecloud module.

_TBD- should crom be renamed to cromlocal or cromdebug?_

A recommended way of doing development is to take a hybrid approach between using your laptop and a GCE VM.  First,
write and edit your code local to your laptop, and optionally sync it from there to GitHub. 
To test your current version, copy the source code to a GCE VM, and build the docker there and run it.   Once you are happy with 
it, push the docker image from the VM to Dockerhub, and push the WDL from the VM to Firecloud. 
 
Other reasonable approaches include laptop-only (replacing the GCE VM with a Virtualbox or other VM that you have sudo priviledges on) 
or GCE VM only (doing all of your development work on the VM using emacs/vi or an IDE, using your laptop as a dumb terminal).  
Using GCE for running the algorithm has the advantage of being more similar to Firecloud VMs than other VMs, and gives you access to 
 more resources (CPUs, RAM, storage) than are available on your laptop.  On the other hand, while it is simpler in 
 some ways to do all of your editing on the GCE VM, it has the downsides of network latency and ongoing billing.

The main workflow described below follows the hybrid laptop-GCE VM approach to create, debug, and deploy a FireCloud module.


## Initial setup
These utilities 
require bash, Python2.7, Git, and Java1.8. For everything to work, these should all be installed and in your path, both 
on your laptop as well as on the GCE VM. Python 3, currently the default on the Macs, causes gsutil to give
strange errors.
 
The first step is to clone this repo to someplace on your local laptop or Linux VM, and then source the fdtsetroot command.  
fdtsetroot sets environment variables, and adds its directories to your path.  Use the -s option to also modify your .bashrc.
```
cd /opt
git clone https://github.com/broadinstitute/firecloud_developers_workbench.git /opt/fdt
cd /opt/fdt
. fdtsetroot -s
```
Next, you should install a few utilities to your local environment. 

To work with GCE VMs, you need gsutil.  
```
install_gsutil_latest_nr.sh   # root not needed
update_gsutil_latest_nr.sh    # run this instead if gsutil is already installed
```
To work with Firecloud, you should install Firecloud-specific utilities.  Cromwell/wdltool is needed on your laptop to 
validate and parse your wdl file.
```
install_cromwell_21_nr.sh          # root not needed.  21 is the current FireCloud version as of Jan 2017.
```
fissfc and firecloud cli are needed to use commandline tools to interact directly with Firecloud, eg for loading wdl files, 
loading data loadfiles, or launching and monitoring workflows.
```
install_firecloudcli_latest_nr.sh  # root not needed. Python2.7 and Git need to already be in the path.
install_fissfc_latest.sh        # root needed unless you set up a python venv
```

## Create your repo and algorithm template

FireCloud algorithms are encapsulated in Docker containers and run by the Cromwell execution engine.  The 'crom' set of tools
wraps common Docker and Cromwell commands needed to test your algorithm on a standalone VM.  These tools assume certain 
files and directories exist in your code repo, and that you are using a particular file naming convention for your 
algorithm.  To make it easier to follow these naming conventions, it can generate a basic, fully functioning hello-world 
task that you can modify.

```
. createnewrepo /absolute/path/to/your/new/repo  # creates new directory structure, including tasks subdirectory. Run before making your first task.
# This repo is intended to be pushed to GitHub.  First add README.md, .gitignore, and LICENSE files, and then run 'git init'.

. createnewtask mytask # creates a complete hello-world task under /path/to/your/new/repo/tasks/mytask
```
* Note that ```createnewrepo``` and ```createnewtask``` set temporary environment variables that indicate the location of 
the repo and the current algorithm, used by the other crom tools.  These variable must be set again if you reboot the VM 
or open a new shell.  To do this, use ```setalgdir```


```
. setalgdir [<your alg directory>] # sets repo and current alg environment variables.  defaults to cwd
```

## Edit the algorithm template
##### src/hello.py
Replace this with your own sophisticated algorithm.  Also copy any task-specific jar files or libraries into this src directory.
* Rather than making redundant copies of source files used by multiple tasks/wdl's, use the sourcefiles.method.list file
described below to reference them in some common location.
* You should avoid including bulky reference files in your source repo.  Instead, pass them in as parameters to your task, and store them
locally on the VM or in a GCS bucket.  If there are numerous reference files,  pack them into a .tar.gz file, and unpack
them in the wrapper code in the wdl command block.
* The default sourcefiles.method.list links the contents of this directory to build/src at build time.


##### taskdef.method.wdl
See https://github.com/broadinstitute/wdl#getting-started-with-wdl for more info on wdl.
* The command block contains a boilerplate script, most of which you probably want to keep.

  * replace the call to hello.py with a call to your own algorithm
  * It is handy to have wrapper code embedded in the WDL to unpack and link inputs and bundle outputs, so that it can be edited without touching the Docker image.
     * When embedding a shell script, be sure to use ' && \' at the end of every command line and '\' at the end of every blank line, to enable non-zero exit codes to flag an error.  
     * An alternative way to ensure failing exit codes are returned is to use something like ```python -c "<python code>"``` to do your work in a non-shell language.  
     * Fumbling the error code return can lead to intermittantly bad behavior.  If everything passes, it works fine.  If something fails but the exit code is not propagated to the end,
     the task will still fail if an output file is missing.  But, if the failure causes a truncated output file, the task may be reported as passing, and something downstream will behave oddly.
  * Note that the process monitor emits logs that indicate static resoureces (eg number of cores) and dynamic usage (cpu, memory, i/o, disk space)
  * Note that every input file will be passed in using different directories, including .bam and .bai files. The recommended 
approach is to link them into a the same directory with a fixed name, and then pass the fixed name to your algorithm. For example, the command block may have the following:
```
        ln -s ${input_bam} my_input1.bam
        ln -s ${input_bai} my_input1.bam.bai
        samtools -h my_input1.bam
```
  * If you do not want to specify individual outputs, a common technique is to bundle them into a .tar.gz file.
  * (insert tip about getting html image references to work, eg for Nozzle reports)
  * The current best-practice is that the algorithm should write _all_ output to the starting cwd.  (This is because currently other locations 
end up on the boot disk of the host VM, and are liable to crash the VM by filling the disk.) If the algorithm must write 
to other locations, such as /tmp or the home directory, before the algorithm starts this script should symlink those locations
to the starting cwd.
* Specify the docker repo, image name, and version via the runtime parameters.  These default to dockerhub, user's 
namespace, the method name, and version 1, but these can be changed freely.  This info lets crom's push_docker command know where
to push the image, and lets Firecloud know where to pull the image from.
* Set the preemptible flag in the runtime parameters. 0 = do not use preemtible instance, 1 = start with a preemtible instance, but on the first retry fallback to a non-preemptible instance.
* Note that all the VM specs in the runtime parameters are ignored by Cromwell while running locally, they were set when you created the GCE VM.
* Test whether your syntax is valid via the `validatewdl` command. A blank line output means it is good. 
* A similar but 
not identical validation is run by Firecloud at the time a method config is imported to a workspace; currently, any Firecloud 
error message ocurring at that step can only be viewed via going into Chrome's developer mode and clicking on the right things.

##### inputtest.method.json
This file is used during non-Firecloud testing to supply arguments for the WDL input parameters.
* You may specify files that live 1) locally on the output disk, 2) in a GCS bucket gs://<bucketname>/file, or 3) an http url.  
  * For #1, files are hard-linked for space and time savings, so they must live on the same volume as the output.  
  * For #2, bucket input paths are only permitted while running on a GCE instance, to avoid egress charges.  
* You can generate a template inputtest file by running ```createinputtest```  . This creates a file inputtest.method.json.template,
 with correctly defined parameters and dummy arguments based on the current taskdef.method.wdl file.
* Note that every file will be put into its own directory before your task sees it, including .bam and corresponding .bai 
files currently in the same local directory.  See the note under taskdef.method.wdl for how to address this.


##### sourcefiles.method.list
List of files to copy into build directory just before building the Docker image.  Used to selectively pull in common files used by multiple tasks.  
* If all of your source
files live in the task's src subdirectory, you can leave this file alone.
* If you want to have multiple wdl files that use the same docker, make a separate task for each wdl, and edit this file 
to pull in source files from a common location.
* A recursive copy is done on all source directories.
* If the destination is a directory, make sure it ends with / to ensure predictable behavior.
##### docker.method.txt
Dockerfile used to build the docker.  Refer to the FDT install directory for ideas about how to install other packages.
* This file will be copied to build/Dockerfile at build time.
* add lines before the algorithm to install the third-party packages you need.
* You can cut-and-paste install scripts from the fdt/install/ folder, and just prepend 'RUN'
* Do not include CMD or ENTRYPOINT directives.  Cromwell and these scripts generate the command based on the taskdef.method.wdl 
file, so including these can cause confusion.
##### Makefile
The task-specific Makefile is where the Firecloud method repo Namespace and Method name are specified.  They default to 
the user's namespace and the task name, but can be changed freely.  The are used for crom's pushwdl command.
##### README.method.md
More detailed description of your task, for documentation on Firecloud's method repo and on GitHub.



## Set up GCE VM
We will use a GCE VM to build and test your algorithm, so let's create one.

You need a Google billing account set up first, along with a Google Project.  The project needs to have priviledges to spin 
up VMs.  The project cannot be the same as your Firecloud project, as Firecloud projects do not allow you to spin up VMs yourself.

First, log into Google from the command-line on your laptop, and choose the project the VM will be billed to.  Perhaps choose us-east1-c 
for the default zone.
```
gcloud init
```

#### Base GCE VM off previously built image

The quickest way to spin up a new VM is off a previously built image that is accessible from your project.  It will be ready to go in perhaps half a minute.
```
create_and_start_vm.sh <vmname> <instance_type> <docker_disk_size>
create_and_start_vm.sh pcawgvm1 n1-standard-2 20
```
* For instance_type, standard = 3.75GB/core, highmem=6.5GB/core, highcpu=0.9GB/core
* For instance_type, last digit is number of cores, must be a power of 2
* Note that 1 cpu core costs the same as 7.5GB of RAM.
* Also, consider super-cheap instances: f1-micro (0.2 cpu, 0.6 GB RAM) and g1-small (0.5 cpu, 1.7GB RAM)
* docker_disk holds both the output directories and docker images from runs made on VM.  Minimum 20.  In GB.  This disk is mounted on the VM as /opt.
* The disk image locations need to be set within the script to point to a project you have access to.
* Keep the VM name relatively short, as you will be typing it multiple times.  Dashes are ok but underscores are not.

Then, login to the VM.  Open a shell from an existing shell window:
```
ssh_to_vm.sh <vmname>
ssh_to_vm.sh pcawgvm1
```
* You should enable anti-idle from your laptop's terminal program to avoid being logged out after an hour.
* The first time you try to log into a GCE VM, you will be prompted to create a password for a new Google SSH key.  You will need this password whenever you access 
the VM from your laptop.

After you spin up a VM  there is some one-time user-specific setup that is needed on the VM.
```
gcloud init # log in with your Google credentials, used to access Firecloud and GCS buckets.
docker login # log into dockerhub, for pushing and pulling private images
sudo gpasswd -a ${USER} docker  # add yourself to the docker unix group, needed for crom to work.  Requires relogin to take effect.
```
* In case you missed it in the line above... you need to log out and back in to be properly joined to the 'docker' unix group.  You can run ```groups``` to see whether 
it knows you are in the docker group.

#### Import a previously built image
If you want to import an image into your project that was created by someone else, these basic notes may be useful...
_TBD make these more complete_
* Load 2 private disk images into your project, to be used as the base for the VMs.  

  * copy into bucket via gsutil cp
  ```
    gsutil mb gs://[BUCKET_NAME]
    gsutil cp /mnt/tmp/myimage.tar.gz gs://[BUCKET_NAME]
  ```

  * make images via below.  The IMAGE_NAMEs must be in sync with those found in ```create\_and\_start\_vm.sh```
  ```
    gcloud compute images create [IMAGE_NAME] --source-uri [URI]
  ```
  * check things are there
  ```
    gcloud compute images describe [IMAGE_NAME]
  ```

#### Base GCE VM of stock image

If you want to customize your image, you can build your VM image from scratch.
* ```create_initial_vm``` creates 2 disk VM based on the debian7bp stock image, the same stock image that Firecloud VMs 
started with.  
* The second disk is mounted on /opt.  
* A symlink has been dropped on the boot disk to move future docker image storage to /opt.
* assuming you want to snapshot this for later, you probably want a very small docker disk size, as what you set here 
will be the minimum allowed later.
```
$FDT_ROOT/gce/setup/create_initial_vm.sh <vmname> <instance_type> <docker_disk_size> 
$FDT_ROOT/gce/setup/create_initial_vm.sh test1 n1-standard-2 10
```


Next, log in to it:
```
ssh_to_vm.sh <vmname>
ssh_to_vm.sh test1
```

Then, install the software you need.  First install Git, next install the Firecloud Developer Tools, and then use the 
FDT installers to install the other packages you need.  The following packages take several minutes total to install. 
* The install scripts that run as non-root have _nr appended.
* If you are going to image your disk to speed up future VM spinups, you do _not_ want to login to Google or Docker Hub as that
would store credentials in the image.
* (In the future there should be a script to make it easier to capture disk images from a set-up VM.)
```
sudo apt-get install -y unzip git tree

 #root not needed
cd /opt
git clone https://github.com/broadinstitute/firecloud_developers_workbench.git /opt/fdt

cd /opt/fdt
. fdtsetroot -s

 #general
install_python_2.7.sh
install_oraclejavajdk_8_debian7bp.sh
install_docker_latest_debian7bp.sh #sets docker unix group membership, needs relogin before it takes effect
set_timezone_ET.sh

 #Google
install_gsutil_latest_nr.sh #note - corrupts the ~/.bashrc if run more than once, needs manual editing to fix #needs python2.7

 #firecloud-specific
install_cromwell_21_nr.sh #needs java  # for better correlation, pick the version currently used on FireCloud
install_firecloudcli_latest_nr.sh #relies on python venv, java
install_fissfc_latest.sh #relies on python pip
```



## Manage GCE VM

Now that your VM has been created, you can work with it in various ways.  Commandline approaches are described below, though
many of the same things can be accomplished via the gui available from console.cloud.google.com, or from the "Cloud Console" 
mobile app from Google.
```
stop_vm.sh <vmname> #powers down the VM so you don't get compute charges for it, only storage charges
start_vm.sh <vmname> #wakes up a VM that was previously stopped, assigns new IP address
reset_vm.sh <vmname> #reboots VM
expand_disk.sh <vmname> <new_docker_disk_size> # enlarges docker_disk, can do either while VM is running or stopped.  Cannot shrink disk.
delete_vm.sh <vmname> #purges VM and docker_disk, halting charges for both compute and storage.
```

```
stop_vm.sh pcawgvm1
start_vm.sh pcawgvm1
reset_vm.sh pcawgvm1
expand_disk.sh pcawgvm1 50
delete_vm.sh pcawgvm1
```

#### Info
To see what VMs you have, both running and halted, use:

```
list_vm.sh  #gives name, state, and ip addresses of your VMs
```
* You can use the external IP address listed here to attach to the VM, via the commandline or IDE. You should authenticate via 
the ~/.ssh/google_compute_engine key you created, instead of a password.

#### File transfer

##### IDE-based file transfer
IDE's can be configured to upload files it changes whenever you hit save, using the same ip address and ssh key.  In 
Pycharm, this is set under Tools -> Deployment -> Configuration
##### rsync-based file transfer
When initially attaching to the VM, or after making changes outside of the IDE, you can rsync to make sure that all the local files live on the VM.
```
rsync_to_vm.py <vmname> <src> [<src2> ...] <dest>
rsync_to_vm.py pcawgvm1 ~/pcawg /opt
```
* As ususal, rsync copies only files it feels it needs to.  Note that this does not delete any files on the VM, or 
(I think) overwrite files at the destination that are newer.  If you want things to be fresh, manually delete things on 
the VM side before performing the rsync
* Note that transfers into GCE are free, while transfers out are expensive if TB-scale.  
* Note that rsync to a VM is much slower than rsync into a bucket, as it runs serially; if you are trying to upload 
many GB it can take a while.  If you are uploading TB's of data, you probably want to use a bucket.
* For code, it may be cleaner to transver via GitHub, eg do `git push origin master` from your local computer 
and `git pull` from the GCE VM, though this involves an extra step than using rsync.

##### bucket-based file transfer
_TBD add details_
* boto file editing
* gsutil cp
* gsutil mb
* pseudo-directories

#### Pricing summary
You can find the cost of various things here: https://cloud.google.com/compute/pricing
* A 2 core standard memory (7.5GB) vm is $0.10/hr, $2.40/day.
* The biggest vm, 32 core highmem (208GB) is $2/hr, $48/day.
* Preemptible or long-running VMs are cheaper.
* VM disk space is $40/TB/mo based on capacity, not space used.
* Bucket storage is $20 or $26/TB/mo for stuff directly accessible, or $10/TB/mo that could work for things you will access less than 1/mo.
* Data egress out of Google can be as much as $120/TB


## Running your algorithm on the VM
Once you have your VM set up and your algorithm repo copied to it, you need to let the FDT know where it lives:
```
. setalgdir <path to your current algorithm>
```

## Build image
To build the docker image for your current algorithm, run:
```
build
```
* This creates a build subdirectory, assembles your Dockerfile and source files there, and runs docker build on it.  
* If the docker build appears to fail intermittantly, it may be because the way docker caches its builds.  Best practice 
recommendation is to include update and install on the same line, eg 'apt-get update && apt-get install -y foo'. To build
without using the cache, run ```buildclean```, and expect it to take longer.

### Run
Runs your image locally.
```
runcromwell [inputtest]
killrun
```
* `runcromwell` runs your docker image via Cromwell using &, so that things don't die if your ssh connection times out.  
If you want to abort it, you need to do `killrun` to kill cromwell and the container.
* `runcromwellfg` runs in the foreground, without using &, so ctrl-C can also abort it.
* If you want to use a different input than the default inputtest.<method>.json, you can specify the inputtest filename (full directory not needed)
* gs:// and http:// files are localized to <method>/localized_inputs, and cached there between runs.
* Output files are written to deep subdirectories under ./cromwell-executions.
* Links are dropped at /opt/execution, /opt/inputs pointing to the latest Cromwell run.  In addition, /opt/src is linked 
to the build/src directory created when you built the docker.

### Troubleshoot on VM
#### Work with output directory during or after run
Cromwell uses a mount for the output directory of the docker image, so you can view it during and after the job is running.
* ```cd `execution` ``` to cd into the latest output directory. (part of the path is a uuid that distinguishes repeated runs). 
* /opt/execution, /opt/inputs, and /opt/src are handy symlinks.
* ```cd `algdir` ``` to cd into the base task directory
* Analyze the `dstat.log.txt` file emitted from process_monitor.py to figure out how to size the VM (cores, RAM, disk)
* `clearoutputs` wipes the outputs from previous runs - they can get bulky.
* See `expand_disk.sh <vmname> <new_docker_disk_size>` for giving yourself extra disk space if you are running out of room.
#### Work inside container
* `attach` gives you a bash prompt inside the currently running container.  (Only works if exactly one container is running). 
* `runbash` to start your container outside of Cromwell, and give you a bash prompt.  This also mounts 
/opt/execution and /opt/inputs  inside the container to point to these same directories outside the container, which
are in turn linked to the the most recent run of Cromwell.  To pick up where the previous run left off, look at the 'script' file
in the output directory to learn what the initial command line was, and drop symlinks at the original inputs and execution directory
pointing to these directories. for example:
```
mkdir -p /root/mymethod_workflow/eedf0dde-c686-4bfd-bc45-b50f182624ea/call-mymethod
ln -s /root/mymethod_workflow/eedf0dde-c686-4bfd-bc45-b50f182624ea/call-mymethod/execution /opt/execution
ln -s /root/mymethod_workflow/eedf0dde-c686-4bfd-bc45-b50f182624ea/call-mymethod/inputs /opt/inputs
```
### Release
```
pushimage   # uploads your image to a repo such as dockerhub, based on the info given in taskdef.method.wdl
pushwdl     # uploads your taskdef.method.wdl to Firecloud, based on the info given in the task's Makefile.
```
## Wire into Firecloud
* note in method repo
* export or import to move to workspace
* import dummy sample, attach it
* run on sample
* modify to use sample annotation point to small yext file
* rerun on sample
* push new version of wdl 
* note how version stamp showd up
* push change to workspace, update, rerun


    
## Porting Tasks from Firehose

### Defining the docker
Typically the hydrant file will indicate what language package is needed in the commandline, eg via something like use R-2.15, or by calling out \<matlab2009a\>.
Based on this info, check the common/dockerfiles directory for a suitable match, and put them into your dockerfile.\<method\>.list file.  Note that .docker files with 'base' in the name must only be in the list file once, at the start.
Other .docker files can be added to the .list file to load third party packages or languages.  The .docker file loading your own module from \<method\>/src should be listed last, to best take advantage of docker build caching.
  
### Generating the command line for non-scatter-gather
The common/utils/firehose_module_adaptor contains utilities to make it easier to port existing Firehose modules into a Firecloud docker container.  The utilities are designed to be coupled only to Firehose, and not to Firecloud or Docker.  

run_module.py is used for normal (ie non-scatter-gather) jobs, enabling you to call the module via a simple command-line, and uses information given in the hydrant and manifest files.  

local_scatter_gather.py is used for scatter-gather jobs, though it is probably mostly useful as an intermediate step.  While it similarly enables you to call the module with a simple commandline,
 all jobs are executed on the same node, and the scatter jobs are run sequentially.  For better throughput you would want to specify scatter-gather in the WDL workflow so that multiple nodes can be used. 
 At some point in the future this utility will probably be enhanced to generate such WDL for you.


To use run_module.py, you copy code from Firehose verbatim, eg unpack the zip file you get from exporting the Firehose task.  This directory is then passed in as the module_libdir argument.
All the other arguments are the ones from the manifest, using the names visible to the user in Firehose.  All parameters are treated as if they were labeled optional, regardless of what the manifest says.

Below is an example showing how the commandline is generated for running the ContEst module. 

```
module_libdir = os.path.join(module_dir,'contest')
cmdStr = os.path.join(adaptor_dir,'run_module.py') 
cmdStr += ' --module_libdir ' + module_libdir + ' ' 

cmdStr += ' '.join(['--reference.file', os.path.join(refdata_dir,'public','human_g1k_v37_decoy.fasta'), 
                    '--intervals', os.path.join(refdata_dir,'public','gaf_20111020+broad_wex_1.1_hg19.bed'), 
                    '--sample.id', os.path.basename(bam_tumor), 
                    '--clean.bam.file', bam_tumor, 
                    '--normal.bam',bam_normal, 
                    '--genotypes.vcf none', 
                    '--pop.vcf', os.path.join(refdata_dir,'protected','hg19_population_stratified_af_hapmap_3.3.fixed.vcf'), 
                    '--force.array.free true',
                    '--snp.six.bed', os.path.join(refdata_dir,'public','SNP6.hg19.interval_list'),
                    '--job.spec.memory','2', '--tmp.dir', tmp_dir #TBD job spec memory was 2; manifest also changed.
                    ])
```

### Generating the commandline for scatter-gather jobs

local_scatter_gather.py can be used for scatter-gather jobs, though it is probably mostly useful as an intermediate initial step.  While it similarly enables you to run the module with a simple commandline, 
all jobs are executed on the same node, and the scatter jobs are run sequentially.  
 
For better throughput you would want to specify scatter-gather in the WDL workflow so that multiple nodes can be used.  

At some point in the future this utility will probably be enhanced to generate such WDL for you.
run_sg_prepare.py, run_sg_scatter.py, and run_sg_gather.py are utilities written assuming the outputs live under a common root directory.  They will likely be tweaked as part of this future enhancement.

### Using the Pipette scheduler
algutil/pipette_server contains a scheduler that can keep the cores busy on a single VM.


## Future plans

#### gce
suspend
idle vm detection/notification
migrate to different sized vm
budget setting/notifications

#### install
x11, vnc
vpn
matlab interactive
gcs-fuse
openssl
rsub

#### crom
multi-task workflow support
move to inline python for wdl command script


#### Firecloud management
