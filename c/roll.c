#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <ctype.h>

/*
 * CLI to do a DnD style roll
 */
void usage(char *problem, char *arg) {
    if (problem)
        fprintf(stderr, "ERROR: %s (%s)\n", problem, arg);
    fprintf(stderr, "usage: roll [#]D#[+#]\n");
    exit(1);
}

int num_dice = 1;
int sides = 100;
int plus = 0;

/*
 * argparse
 * 	lex the argument string to get
 *	    number of dice
 *	    number of sides
 *	    a plus or minus
 */
void argparse(char *arg) {
    char *s = arg;
    // see if there is a leading number
    int n = 0;
    while(isdigit(*s)) {
        n *= 10;
	n += *s++ - '0';
    }
    if (n > 0)
        num_dice = n;

    // should be followed by a D and another number
    if (*s != 'd' && *s != 'D')
        usage("no D expression", arg);

    n = 0;
    s++;
    while(isdigit(*s)) {
        n *= 10;
	n += *s++ - '0';
    }
    if (n == 0)
	usage("no number after D", arg);
    sides = n;

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
    srand(time(0));

    return(1 + (rand() % sides));
}

/*
 * main
 *	parse the arguments
 *	roll the specified dice
 */
int main(int argc, char **argv) {
    if (argc > 2)
        usage(NULL, NULL);

    if(argc == 2)
        argparse(argv[1]);

    int sum = 0;
    for(int i = 0; i < num_dice; i++)
    	sum += roll(sides);
    sum += plus;
    printf("%d\n", sum);
    exit(0);
}

