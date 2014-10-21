#!/usr/bin/perl
#
# script: walker
#	
# purpose:
#	program skeleton to walk a tree of directories and files
#

#
# enabling compulsive error checking finds a great many errors
#
use warnings;
use strict;
use Carp;

#
# a few standard services
#
use Getopt::Std;
use File::Basename;
use Time::Local;

my $PGM = "walker.pl";
sub usage()
{	
	print STDERR "Usage: $PGM [switches] [file ...] [dir ...]\n";
	print STDERR "       -v    ... verbose output\n";
	print STDERR "       -n    ... notouch (just see what it would do)\n";
	print STDERR "	     -s xxx .. process only files w/suffix xxx\n";
}

# parameters 
my @suffixes = ( "mp3", "wma", "m4a" );
my $verbose  = 0;
my $notouch = 0;

# problem counters
my $errors   = 0;
my $warnings = 0;

# exit codes
my $OK  	= 0;
my $WARN	= 1;
my $FATAL	= 2;

#
# collected statistics
#
my $num_files	= 0;	# total number of files processed
my $num_dirs	= 0;	# total number of directories processed

#
# routine:	leader
#
# purpose:	to print out a leader, appropriate for a depth
#
# parameters:	depth (>=0)
#
sub leader
{	(my $depth) = ($_[0]);
	for ( my $i = 0; $i < $depth; $i ++ ) {
		print STDOUT "...";
	}
}

#
# routine:	good_suffix
#
# purpose:	determine whether or not a file has a suffix we are interested in
#
# parameter:	suffix to be examined
#
# returns:	true/false
#
sub good_suffix
{	(my $suf) = ($_[0]);

	my $numsuf = scalar @suffixes;
	for ( my $i = 0; $i < $numsuf; $i++ ) {
		if ($suf eq $suffixes[$i]) {
			return( 1 );
		}
	}

	return( 0 );
}

sub do_process
{	my ($dir, $base, $suf) = ($_[0], $_[1], $_[2]);

	# do what ever it is you would want to do with this file }

	return( 1 );
}

#
# routine:	process_file
#
# purpose:
#	process one (suspected) log file
#
# parameters:
#	fully qualified path to directory
#	name of this file within that directory
#	depth (relative to command line args = 0)
#
# returns:
#	true ... this was an interesting file
#	false .. this was not an interesting file
#
sub process_file
{	(my $dirname, my $filename, my $depth) = ( $_[0], $_[1], $_[2] );

	# does this file have an interesting suffix
	if ($filename =~ /(.+)\.(.+)/) {
		my $base = $1;
		my $suffix = $2;

		if (!good_suffix( $2 )) {
			return( 0 );
		}

		if ($verbose) {
			leader( $depth );
			print STDOUT " processing $suffix file \'$base\'\n";
		}

		my $ret = 1;
		if (! $notouch) {
			$ret = do_process( $dirname, $base, $suffix );
		}
		return( $ret );
	} 
	# no suffix -> uninteresting
	return( 0 );
}

#
# routine:	process_dir
#
# purpose:
#	process all the files in this directory
#	then walk all of its sub-directories
#	(recursive pre-order traversal)
#	
# parameters:
#	fully qualified path to directory
#	depth (relative to command line args = 0)
#	
#	
# NOTES on sub-tree walk
#	1. to run on both Windows and Linux, I am using glob() rather
#	   than `ls` to get a list of file names.
#	2. to get a clean list of file names, I chdir into each directory
#	   before calling glob.
# 	3. this means that once I start recursing, I must assume that my
#	   subdir has changed.
#	4. I specifically do not follow symbolic links to directories
#	   as these can lead to loops and other unpleasant surprises
#
sub process_dir 
{	(my $dirname, my $depth) = ( $_[0], $_[1] );
	my $numsub = 0;		# processed subdirectories
	my $subfiles = 0;	# files actually processed
	my $subtotfiles = 0;	# total files found
	
	# print out a processing header for this directory
	if ($verbose) {
		leader( $depth );
		print STDOUT " processing directory \'$dirname\'\n";
	}
	
	# get a list of everything in this directory
	chdir( $dirname );
	my @names = glob( '*' );
	my $numnames = scalar @names;
	if ($numnames == 0) {
		if ($verbose) {
			leader( $depth );
			print STDOUT " directory $dirname is empty\n";
		}
		return
	}

	# pass I: process all files in this directory
	for ( my $i = 0; $i < $numnames; $i++ ) {
		my $filename = $names[$i];
		if ( -f $filename ) {
			if ( process_file( $dirname, $filename, $depth+1 ) ) {
				$subfiles++;
			}
			$subtotfiles++;
			$num_files++;
		}
	}

	# pass II: process all sub-directories this directory
	for ( my $i = 0; $i < $numnames; $i++ ) {
		my $subdir = "$dirname/$names[$i]";	# TRICK: fully-qualified name
		if ( -d $subdir && ! -l $subdir) {
			process_dir( $subdir, $depth+1 );
			$numsub++;
		}
	}
	
	# print out a processing summary for this directory
	if ($verbose) {
		leader( $depth );
		print STDOUT " processed $numsub subdirs, $subfiles/$subtotfiles files\n";
	}

	$num_dirs++;
}

# routine:	main
#
# purpose:	argument processing
#		drive main loop
#
sub main
{	
	# parse the simple imput switches
	my %options = ();
	if (!getopts('vns:', \%options)) {
		usage();
		exit($FATAL);
	}

	if (defined( $options{v} )) {
		$verbose = 1;
	}

	if (defined( $options{n} )) {
		$notouch = 1;
	}

	if (defined( $options{s} )) {
		# override the default suffix
		@suffixes = split(/,/, $options{s} );

		print STDERR "(processing only files w/suffix(es) @suffixes)\n";
	}

	# make sure we have some  names
	my $argc = @ARGV;
	if ($argc < 1) {
		print STDERR "Error: no file or directory names specified\n";
		usage();
		exit($FATAL);
	}

	# process each specified file or directory
	while( $argc-- > 0 ) {
		my $nextname = shift @ARGV;
		if ( -d $nextname ) {
			process_dir( $nextname, 0 );
		} else {
			process_file( $nextname, 0 );
		}
		shift;
	}

	if ($verbose) {
		print STDOUT "\nProcessed $num_files files and $num_dirs directories\n";
	}

	# program exit code is determined by how well things went
	if ($errors) {
		exit( $FATAL );
	} elsif ($warnings) {
		exit( $WARN );
	} 
	exit( $OK );
}

main();
