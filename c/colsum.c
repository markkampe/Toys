/*
 * colsum ... sum columns of numerical data
 *
 * usage:
 *	colsum [-v] [--verbose] -p#] [--places=#][file ...]
 */

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <getopt.h>
#include <stdbool.h>

/* input and output format parameters				*/
#define MAXCOLS	20	/* max supported columns per line	*/
#define	MAXLINE	512	/* maximum width input line		*/
#define PADDING 2	/* sum is wider than largest addend	*/
#define MINSEP	1	/* minimum distance between columns	*/

/* what we know about the data in each column	*/
struct column {
	enum { none = 0, integer, decimal } coltype;
	float colsum;	// sum for this column
	int values;	// number of numerical values found
	int left_edge;	// left-most position in this col
	int right_edge;	// right-most position in this col
	char format[10]; // output format
};

int places = 2;		// number of decimal places to print
bool echo_lines = 0;	// echo each tallied input line
bool debug = 0;		// enable diagnostic output

/*
 * parse off a single white-space delimited token,
 * 	and if it is a number, tally it in a column
 *
 * @param s	first character of token
 * @param col	associated column structure
 * @return	whether or not a number was found in this column
 */
bool add_parse( const char *s, struct column *col ) {
    int sign = 1;
    int wholepart = 0;
    int factor = 0;
    float fraction = 0.0;

    // scan until we hit a number
    while( *s < '0' || *s > '9' ) {
	if (*s == '$' || *s == '+') {	// ignore dollar/plus signs
	    s++;
	    continue;
	}

	if (*s == '-' || *s == '(') {	// - or left paren is negative
	    sign = -1;
	    s++;
	    continue;
	}

	if (*s == '.')
		break;

	return false;			// anything else is non-numeric
    }

    // now try to scan off the number
    while( *s ) {
	// have we hit the first decimal point?
	if (factor == 0 && *s == '.') {
	    factor = 10;
	    s++;
	    continue;
	}

	// accumulate digits
	if (*s >= '0' && *s <= '9') {
	    if (factor > 0) {
		float f = *s++ - '0';
		fraction += f / factor;
		factor *= 10;
	    } else {
		wholepart *= 10;
		wholepart += *s++ - '0';
	    }
	    continue;
	}

	// digits must end with a reasonable delimiter
	if (*s == ' ' || *s == '\t' || *s == '\n' || *s == ')' || *s == 0) {
	    col->colsum += wholepart * sign;
	    if (factor) {
		col->colsum += fraction * sign;
		col->coltype = decimal;
	    } else if (col->coltype == none)
		col->coltype = integer;

	    col->values++;
	    return true;
	}

	// did not hit digits or field contained unreasonable characters
    	return false;
    }
    // end of string w/o reasonable delimiter
    return false;
}

/*
 * process a file, reading lines, parsing columns, and trying to add them up
 */
int process_file( const char *name, int numcol, struct column *cols ) {

    FILE *input;
    char inbuf[MAXLINE];

    if (name == 0)
	input = stdin;
    else {
	input = fopen(name, "r");
	if (input == NULL) {
	    fprintf(stderr, "Unable to open input file %s\n", name);
	    return(-1);
	}
    }

    int lines, c;
    char *s;
    for( lines = 0; (s = fgets(inbuf, sizeof inbuf, input)); lines++ ) {
	c = 0;
	int good_cols = 0;	// # cols containing numerical data
	while( c < numcol ) {
	    // skip to the start of the next column
	    if (*s == ' ' || *s == '\t') {
		while( *s == ' ' || *s == '\t' )
		    s++;
		c++;
	    }

	    // see if we have run out of input
	    if (*s == '\n' || *s == 0)
		break;

	    // try to parse a numerical value
	    bool got_some = add_parse( s, &cols[c] );
	    if (got_some && (s - inbuf) < cols[c].left_edge)
	    	cols[c].left_edge = s - inbuf;

	    do {	 // skip to the end of this field
		s++;
	    } while( *s != ' ' && *s != '\t' && *s != '\n' && *s != 0 );
	    if (got_some) {
		int last_col = (s - inbuf) - 1;
	    	if (last_col > cols[c].right_edge)
	    		cols[c].right_edge = last_col;
	        good_cols++;
	    }
	}

	// if there were any numerical columns, this should be printed
    	if (good_cols && echo_lines)
	    fputs(inbuf, stdout);
    }

    if (input != stdin)
	fclose(input);
    return( 0 );
}

/*
 * print out a vector of numbers, perhaps with a file name
 */
void print_vector( int numcol, struct column *cols ) {

    int outcol = 0;

    if (echo_lines) {	// print a vinculum under each numerical column
    	for(int c = 0; c < numcol; c++) {
    	    if (cols[c].values == 0)
		continue;

	    // move us to the left edge position
	    while(outcol < cols[c].left_edge) {
		fputc(' ', stdout);
		outcol++;
	    }
	    // output the right number of underline characters
	    while(outcol <= cols[c].right_edge) {
		fputc('-', stdout);
		outcol++;
	    }
    	}

	fputc('\n', stdout);
	outcol = 0;
    }

    /* print out a sum for each valid column	*/
    for(int c = 0; c < numcol; c++) {
	if (cols[c].values == 0)
	    continue;

	if (echo_lines) {
	    // move us to a reasonable left edge position
	    int start_col = cols[c].left_edge - PADDING;
	    if (start_col < outcol + MINSEP)
		start_col = outcol + MINSEP;
	    while(outcol < start_col) {
		fputc(' ', stdout);
		outcol++;
	    }
	} else if (outcol != 0) {	// one space between columns
	    fputc(' ', stdout);
	    outcol++;
	}

	if (echo_lines) {
	    // figure out a reasonable output format
	    int width =  PADDING + (cols[c].right_edge + 1) - cols[c].left_edge;
	    if (cols[c].coltype == integer)
		sprintf(cols[c].format, "%%%dd", width);
	    else if (cols[c].coltype == decimal)
		sprintf(cols[c].format, "%%%d.%df", width, places);
    	    outcol += width;
	} else {
	    // what ever size fits
	    if (cols[c].coltype == integer)
		sprintf(cols[c].format, "%%d");
	    else if (cols[c].coltype == decimal)
		sprintf(cols[c].format, "%%.%df", places);
	    outcol++;	// doesn't matter
	}

	// print the column sum
	if (cols[c].coltype == integer)
	    fprintf(stdout, cols[c].format, (int) cols[c].colsum);
	else
	    fprintf(stdout, cols[c].format, cols[c].colsum);
    }
    fputc('\n', stdout);

    if (debug) {
	for(int c = 0; c < numcol; c++) {
    	    if (cols[c].values > 0)
	    	fprintf(stderr, "DEBUG: col %d: %d-%d, %d values, format: %s\n",
			c, cols[c].left_edge, cols[c].right_edge, 
			cols[c].values, cols[c].format);
    	}
    }
}

/* supported command line arguments	*/
struct option args[] = {
 /*	 switch       has arg	...   return value */
	{"verbose",	0,	NULL, 'v'},	/* print every counted line	*/
	{"places",	1,	NULL, 'p'},	/* decimal places to print	*/
	{"debug",	0,	NULL, 'D'},	/* enable debug output		*/
	{ 0, 0, 0, 0 }
};

const char *usage = "[--verbose] [--places=#] [filename ...]";

/*
 * if file names are specified, process each listed file
 *	followed by a grand total
 * else
 *	process stdin
 */
int main( int argc, char *argv[] ) {

    int numcol = MAXCOLS;	/* not worth computing dynamically	*/
    int retcode = 0;

    /* allocate/initialize our column info	*/
    struct column *sums = (struct column *) malloc( numcol * sizeof(struct column));
    for ( int c = 0; c < numcol; c++ ) {
	sums[c].coltype = none;
	sums[c].colsum = 0.0;
	sums[c].values = 0;
	sums[c].left_edge = MAXLINE;	// any column start will be less
	sums[c].right_edge = -1;	// any column end will be more
    }

    /* see if we have any command line switches */
    while( true ) {
    	int i = getopt_long(argc, argv, "vp:D", args, NULL);
	if (i < 0)		// end of switches
	    break;

        switch (i) {
	    case 'v':		// --verbose
	    	echo_lines = true;
		break;
	    case 'p':		// --places=#
	    	places = atoi(optarg);
		break;
	    case 'D':		// --DEBUG
	    	debug = true;
		break;

	    default:
		fprintf(stderr, "Usage: %s %s\n", argv[0], usage);
		exit(-1);
	}
    }

    if (optind >= argc) {	/* process stdin	*/
	if (process_file(0, numcol, sums) == 0)
	    print_vector(numcol, sums);
	else
	    retcode = 1;
    } else {		/* process named input files */
	/* create a grand total	accumulation */
	struct column *grand = (struct column *) malloc( numcol * sizeof(struct column));
	for ( int c = 0; c < numcol; c++ ) {
	    grand[c].coltype = none;
	    grand[c].colsum = 0.0;
	}
	int num_files = 0;

	/* process each input file	*/
	for( int i = optind; i < argc; i++ ) {
	    printf("%s:\n", argv[i]);
	    if (process_file(argv[i], numcol, sums) == 0) {
		print_vector( numcol, sums);
		fputs("\n", stdout);
	    	num_files++;
	    } else
		retcode = 1;

	    /* add it to grand total, and reset sums */
	    for ( int c = 0; c < numcol; c++ ) {
		if (sums[c].values == 0)
		    continue;

		if (sums[c].coltype > grand[c].coltype)
		    grand[c].coltype = sums[c].coltype;
		grand[c].colsum += sums[c].colsum;
		grand[c].coltype = sums[c].coltype;
		grand[c].values += sums[c].values;
		grand[c].left_edge = sums[c].left_edge;
		grand[c].right_edge = sums[c].right_edge;

		// reset all collumn info for next file
		sums[c].coltype = none;
		sums[c].colsum = 0.0;
		sums[c].values = 0;
		sums[c].left_edge = MAXLINE;
		sums[c].right_edge = -1;
	    }

	}

	if (num_files > 1) {
	    printf("GRAND TOTAL:\n");
	    print_vector(numcol, grand);
	}
	free(grand);
    }

    free(sums);
    return( retcode );
}
