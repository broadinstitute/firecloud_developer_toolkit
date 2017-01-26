
# Makefile.inc: common definitions for gdac-firecloud Makefiles

##################################################
# Variables and Globals
##################################################
SHELL=/bin/bash

# TBD - should CUR_DIR be set to $FDT_CURRENT_ALG_ROOT?
CUR_DIR=$(shell pwd)
FOLDER=$(shell echo $${PWD\#\#*/})

TOOLS=$(FDT_ROOT)/crom/private
#LOCAL_BIN holds cromwell, wdltool, gsutil, etc.  For installs not requiring root.
LOCAL_BIN=$(FDT_BIN_ROOT)


#Locations of tools/files
CROMWELLJAR=$(LOCAL_BIN)/cromwell.jar
WDLTOOLJAR=$(LOCAL_BIN)/wdltool.jar
#


# these filenames are in sync with template_generator.py
TASKDEF=$(CUR_DIR)/taskdef.$(FOLDER).wdl
README=$(CUR_DIR)/README.$(FOLDER).md
DOCKERFILE=$(CUR_DIR)/docker.$(FOLDER).txt
SOURCEFILES=$(CUR_DIR)/sourcefiles.$(FOLDER).list
INPUTTEST=$(CUR_DIR)/inputtest.$(FOLDER).json

LOCALIZEDINPUTSDIR=$(CUR_DIR)/localized_inputs
OUTPUTDIR=$(CUR_DIR)/cromwell-executions
BUILDDIR=$(CUR_DIR)/build
CP_LOG=$(BUILDDIR)/cplog.txt

DOCKER_IMAGE_USERTAG=`${TOOLS}/extract_docker_name_from_wdl.py usertag ${TASKDEF}`
DOCKER_IMAGE_BASE=`${TOOLS}/extract_docker_name_from_wdl.py base ${TASKDEF}`


SYNC_FILE=$(CUR_DIR)/SYNC_TASKS

#Firecloud configurations
FIRECLOUD_API_URL=https://api.firecloud.org/api

TIMESTAMP=$(shell echo `date +'%Y-%m-%d__%H-%M-%S'`)


##################################################
# Help targets
##################################################


default:
	@echo "Make targets to simplify docker machine creation"
	@echo
	@echo "1. host                       Start the docker host VM."
	@echo "                              Creates a new VM if one doesn't exist"
	@echo
	@echo "2. stop                       Shuts down the docker host VM."
	@echo
	@if [ -s $(CUR_DIR)/Dockerfile ]; then \
		echo ; \
		echo This folder also contains a Dockerfile, and supports these additional commands: ; \
		echo ;\
		$(MAKE) image_help ;\
	fi;

image_help:
	@echo "1. build                      Build image from Dockerfile in this folder"
	@echo
	@echo "2. pushimage, pushwdl         Push image to Docker HUB and taskdef to Firecloud."
	@echo "                              Dockerhub namespace, image name, and version are extracted from WDL"
	@echo "                              Firecloud namespace and method name are set in task's own Makefile"

	@echo 
	@echo "3. runbash                    Run image interactively with bash"
	@echo
	@echo "3a. attach                    Attach a new bash shell to the (single) currently running container."
	@echo

	@echo "4. validatewdl                Validate workflow in this folder with cromwell"
	@echo 
	@echo "5. createinputtest            Create an inputs.json file for the workflow"
	@echo
	@echo "6. runcromwell                Run the workflow locally with cromwell."
	@echo "                              Uses $(TASKDEF) as input to the workflow."
	@echo "                              Runs asynchronously, halt via make killrun."
	@echo
	@echo "7. runcromwellfg              Like runcromwell but synchronous."
	@echo "                              Uses $(TASKDEF) as input to the workflow."
	@echo
	@echo "8. killrun                    Halts a cromwell run that was started via make run."
	@echo
	@echo "9. clearoutputs               Deletes the output of previous runs."
	@echo



#cl
#ad



##########################
# GCE Setup
##########################
#TBD - move these to gce folder
#login:
#	gcloud init
#	docker login

#setup:
#	@# TODO make this path more general
#	echo 'export PATH=${TOOLS}:$$PATH' >> ~/.bashrc
#	@# todo setup firecloud-cli for the user
#
#	@# add user to the docker group
#	@sudo gpasswd -a ${USER} docker
#	@sudo service docker restart

#expand:
#	sudo resize2fs /dev/disk/by-id/google-persistent-disk-1
#	df -h | grep /dev/sdb




##################################################
# Error Checking / Validation
##################################################

task_check:
	@cd .. && \
	if [ "$${PWD##*/}" != "tasks" ]; then \
		echo Error: this action is only available in a task folder; exit 1; \
	fi;

workflow_check:
	@cd .. && \
	if [ "$${PWD##*/}" != "workflows" ]; then \
		echo Error: this action is only available in a workflow folder; exit 1; \
	fi;


dockerfile_check:
	@if [ ! -s $(DOCKERFILE) ]; then \
		echo Error: No docker.method.txt in this folder ; exit 1 ; \
	fi;

wdl_check:
	@if [ ! -s $(TASKDEF) ]; then \
		echo Error: WDL misnamed or not found in this folder ; exit 1 ; \
	fi; 

sync_check:
	@if [ ! -s $(SYNC_TASKS) ]; then \
		echo Error: No SYNC_TASKS file in this folder ; exit 1 ; \
	fi; 

fissfc_check:
	@if [ -z `which fissfc` ]; then \
		echo "FISSFC not installed, installing latest version with pip..."; \
		pip install fissfc; \
	fi;

version_check:
	@if [ -z $(DOCKER_IMAGE_BASE) ]; then \
		echo "wdl file needs a single, properly formatted docker line"; exit 1; \
	fi;

check: wdl_check dockerfile_check version_check

stage_build: sourcefiles.${FOLDER}.list dockerfile_check  task_check
	@# create BUILDDIR, and copy the sourcecode and Dockerfile into it.
	@rm -rf ${BUILDDIR}
	@mkdir ${BUILDDIR}

	@touch $(CP_LOG)

	@# if destinations are directories, they should end with / for more consistency during the copy
	@# note filenames and directories should not include spaces
	@echo "Localizing files in sourcefiles.method.list to ./build via hard link"; \
	IFS=$$'\t'; \
	tail -n +2 $(SOURCEFILES) | while read SRC DEST; do \
		mkdir -p `dirname $$DEST` ;  \
		if [ `echo -n $$DEST | tail -c 1` == "/" ]; then \
			mkdir -p $$DEST; \
		fi;\
		cp -r -v -l $$SRC $$DEST >> $(CP_LOG); \
	done;
	@cp $(DOCKERFILE) $(BUILDDIR)/Dockerfile

##################################################
# Docker Images
##################################################

build: stage_build version_check

	@#Build the docker image from sources in the ${BUILDDIR} directory
	@docker build -t ${DOCKER_IMAGE_BASE}:${DOCKER_IMAGE_USERTAG} ${BUILDDIR}
	@docker images

buildclean: stage_build version_check

	@#Build the docker image from sources in the ${BUILDDIR} directory
	@docker build --no-cache -t ${DOCKER_IMAGE_BASE}:${DOCKER_IMAGE_USERTAG} ${BUILDDIR}
	@docker images

pushimage: task_check
	docker push ${DOCKER_IMAGE_BASE}:${DOCKER_IMAGE_USERTAG}

pullimage: task_check
	docker pull ${DOCKER_IMAGE_BASE}:${DOCKER_IMAGE_USERTAG}

runbashisolated: dockerfile_check version_check task_check
	docker run --rm -it --name test_container ${DOCKER_IMAGE_BASE}:${DOCKER_IMAGE_USERTAG}  /bin/bash

runbash: dockerfile_check version_check task_check
	docker run --rm -it -v /opt/execution:/opt/execution -v /opt/inputs:/opt/inputs --name test_container ${DOCKER_IMAGE_BASE}:${DOCKER_IMAGE_USERTAG} /bin/bash

attach:
	docker exec -it $(shell ${TOOLS}/active_docker.py) /bin/bash

##################################################
# WDL Authoring and Testing
##################################################

validatewdl: wdl_check
	@java -jar $(WDLTOOLJAR) validate $(TASKDEF)

createinputtest: wdl_check
	java -jar $(WDLTOOLJAR) inputs $(TASKDEF) 1>$(INPUTTEST).template

localizeinputs:
	$(TOOLS)/localize_inputs.py $(INPUTTEST) $(LOCALIZEDINPUTSDIR)/localized_inputs.$(FOLDER).json $(LOCALIZEDINPUTSDIR)

#TBD - perhaps move the cromwell_test_config.json to the new repo
#wdl_check
runcromwell: validatewdl localizeinputs
	@mkdir -p ${OUTPUTDIR}
	#
	# Running asynchronously with &.  Things will keep running if the ssh connection timeouts, but ctrl-c won't work.  Kill via:
	# make kill_run
	#
	java -jar $(CROMWELLJAR) run $(TASKDEF) $(LOCALIZEDINPUTSDIR)/localized_inputs.$(FOLDER).json  $(TOOLS)/cromwell_test_config.json ${OUTPUTDIR}/run_metadata__${TIMESTAMP}.json &
	sleep 15
	# link to the most recent run, which will be the one just started if it did not fail right away.
	#TBD force it to link to the run just launched
	if [ -n $(indir) ]; then \
	    sudo mkdir -p /opt; \
	    sudo rm -f /opt/src; \
	    sudo ln -s `algdir`/build/src /opt/src; \
	    sudo rm -f /opt/inputs; \
	    sudo ln -s `indir` /opt/inputs; \
	    sudo rm -f /opt/execution;\
	    sudo ln -s `indir`/../execution /opt/execution; \
	fi

killrun:
	@#ps -ef | egrep [c]romwell | cut -f 2 -d ' ' | xargs kill -9
	@killall -9 cromwell
	@docker kill $(shell ${TOOLS}/active_docker.py)

runcromwellfg: validatewdl localize_inputs
	@mkdir -p ${OUTPUTDIR}
	#
	# Running synchronously, without &.  You can kill via ctrl-c, but you need to worry about ssh timeouts
	#
	java -jar $(CROMWELLJAR) run $(TASKDEF) $(LOCALIZEDINPUTSDIR)/localized_inputs.$(FOLDER).json  $(TOOLS)/cromwell_test_config.json ${OUTPUTDIR}/run_metadata__${TIMESTAMP}.json

clearoutputs:
	sudo rm -rf ${OUTPUTDIR}

pushwdl: wdl_check fissfc_check
	@#FIRECLOUD_WDL_DOMAIN and FIRECLOUD_WDL_METHOD_NAME are defined in the task specific Makefile.
	fissfc -u $(FIRECLOUD_API_URL) flow_new  -d $(README) $(FIRECLOUD_WDL_DOMAIN) $(FIRECLOUD_WDL_METHOD_NAME) $(TASKDEF) $(FOLDER); \


sync: workflow_check wdl_check sync_check
	@python sync_tasks.py $(WDL) -s $(SYNC_FILE)

## Push both docker image and wdl
#push: pushimage pushwdl



.PHONY: host stop image common workflow_check task_check sync version_check test

clean:
	\rm -f *~
