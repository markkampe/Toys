BASE_CLASSES = base.py gameobject.py gameactor.py gameaction.py gamecontext.py dice.py
SUB_CLASSES = interaction.py weapon.py npc_guard.py
PROGRAMS = test.py
ALL = $(BASE_CLASSES) $(SUB_CLASSES) $(PROGRAMS)

test:
	python3 test.py

all:
	@echo Dice:
	python3 dice.py
	@echo
	@echo Base:
	python3 base.py
	@echo
	@echo GameObject:
	python3 gameobject.py
	@echo
	@echo GameAction:
	python3 gameaction.py
	@echo
	@echo Weapon.py:
	python3 weapon.py
	@echo
	@echo GameActor:
	python3 gameactor.py
	@echo
	@echo Full scenario
	python3 test.py

doc:
	epydoc -v --graph=umlclasstree $(ALL)
	@echo PyDocumentation can be found in html subdirectory

DISABLES= --disable=duplicate-code --disable=fixme
lint:
	pylint3 $(DISABLES) $(ALL)
	pep8 $(ALL)

clean:
	-rm -f *.pyc
	-rm -f __pycache__/*
	-rm -rf html

