/*
 * @(#)linecount	1.1 - 6/8/88 - IS/3
 *
 *      This is a program to count lines of code in a C program or an
 *      assembler program.
 */
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

#define MAXLINE 512

/* globals for aggrigating total line counts for all files processed    */
int     b_lines;        /* lines of blank or white space                */
int     c_lines;        /* lines of comments                            */
int     i_lines;        /* lines with in-line comments                  */
int     p_lines;        /* lines of pre-processor statements            */
int     r_lines;        /* lines of real code                           */
int     t_lines;        /* total number of lines processed              */
int     t_files;        /* total number of files processed              */

char    qflag;          /* user desires totals only                     */

void count( FILE *file, char *cs, char *ce, char *pp );
void report( int blanks, int cmts, int inln_cmts, int preproc, int real, int total );
int prefix( char *buf, char *pat );

int main( int argc, char **argv )
{       register int i;
	register char *s;
	char *comstrt = "/*";
	char *comstop = "*/";
	char *preproc = "#";
	FILE *f;

	for (i = 1; i < argc; i++)
	{       s = argv[i];
		if (*s == '-')
		{       switch (s[1])
			{  case 'c':    /* C syntax     */
				comstrt = "/*";
				comstop = "*/";
				preproc = "#";
				break;

			   case 'a':    /* ASM syntax   */
				comstrt = "/";
				comstop = "";
				preproc = "";
				break;

			   case 'b':    /* BAL syntax   */
				comstrt = "*";
				comstop = "";
				preproc = "";
				break;

			   case 'p':    /* set preprocessor line character */
				preproc = &s[2];
				break;

			   case 's':    /* set comment start character     */
				comstrt = &s[2];
				break;

			   case 'e':    /* set comment end character       */
				comstop = &s[2];
				break;

			   case 'q':    /* quiet - totals only             */
				qflag++;
				break;

			   default:
				fprintf(stderr, "Unknown flag (%s)\n", s );
				fprintf(stderr, "Usage: linecount [flags] [filename] ...\n");
				fprintf(stderr, "       -q      Quiet - print totals only\n");
				fprintf(stderr, "       -c      Use C syntax rules\n");
				fprintf(stderr, "       -a      Use asm syntax rules\n");
				fprintf(stderr, "       -b      Use BAL syntax rules\n");
				fprintf(stderr, "       -s<str> Specify start of comment string\n");
				fprintf(stderr, "       -e<str> Specify end of comment string\n");
				fprintf(stderr, "       -p<str> Specify preprocessor statement prefix\n");
				fprintf(stderr, "       default is C syntax rules (-s/* -e*/ -p#)\n");
				exit( -1 );
			}
		} else
		{       t_files++;
			f = fopen( s, "r" );
			if (f)
			{       printf("File: %s\n", s);
				count( f, comstrt, comstop, preproc );
				fclose( f );
			} else
				fprintf(stderr, "linecount: unable to open %s\n", s);
		}
	}

	if (t_files == 0)
	{       t_files++;
		count( stdin, comstrt, comstop, preproc );
	}

	if (t_files > 1)
	{       printf("\nTotals for all %d files:\n", t_files );
		report( b_lines, c_lines, i_lines, p_lines, r_lines, t_lines );
	}

	exit( 0 );
}

void count( FILE *file, char *cs, char *ce, char *pp )
{       register char *s;
	register int i;
	int     b_count = 0;    /* lines of blank or white space        */
	int     c_count = 0;    /* lines of comments                    */
	int     i_count = 0;    /* lines with in-line comments          */
	int     p_count = 0;    /* lines of pre-processor statements    */
	int     r_count = 0;    /* lines of real code                   */
	int     t_count = 0;    /* total number of lines processed      */
	int     incomment = 0;  /* are we currently in a comment        */
	int     hascomment = 0; /* does this line contain a comment     */
	char    linebuf[MAXLINE];

	while (fgets(linebuf, MAXLINE, file ))
	{       t_count++;

		/*
		 * check for lines which are entirely blank
		 */
		for( s = linebuf; *s && isspace( *s ); s++ );
		if (*s == 0)
		{       b_count++;
			continue;
		}

		/*
		 * check for comments on this line, and turn all text
		 *       within a comment into blanks
		 */
		hascomment = incomment;
		for( s = linebuf; *s; s++ )
		{       if (incomment)
			{       if (prefix(s, ce))
				{       incomment = 0;
					for( i = strlen( ce ); i; i-- )
						s[i-1] = ' ';
				} else
					*s = ' ';
			} else
			{       if (prefix(s, cs))
				{       incomment = 1;
					hascomment = 1;
					for( i = strlen( cs ); i; i-- )
						s[i-1] = ' ';
				}
			}
		}

		if (*ce == 0)
			incomment = 0;

		/*
		 * check for lines which are meant for the pre-processor
		 */
		if (prefix( linebuf, pp ))
		{       p_count++;
			i_count += hascomment;
			continue;
		}

		/*
		 * see if there is any code on the line
		 */
		for( s = linebuf; *s && isspace( *s ); s++ );
		if (*s == 0)
			c_count++;
		else
		{       r_count++;
			i_count += hascomment;
		}
	}

	if (qflag == 0)
		report( b_count, c_count, i_count, p_count, r_count, t_count );

	b_lines += b_count;
	c_lines += c_count;
	i_lines += i_count;
	p_lines += p_count;
	r_lines += r_count;
	t_lines += t_count;
}

void report( int blanks, int cmts, int inln_cmts, int preproc, int real, int total )
{       int cpct, bpct, ipct, ppct, rpct;


	if (total)
	{       bpct = (blanks * 100) / total;
		cpct = (cmts * 100) / total;
		rpct = ((real+preproc) * 100) / total;
	} else
	{       bpct = 0;
		cpct = 0;
		rpct = 0;
	}

	if (preproc + real)
	{       ipct = (inln_cmts * 100) / (preproc + real);
		ppct = (preproc * 100) / (preproc + real);
	} else
	{       ipct = 0;
		ppct = 0;
	}

	printf("\ttotal lines:     %d\n", total );
	printf("\tcode/text lines: %d\t(%2d%% of total lines)\n", real+preproc, rpct );
	printf("\tcomment lines:   %d\t(%2d%% of total lines)\n", cmts, cpct );
	printf("\tblank lines:     %d\t(%2d%% of total lines)\n", blanks, bpct );
	printf("\tpreproc lines:   %d\t(%2d%% of code lines)\n",  preproc, ppct );
	printf("\tinline comments: %d\t(%2d%% of code lines)\n", inln_cmts, ipct );
	printf("\n\n");
}

int prefix( char *buf, char *pat )
{
	if (*pat == 0)
		return( 0 );

	while( *pat  &&  (*pat == *buf))
	{       pat++;
		buf++;
	}

	if (*pat)
		return( 0 );
	else
		return( 1 );
}
