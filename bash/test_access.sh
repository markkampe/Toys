#!/bin/bash

#
# create a tree full of test files to determine whether or not we
# have the correct access to each of them.
#
# Run create_files.sh to create a test hierarchy
#
# Make sure that TEST_PGM and TEST_DIR agree with the values in create_files.sh
#
# Then run this script five different ways:
#   1. as the user who ran create_files.sh
#   2. as a different user in the same group as the user who ran create_files.sh
#   3. as a different user not the same group as the user who ran create_files.sh
#
#   4. chmod 4755 check_access
#      run as a different user not the same group as the user who ran create_files.sh
#
#   5. chmod 2755 check_access
#      run as a different user not the same group as the user who ran create_files.sh
#

# program that can be executed for testing purposes
TEST_PGM=./check_access
if [ ! -x $TEST_PGM ]
then
	echo "ERROR: test program $TEST_PGM does not exist"
	exit -1
fi

# directory under which all of this testing should take place
TEST_DIR="/tmp/wherever"
if [ ! -d $TEST_DIR ]
then
	echo "ERROR: test directory $TEST_DIR does not exist"
	exit -1
fi

MANIFEST="$TEST_DIR/Manifest"
if [ ! -f $MANIFEST ]
then
	echo "ERROR: test Manifest $MANIFEST  does not exist"
	exit -1
fi

# check access to every file in the manifest
function process {
	while read -r line
	do
		$TEST_PGM -v $line
	done
}

process < $MANIFEST
