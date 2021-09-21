#!/bin/bash
#
#   convert ASCII text to pdf and print it
#
LINES=70

while [ -n "$1" ]
do
    enscript -B -L$LINES --margins=::0:0 -o /tmp/$$.ps $1 2>/tmp/stderr
    if [ $? -eq 0 ]
    then
	ps2pdf /tmp/$$.ps /tmp/$$.pdf
	lp /tmp/$$.pdf
	rm /tmp/$$.ps /tmp/$$.pdf
    else
    	cat stderr
	rm /tmp/$$.ps
	exit 1
    fi
    shift
done
