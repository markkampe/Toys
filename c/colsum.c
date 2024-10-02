/*
 * colsum ... sum columns of numerical data
 *
 * usage:
 *	colsum [file ...]
 */

// TODO - add -v option
//		print each processed line
//		figure out how to align columns
//		print totals line
//		print totals
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>

/* input and output format parameters				*/
#define MAXCOLS	20	/* max supported columns per line	*/
#define	MAXLINE	512	/* maximum width input line		*/

#define	COLWID	8	/* output column width			*/
#define	PLACES	2	/* number of FP decimal places		*/
#define	COLSEP	2	/* output inter-column separation	*/
#define	MAXFMT	(COLSEP+10)	/* maximum format width		*/

#define	TOTAL_TITLE "Grand Total"

/* what we know about the data in each column	*/
struct column {
	enum { none = 0, integer, decimal } coltype;
	float colsum;	// sum for this column
	int values;	// number of numerical values found
	int left_edge;	// left-most position in this col
	int right_edge;	// right-most position in this col
};

bool echo_lines = 0;	// echo each tallied input line
bool debug = 0;		// diagnostic output

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
    for( lines = 0; s = fgets(inbuf, sizeof inbuf, input); lines++ ) {
	c = 0;
	int good_cols = 0;
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

	    // try to parse off the value
	    bool got_some = add_parse( s, &cols[c] );
	    if (got_some && (s - inbuf) < cols[c].left_edge)
	    	cols[c].left_edge = s - inbuf;

	    // skip to the end of this field
	    do {
		s++;
	    } while( *s != ' ' && *s != '\t' && *s != '\n' && *s != 0 );
	    if (got_some && (s - inbuf) > cols[c].right_edge)
	    	cols[c].right_edge = s - inbuf;

	    if (got_some)
	        good_cols++;
	}

    	if (good_cols && echo_lines)
	    fwrite(inbuf, 1, strlen(inbuf), stdout);
    }

    if (input != stdin)
	fclose(input);
    return( 0 );
}

char n_fmt[MAXFMT+1] = "%s";	/* output format for names		*/
char i_fmt[MAXFMT+1] = "%f";	/* output format for integers		*/
char f_fmt[MAXFMT+1] = "%f";	/* output format for decimal numbers	*/

/*
 * print out a vector of numbers, perhaps with a file name
 */
void print_vector( const char *name, int numcol, struct column *cols ) {

    /* output the name if we have one	*/
    if (name != 0)
	fprintf(stdout, n_fmt, name);

    /* print out a sum for each valid column	*/
    for(int c = 0; c < numcol; c++) {
	if (cols[c].coltype == integer)
	    fprintf(stdout, i_fmt, cols[c].colsum);
	else if (cols[c].coltype == decimal)
	    fprintf(stdout, f_fmt, cols[c].colsum);
    }
    fputc('\n', stdout);

    if (debug) {
	for(int c = 0; c < numcol; c++) {
    	    if (cols[c].values > 0)
	    	fprintf(stderr, "DEBUG: col %d: %d-%d, %d values\n",
			c, cols[c].left_edge, cols[c].right_edge, cols[c].values);
    	}
    }
}

/*
 * create a set of output formats for the requested field widths
 */
 void make_formats( int colwid, int decimals, int colsep ) {
    int i;

    /* the numerical formats	*/
    for( i = 0; i < colsep; i++ ) {
	i_fmt[i] = ' ';
	f_fmt[i] = ' ';
    }
    i_fmt[i] = '%';
    f_fmt[i++] = '%';
    if (colwid > 9) {
	i_fmt[i] = '0' + (colwid/10);
	f_fmt[i++] = '0' + (colwid/10);
    }
    i_fmt[i] = '0' + (colwid%10);
    f_fmt[i++] = '0' + (colwid%10);
    i_fmt[i] = '.';
    f_fmt[i++] = '.';
    i_fmt[i] = '0';
    f_fmt[i++] = '0' + (decimals%10);
    i_fmt[i] = 'f';
    f_fmt[i++] = 'f';
    i_fmt[i] = 0;
    f_fmt[i] = 0;
 }

/*
 * if file names are specified, process each listed file
 *	followed by a grand total
 * else
 *	process stdin
 *
 * If I ever care, I should accept a parameter for the number of floating
 *	point decimal places desired in the columnar sum ouput.
 */
int main( int argc, const char *argv[] ) {

    int numcol = MAXCOLS;	/* not worth computing dynamically	*/
    int retcode = 0;

    /* allocate/initialize our column info	*/
    struct column *sums = (struct column *) malloc( numcol * sizeof(struct column));
    for ( int c = 0; c < numcol; c++ ) {
	sums[c].coltype = none;
	sums[c].colsum = 0.0;
	sums[c].values = 0;
	sums[c].left_edge = 999;
	sums[c].right_edge = 0;
    }

    /* initialize the column output formats	*/
    make_formats(COLWID, PLACES, COLSEP);

    /* see if we have any command line switches */
    int first_arg = 1;
    while( argc > first_arg && argv[first_arg][0] == '-') {
	const char *arg = argv[first_arg];
	if (strcmp(arg, "-v") == 0 || strcmp(arg, "--verbose") == 0) {
	    echo_lines = true;
	    first_arg++;
	    continue;
	} else if (strcmp(arg, "--debug") == 0) {
	    debug = true;
	    first_arg++;
	} else {
	    fprintf(stderr, "Unrecognized argument: %s\n", arg);
	    exit(-1);
	}
    }
    if (argc == first_arg) {	/* process stdin	*/
	if (process_file(0, numcol, sums) == 0)
	    print_vector(0, numcol, sums);
	else
	    retcode = 1;
    } else {		/* process named input files */

	/* figure out how wide a file name needs to be	*/
	int nwid = strlen(TOTAL_TITLE);
	for( int i = first_arg; i < argc; i++ ) {
	    int n = strlen(argv[i]);
	    if (n > nwid)
		nwid = n;
	}
	snprintf(n_fmt, MAXFMT, "%%-%ds", nwid);

	/* accumulate a grand total	*/
	struct column *grand = (struct column *) malloc( numcol * sizeof(struct column));
	for ( int c = 0; c < numcol; c++ ) {
	    grand[c].coltype = none;
	    grand[c].colsum = 0.0;
	}

	/* process each input file	*/
	for( int i = 1; i < argc; i++ ) {
	    if (process_file(argv[i], numcol, sums) == 0) {
		print_vector(argv[i], numcol, sums);
		fputs("\n", stdout);
	    } else
		retcode = 1;

	    /* add it to grand total, and reset sums */
	    for ( int c = 0; c < numcol; c++ ) {
		if (sums[c].coltype > grand[c].coltype)
		    grand[c].coltype = sums[c].coltype;
		grand[c].colsum += sums[c].colsum;
		sums[c].coltype = none;
		sums[c].colsum = 0;
	    }

	}

	print_vector(TOTAL_TITLE, numcol, grand);
	free(grand);
    }

    free(sums);
    return( retcode );
}
