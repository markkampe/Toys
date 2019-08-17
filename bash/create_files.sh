#!/bin/bash

#
# create a tree full of files that can be used to verify access
# checking behavior.
#
# You will want to change TEST_DIR to be on the file system to be tested.
# You might want to change TEST_PGM to be a fully qualified file name
#

# program that can be executed for testing purposes
TEST_PGM=./check_access

# directory under which all of this testing should take place
TEST_DIR="/tmp/wherever"

if [ -d $TEST_DIR ]
then
	echo cleaning previous $TEST_DIR
	rm -rf $TEST_DIR/*
else
	echo "creating $TEST_DIR"
	mkdir $TEST_DIR
	chmod 777 $TEST_DIR
fi

MANIFEST="$TEST_DIR/Manifest"
echo $TEST_DIR > $MANIFEST

# figure out who is going to own these files
MY_UID=`id -u`
MY_GID=`id -g`

# create top level directories with a range of accesses
for dirmode in 500 700 750 770 775 777
do
    dirname=$TEST_DIR/UID_"$MY_UID"_GID_"$MY_GID"_MODE_"$dirmode"
    mkdir $dirname
    echo $dirname >> $MANIFEST

    # create files with a range of accesses
    for filemode in 400 500 700 740 750 770 744 755 777
    do
    	filename=UID_"$MY_UID"_GID_"$MY_GID"_MODE_"$filemode"
	cp $TEST_PGM $dirname/$filename
	chmod $filemode $dirname/$filename
	echo $dirname/$filename >> $MANIFEST
    done

    # we chmod at the end, because some are not me-writeable
    chmod $dirmode $dirname
done
