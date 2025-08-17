#!/bin/bash
#
# Process per-user score files and send each, as e-mail, to the associated student.
#
# NOTES:
#	this script correctly handles multiple comma-separated 
#	submitters on a single EMAIL: line
#
#	the script tries to identify obviously bogus score files
#	(e.g. that have no total or email address) and will not
#	try to send messages for them, but it is best to run the
#	script with the "--test" option and clean up any garbage
#	before the final run.
#
#	the --test option looks over the files and makes sure they
#	seem correct and complete, but does not actually send email.
#
#	the --fixok option tells the program it is OK to send out
#	scores that still have FIX lines in them ... which they
#	should not.
#
USAGE="$0 [--test] [--fixok] score-file ..."

NAMEFILE=./course_title
DEBUG=0

# see if we are only testing for presence of all information
if [ -n "$1" -a "$1" == "--test" ]; then
	let testing=1
	shift
else
	let testing=0
fi

# see if we are checking for FIX lines
if [ -n "$1" -a "$1" == "--fixok" ]; then
	let checkfixes=0
	shift
else
	let checkfixes=1
fi

# figure out the course name
if [ -s $NAMEFILE ]; then
    COURSE=`cat $NAMEFILE`
else
    >& 2 echo "Course: unspecified, please create $NAMEFILE"
    COURSE='CS???'
fi

let errors=0
# sendMail address assignment scorefile comment
function sendMail {
	ats=`echo $1 | grep '@' | wc -l`
	if [ $ats -eq 1 ]; then
		# if they wanted to see the detailed command
		if [ $DEBUG -eq 1 ]; then
		    echo "mutt -s \"$2\" $1 < $3"
		fi
		echo -e -n "   $3 ($4) \t -> $1 ... " 
		if [ $testing -eq 0 ]; then
			mutt -s "$2" $1 < $3
			ret=$?
			if [ $ret -eq 0 ]; then
				echo "OK"
			else
				echo "mutt returns $ret"
			fi
		else
			echo "READY"
		fi
	else
		>& 2 echo "ERROR - $3: INVALID EMAIL ADDRESS ($1)"
		let errors+=1
	fi
}

# iterate through all specified files
while [ -n "$1" ]; do
	if [ ! -s $1 ]; then
		>& 2 echo "    $1 ... UNABLE TO OPEN"
		let errors+=1
	else 
		# some people edit their files on Windows!!!
		tr '\r' '\n' < $1 > /tmp/$$

		# pull some interesting information out of the assignment
		EMAIL=`grep -i "EMAIL:" /tmp/$$ | grep -v "missing" | cut -s -d: -f2 | tr -d \[:blank:\]`
		TOTAL=`grep -i "total score:" /tmp/$$ | cut -s -d: -f2 | tr -d \[:blank:\]`
		ASSGT=`grep -i "ASSIGNMENT:" /tmp/$$ | cut -s -d: -f2 | xargs | cut -d\  -f1`

		# see if there are any FIX tags left in the file
		if [ $checkfixes -ne 0 ]; then
			grep "FIX" /tmp/$$ > /dev/null
			if [ $? -ne 0 ]; then
				let fixes=0
			else
				let fixes=1
			fi
		else
			let fixes=0
		fi

		# make sure we have enough information
		if [ -z "$EMAIL" ]; then
			>& 2 echo "ERROR - $1: CONTAINS NO EMAIL ADDRESS"
			let errors+=1
		elif [ -z "$TOTAL" ]; then
			>& 2 echo "ERROR - $1: CONTAINS NO TOTAL SCORE"
			let errors+=1
		elif [ $fixes -ne 0 ]; then
			>& 2 echo "ERROR - $1: CONTAINS 'FIX'es"
			let errors+=1
		else
			# see if the EMAIL field contains multiple addresses
			email=`echo $EMAIL | cut -s -d, -f1`
			if [ -n "$email" ]; then
				field=1
				while [ -n "$email" ]; do
					sendMail $email "$COURSE: $ASSGT" $1 $TOTAL
					let field+=1
					email=`echo $EMAIL | cut -d, -f$field`
				done
			else
				sendMail $EMAIL "$COURSE: $ASSGT" $1 $TOTAL
			fi
		fi

		rm -f /tmp/$$
	fi
	shift
done

if [ $errors -eq 0 ]; then
	exit 0
else
	exit 1
fi
