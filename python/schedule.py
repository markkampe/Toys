#!/usr/bin/python
#
#   process readings, topics and lectures to create a lecture schedule
#       day/date, title, topics, readings, quiz, slides
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

    def __init__(self, slidepath="slides/", quizpath="quizzes/",
                 trial=False, indent=4):
        """ initialize the instance variables """
        self.indent = indent
        self.slides = slidepath
        self.quizzes = quizpath
        self.trial = trial

        self.topicMap = {}      # map from topics to lectures
        self.topics = {}        # topics for each lecture
        self.readings = {}      # readings for each lecture
        self.pages = {}         # pages per topic
        self.minutes = {}       # minutes per topic
        self.dayMap = {
            'Mon': 'M', 'Tue': 'T', 'Wed': 'W', 'Thu': 'R',
            'Fri': 'F', 'Sat': 'Sa', 'Sun': 'Su'}

    def addTopic(self, lecture, topicID, subject, time):
        """ add a topic to a lecture """
        self.topicMap[topicID] = lecture
        if lecture not in self.topics:
            self.topics[lecture] = []
        self.topics[lecture].append(subject)
        if lecture not in self.minutes:
            self.minutes[lecture] = time
        else:
            self.minutes[lecture] += time
        # print "TOPIC %s(%s) -> %d" % (topicID, subject, lecture)

    def addReading(self, topic, url, pp):
        """ register a reading for a topic->lecture """
        # make sure the associated topic is being taught
        if topic not in self.topicMap:
            return

        l = self.topicMap[topic]
        # print "READING %d(%s): %s(%dpp)" % (l, topic, url, pp)
        if l not in self.readings:
            self.readings[l] = []
        self.readings[l].append(url)
        if l not in self.pages:
            self.pages[l] = pp
        else:
            self.pages[l] += pp

    def addLecture(self, number, day, date, title, quiz):
        """ register a new lecture by its number and title
                number: integer lecture #, 0-> no lecture
                day: excel 3 letter day
                date: m/d/yyyy
                title: topic for this lecture/day
                quiz: what to put in quiz field
        """
        when = self.dayMap[day] + ' ' + date[0:-5]
        if number == 0:
            self.printActivity(when, title)
        else:
            self.printLecture(when, number, quiz)

    def tableHead(self):
        """ called to produce the start of the table definition """

        print "<TABLE align=center border cellspacing=0 cellpadding=5>"
        print "%s<TR>" % (' ' * self.indent)
        print "%s<TH>Date</TH>" % (' ' * (2 * self.indent))
        print "%s<TH>Lecture/Lab Topics</TH>" % (' ' * (2 * self.indent))
        print "%s<TH>Assigned Reading</TH>" % (' ' * (2 * self.indent))
        print "%s<TH>%s</TH>" % \
              (' ' * (2 * self.indent), "Minutes" if self.trial else "Quiz")
        print "%s<TH>%s</TH>" % \
              (' ' * (2 * self.indent), "Pages" if self.trial else "Slides")
        print "%s</TR>" % (' ' * self.indent)

    def printActivity(self, date, subject):
        print "%s<TR>" % (' ' * self.indent)
        print "%s<TD> %s </TD> <TD> %s </TD>" % \
              (' ' * self.indent, date, subject)
        print "%s</TR>" % (' ' * self.indent)

    def printLecture(self, date, lecture, quiz):
        print "%s<TR>" % (' ' * self.indent)
        print "%s<TD> %s </TD>" % (' ' * 2 * self.indent, date)

        print "%s<TD>" % (' ' * 2 * self.indent)
        for t in self.topics[lecture]:
            print "%s%s<br>" % (' ' * 3 * self.indent, t)
        print "%s</TD>" % (' ' * 2 * self.indent)

        print "%s<TD>" % (' ' * 2 * self.indent)
        if lecture in self.readings:
            for r in self.readings[lecture]:
                print "%s%s<br>" % (' ' * 3 * self.indent, r)
        print "%s</TD>" % (' ' * 2 * self.indent)

        try:
            # numbered lectures have quizzes and slides
            int(lecture)
            if self.trial:
                s = self.minutes[lecture] if lecture in self.minutes else 0
            else:
                s = quiz % (lecture) if "%s" in quiz else quiz
            print "%s<TD> %s </TD>" % (' ' * 2 * self.indent, s)

            if self.trial:
                s = self.pages[lecture] if lecture in self.pages else 0
            else:
                s = "%s<a href=\"%slecture_%s.pdf\">lecture %s</a>" % \
                    (' ' * 2 * self.indent, self.slides, lecture, lecture)
            print "%s<TD> %s </TD>" % (' ' * 2 * self.indent, s)
        except ValueError:
            pass

        print "%s</TR>" % (' ' * self.indent)

    def tableFin(self):
        print "</TABLE>"


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
            elif s in ["Subject", "Sub", "sub"]:
                self.cSub = c
            elif s in ["Objective", "objective"]:
                self.cObj = c
            elif s in ["Category", "category", "Type", "type"]:
                self.cCat = c
            elif s in ["Priority", "priority", "Pri", "pri"]:
                self.cPri = c
            elif s in ["Difficulty", "difficulty"]:
                self.cDif = c
            elif s in ["URL", "url"]:
                self.cURL = c
            elif s in ["Day", "day"]:
                self.cDay = c
            elif s in ["Date", "date"]:
                self.cDate = c
            elif s in ["Reading", "reading", "Pages", "pages", "pp"]:
                self.cPage = c
            elif s in ["Minutes", "minutes"]:
                self.cMin = c
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

    # note a topic
    def readTopics(self, obj, lectHead):
        line = 1
        for cols in self.instream:
            for c in range(len(cols)):
                cols[c] = cols[c].strip()
            if line == 1:
                self.analyze(cols, lectHead)
                if not hasattr(self, 'cTop'):
                    sys.stderr.write("Topics: Topic column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cLec'):
                    sys.stderr.write("Topics: Lecture column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cSub'):
                    sys.stderr.write("Topics: Subject column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cMin'):
                    sys.stderr.write("Topics: Minutes column unknown\n")
                    sys.exit(-1)
            elif cols[self.cLec] != "":
                l = cols[self.cLec]
                m = int(cols[self.cMin]) if cols[self.cMin] != "" else 0
                obj.addTopic(l, cols[self.cTop], cols[self.cSub], m)
            line = line + 1

    # note a reading
    def readReadings(self, obj):
        line = 1
        for cols in self.instream:
            for c in range(len(cols)):
                cols[c] = cols[c].strip()
            if line == 1:
                self.analyze(cols)
                if not hasattr(self, 'cTop'):
                    sys.stderr.write("Reading: Topic column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cURL'):
                    sys.stderr.write("Reading: URL column unknown\n")
                    sys.exit(-1)
                if not hasattr(self, 'cPage'):
                    sys.stderr.write("Reading: Pages column unknown\n")
                    sys.exit(-1)
            elif cols[self.cTop] != "" and cols[self.cURL] != "":
                p = 0 if cols[self.cPage] == "" else int(cols[self.cPage])
                obj.addReading(cols[self.cTop], cols[self.cURL], p)
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
    umsg = "usage: %prog [options] READINGS.csv"
    parser = OptionParser(usage=umsg)
    parser.add_option("-l", "--lectures", dest="lectures", metavar="FILE",
                      default=None)
    parser.add_option("-t", "--topics", dest="topics", metavar="FILE",
                      default=None)
    parser.add_option("-p", "--prolog", dest="prolog", metavar="FILE",
                      default=None)
    parser.add_option("-e", "--epilog", dest="epilog", metavar="FILE",
                      default=None)
    parser.add_option("-c", "--col", dest="column", metavar="#LECTURES",
                      default="28")
    parser.add_option("-s", "--slides", dest="slidepfx", metavar="PATH",
                      default="slides/")
    parser.add_option("-q", "--quizzes", dest="quizpfx", metavar="PATH",
                      default="quizzes/")
    parser.add_option("-x", "--trial", dest="trial", action="store_true",
                      default=False)
    (opts, files) = parser.parse_args()

    # count the file names to decide what to do
    if len(files) != 1:
        sys.stderr.write("usage: %s" + umsg + "\n")
        sys.exit(-1)

    obj = schedule(opts.slidepfx, opts.quizpfx, opts.trial)

    if opts.topics is not None:     # build topics->lectures map
        csvReader(opts.topics).readTopics(obj, opts.column)
    csvReader(files[0]).readReadings(obj)         # process readings

    # print the prolog
    if opts.prolog is not None:
        interpolate(opts.prolog)
    else:
        print "<HTML>"

    # print the table
    obj.tableHead()
    if opts.lectures is not None:       # process lectures
        csvReader(opts.lectures).readLectures(obj)
    obj.tableFin()

    if opts.epilog is not None:
        print ""
        print "<P>"
        now = datetime.date.today()
        print "Last updated: %d/%d/%d" % (now.month, now.day, now.year)
        print "</P>"
        interpolate(opts.epilog)
    else:
        print "</HTML>"

    sys.exit(0)
