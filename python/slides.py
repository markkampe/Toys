#!/usr/bin/python
#
#   process lectures to create an index to lecture slides
#
#
import sys
import os.path
from csv import reader
from optparse import OptionParser
import datetime


class schedule:
    """ This class accepts lectures, topics and readings
        and outputs them as an HTML schedule per session
    """
    def __init__(self, slidepath="", indent=4):
        """ initialize the instance variables """
        self.indent = indent
        self.slides = slidepath

    def addLecture(self, number, day, date, title, quiz):
        """ register a new lecture by its number and title
                number: integer lecture #, 0-> no lecture
                day: excel 3 letter day
                date: m/d/yyyy
                title: topic for this lecture/day
                quiz: what to put in quiz field
        """
        try:
            # only numbered lectures have slides
            l = int(number)
        except ValueError:
            l = 0
        if l != 0:
            self.printLecture(l, title)
        else:
            self.printActivity(title)

    def listHead(self):
        """ called to produce the start of the table definition """
        print "<OL type=\"1\">"

    def printActivity(self, subject):
        """ I don't think activities have any place here """
        return

    def printLecture(self, lecture, title):
        print '%s<LI><A href="%slecture_%s.pdf">%s</A></LI>' % \
              ((' ' * self.indent), self.slides, lecture, title)

    def listFin(self):
        print "</OL>"


class csvReader:
    """ This class reads CSV files for lectures, topics and readings
        and uses the schedule class to record them
    """
    def __init__(self, infile):
        input = open(infile, 'rb')
        self.instream = reader(input, skipinitialspace=True)

    def analyze(self, cols, lectHead=None):
        """ figure out which column contains what information """
        for c in range(len(cols)):
            s = cols[c]
            if s in ["Lecture", "lecture"]:
                self.cLect = c
            elif s in ["Topic", "topic", "Title", "title"]:
                self.cTop = c
            elif s in ["Day", "day"]:
                self.cDay = c
            elif s in ["Date", "date"]:
                self.cDate = c
            elif s in ["Quiz", "quiz"]:
                self.cQuiz = c
            elif s == lectHead:
                self.cLec = c

    # note a date/lecture
    def readLectures(self, obj):
        line = 1
        for cols in self.instream:
            for c in range(len(cols)):
                cols[c] = cols[c].strip()
            if line == 1:
                self.analyze(cols)
                if not hasattr(self, 'cLect'):
                    sys.stderr.write("Lectures: Lecture column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cTop'):
                    sys.stderr.write("Lectures: Title column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cDay'):
                    sys.stderr.write("Lectures: Day column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cDate'):
                    sys.stderr.write("Lectures: Date column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cQuiz'):
                    sys.stderr.write("Lectures: Quiz column unknown\n")
                    sys.exit(-1)
            elif cols[self.cDate] != "":
                c = cols[self.cLect]
                l = 0 if (c == "") else c
                obj.addLecture(l, cols[self.cDay], cols[self.cDate],
                               cols[self.cTop], cols[self.cQuiz])
            line = line + 1


def interpolate(file, indent=0):
    """ copy a file to our output with optional indentation """
    if os.path.exists(file):
        input = open(file, 'rb')
        for line in input:
            print "%s%s" % (' ' * indent, line.rstrip('\n'))
        input.close()


if __name__ == '__main__':
    """ process specified input files, or test data """

    # process arguments to get input file names
    umsg = "usage: %prog [options]"
    parser = OptionParser(usage=umsg)
    parser.add_option("-l", "--lectures", dest="lectures", metavar="FILE",
                      default=None)
    parser.add_option("-p", "--prolog", dest="prolog", metavar="FILE",
                      default=None)
    parser.add_option("-e", "--epilog", dest="epilog", metavar="FILE",
                      default=None)
    parser.add_option("-s", "--slides", dest="slidepfx", metavar="PATH",
                      default="")
    (opts, files) = parser.parse_args()

    obj = schedule(opts.slidepfx)

    # print the prolog
    if opts.prolog is not None:
        interpolate(opts.prolog)
    else:
        print "<HTML>"
        print "<BODY>"

    # print the table
    obj.listHead()
    if opts.lectures is not None:       # process lectures
        csvReader(opts.lectures).readLectures(obj)
    obj.listFin()

    if opts.epilog is not None:
        print ""
        print "<P>"
        now = datetime.date.today()
        print "Last updated: %d/%d/%d" % (now.month, now.day, now.year)
        print "</P>"
        interpolate(opts.epilog)
    else:
        print "</BODY>"
        print "</HTML>"

    sys.exit(0)
