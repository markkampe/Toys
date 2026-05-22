# most of these were one-time, but a few are of ongoing use
APPS = glucose logdump quiz

.PHONY: lint $(APPS)

lint: $(APPS)

# this rule will be invoked for each element of APPS
$(APPS):
	pylint $@.py
	pycodestyle $@.py
