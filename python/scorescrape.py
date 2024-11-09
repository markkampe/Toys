#!/usr/bin/python3
"""
   process a file full of scraped coments vs a rubric and
   produce a score file
"""
import sys
import os.path
import argparse

template = []       # standard score output

item_default = {}    # per item, default value
item_score = {}      # per item, score
min_score = {}       # per item, min possible
max_score = {}       # per item, max possible
item_comments = {}   # per item, comments
student_name = ""


def digest(rubric, tag):
    """ read rubric file and accumulate a score model """
    if os.path.exists(rubric):
        with open(rubric, 'rb', encoding='ascii') as instream:
            for line in instream:
                if line.startswith("#"):
                    fields = line.split()
                    if len(fields) >= 4 and fields[1] == tag:
                        item = fields[2]
                        max_score[item] = int(fields[3])
                        min_score[item] = int(fields[4]) if len(fields) > 4 else 0
                        item_default[item] = \
                            int(fields[5]) if len(fields) > 5 else int(fields[3])
                else:
                    # it is output
                    template.append(line)
    else:
        sys.stderr.write("unable to open rubric file " + rubric)


def score_reset():
    """ reset all scores to default values """
    for k in item_default.keys():
        item_score[k] = item_default[k]
        item_comments[k] = []
    student_name = ""


def score(line, tag):
    """ parse a score out of a SCORE comment """
    # lex off the score item name
    start = line.index(tag) + len(tag)
    while line[start:start+1].isspace():
        start += 1
    end = start + 1
    while line[start:end+1].isalnum():
        end += 1
    item = line[start:end]
    if item not in item_score.keys():
        sys.stderr.write(f"Unknown rubric item: {line}")
        return

    # skip over colons and white space
    start = end
    while line[start:start+1].isspace() or line[start:start+1] == ":":
        start += 1

    # see if the score item starts with a +/-
    sign = line[start:start+1]
    if sign == "+" or sign == "-":
        start += 1

    # find the end of the number
    end = start + 1
    while line[end:end+1].isdigit() or line[end:end+1] == ".":
        end += 1
    num = float(line[start:end])

    # calculate the updated score
    cur = item_score[item]
    if sign == "+":
        cur += num
    elif sign == "-":
        cur -= num
    else:
        cur = num

    # sanity check the updated score
    if cur < min_score[item]:
        sys.stderr.write(f"ERROR: {item} below minimum {min_score[item]}\n")
        cur = min_score[item]
    elif cur > max_score[item]:
        sys.stderr.write(f"ERROR: {item} above maximum {max_score[item]}\n")
        cur = max_score[item]

    item_score[item] = cur

    # look for comments
    while line[end:end+1].isspace():
        end += 1
    if end < len(line):
        item_comments[item].append(line[end:])
    return


def process(file, tag, nametag):
    """ process a file of scraped comments """
    if os.path.exists(file):
        # find and process all of the SCORE comments
        input = open(file, 'rb')
        for line in input:
            if tag in line:
                score(line, tag)
            elif nametag in line:
                global student_name
                student_name = line

        input.close()
    else:
        sys.stderr.write("unable to open input file " + file)


def total():
    """ compute the total score for this file """
    sumtotal = 0
    maxtotal = 0
    for k in item_score.keys():
        sumtotal += item_score[k]
        maxtotal += max_score[k]
    # FIX find some way to exclude extra credit
    item_score["TOTAL"] = sumtotal
    max_score["TOTAL"] = maxtotal


def interpolate(comments=False):
    """ produce the standard template output, interpolating scores """
    for line in template:
        if "$" in line:
            for i in range(0, len(line)):
                if line[i:i+1] == "$":
                    # find the end of the identifier
                    start = i+1
                    end = i+1
                    while l[start:end+1].isalnum():
                        end += 1
                    id = line[start:end]
                    if id in item_score.keys():
                        sys.stdout.write(l[0:start-1])
                        sys.stdout.write("%.1f/%.1f" %
                                         (item_score[id], max_score[id]))
                        sys.stdout.write(l[end:])
                        if comments and id in item_comments.keys():
                            for line in item_comments[id]:
                                sys.stdout.write("\t" + l)
                    elif id == "STUDENTNAME":
                        sys.stdout.write(student_name + "\n")
                    else:
                        sys.stderr.write(f"unknown {tag} item: {id}\n")
        else:
            sys.stdout.write(l)


if __name__ == '__main__':
    """ process specified input files, or test data """

    # process arguments to get input file names
    DESCR = "extract/accumulate score information from file annotations"
    parser = argparse.ArgumentParser(description=DESCR)
    parser.add_argument("file", nargs="+",
                        help="score files to be scraped")
    parser.add_argument("-r", "--rubric", default=None,
                        help="file of rubric rules")
    parser.add_argument("-t", "--tag", default='SCORE',
                        help="tag for score to be extracted")
    parser.add_argument("-n", "--name", default='@author',
                        help="tag for student name")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="verbose output for each copy")
    parser.add_argument("-c", "--comments",  action="store_true",
                        help="preserve score comments")
    args = parser.parse_args()

    # digest the rubric
    if args.rubric is not None:
        digest(args.rubric, args.tag)

    # dump out the known rubric items
    if args.verbose:
        sys.stdout.write("Rubric items:\n")
        for k in item_default.keys():
            sys.stdout.write("\t%s min=%d, max=%d, dflt=%d\n" %
                             (k, min_score[k], max_score[k], item_default[k]))

    # process the specified input files
    if file is None:
        parser.print_help()
    else:
        for f in file:
            score_reset()
            process(f, args.tag, args.name)
            total()
            interpolate(args.comments)

    sys.exit(0)
