/*
 * Program to assist in the verification of correct authorization checking
 * for NTFS file systems exported to Linux/MacOS via NFS.  Given the name
 * of a file (or directory) it attempts to exercise each possible mode of
 * access:
 *      file:   stat, open for read, open for write, exec
 *      dir:    stat, open for read, create/delete, search
 *
 * no libraries or special options required
 *      cc -o check_access check_access.c
 */
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <wait.h>
#include <stdio.h>
#include <getopt.h>
#include <string.h>

/* exit codes   */
#define NO_STAT         1
#define NO_READ         2
#define NO_WRITE        4
#define NO_EXEC         8

/* supported command line arguments     */
struct option args[] = {
     /* switch          has arg flag     return value   */
        {"verbose",     0,      NULL,   'v'},
        {"help",        0,      NULL,   'h'},
        { 0,            0,      0,      0}
};
char *usage = "[-v] [filename ...]";

int verbose = 0;        /* verbose output               */
int is_directory = 0;   /* to save calls to is_dir      */
char namebuf[256];      /* buffer for files in dirs     */

/*
 * print out my real and effective user and group IDs
 */
void whoami() {
        uid_t my_uid, eff_uid, saved_uid;
        if (getresuid(&my_uid, &eff_uid, &saved_uid) != 0) {
                fprintf(stderr, "UNABLE TO GET UID\n");
                exit(-1);
        }

        gid_t my_gid, eff_gid, saved_gid;
        if (getresgid(&my_gid, &eff_gid, &saved_gid) != 0) {
                fprintf(stderr, "UNABLE TO GET GID\n");
                exit(-1);
        }

        printf("Running as UID=%d", my_uid);
        if (eff_uid != my_uid)
                printf(" (effective=%d)", eff_uid);

        printf(", GID=%d", my_gid);
        if (eff_gid != my_gid)
                printf(" (effective=%d)", eff_gid);
        printf("\n");
}


/*
 * print out the ownership and protection on a file
 *
 *      parms:  name of file to check
 *      returns: seeting of is_directory
 */
void check_directory(char *filename) {
        struct stat statb;

        if (stat(filename, &statb) == 0) 
                is_directory = statb.st_mode & S_IFDIR ? 1 : 0;
        else
                is_directory = 0;
}

/*
 * print out the ownership and protection on a file
 *
 *      parms:  name of file to check
 *      returns: exit codes
 *               and a setting of is_directory
 */
int ownership(char *filename) {
        struct stat statb;

        if (stat(filename, &statb) != 0) {
                return(NO_STAT);
        }

        /* print out the ownership information  */
        if (verbose) {
                printf("        ");
                printf("OWNER=%d, GROUP=%d", statb.st_uid, statb.st_gid);

                printf(", MODES=");
                char *key = "rwxrwxrwx";
                for(int bit = 0400; bit !=0; bit >>= 1) {
                        putchar(statb.st_mode & bit ? *key : '-');
                        key++;
                }

                if (statb.st_mode & S_ISUID)
                        printf(", SETUID");

                if (statb.st_mode & S_ISGID)
                        printf(", SETGID");

                putchar('\n');
        }

        return(0);
}

/*
 * figure out what access we have to a specified file
 *
 *      parms:  name of file to check
 *              setting of is_directory (side effect)
 *      returns: exit codes
 */
int check_access(char *filename) {
        int ret = 0;

        if (verbose)
                printf("        ");

        /* can I open the file for read access */
        int fd = open(filename, O_RDONLY);
        if (fd >= 0) {
                if (verbose)
                        printf("READ");
                close(fd);
        } else {
                if (verbose)
                        printf("NO READ");
                ret |= NO_READ;
        }

        /* write access means different things for files and directories      */
        if (is_directory) {
                /* can I create and delete files within the directory   */
                strncpy(namebuf, filename, sizeof namebuf);
                strncat(namebuf, "/!!!STUPID_TEST_FILE!!!", sizeof namebuf);
                fd = creat(namebuf, 0666);
                if (fd < 0) {
                        printf(", NO CREATE/DELETE");
                        ret |= NO_WRITE;
                } else {
                        close(fd);
                        if (unlink(namebuf) == 0) {
                                printf(", CREATE/DELETE");
                        } else {
                                printf(", CREATE NO-DELETE");
                                ret |= NO_WRITE;
                        }
                }
        } else {
                /* can I open the file for write access */
                fd = open(filename, O_WRONLY);
                if (fd >= 0) {
                        if (verbose)
                                printf(", WRITE");
                        close(fd);
                } else {
                        if (verbose)
                                printf(", NO WRITE");
                        ret |= NO_WRITE;
                }
        }

        /* execute access means different things for files and directories      */
        if (is_directory) {
                /* check directory searching */
                strncpy(namebuf, filename, sizeof namebuf);
                strncat(namebuf, "/.", sizeof namebuf);
                fd = open(namebuf, O_RDONLY);
                if (fd >= 0) {
                        if (verbose)
                                printf(", SEARCH");
                        close(fd);
                } else {
                        if (verbose)
                                printf(", NO SEARCH");
                        ret |= NO_EXEC;
                }
        } else {
                /* see if we can execute the file       */
                fflush(stdout);         /* I was seeing a double print  */
                pid_t childpid = fork();
                if (childpid == -1)
                        fprintf(stderr, "UNABLE TO FORK\n");
                else if (childpid == 0) {
                        /* child: try to exec the file  */
                        execl(filename, "TESTING", (char *) NULL);
                        exit(-1);
                } else {
                        /* collect the exit status      */
                        int status;
                        waitpid(childpid, &status, 0);
                        if (status == 0) {
                                if (verbose)
                                        printf(", EXECUTE");
                        } else {
                                if (verbose) 
                                        printf(", NO EXECUTE");
                                ret |= NO_EXEC;
                        }
                }
        }


        if (verbose)
                printf("\n");

        return(ret);
}


/*
 * process command line switches, and check access on all specified files
 */
int main(int argc, char **argv) {
        
        /* process switch arguments     */
        int i;
        while( (i = getopt_long(argc, argv, "vh", args, NULL) ) != -1) {
            switch(i) {
                case 'v':
                        verbose = 1;
                        break;

                case 'h':
                case '?':
                default:
                        fprintf(stderr, "Usage: %s %s\n", argv[0], usage);
                        exit(-1);
            }
        }

        /* print out who we are running as      */
        if (verbose)
                whoami();

        /* process file names           */
        int ret;
        while(optind < argc) {
                check_directory(argv[optind]);
                if (verbose)
                        printf("    %s: %s\n", 
                                is_directory ? "Directory" : "File",
                                argv[optind]);
                ret |= ownership(argv[optind]);
                ret |= check_access(argv[optind++]);
        }

        /* exit code is union of results      */
        exit(ret);
}
