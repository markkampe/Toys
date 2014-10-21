/*
 * choose ... random numbers and choices
 *
 */
char *use[] = {
	"usage: choose #                number between 1 and #\n",
	"       choose #1 #2            number between #1 and #2 (inclusive)\n",
	"       choose o1 o2 ... on     choose one of specified options\n",
	"\n",
	"    where an option is:\n",
	"        weight:string          where weight is an integer\n",
	"        string                 default weight=1\n",
	"\n",
	"    switches:\n",
	"        -n #                   generate # choices\n",
	"        -d                     diagnostic output\n",
	"        -s #                   initialize random number generator seed\n",
	0
};

#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>



/* routine declarations 						*/
void initrand();		/* my own reandom number initializer	*/
int strtonum(char *, char**);	/* my own error checking converter	*/

void get_choices( char**args, int numargs );
char *makechoice( int v );
void usage();

/* globals						*/
int min, max;		/* min/max desired values	*/
char **choices = 0;	/* list of output choices	*/
int *weights = 0;	/* weights for each choice	*/

int debug = 0;


/*
 * main
 *	argument handling and main loop
 */
int main( int argc, char **argv )
{	
	long r, v;
	int c, i;
	int argsleft;
	char *s;
	int count = 1;
	int seed = 0;
	

	/* check for switches	*/
	while( (c = getopt( argc, argv, "ds:n:" )) != EOF ){
		switch (c ) {
			case 'd':
				debug = 1;
				continue;
			case 's':
				seed = atoi(optarg);
				continue;
			case 'n':
				count = atoi(optarg);
				continue;
		}
	}

	/* there must be at least one more argument	*/
	argsleft = argc - optind;
	if (argsleft < 1)
		usage();

	/* more than two arguments means a choice list 	*/
	if (argsleft > 2)
		get_choices( &argv[optind], argsleft );

	else {	/* one or two arguments		*/
		s = argv[optind++]; argsleft--;
		c = strtonum( s, 0 );
		if (c >= 0) {	/* numeric argument	*/
			if (argsleft == 0) {
				min = 1;
				max = c;
			} else if (argsleft == 1) {
				min = c;
				max = strtonum( argv[optind], 0 );
				if (max < 0) 
					usage;
				if (max <= min) {
					fprintf(stderr, "ERROR: max (%d) < min (%d)\n",
					max, min );
				exit( -1 );
				}
			} else
				usage();
		} else
			usage();
	}
		

	/* 
	 * for the requested number of iterations
	 * 	generate a random number between min and max
	 *	printout the number or the indexed choice
	 */
	initrand( seed );
	for( i = 0; i < count; i++ ) {
		r = random();
		v = (r%(1+max-min))+min;

		if (debug)
			fprintf(stderr,"random(%d-%d) = %d\n", min, max, v);

		if (choices)
			printf("%s\n", makechoice(v));
		else
			printf("%ld\n", v);
	}
}

void usage()
{	int i;
	
	for( i = 0; use[i]; i++ )
		fprintf(stderr, use[i]);

	exit(0);
}

/*
 * get choices	
 *		process a list of choices
 *
 * parms:	among and a sequence of values
 *		weighted and a sequence of weight:values
 *
 * returns:	setting of min, max, choices, and weights
 */
void get_choices( char**args, int numargs )
{	int i, j, w;
	char *s, *p;

	/* allocate arrays for choices and weights	*/
	choices = malloc( (numargs+1) * sizeof (char *) );
	weights = malloc( (numargs+1) * sizeof (int) );
	min = 0;
	max = 0;

	/*
	 * process eqch argument into the choices/weights array
	 * 
	 * Note that all arguments are treated as strings (rather than
	 * numbers) and that any argument can have an optional weight
	 * prefixed to it.
	 */
	for(i = 0, j = 0; i < numargs; i++) {
		s = args[i];

		/* old/optional arguments no longer necessary	*/
		if (strcmp(s, "among") == 0  || strcmp(s, "weighted") == 0)
			continue;

		/* see if this is a weighted argument	*/
		w = strtonum( s, &p );
		if (w >= 0 && *p == ':') {
			/* there should be a value following the colon	*/
			if (p[1] != 0) 
				s = &p[1];
			else {
				fprintf(stderr,"invalid argument: %s\n", s );
				exit( -1 );
			}
		} else	/* if no weight specified, assume it to be one	*/
			w = 1;
		
		/* add this (cumulative) weight and value to our choice list	*/
		weights[j] = w;
		choices[j] = s;
		max += w;

		if (debug) {
			fprintf(stderr, "Option %d: weight=%d, opt=%s\n",
				j, w, s );
		}
		j++;
	}

	/* mark the end of the table	*/
	choices[i] = 0;

	/* we bumped max one time too many	*/
	max--;
}

/*
 * makechoice
 *	choose a value out of the weights/choices array
 * 
 * parameters:
 *	number between 0 and sum-of-wheights - 1
 */
char *makechoice( int v ) 
{	int i;

	/* see how far the value reaches into the weights */
	for( i = 0; choices[i] && v >= weights[i]; i++ )
		v -= weights[i];

	return( choices[i] );
}


#include <ctype.h>

/*
 * strtonum
 *	my own verson of strtol that doesn't allow negative
 *	numbers or whitespace, is always base 10 ... but
 *	still returns a pointer to where the lexing ended 
 *
 * parameters:
 *	string to be lexed
 *	pointer to where end pointer can be stored
 *		so I can see where the number ended
 */
int strtonum( char *s, char **end  )
{	int v;

	if (!isdigit(*s))
		return( -1 );

	for( v = 0; isdigit( *s ); s++ ) {
		v *= 10;
		v += *s - '0';
	}

	if (end != 0)
		*end = s;

	return( v );
}


#include <time.h>
#include <sys/timeb.h>

/*
 * initrand
 *	my own random number generator initializer, 
 *	that (if no seed is specified) generates a relatively
 *	random one (rather than a constant).
 *
 * parameters
 *	number generator seed
 */
void initrand( unsigned int s ) {
	struct timeb buf;

	if (s == 0) {
		ftime( &buf );
		s = buf.time + buf.millitm;
	}

	if (debug)
		fprintf(stderr, "Using seed %d\n", s );

	srandom( s );
}
