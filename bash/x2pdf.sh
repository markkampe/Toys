#!/bin/bash
#
# Turn an ASCII text exam submission into a pdf for up-load to Gradescope.
#
# input file should one question per page, ASCII text exam submission
#    likely obtained by going to Sakai Dropbox, going to submission,
#    and right-clicking Download-Link
#
# usage:	x2pdf input_file output_basename
#	e.g. x2pdf x1.txt markk
#	create markk.pdf from x1.txt
#
if [ ! -r $1 ]
then
	echo "ERROR: input file $1 does not exist" >& 2
	exit 1
fi

if [ -z "$2" ]
then
	echo "usage: $0 input-file student-name" >& 2
	exit 1
fi

echo " ... Converting $1 to $2.ps"
enscript -B -L70 --margins=::0:0 -o $2.ps $1 2>stderr
if [ $? -eq 0 ]
then
	sed -e "s/^/     /" < stderr
	echo " ... Converting $2.ps to $2.pdf"
	ps2pdf $2.ps $2.pdf
	if [ $? -eq 0 ]
	then
		rm -f stderr $2.ps
		exit 0
	else
		cat stderr
		exit 1
	fi
else
	exit 1
fi
