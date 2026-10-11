/*
 * bmp - analyze and create .bmp files
 *
 *	usage: bmp [-v] [--outfile=name] infile ...
 *
 *		if no outfile is specified, all input files are assumed
 *		   to be bmp files, and their characteristics are dumped.
 *		if an oufile is specified, it is assumed to be a file of
 *		   text input lines to be convered into a bitmap.
 */
#include <stdio.h>
#include <getopt.h>
#include <fcntl.h> 
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

# pragma pack(push, 1)	/* int on a short boundary	*/
struct bmp_head {
	char signature[2];	/* BM	*/
	int fileSize;		/* should be correct	*/
	int reserved;
	int dataOffset;		/* offset of start of data	*/
};
#pragma pack(pop)

struct bmp_info {
	int hdrSize;		/* length of this structure	*/
	int width;			/* pixels per scan-line		*/
	int height;			/* number of scan-lines		*/
	short planes;		/* number of image planes	*/
	short bitsPer;		/* number of bits per pixel	*/
	int compression;	/* see below				*/
	int imageSize;		/* number of bytes of image	*/
	int x_per_m;		/* meters per pixel			*/
	int y_per_m;		/* meters per pixel			*/
	int colors_used;	/* total number of colors	*/
	int colors_important;
};

char *comp_type[] = {"BI_RGB", "BI_RLE8", "BI_RLE4"};

struct bmp_color {
	unsigned char red;
	unsigned char green;
	unsigned char blue;
	unsigned char reserved;
};

char *usage = "[-v] [--oufile=file] input ...";
int verbose = 0;

#define S_RWALL S_IWUSR+S_IRUSR+S_IWGRP+S_IRGRP+S_IWOTH+S_IROTH
#define MAXLINE 128	/* max 1023 pixels	*/
#define MAXROWS 128	/* max scan lines	*/

/*
 * print out the header info
 */
int bmp_dump(char *infile) {
	struct bmp_head header;
	struct bmp_info info;
	struct bmp_color color;
	int expected_size = 0;
	char inbuf[MAXROWS][MAXLINE/8];
	char *bit_on = "**";	/* two characters per horizontal pixel	*/
	char *bit_off = "  ";

	int infd = open(infile, O_RDONLY);
	if (infd < 0) {
		fprintf(stderr, "Unable to open input file: %s\n", infile);
		return(-1);
	}

	printf("%s:\n", infile);

	/* all .bmp files start with a simiple file header	*/
	int got = read(infd, &header, sizeof header);
	if (got != sizeof header) {
		fprintf(stderr, "Unable to read BMP header\n");
		return(-1);
	}
	expected_size += got;

	if (header.signature[0] != 'B' || header.signature[1] != 'M') {
		fprintf(stderr, "Not a .bmp\n");
		return(-1);
	}
	printf("    file size:\t%d (bytes)\n", (int) header.fileSize);
	printf("    data offset:\t%d\n", header.dataOffset);

	/* all .bmp files have an image info header	*/
	got = read(infd, &info, sizeof info);
	if (got != sizeof info) {
		fprintf(stderr, "Unable to read BMP info\n");
		return(-1);
	}
	expected_size += got;

	/* figure out how large we expected the image to be	*/
	int scan_lines = info.height;
	int bytes_per = 4 * (((info.width * info.bitsPer) + 31) / 32);
	expected_size += scan_lines * bytes_per;

	if (verbose)
		printf("    header size: %d (bytes)\n", info.hdrSize);
	printf("    image size:\t%d ... %d %d-byte (%d-pixel) scan-lines\n", 
			info.imageSize, scan_lines, bytes_per, info.width);
	printf("    planes:\t%d\n", info.planes);
	printf("    bits per:\t%d\n", info.bitsPer);
	printf("    compression: %d (%s)\n", 
			info.compression, comp_type[info.compression]);
	if (verbose) {
		printf("    h/v res:\t%dx%d/m\n", info.x_per_m, info.y_per_m);
		printf("    colors:\t%d/%d\n", info.colors_important, info.colors_used);
	}

	/* color definitions will only be present for <= 256 colors	*/
	if (info.bitsPer < 8) {
		for(int i = 0; i < info.colors_used; i++) {
			got = read(infd, &color, sizeof color);
			if (got != sizeof color) {
				fprintf(stderr, "Unable to read BMP color #%d\n", i);
				return(-1);
			}
			expected_size += got;
			if (verbose)
				printf("        %d:\t<%d,%d,%d>\n",
					   i, color.red, color.green, color.blue);

			/* figure out whether ones are black or white	*/
			unsigned int non_black = color.red + color.green + color.blue;
			if (i == 0)
				bit_off = (non_black > 0) ? "**" : "  ";
			else
				bit_on = (non_black > 0) ? "**" : "  ";
		}
	}

	if (header.fileSize != expected_size)
		fprintf(stderr, "WARNING: file size = %d vs %d expected\n",
				header.fileSize, expected_size);

	/* we can try to dump out simple monochrome images */
	if (verbose && info.planes == 1 && info.bitsPer == 1) {
		/* construct an attractive separator	*/
		char *p = inbuf[0];
		for(int i = 0; i < info.width; i++) {
			*p++ = '='; *p++ = '=';
		}
		*p++ = '\n';	*p++ = 0;
		p = &inbuf[0][4 + info.width/2];
		for(char *s = " BITMAP "; *s; *p++ = *s++);
		fputs(inbuf[0], stdout);

		/* re-read every line			*/
		for(int i = 0; i < scan_lines; i++)
			got = read(infd, &inbuf[i][0], bytes_per);

		/* print them in reverse order	*/
		for(int i = scan_lines - 1; i >= 0; i--) {
			for(int j = 0; j < info.width; j++) {
				unsigned int byte = inbuf[i][j/8];
				unsigned int bit = 0x80 >> (j%8);
				fputs(byte & bit ? bit_on : bit_off, stdout);
			}
			putc('\n', stdout);
		}
	}
	close(infd);
	return(0);
}

int new_bmp(char *infile, char *outfile) {
	char inbuf[MAXLINE];	/* textinput	*/
	char outbuf[MAXROWS][MAXLINE/8];
	struct bmp_head header;
	struct bmp_info info;
	struct bmp_color color;

	/* start by measuring the input image */
	FILE *textfile = fopen(infile, "r");
	if (textfile == NULL) {
		fprintf(stderr, "Unable to open input file: %s\n", infile);
		return(-1);
	}

	int lines = 0;
	int maxwid = 0;
	while(fgets(inbuf, sizeof inbuf, textfile) != NULL) {
		lines++;
		int wid = strlen(inbuf) - 1;
		if (wid > maxwid)
			maxwid = wid;
	}
	if (verbose)
		printf("%s: %d %d-pixel lines\n", infile, lines, maxwid);

	/* figure out how big the output file will be */
	int expected_size = sizeof header + sizeof info + (2 * sizeof color);
	int longs_wide = (maxwid + 31)/32;		/* round up to four byte boundary	*/
	int bytes_wide = longs_wide * 4;		/* that, in bytes */
	expected_size += lines * bytes_wide;
	if (verbose)
		printf("expected file size: %d+%d + 2*%d + %d*%d = %d\n",
			(int) sizeof header, (int) sizeof info, (int) sizeof color,
			lines, bytes_wide, expected_size);
		

	/* create the output file and headers	*/
	int outfd = creat(outfile, S_RWALL);
	if (outfd < 0) {
		fprintf(stderr, "Unable to create out file: %s\n", outfile);
		return(-1);
	}

	/* file header	*/
	header.signature[0] = 'B'; header.signature[1] = 'M';
	header.fileSize = expected_size;
	header.reserved = 0;
	header.dataOffset = sizeof header + sizeof info + (2 * sizeof color);
	write(outfd, &header, sizeof header);

	/* bmp header */
	info.hdrSize = sizeof info;
	info.width = maxwid;
	info.height = lines;
	info.planes = 1;
	info.bitsPer = 1;		/* monochrome */
	info.compression = 0;	/* BI_RGB */
	info.imageSize = lines * bytes_wide;
	info.x_per_m = 2925;	/* 1/3 mm */
	info.y_per_m = 2925;	/* 1/3 mm */
	info.colors_used = 2;	/* black and white */
	info.colors_important = 2;
	write(outfd, &info, sizeof info);

	/* black and white color definitions */
	color.red = 0;
	color.green = 0;
	color.blue = 0;
	color.reserved = 0;
	write(outfd, &color, sizeof color);
	color.red = 255;
	color.green = 255;
	color.blue = 255;
	write(outfd, &color, sizeof color);
		
	/* start with a completely blank image	*/
	for(int i = 0; i < lines; i++)
		for(int j = 0; j < MAXLINE/8; j++)
			outbuf[i][j] = 0;

	/* read each line of input and turn it into bits */
	int pixels = 0;
	int scanlines = 0;
	rewind(textfile);
	while(fgets(inbuf, sizeof inbuf, textfile) != NULL) {
		/* turn each non-blank character into a black pixel */
		int byte_offset, bit_value;
		for(int i = 0; i < maxwid; i++) {
			if (inbuf[i] == '\n')
				break;
			/* blank space is white	*/
			if (inbuf[i] == ' ') {
			    byte_offset = i / 8;
			    bit_value = 0x80 >> (i%8);
			    outbuf[scanlines][byte_offset] |= bit_value;
			    pixels++;
			}
		}
		scanlines++;
	}
	fclose(textfile);

	/* write them out bottom to top */
	for(int i = scanlines - 1; i >= 0; i--)
		write(outfd, &outbuf[i][0], bytes_wide);

	if (verbose)
		printf("wrote %d %d-byte scan-lines, %d on-pixels\n",
				scanlines, bytes_wide, pixels);
	close(outfd);

	return(0);
}

int main(int argc, char *argv[]) {
	struct option long_options[] = {
		{"verbose", no_argument, 		NULL,	'v'},
		{"help",	no_argument, 		NULL,	'h'},
		{"outfile",	required_argument,	NULL,	'o'},
		{NULL,		0,					NULL,	0 }
	};
	char *outfile = NULL;

	int opt;
	while((opt = getopt_long(argc, argv, "vho:", long_options, NULL)) != -1) {
		switch(opt) {
			case 'v':
				verbose = 1;
				break;
			case 'o':
				outfile = optarg;
				break;

			case 'h':
			default:
				fprintf(stderr, "Usage: %s %s\n", argv[0], usage);
				exit(-1);
		}
	}

	/* at least one input file is required */
	if (optind >= argc) {
		fprintf(stderr, "Usage: %s %s\n", argv[0], usage);
		exit(-1);
	}

	if (outfile) {	/* creade a new bmp */
		exit(new_bmp(argv[optind], outfile));
	} else {	/* dump a bunch of bmps */
		int ret = 0;
		while(optind < argc) {
			ret += bmp_dump(argv[optind++]);
			printf("\n");
		}
		exit(ret);
	}
}
