#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <keyutils.h>

/*
 * test program for persistent key lookup
 *
 * setup:
 *	% id=`keyctl get_persistent`
 *	% keyctl add user <keyname> <keyvalue> $id
 */
int main( int argc, char *argv[] ) {
	/* confirm we have the expected argument */
	if (argc != 2) {
		fprintf(stderr, "Usage: %s key-name\n", argv[0]);
		return( -1 );
	}

	/* get a reference to my persistent keyring	*/
	key_serial_t ring = keyctl_get_persistent(-1, KEY_SPEC_USER_KEYRING);
	if (ring == -1) {
		perror("Unable to reference persistent key ring");
		exit(-2);
	}

	/* look up the requested key	*/
	key_serial_t id = request_key( "user", argv[1], (char *) 0, ring );
	if (id == -1) {
		perror("Error looking up key");
		fprintf(stderr, "Key=%s, Ring=%d\n", argv[1], ring);
		return(-2);
	}

	/* get the value of the requested key	*/
	char keybuf[256];
	int ret = keyctl_read(id, keybuf, sizeof keybuf);
	if (ret == -1) {
		perror("Error getting key value");
		return(-3);
	} else {
		fprintf(stderr, "len=%d\n", ret);
		fwrite(keybuf, 1, ret, stdout);
		fwrite("\n", 1, 1, stdout);
	}
}

