/*
 * unixtime ... convert a unix time (seconds since 1970) into a local time/date
 *
 * usage:
 *	unixtime [--offset=#] [decimal time]
 *	
 *	if no time is given, it will read times from stdin
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <getopt.h>

#define MAXLEN 16				// these are 10-digit numbers
#define TIMELEN 32				// maximum length of a time string

/* supported command line arguments	*/
char *usage = "[--offset=#] [seconds (decimal) ...]";
char *error = "Invalid input: %s ... expected (10-digit) decimal integer\n";
struct option args[] = {
    /* switch	hasarg	flag	retval	*/
    {"offset",	1,	0,	'o'},
    {0,		0,	0,	0}
};

long gmt_offset = 0;		// seconds between local and GMT


/*
 * convert a number of seconds since EPOCH to a local time/date
 */
void convert(time_t seconds) {
	char tbuf[TIMELEN];
	char *s = ctime_r(&seconds, tbuf);
	printf("%s", s);
}

/*
 * process each supplied UNIX time
 */
int main(int argc, char **argv) {

	// check for switches
	int i;
	while( (i = getopt_long(argc, argv, "o:", args, NULL)) != -1) {
		switch(i) {
			case 'o':
    				gmt_offset = atol(optarg) * 3600;
				break;
			default:
				fprintf(stderr, "Usage: %s %s\n", argv[0], usage);
				exit(-1);
		}
	}

	long seconds;			// number to be converted;

	if (optind >= argc) {	// process stdin
		char inbuf[MAXLEN];
		for(;;) {
			fprintf(stderr, "seconds: ");
			char *s = fgets(inbuf, sizeof inbuf, stdin);
			if (s) {
				seconds = atol(inbuf);
				if (seconds == 0) {
					fprintf(stderr, error, inbuf);
					exit(-1);
				} else
					convert((time_t) seconds );
			} else
				break;
		}
	} else {				// process times on command line
		for( i = optind; i < argc; i++ ) {
			seconds = atol(argv[i]);
			if (seconds == 0) {
				fprintf(stderr, error, argv[i]);
				exit(-1);
			} else
				convert((time_t) seconds);
		}
	}

	exit(0);
}
