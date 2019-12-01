#include <stdio.h>

extern int __open(const char *, int, int);
extern int __read(int, char *, int);
extern int __write(int, char *, int);

int open(const char *path, int flags, int modes) {
	fprintf(stderr, ">intercepted open of %s\n", path);
	return(__open(path, flags, modes));
}

int read(int fd, char *buf, int count) {
	if (fd > 2) {
		fprintf(stderr, ">intercepted read for fd%d, %d bytes\n", fd, count);
	}
	return(__read(fd, buf, count));
}

int write(int fd, char *buf, int count) {
	if (fd > 2) {
		fprintf(stderr, ">intercepted write for fd%d, %d bytes\n", fd, count);
	}
	return(__write(fd, buf, count));
}
