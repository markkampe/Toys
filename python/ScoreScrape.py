#!/usr/bin/python
#
#   process a file full of scraped coments vs a rubric and
#   produce a score file
#
#
import sys
import os.path
from optparse import OptionParser

tag = "SCORE"

template = []       # standard score output

itemDefault = {}    # per item, default value
itemScore = {}      # per item, score
minScore = {}       # per item, min possible
maxScore = {}       # per item, max possible
itemComments = {}   # per item, comments


def digest(rubric):
    """ read rubric file and accumulate a score model """
    if os.path.exists(rubric):
        input = open(rubric, 'rb')
        for line in input:
            if line.startswith("#"):
                fields = line.split()
                if len(fields) >= 4 and fields[1] == tag:
                    item = fields[2]
                    maxScore[item] = int(fields[3])
                    minScore[item] = int(fields[4]) if len(fields) > 4 else 0
                    itemDefault[item] = int(fields[5]) if len(fields) > 5 else int(fields[3])
            else:
                # it is output
                template.append(line)
        input.close()
    else:
        sys.stderr.write("unable to open rubric file " + rubric)


def score_reset():
    """ reset all scores to default values """
    for k in itemDefault.keys():
        itemScore[k] = itemDefault[k]
        itemComments[k] = []


def score(line):
    """ parse a score out of a SCORE comment """
    # lex off the score item name
    start = line.index(tag) + len(tag)
    while line[start:start+1].isspace():
        start += 1
    end = start + 1
    while line[start:end+1].isalnum():
        end += 1
    item = line[start:end]
    if item not in itemScore.keys():
        sys.stderr.write("Unknown rubric item: %s" % (line))
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
    if line[start:end] == ".":
        end += 1
    while line[end:end+1].isdigit():
        end += 1
    num = float(line[start:end])

    # calculate the updated score
    cur = itemScore[item]
    if sign == "+":
        cur += num
    elif sign == "-":
        cur -= num
    else:
        cur = num

    # sanity check the updated score
    if cur < minScore[item]:
        sys.stderr.write("ERROR: %s below minimum %d\n" %
                         (item, minScore[item]))
        cur = minScore[item]
    elif cur > maxScore[item]:
        sys.stderr.write("ERROR: %s above maximum %d\n" %
                         (item, maxScore[item]))
        cur = maxScore[item]

    itemScore[item] = cur

    # look for comments
    while line[end:end+1].isspace():
        end += 1
    if end < len(line):
        itemComments[item].append(line[end:])
    return


def process(file):
    """ process a file of scraped comments """
    if os.path.exists(file):
        # find and process all of the SCORE comments
        input = open(file, 'rb')
        for line in input:
            if tag in line:
                score(line)
        input.close()
    else:
        sys.stderr.write("unable to open input file " + file)


def total():
    """ compute the total score for this file """
    sumtotal = 0
    maxtotal = 0
    for k in itemScore.keys():
        sumtotal += itemScore[k]
        maxtotal += maxScore[k]
    itemScore["total"] = sumtotal
    maxScore["total"] = maxtotal


def interpolate():
    """ produce the standard template output, interpolating scores """
    for l in template:
        if "$" in l:
            for i in range(0, len(l)):
                if l[i:i+1] == "$":
                    # find the end of the identifier
                    start = i+1
                    end = i+1
                    while l[start:end+1].isalnum():
                        end += 1
                    id = l[start:end]
                    if id in itemScore.keys():
                        sys.stdout.write(l[0:start-1])
                        sys.stdout.write("%.1f/%.1f" %
                                         (itemScore[id], maxScore[id]))
                        sys.stdout.write(l[end:])
                        if id in itemComments.keys():
                            for l in itemComments[id]:
                                sys.stdout.write("\t" + l)
                    else:
                        sys.stderr.write("unknown %s item: %s\n" % (tag, id))
        else:
            sys.stdout.write(l)


if __name__ == '__main__':
    """ process specified input files, or test data """

    # process arguments to get input file names
    umsg = " [--rubric=file] scrapedinput ..."
    parser = OptionParser(usage=umsg)
    parser.add_option("-r", "--rubric", dest="rubric", metavar="FILE",
                      default=None)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      default=False)
    (opts, files) = parser.parse_args()

    # digest the rubric
    if opts.rubric is not None:
        digest(opts.rubric)

    # dump out the known rubric items
    if opts.verbose:
        sys.stdout.write("Rubric items:\n")
        for k in itemDefault.keys():
            sys.stdout.write("\t%s min=%d, max=%d, dflt=%d\n" %
                             (k, minScore[k], maxScore[k], itemDefault[k]))

    # process the specified input files
    if len(files) < 1:
        sys.stderr.write("usage: %s" + umsg + "\n")
    else:
        for f in files:
            score_reset()
            process(f)
            total()
            interpolate()

    sys.exit(0)
