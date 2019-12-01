/*
 * This is a simple test program to prove that I can use leveldb
 */
#include <string>
#include <leveldb/db.h>

#define	DBASE	"./leveldb_dir"

main(int argc, char **argv) 
{
	leveldb::DB *db;
	leveldb::Options db_opts;

	leveldb::Iterator *it;
	leveldb::Status status;
	leveldb::Slice key;
	std::string value;

	// open/create a database
	printf("open/create database ... ");
	db_opts.create_if_missing = true;
	status = leveldb::DB::Open(db_opts, DBASE, &db);
	if (status.ok())
		printf("OK\n");
	else
		printf("%s\n", status.ToString().c_str());

	// figure out what we are supposed to do
	switch (argc) {
	    case 1:	// dump the databse
	    	printf("Dump:\n");
		it = db->NewIterator(leveldb::ReadOptions());
		for( it->SeekToFirst(); it->Valid(); it->Next()) {
			printf("\t%s:\t%s\n",
				it->key().ToString().c_str(),
				it->value().ToString().c_str());
		}
		break;

	    case 2:	// get the specified value
	    	printf("get(%s) ... ", argv[1]);
		key = argv[1];
		status = db->Get(leveldb::ReadOptions(), key, &value);
		if (status.ok())
			printf("%s\n", value.c_str());
		else
			printf("%s\n", status.ToString().c_str());
		break;

	    case 3:	// set the specified value
	    	printf("set(%s,%s) ... ", argv[1], argv[2]);
		key = argv[1];
		value = argv[2];
		status = db->Put(leveldb::WriteOptions(), key, value);
		if (status.ok())
			printf("OK\n");
		else
			printf("%s\n", status.ToString().c_str());
		break;
	}

	// close the database
	delete db;
}


