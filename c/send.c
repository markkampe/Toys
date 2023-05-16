/* name:
	send

function:
	A message sending program modeled after the tenex program
	sndmsg.

parameters:
	Optional, a list of recipients

compile time parameters:
	If you want the standard unix editing characters ( #, @, del ) to
	work, define unixchars.  If you don't want them, leave that variable
	undefined.


returns:
	It delivers local mail by appending it to a file called mailbox
	in the user's root.
	The delivery of network mail is not yet implemented, but will
	probably by dropping the file into a daemons mailbox.
	If mail is undeliverable, a copy of the letter is left in
	a file called unsent.mail, in the senders current directory.

history:
	Originally written by someone at Berkeley (Murray Bowles?)
	Reorganized and augmented by Mark Kampe 10/75

 */
main(argc,argv)
char *argv[];
int argc;
{
	register char *p;
	register char *s;
	register int i;
	int vector[2];
	if ((pwfd = open("/etc/passwd",0)) < 0)
		{
		printf("Couldn't open password file!\n");
		exit();
		}
	getname(from);
	time(vector);
	date = arpadate(vector);
	p = to;
	for(i = 1; i < argc; i++)
	{	for(s = argv[i]; *s; *p++ = *s++);
		*p++ = ',';
	}
	if (p == to) then
	{	printf("To: ");
		gather(to);
	}
	else	*--p = '\000';
	if (*to == '\000') { printf("No destination?\n"); exit(); }
	printf("cc: "); gather(cc);
	printf("Subject: "); gather(subject);
	printf("Type letter:\n-----\n"); input();
	send(to);
	send(cc);
	if (unsent)
	{	fd = creat("unsent.mail",0644);
		if (fd < 0)
		{	printf("unable to create unsent .mail\n");
			exit(1);
		}
		writef(fd,letter);
		close(fd);
		chown("unsent.mail",myuid);
		printf("A copy of this letter has been left in 'unsent.mail'\n");
	}
	
	close(tmpfd);
	unlink(tempfile);
	
	if (netmsgs)
	{	printf("Send network mail now? ");
		gather(answer);
		if (answer[0] != 'y') exit(0);
		else	execl("/usr/bin/maildaemon", "send netmail", 0);
	}
}
/* name:
	gather

function:
	read a single line of console input into the user specified
	buffer.  Currently standard unix editing is in effect, but
	this will later be changed to use the same sexy editing as
	does the message inputting routine.

algorithm:
	Read a character:
	If it is an unescaped new line, null terminate the buffer and return.
	Otherwise, stash the character into the buffer.
	If the length of the buffer has been reached, echo a new line and
	return.

parameters:
	*char	pointer to user buffer of length SMALLBUFLEN

returns:
	nothing

globals:
	SMALLBUFLEN

calls:
	getchar
	slashc

called by:
	main
	send

history:
	Recoded by Mark Kampe 11/22/75

 */
gather(sp)
char *sp;
{
register char c;
register char *p;

p = sp;
while( ((c = getchar(0)) != '\n') && (c>0) )
{	if (c == '\\') *p++ = slashc();
	else *p++ = c;
	if ((p - sp) >= SMALLBUFLEN) break;
}
*p = '\0';
}


/* name:
	writef

function:
	Write a null terminated string

algorithm:
	Determine the length of the string.
	Write it out.
 CAVEAT	This call is not buffered, so use it carefully or pay the cost
	of high I/O expense.  It was writted to decrease subroutine linkage
	 global variable referencing and module size.  But those wins can
	easily be lost if writef is consistantly called with small strings.

parameters:
	int	file descriptor of output file.
	*char	pointer to null terminated string.

returns:
	int	value returned by write.

globals:

calls:
	write	(system)

called by:
	lotsa people

history:
	Initially coded by Mark Kampe 11/22/75

 */
writef(afd,str)
int afd;
char *str;
{	register int count;
	register char *s;

	s = str;
	for(count=0; *s++; count++);

	return(write(afd,str,count));
}

/* name:
	input

function:
	To accept the text of the message while doing all of the sexy
	sndmsg type editing.

algorithm:
	Allocate a huge buffer.
	Read characters (editing sexily as I go)
	Return when I get a ctl-d or ctl-z

parameters:
	none

returns:
	With a null terminated letter in the string pointed to by
	the global variable letter.

globals:
	letter	address of the buffer.

calls:
	rawmode
	normal
	writef
	write	system
	printf
	getchar
	sbreak	system
	gtty	system

called by:
	main

history:
	Originally coded by someone at Berkeley
	Fixed up and augmented by Mark Kampe.

 */
input()
{
char *tp;
register char *p,c;
register int i;
int eomem;
char filename[50];

p = letter = sbrk(1000); /* Tried to avoid this! */
eomem = letter+1000;
gtty(0,ttys);

rawmode();
loop	{
		c = getchar(0);
		if (p >= eomem)
		{	sbrk(1000);
			eomem =+ 1000;
		}
		switch (c)
			{
case controla:	/* tty oriented character delete */
			if (p > letter)
			{	write(1,"\\",1);
				write(1,--p,1);
			}
			continue;

case controlb:	/* input a file at this point */
case controlf:		printf("\nInput file: ");
			normal();
			gather(filename);
			if ((fd = open(filename,0)) < 0)
				printf("Couldn't open %s\n",filename);
			else
			{	sbrk(512);
				eomem =+ 512;
				for(i=read(fd,p,512); i>0; i=read(fd,p,512))
				{	p =+ i;
					sbrk(512);
					eomem =+ 512;
				}
				close(fd);
				printf("%s has been included\n", filename);
			}
			rawmode();
			continue;

case controlc:	/* breakout */
#ifdef unixchars
case del:
#endif
			normal();
			exit();

case controld:	/* normal end of message */
case controlz:		if (*(p-1) != '\n')
			{	*p++ = '\n';
				printf("\n");
				/* Guarentee msg ends with a new line */
			}
			*p = '\000';
			printf("-----\n");
			goto out;

case controlh:		if (p > letter) write(1, " \b", 2);
#ifdef unixchars
case '#':
#endif
			if (p > letter) p--;
			continue;

case controlr:	/* retype current line */
			tp = p;
			while ((tp > letter) && (*tp != '\n')) tp--;
			*p = '\0';
			if (tp == letter) write(1,"\n",1);
			writef(1,tp);
			continue;

case controls:	/* retype entire message */
			*p = '\000';
			write(1,"\n",1);
			writef(1,letter);
			continue;

case controlw:	/* back up over the last word typed */
			--p;
			while((p > letter) &&
				((*p != ' ') &&
				 (*p != ',') &&
				 (*p != '\n') &&
				 (*p != '\t') ) )
				{ write(1,"\b \b",3);
				  p--;
				};
			while ((p>letter) &&
			       ((*p == ' ') || (*p == '\t')) )
			{	write(1,"\b \b",3);
				p--;
			};
			*++p = '\0';
			continue;

case controlx:	/* line delete */
			write(1,"XXX",3);
#ifdef unixchars
case '@':
#endif
			write(1,"\n",1);
			p--;
			while ((p >= letter) && (*p != '\n')) p--;
			*++p = '\0';
			continue;

case abortchar:		/* sigh */
			normal();
			abort();

case '\\':		c = slashc();
default:		*p++ = c;
			} /* end switch */
	} /* end of while loop */
out:	/* restore console modes and make the tempfile */
	normal();
	tmpfile(tempfile);	/* get a filename */
	if ((tmpfd = creat(tempfile,0644)) < 0)
	{	printf("Unable to create temp file\n");
		exit(1);
	}
	
	write(tmpfd,"Date: ",6);
	writef(tmpfd,date);
	write(tmpfd,"\nFrom: ",7);
	writef(tmpfd,from);
	writef(tmpfd," at UCLA-ATS");
	if (*subject)
	{	write(tmpfd,"\nSubject: ",10);
		writef(tmpfd,subject);
	}
	write(tmpfd,"\nTo: ",5);
	writef(tmpfd,to);
	if (*cc)
	{	write(tmpfd,"\nCC: ",5);
		writef(tmpfd,cc);
	}
	write(tmpfd,"\n-----\n",7);
	writef(tmpfd,letter);
	write(tmpfd,"-----\n\n",7);
	/* whole message is now in temp file */
	/* close it and reopen it for input */
	close(tmpfd);
	tmpfd = open(tempfile,0);
} /* end of input */
/* name:
	rawmode and normal

function:
	to put the console into raw mode and normal mode respectively.

globals:
	oldmode

calls:
	stty

called by:
	input

history:
	written at berkeley

 */
normal()
{
ttys[2] = oldmode;
stty(0,ttys);
}

rawmode()
{
oldmode = ttys[2];
ttys[2] =| 040; /* raw mode */
stty(0,ttys);
}

/* name:
	send

function:
	To take a list of recipients and take steps to deliver the
	message (now in the temp file) to all of them.

algorithm:
	parse off a name.
	If it is a name:, open that file and read from it for a while.
	If it is a local user id, call post
	If it is a network user id, call netpost

parameters:
	Pointer to a null terminated characterstring which is a list
	of recipients.

returns:

globals:
	unsent

calls:
	valid
	open	(system)
	printf
	network
	findlocal
	netpost
	post

called by:
	main

history:
	Coded by someone at berkely.
	Minor modifications by Mark Kampe.

 */
send(list)
char *list;
{
register char *name,*curp;
char user[40];
register char c;

curp = list;
while (file || *curp)
{	name = user;
	while (valid(c = file?getchar(namefd):*curp++))
		*name++ = c;
	*name = '\0';
	switch (c)
		{
case ':':	if (file)
			printf("Nested name files not allowed.\n");
		else
			{
			if ((namefd = open(user,0)) < 0)
				{
				printf("Couldn't open %s\n",user);
				unsent++;
				continue;
				}
			else
				{
				file++;
				continue;
				}
			}

case -1:	close(namefd);
		file = false;
		continue;
case ',':
case ' ':
case '\n':
case '\0':
		if (*user == '\000') continue;
		printf("%s...",user);
		if (network(user))
		{	netpost(user,hostname);
			continue;
		}
		else if (findlocal(user))
		{	stcat("/mailbox",mailbox);
			post();
			continue;
		}
		else
		{	printf("Not a known user\n");
			unsent++;
			continue;
		}

default:	printf("Illegal terminator %c.\n",c);
		printf("User name %s ignored.\n",user);
		} /* end switch */
	}
} /* end send */
/* name:
	findlocal

function:
	To ascertain whether or not someone is a local user, and
	if they are, to find the name of their root directory.

algorithm:
	Rewind the password file.
	Search it for a line starting with the user name.
	If found:
		extract all the info about uid, gid mailbox, etc.
		return.
	Else, continue the search.
	Announce that he isn't a known user.

parameters:
	*char	pointer to null terminated user name.

returns:
	boolean	whether or not he was found.

globals:
	pwfd
	uid
	gid
	mailbox
	pwcount

calls:
	getpwchar
	seek	(system)

called by:
	send

history:
	Written by Mark Kampe

 */
findlocal(name)
char *name;
{
register char *np;
register char pwc;

/*	rewind the password file */
seek(pwfd,0,0);
pwcount = 0;

pwc = 1;
while(pwc > 0)
{	np = name;	/* search for a line starting with name */
	for(pwc = getpwchar(); pwc == *np++; pwc = getpwchar());
	if ((pwc == ':') && (*--np == '\000')) goto gotuser;
	while( (pwc != '\n') && (pwc > 0) ) pwc = getpwchar();
}
return(false);

gotuser:	/* extract all neat info from pw entry */
for(pwc = getpwchar(); pwc != ':'; pwc = getpwchar());
/* we have skipped over the password */
for(uid = 0; (pwc = getpwchar()) != ':'; uid =+ (9*uid) + pwc - '0');
for(gid = 0; (pwc = getpwchar()) != ':'; gid =+ (9*gid) + pwc - '0');
for(pwc = getpwchar(); pwc != ':'; pwc = getpwchar());
/* we have skipped over the gecos bin */
np = mailbox;
for(pwc = getpwchar(); pwc != ':'; pwc = getpwchar()) *np++ = pwc;
*np = '\000';
return(true);
}
/* name:
	network

function:
	To determine whether a user is a network user, and if he
	is, to break the name up into a hostname and ultimately
	a list of user names.

algorithm:
	Look for an @ in the name, if not found, not net
	Copy the hostname into a separate buffer and truncate
		it off of the user name.

parameters:
	*char	pointer to null terminated user name.

returns:
	boolean	Whether or not guy was a network user.
	and	if he was:
		Hostname has been truncated off of user name and
		put into the global buffer hostname.

globals:
	hostname.

calls:

called by:
	send

history:
	Written by Mark Kampe	11/27/75

 */
network(name)
char *name;
{	register char *c;
	register char *d;
	register char *e;

	for(c = name; *c; c++) if (*c == '@') goto netname;
	return(false);

netname:
	*c++ = '\000';
	d = hostname;
	for(e = "/dev/net/"; *e;) *d++ = *e++;
	while(*d++ = *c++);
	return(true);
}
/* name:
	tempfile

function:
	To select a unique name for and creat a temporary file.

algorithm:
	Use send<processid> as the filename.

parameters:
	*char	pointer to user buffer of adequate length.

returns:
	*char	pointer to the chosen name
	and	tmpfd is the file descriptor for that file.

globals:
	tmpfd

calls:
	creat
	getpid

called by:
	input

history:
	Coded by someone at Berkeley

 */
tmpfile(ubuf)
char *ubuf;
{
register int i;
register char *p1;
register char *p2;

p1 = ubuf;
for(p2 = "/tmp/send"; *p2 ; *p1++ = *p2++);
p2 = getpid();
for(i=0; i<5; i++)
{	*p1++ = (p2 & 07) + '0';
	p2 =>> 3;
}
return(ubuf);
}
/* name:
	post

function:
	To mail a letter (in tempfile) to some individual unix user.

algorithm:
	Create a mailbox if he doesn't have one.
	If he had one make sure it is not in use.
	Append the contents of the tempfile to it.
	Make recipient the owner if he wasn't already.

parameters:
	none
	but..	null terminated name of recipients directory is in in mailbox.

returns:
	boolean	Whether or not it was successfully sent.

globals:
	mailbox
	mbfd
	tmpfd
	bigbuf
	unsent

calls:
	creat
	seek
	read
	write
	printf
	stcat

called by:
	send

history:
	WRewritten by Mark Kampe 11/24/75

 */
post()
{
	register int i;

	if (stat(mailbox,&statb) < 0)
	{	mbfd = creat(mailbox,0644);
		if (mbfd < 0)
		{	printf("Unable to create mailbox\n");
			unsent++;
			return(false);
		}
	}
	else
	{	if (statb.s_nlinks > 1)
		{	printf("Mailbox is busy\n");
			unsent++;
			return(false);
		}
		mbfd = open(mailbox,2);
		if (mbfd < 0)
		{	printf("Unable to open mailbox\n");
			unsent++;
			return(false);
		}
		seek(mbfd,0,2);	/* seek end of file */
	}

	seek(tmpfd,0,0); /* rewind the file containing the message */
	i = read(tmpfd,bigbuf,512);
	while(i > 0)
	{	write(mbfd,bigbuf,i);
		i = read(tmpfd,bigbuf,512);
	}

	close(mbfd);
	chown(mailbox,uid);
	printf("ok\n");
	return(true);
} /* end post */
/* name:
	netpost

function:
	to attempt to mail off a piece of network mail.

algorithm:
	Contrive a unique name for a network mail file.
	Create it in the netmail daemon's mailbox
	put destination host, users and sender names into file.
	copy message into the file.

parameters:
	*char	pointer to null terminated user name
	*char	pointer to null terminated host name

returns:
	boolean	whether or not it worked

globals:
	unsent
	netmsgs		count of number of net msgs so far
	tmpfd
	bigbuf

calls:
	read
	write
	printf
	creat
	close
	stat
	chown

called by:
	send

history:
	Initially coded by Mark Kampe

 */
netpost(uname,hname)
 char *uname;
 char *hname;
{
	register char *p1;
	register char *p2;
	register int i;

	if (stat(hname,&statb) == -1)
	{	printf("host is unknown\n");
		unsent++;
		return(false);
	}

	p2 = netfile;
	for(p1 = "/usr/netmail/"; *p1; *p2++ = *p1++);
	i = p2;
	for(p1 = from; *p1; *p2++ = *p1++);
	while((p2 - i) < 14) *p2++ = '0';
	*p2-- = '\000';
	for(i = 'a'; i <= 'z'; i++)
	{	*p2 = i;
		if (stat(netfile,&statb) == -1) goto gotname;
	}
	printf("Too many messages awaiting transmission\n");
	unsent++;
	return(false);

gotname:
	mbfd = creat(netfile, 0444);
	if (mbfd < 0)
	{	printf("Unable to create mailfile for %s@%s\n",
			uname,hname);
		unsent++;
		return(false);
	}

	writef(mbfd,hname);
	write (mbfd,":",1);
	writef(mbfd,uname);
	write (mbfd,":",1);
	if (findlocal(from)) writef(mbfd,mailbox);
	write (mbfd, ":\n",2);

	seek(tmpfd, 0, 0);
	for(i = read(tmpfd,bigbuf,512); i; i = read(tmpfd,bigbuf,512))
		write(mbfd,bigbuf,i);

	close(mbfd);
	chown(netfile,myuid);
	printf("Queued for transmission\n");
	netmsgs++;
	return(true);
}

/* name:
	getname 

function:
	To find out the name of the user who forked me.

algorithm:
	Get my real user id and look it up in the password table

parameters:
	*char	pointer to buffer where name should be placed.

returns:
	*char pointer to buffer wher callers's name was placed.

globals:

calls:
	getuid
	getpw
	printf

called by:
	main

history:
	Rewritten by Mark Kampe

 */
getname(caller)
char *caller;
{
char linebuf[100];
char *cp,*lp;

myuid = getuid() & 0377;
if (getpw(myuid, linebuf))
{
	printf("Your user id is not in the password file?!?\n");
	exit();
}
cp = caller;
lp = linebuf;
while(*lp != ':') *cp++ = *lp++;
*cp = '\000';
return(caller);
}


/* name:
	slashc

function:
	Given that the last input character seen was a backslash, this
	routine returns the character that is being escaped.

algorithm:
	If terminal is half ascii
		If next char is lower case, return its upper case counterpart.
		If it is the preimage of a non-half ascii character, return
			that character.
	Else, return the next character.

parameters:

returns:
	A character.

globals:
	ttys	to check out the console modes.

calls:
	getchar

called by:
	people who do rawmode input (namely input)

history:
	Initial coding by someone at berkeley.

 */
slashc()
{
char c;
c = getchar(0);
if (ttys[2] & 04) /* Half-ASCII */
	{
	if (c >= 'a' && c <= 'z') return(c-'a'+'A');
	switch (c)
		{
case '!':	return('|');
case '\'':	return('`');
case '^':	return('~');
case '(':	return('{');
case ')':	return('}');
default:	return(c);
		} /* end switch */
	} /* end half-ASCII */
	else return(c);
} /* end slashc */



/* name:
	getchar

function:
	To read a character from a specified file.

algorithm:
	Do a read, and if we got an end of file, return a -1.
	CAVEAT	Input is unbuffered.

parameters:
	int	file descriptor of file to be read from.

returns:
	char	or -1;

globals:

calls:
	read	(system)

called by:
	lots of people

history:
	Someone at berkeley.

 */
char getchar(cfd)
{	char c;
	register int i;

	i = read(cfd,&c,1);
	if (i <= 0) return(-1);
	else return(c&0177);
}
char getpwchar()
{
tryagain:
	if (pwcount > 0)
	{	pwcount--;
		return(*pwptr++);
	}
	else
	{	pwcount = read(pwfd,pwbuf,512);
		if (pwcount <= 0) return(-1);
		pwptr = pwbuf;
		goto tryagain;
	}
}
valid(ch)
char ch;
{
return(((ch >= 'a') && (ch <= 'z')) | ((ch >= '0') && (ch <= '9')) |
	(ch == '.') | (ch == '/') | (ch == '-') | (ch == ';') |
	(ch == '@') | (ch == '(') | (ch == ')') |
	((ch >= 'A') && (ch <= 'Z'))   );
}
stcat(latter,former)
char *latter,*former;
{
register char *fp,*lp;
fp = former;
lp = latter;
while (*fp++);
fp--;
while (*fp++ = *lp++);
}
/* name:
	arpadate

function:
	to get an ARPA format date (format described in rfc 680)

algorithm:
	Get the unix format date and jumble it around to be arpa format
	Unix format is:
	day mmm dd hh:mm:ss yyyy
	Arpa format is:
	dd mmm yyyy at hhmm-zzz

parameters:
	pointer to the doubleword time

returns:
	pointer to the arpa format date corresponding to that time

globals:
	dbuf

calls:
	ctime
	localtime

called by:
	main

history:
	Designed and coded by mark Kampe 1/9/76

 */
char *arpadate(tvec)
 int tvec[2];
{	register int *i;
	register char *p;
	register char *t;

	t = ctime(tvec);
	p = dbuf;

	*p++ = t[8];
	*p++ = t[9];
	*p++ = ' ';
	*p++ = t[4];
	*p++ = t[5];
	*p++ = t[6];
	*p++ = ' ';
	*p++ = t[20];
	*p++ = t[21];
	*p++ = t[22];
	*p++ = t[23];
	*p++ = ' ';
	*p++ = 'a';
	*p++ = 't';
	*p++ = ' ';
	*p++ = t[11];
	*p++ = t[12];
	*p++ = t[14];
	*p++ = t[15];
	*p++ = '-';
	*p++ = 'P';
	i = localtime(tvec);
	if (i[8]) *p++ = 'D';
	else *p++ = 'S';
	*p++ = 'T';
	*p++ = '\000';

	return(dbuf);
}


