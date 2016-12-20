#!/usr/bin/python
#
#   This is a utility to operate on exam-question files,
#   pulling out an exam, solutions, or rubric.  This enables
#   me to put everything I know about an exam question in one
#   file and avoid any copy-pastes, or even format tweaking.
#
import os
import sys
from question import question
from pager import pager
from optparse import OptionParser

# TODO
#   ?default output files based on exam name?
#


#
# copy a specified input file to the output
#
def interpolate(infile, output):

    # see if we can open the input file
    if not os.path.exists(infile):
        print "Unable to open file: %s" % (infile)
        return

    # process the input file
    input = open(infile, 'rb')
    for line in input:
        output.write(line)
    input.close()


if __name__ == '__main__':
    """ process the arguments and input files """

    umsg = "usage: %prog [options] examfile.csv"
    parser = OptionParser(usage=umsg)
    parser.add_option("-q", "--questions", dest="qdir", metavar="DIR",
                      default=None)
    parser.add_option("-x", "--exams", dest="exams", metavar="FILE",
                      default=None)
    parser.add_option("-s", "--solns", dest="solns", metavar="FILE",
                      default=None)
    parser.add_option("-r", "--rubric", dest="rubric", metavar="FILE",
                      default=None)
    parser.add_option("-p", "--prolog", dest="soln_prolog", metavar="FILE",
                      default="soln_prolog.html")
    parser.add_option("-e", "--epilog", dest="soln_epilog", metavar="FILE",
                      default="soln_epilog.html")
    parser.add_option("-l", "--length", dest="page_length", metavar="LINES",
                      default="65")
    parser.add_option("-w", "--width", dest="line_width", metavar="CHARS",
                      default="90")
    (opts, files) = parser.parse_args()

    # make sure we got a valid exam file
    if not files:
        input = sys.stdin
    else:
        examfile = files[0]
        if not os.path.exists(examfile):
            sys.stderr.write("ERROR - no such file: %s\n" % examfile)
            sys.exit(-1)
        input = open(examfile)

    # start the exam file if any
    outX = None if opts.exams is None else open(opts.exams, 'w')
    pager = None if outX is None else \
        pager(outX, int(opts.line_width), int(opts.page_length))

    outR = None if opts.rubric is None else open(opts.rubric, 'w')

    # start the solutions file (if any)
    outS = None if opts.solns is None else open(opts.solns, 'w')
    if outS and opts.soln_prolog:
        interpolate(opts.soln_prolog, outS)

    # process each exam line in the input file
    lineNum = 0
    heading = False
    for line in input:
        lineNum += 1

        # strip off leading/trailing blanks
        stripped = line.strip()
        if stripped == "":
            continue

        # ignore comment lines
        if stripped.startswith('#'):
            continue

        # pull out the fields for this question
        fields = stripped.split(',')
        if len(fields) < 4:
            print("ignoring line %d: %d fields" % (lineNum, len(fields)))
            continue

        xname = fields[0].strip()
        qnum = fields[1].strip()
        qname = fields[2].strip()
        role = fields[3].strip()

        # print out the information for this question
        q = question(qname, role, qnum, opts.qdir)
        sum = q.summary()

        if not heading:
            print "## " + q.heading(False)
            print "-- " + q.heading(True)
            heading = True

        # prefixed number may be line count or question number
        prefix = "   "
        if outX:
            prefix = "%2d " % (q.printExam(pager))
        elif qnum != "":
            prefix = "%2s " % (qnum)
        print prefix + sum

        if outS:
            q.printSolution(outS)
        if outR:
            q.printRubric(outR)

    # generate the solution epilog (if any)
    if outS and opts.soln_epilog:
        interpolate(opts.soln_epilog, outS)

    # close al the output files
    if outX is not None:
        pager.flush(True)
        outX.close()
    if outS is not None:
        outS.close()
    if outR is not None:
        outR.close()
