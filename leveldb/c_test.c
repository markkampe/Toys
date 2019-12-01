/*
 * This is a simple test program to prove that I can use leveldb
 */
#include <leveldb/c.h>
#include <stdio.h>
#include <string.h>
#include <malloc.h>

#define DBASE	"./leveldb_dir"
#define MAX_VALUE 256

main(int argc, char **argv) 
{
	char *err = NULL;
	const char *key;
	const char *value;
	size_t read_len;
	char buf[MAX_VALUE];

	/* open/create a database		*/
	leveldb_options_t *db_opts = leveldb_options_create();
	leveldb_options_set_create_if_missing(db_opts, 1);
	printf("open/create database ... ");
	leveldb_t *db = leveldb_open(db_opts, DBASE, &err);
	if (err == NULL)
		printf("OK\n");
	else {
		printf("OPEN FAILURE(%s)\n", err);
		free(err);
		err = NULL;
		return(-1);
	}

	/* initialize a couple of handy structures	*/
	leveldb_readoptions_t *roptions = leveldb_readoptions_create();
	leveldb_writeoptions_t *woptions = leveldb_writeoptions_create();
	leveldb_iterator_t *it;

	// figure out what we are supposed to do
	switch (argc) {
	    case 1:	// dump the databse
	    	printf("Dump:\n");
		it = leveldb_create_iterator(db, roptions);
		for( leveldb_iter_seek_to_first(it); 
		     leveldb_iter_valid(it);
		     leveldb_iter_next(it)) {
			// print out the key
			key = leveldb_iter_key(it, &read_len);
			strncpy(buf, key, read_len);
			buf[read_len] = 0;
			printf("\t%s:\t", buf);

			// print out the value
			value = leveldb_iter_value(it, &read_len);
			strncpy(buf, value, read_len);
			buf[read_len] = 0;
			printf("%s\n", buf);
		}
		leveldb_iter_destroy(it);
		break;

	    case 2:	// get the specified value
	    	printf("get(%s) ... ", argv[1]);
		key = argv[1];
		value = leveldb_get(db, roptions, key, strlen(key), &read_len, &err);
		/* FIX ... missing key returns 0 len, but no error */
		if (err == NULL) {
			if (value != NULL) {
				strncpy(buf, value, read_len);
				buf[read_len] = 0;
				printf("%s, len=%d\n", buf, (int) read_len);
			} else {
				printf("not in database\n");
			}
		} else {
			printf("GET FAILURE (%s)\n", err);
			free(err);
			err = NULL;
		}
		break;

	    case 3:	// set the specified value
	    	printf("set(%s,%s) ... ", argv[1], argv[2]);
		key = argv[1];
		value = argv[2];
		leveldb_put(db, woptions, key, strlen(key), value, strlen(value), &err);
		if (err == NULL)
			printf("OK\n");
		else {
			printf("PUT FAILURE (%s)\n", err);
			free(err);
			err = NULL;
		}
		break;
	}

	// close the database
	leveldb_close(db);
}


