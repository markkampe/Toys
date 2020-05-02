BASE_CLASSES = gameobject.py gameactor.py gameaction.py gamecontext.py dice.py
SUB_CLASSES = interaction.py skills.py weapon.py npc_guard.py
PROGRAMS = test.py
ALL = $(BASE_CLASSES) $(SUB_CLASSES) $(PROGRAMS)

test:
	python3 test.py

all_test:
	python3 dice.py
	@echo
	python3 gameobject.py
	@echo
	python3 test.py

doc:
	epydoc -v --graph=umlclasstree $(ALL)
	@echo PyDocumentation can be found in html subdirectory

DISABLES= --disable=duplicate-code
lint:
	pylint $(DISABLES) $(ALL)
	pep8 $(ALL)

clean:
	-rm -f *.pyc
	-rm -f __pycache__/*
	-rm -rf html

