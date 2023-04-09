#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <ctype.h>

/*
 * simple CLI to do expression-based dice rolls
 */
void usage(char *problem, char *arg) {
    if (problem)
        fprintf(stderr, "ERROR: %s (%s)\n", problem, arg);
    fprintf(stderr, "usage: roll [#]D#[+#]\n");
    // I don't mention the -D (debug) switch
    exit(1);
}

int num_dice = 1;
int sides = 100;
int plus = 0;
int debug = 0;

/*
 * argparse
 * 	lex the argument string to get
 *	    number of dice
 *	    number of sides
 *	    a plus or minus
 */
void argparse(char *arg) {
    char *s = arg;
    // default values for optional parameters
    num_dice = 1;
    plus = 0;

    // see if there is a leading number
    int n = 0;
    while(isdigit(*s)) {
        n *= 10;
	n += *s++ - '0';
    }

    if (n > 0)
        num_dice = n;

    // should be followed by a D and another number (or %)
    if (*s != 'd' && *s != 'D')
        usage("no D expression", arg);

    n = 0;
    s++;
    if (*s == '%') {
        sides = 100;
    	s++;
    } else {
	    while(isdigit(*s)) {
		n *= 10;
		n += *s++ - '0';
	    }
	    if (n == 0)
		usage("no number after D", arg);
	    sides = n;
    }

    // might be followed by a +/- and another number
    if (*s == 0)
       return;
    int sign = 0;
    switch(*s++) {
        case '-':
	    sign = -1;
	    break;
	case '+':
	    sign = 1;
	    break;
	default:
	    usage("unrecognized +/- expression", arg);
    }
    n = 0;
    while(isdigit(*s)) {
        n *= 10;
	n += *s++ - '0';
    }
    plus = sign * n;
}

/*
 * roll
 *	compute a dice roll
 */
int roll(int sides) {
    // initialize the random number generator
    static int initialized = 0;
    if (!initialized) {
    	srand(time(0));
	initialized = 1;
    }

    // do the roll
    int value = 1 + (rand() % sides);
    if (debug)
    	fprintf(stderr, " ... D%d = %d\n", sides, value);
    return value;
}

/*
 * main
 *	parse the arguments
 *	roll the specified dice
 */
int main(int argc, char **argv) {
    int did = 0;

    for(int i = 1; i < argc; i++) {
    	if (argv[i][0] == '-') {
	    debug = (argv[i][1] == 'd' || argv[i][1] == 'D');
	} else {
	    // parse this argument and make the rolls
	    argparse(argv[i]);

	    int sum = 0;
	    for(int i = 0; i < num_dice; i++)
		sum += roll(sides);
	    sum += plus;
	    did++;
	    printf("%d\n", sum);
	}
    }

    // if no rolls specified, just do D100
    if (did == 0)
        printf("%d\n", roll(100));

    exit(0);
}

