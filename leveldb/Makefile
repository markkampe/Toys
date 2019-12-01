#
# these are simple C and C++ test programs to prove that I
# know how to write code that uses leveldb.
#

# packages: libleveldb-dev and libsnappy-dev
LIBS=-lleveldb -lpthread -lsnappy

PGMS=cpp_test c_test

OBJS=cpp_test.o c_test.o

DBASE=leveldb_dir

all:	$(PGMS)

clean:
	rm -f $(OBJS)

clobber:
	rm -f $(PGMS) $(OBJS)
	rm -rf $(DBASE)

cpp_test: cpp_test.cpp
	gcc -o $@ $< $(LIBS)

c_test: c_test.c
	gcc -o $@ $< $(LIBS)
