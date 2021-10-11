#!/bin/bash
#
# put up (or take down) an exam
#
CLASSES="/home/infosys/www/courses"
CLASS="2021/fall/cs181aa"

# see if this is a put-up or a take-down
if [ -n "$1" -a "$1" = "-d" ]
then
    mode="down"
    shift
else
    mode="up"
fi

# make sure the argument is valid
if [ -z "$1" ]
then
    echo "Usage: $0 [-d] exam" >&2
    exit -1
else
    exam="$CLASSES"/"$CLASS"/exams/"$1"
    if [ ! -r $exam.txt ]
	then
        echo "NO SUCH FILE: $exam.txt" >&2
	exit -1
    fi
fi

if [ "$mode" = "up" ]
then
    if [ ! -r $exam.EXAM ]
    then
    	echo "NO SUCH FILE: $exam.EXAM" >&2
        exit -1
    else
	# replace the dummy with the real exam, make it readable
    	mv $exam.txt $exam.DUMMY
	mv $exam.EXAM $exam.txt
	chmod 644 $exam.txt
    	ls -l $exam.*
    fi
else
    if [ -r $exam.EXAM ]
    then
        echo "ERROR: $exam.EXAM already exists" >&2
	exit 1
    else
	# read-protect the real exam and restore the dummy
    	mv $exam.txt $exam.EXAM
	chmod 600 $exam.EXAM
    	if [ -r $exam.DUMMY ]
	then
	    mv $exam.DUMMY $exam.txt
	else
	    echo "WARNING: no $exam.DUMMY"
	fi
    	ls -l $exam.*
    fi
fi
