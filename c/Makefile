ALL=colsum choose check_access lptest roll xterm-title interpose.o
DFLT=colsum
CFLAGS= -Dwall -Dextra

default: $(DFLT)

all:	$(ALL)

clean:
	rm -f $(ALL)

choose: choose.c
	gcc -o $@ $(CFLAGS) $<

check_access: check_access.c

colsum: colsum.c

lptest: lptest.c

roll: roll.c

# for testing system call interception
interpose.o: interpose.c
	gcc -c $(CFLAGS) $<

# was playing on MacOS
#key_lookup: key_lookup.c
#	gcc -o $@ $< -lkeyutils

