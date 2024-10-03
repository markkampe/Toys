#include <unistd.h>

#define MIN_CHAR	33
#define MAX_CHAR	126
#define MIN_COLS	80
#define MAX_LINES	120
#define MAX_COLS	160

void printline(int lineno, int width) {
	char buf[MAX_COLS+2];
	
	// start with a line number
	int col = 0;
	buf[col++] = '0' + lineno / 100;
	buf[col++] = '0' + (lineno / 10) % 10;
	buf[col++] = '0' + lineno % 10;
	buf[col++] = ' ';

	// fill the rest of the line with a pattern
	while( col < width ) {
		buf[col++] = MIN_CHAR + ((lineno + col) % (MAX_CHAR - MIN_CHAR));
	}

	buf[col++] = '\n';
	buf[col] = 0;
	(void) write(1, buf, col);
}

void widthTest(int cols) {
	char buf[MAX_COLS+2];
	int c;

	// write out the tens
	for( c = 0; c < cols; c++ ) {
		if (c % 10 == 0) {
			buf[c] = '0' + c / 100;
			buf[c+1] = '0' + (c / 10) % 10;
			buf[c+2] = '0' + c % 10;
			c += 2;
		} else
			buf[c] = ' ';
	}
	buf[c++] = '\n';
	buf[c] = 0;
	write(1, buf, c);

	// write out the ones
	for( c = 0; c < cols; c++ )
		buf[c] = '0' + c % 10;
	buf[c++] = '\n';
	buf[c] = 0;
	(void) write(1, buf, c);
}

int main(int argc, char **argv) {

	int l;
	for(l = 0; l < MAX_LINES; l++) {
		printline(l, MIN_COLS);
	}

	widthTest(MAX_COLS);
}
