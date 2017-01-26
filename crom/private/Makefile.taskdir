include ../Makefile.inc

help: default
	@echo 
	@echo "You can also build and push specific images by name with:"
	@echo "make <task_name>"
	@echo "make push_<task_name>"
	@echo
	@echo "List available packages with 'make list'"


TASK=template

template:
	@if [[ "$(TASK)" =~ ^[a-z_][a-z0-9_]*$$ ]]; then \
		echo "Creating task folder for:  $(TASK)" ; \
		${TOOLS}/template_generator.py -t $(TASK); \
	else echo "Invalid task name, folders must be in lowercase separated by underscores, beginning with a letter"; \
	fi;




list:
	@$(MAKE) pretty_print LIST="$(GDAC_IMAGES)"

#TODO: Make this an automated lookup?
GDAC_IMAGES=\
	cnmf_report \
	cnmf_select_cluster \
	nmf_consensus_clustering \
	top_genes_for_cluster 

#Build an individual image
$(GDAC_IMAGES):
	@cd $@ && \
		$(MAKE) image

PUSH_IMAGES=$(GDAC_IMAGES:%=push_%)

$(PUSH_IMAGES):
	@IMGNAME=`echo $@ | sed 's/^push_//'` && \
		cd $$IMGNAME && $(MAKE) push


.PHONY: help $(GDAC_IMAGES) $(PUSH_IMAGES) list template

pretty_print:
	@for thing in $(LIST) ; do \
		printf "\t$$thing\n" ; \
	done
