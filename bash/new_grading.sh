#!/bin/bash
#  usage: new_grading.sh {os,swe}
#  create a new grading directory

DIR="$HOME/Grading"

# Harvey Mudd course numbers
CRS_SWE="CS181AA"
CRS_OS="CS134"

# locations of repos for source files
GIT_SWE="/home/git/Big-Software"
GIT_TOY="/home/git/Toys"
GIT_OS="FIXME"
WIP="/home/markk/WIP"

# get the course name
if [ -n "$1" -a "$1" = "os" ]
then
    course="$CRS_OS"
    repo="$GIT_OS"
elif [ -n "$1" -a "$1" = "swe" ]
then
    course="$CRS_SWE"
    repo="$GIT_SWE"
else
    echo "Usage: new_grading.sh course" >&2
    echo "       where course is 'os' or 'swe'" >&2
    exit 1
fi

# top level directory creation
if [ -d $DIR ]
then
    echo "... updating existing $DIR for $course"
    rm -f $DIR/Rubric $DIR/grademail.sh $DIR/perteam.sh $DIR/peruser.sh $DIR/scorefiles.sh
    rm -f $DIR/slip_days $DIR/teams.csv
    rm -f $DIR/x2pdf.sh
else
    echo "... creating new $DIR" for "$course"
    mkdir $DIR
fi

if [ -d "$DIR/scores" ]
then
    echo "... deleting contents of existing $DIR/scores"
    rm -f $DIR/scores/*
else
    echo "... creating new $DIR/scores"
    mkdir $DIR/scores
fi

echo $course > $DIR/course_title

# create links to grading scripts
if [ $course = $CRS_SWE ]
then
	echo "... creating links to SWE project grading scripts"
	ln -s $GIT_SWE/projects/Rubric $DIR/Rubric
	ln -s $GIT_SWE/projects/Rubric/grademail.sh $DIR
	ln -s $GIT_SWE/projects/Rubric/perteam.sh $DIR
	ln -s $GIT_SWE/projects/Rubric/peruser.sh $DIR
	ln -s $GIT_SWE/projects/Rubric/scorefiles.sh $DIR
	ln -s $GIT_TOY/bash/x2pdf.sh $DIR
	if [ -r "$WIP/slip_days" ]
	then
		ln -s "$WIP/slip_days" $DIR
	fi
	if [ -r "$WIP/teams.csv" ]
	then
		ln -s "$WIP/teams.csv" $DIR
	fi
elif [ $course = $CRS_OS ]
then
	echo "... OS grading directory creation not yet automated"
	ln -s $GIT_TOY/bash/x2pdf.sh $DIR
fi

# show what we've done
ls -l $DIR
