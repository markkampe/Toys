ALL=colsum choose check_access icalc linecount lptest roll xterm-title unixtime interpose.o
DFLT=colsum icalc linecount roll unixtime
CFLAGS= -Dwall -Dextra

default: $(DFLT)

all:	$(ALL)

clean:
	rm -f $(ALL)

choose: choose.c
	gcc -o $@ $(CFLAGS) $<

check_access: check_access.c

colsum: colsum.c

icalc: icalc.c

linecount: linecount.c

lptest: lptest.c

roll: roll.c

unixtime: unixtime.c

# for testing system call interception
interpose.o: interpose.c
	gcc -c $(CFLAGS) $<

# was playing on MacOS
#key_lookup: key_lookup.c
#	gcc -o $@ $< -lkeyutils

