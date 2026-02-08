# most of these were one-time, but a few are of ongoing use
APPS = glucose logdump

.PHONY: lint $(APPS)

lint: $(APPS)

# this rule will be invoked for each element of APPS
$(APPS):
	pylint $@.py
	pycodestyle $@.py
