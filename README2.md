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

This framework assumes 1) you have sudo privileges that do not require a password re-prompt, 2) you are in the docker group,  3) you will be using the /opt directory for your development work, and 4) you are using a Linux rather than a BSD/Mac system.  These assumptions are consistent with the Google VM setup above.


#### Create repo


#### Create task

###### Simple task

###### Workflow

###### Best practices


#### Run task


#### Debug task







