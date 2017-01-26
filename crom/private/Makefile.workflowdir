include ../Makefile.inc
help: default
	@echo 
	@echo "3. template FLOW=<_workflow_name>    create a template workflow"

FLOW=template

template:
	@if [[ "$(FLOW)" =~ ^[a-z_][a-z0-9_]*$$ ]]; then \
		echo "Creating workflow folder for: $(FLOW)" ; \
		../bin/template_generator.py -w $(FLOW); \
	else \
		echo "Missing or invalid workflow name, workflow names must contain" ; \
		echo "only lowercase letters or underscores, and begin with a letter" ;\
	fi
