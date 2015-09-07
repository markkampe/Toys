/*
 * set the title of an xterm with the designated escape sequence
 */
#include <stdio.h>

#define SET_ICON	"\033]1;"
#define SET_WINDOW	"\033]2;"
#define SET_BOTH	"\033]0;"
#define	SET_END		"\007"

int main(int argc, char **argv) {

	const char *start = SET_WINDOW;

	if (argc < 1)
		return(-1);

	int i = 1;
	if (argv[1][0] == '-') {
		if (argv[1][1] == 'b')
			start = SET_BOTH;
		else if (argv[1][1] == 'i')
			start = SET_ICON;
		i++;
	}

	printf("%s", start);
	while( i < argc ) {
		printf( (i == 1) ? "%s" : " %s", argv[i++] );
	}

	printf("%s", SET_END);
}
