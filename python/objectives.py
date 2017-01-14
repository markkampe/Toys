#!/usr/bin/python
#
#   Right now this does what I need it to do, as simply as possible
#   Maybe someday I should make it autoconfig categories list from
#   the input.
#
import sys
import os.path
from csv import reader
from optparse import OptionParser
import datetime


class objectives:
    """ This class accepts lectures and learning objectives
        and outputs them as an HTML table per lecture/category
    """

    def __init__(self, categories):
        """ initialize the instance variables """
        self.lectures = 0    # number of initialized lectures
        self.titles = []    # title of each lecture
        self.topicMap = {}  # mapp from topics to lectures
        self.prefix = {}    # per priority typeface start
        self.suffix = {}    # per priority typeface end
        self.lists = []     # lecture lists of objectives

        # create a list for each category
        self.names = categories
        for c in categories:
            self.lists.append([])

    def priority(self, priority, typeface):
        """ set the typeface to use for a priority """
        self.prefix[priority] = "<%s>" % (typeface)
        self.suffix[priority] = "</%s>" % (typeface)

    def needLecture(self, number, havename=False):
        """ make sure we have data structures for required lecture """
        while self.lectures <= number:
            if havename:
                self.titles.append(None)
            for l in self.lists:
                l.append([])
            self.lectures += 1

    def addLecture(self, number, title):
        """ register a new lecture by its number and title """
        self.needLecture(number, True)
        self.titles[number] = title
        return None

    def addObjective(self, lecture, title, category, priority=2, difficulty=1):
        """ register a new learning objective, add to appropriate lists """

        # figure out what category this is in
        try:
            x = self.names.index(category)
        except ValueError:
            return("Unrecognized category: " + category)
        else:
            # add this to the per lecture sub-list for that category
            self.needLecture(lecture)
            catlist = self.lists[x]
            catlist[lecture].append((title, priority, difficulty))
            return None

    def addTopic(self, lecture, topic):
        """ note what lecture a topic is in """
        self.topicMap[topic] = lecture

    def table(self, breaks=False, indent=4):
        """ called after all registrations to print the table """

        print "<TABLE align=center border cellspacing=0 cellpadding=5>"
        print "%s<TR>" % (' ' * indent)
        print "%s<TH>Lecture</TH>" % (' ' * (2 * indent))
        if len(self.titles) > 0:
            print "%s<TH>Subject</TH>" % (' ' * (2 * indent))
        for list in self.names:
            print "%s<TH>%s</TH>" % ((' ' * (2 * indent)), list)
        print "%s</TR>" % (' ' * indent)

        eol = "<BR>" if breaks else ","
        for lect in range(1, len(self.lists[0])):
            print "%s<TR>" % (' ' * indent)
            print "%s<TD>%d</TD>" % (' ' * (2 * indent), lect)
            if len(self.titles) > 0:
                print "%s<TD>%s</TD>" % \
                      (' ' * (2 * indent), self.titles[lect])

            for list in self.lists:
                print "%s<TD>" % (' ' * (2 * indent))
                for (t, p, d) in list[lect]:
                    pfx = self.prefix[p] if p in self.prefix else ""
                    sfx = self.suffix[p] if p in self.suffix else ""
                    print "%s%s%s%s%s" % \
                          (' ' * (3 * indent), pfx, t, sfx, eol)
                print "%s</TD>" % (' ' * (2 * indent))
            print "%s</TR>" % (' ' * indent)
        print "</TABLE>"


class csvReader:
    """ This class reads CSV files for lectures and learning objectives
        and uses the objectives class to record them
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
            elif s == lectHead:
                self.cLect = c

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
            elif cols[self.cLect] != "":
                try:
                    l = int(cols[self.cLect])
                    obj.addLecture(l, cols[self.cTop])
                except ValueError:
                    pass
            line = line + 1

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
                if not hasattr(self, 'cLect'):
                    sys.stderr.write("Topics: Lecture column unknown\n")
                    sys.exit(-1)
            elif cols[self.cLect] != "":
                try:
                    l = int(cols[self.cLect])
                    obj.addTopic(l, cols[self.cTop])
                except ValueError:
                    pass
            line = line + 1

    def readObjectives(self, obj):
        line = 1
        for cols in self.instream:
            for c in range(len(cols)):
                cols[c] = cols[c].strip()
            if line == 1:
                self.analyze(cols)
                if not hasattr(self, 'cTop'):
                    sys.stderr.write("Objectives: Lecture column unknown\n")
                    sys.exit(-1)
                elif not hasattr(self, 'cObj'):
                    sys.stderr.write("Objectives: Objective column unknown\n")
                    sys.exit(-1)
                elif not hasattr(self, 'cCat'):
                    sys.stderr.write("Objectives: Category column unknown\n")
                    sys.exit(-1)
                elif not hasattr(self, 'cPri'):
                    sys.stderr.write("Objectives: Priority column unknown\n")
                    sys.exit(-1)
            else:
                t = cols[self.cTop]
                p = cols[self.cPri]
                if t in obj.topicMap.keys() and p != '':
                    l = obj.topicMap[t]
                    err = obj.addObjective(l, cols[self.cObj],
                                           cols[self.cCat], int(p))
                    if err is not None:
                        sys.stderr.write("%d: %s\n" % (line, err))
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
    umsg = "usage: %prog [options] OBJECTIVES.csv"
    parser = OptionParser(usage=umsg)
    parser.add_option("-l", "--lectures", dest="lectures", metavar="FILE",
                      default=None)
    parser.add_option("-t", "--topics", dest="topics", metavar="FILE",
                      default=None)
    parser.add_option("-p", "--prolog", dest="prolog", metavar="FILE",
                      default=None)
    parser.add_option("-d", "--describe", dest="describe",
                      default=False, action="store_true")
    parser.add_option("-e", "--epilog", dest="epilog", metavar="FILE",
                      default=None)
    parser.add_option("-c", "--col", dest="column", metavar="#lectures",
                      default="10")
    (opts, files) = parser.parse_args()

    # count the file names to decide what to do
    if len(files) != 1:
        sys.stderr.write("usage: %s" + umsg + "\n")
        sys.exit(-1)

    # create an appropriate objectives instance
    # NOTE: if I were cooler, I would take these as parms
    categories = ("Concept", "Issue", "Approach", "Skill")
    obj = objectives(categories)

    # choose type faces
    obj.priority(1, "strong")
    obj.priority(3, "em")

    if opts.lectures is not None:   # build lectures list
        csvReader(opts.lectures).readLectures(obj)
    if opts.topics is not None:     # build topics->lectures map
        csvReader(opts.topics).readTopics(obj, opts.column)
    csvReader(files[0]).readObjectives(obj)         # process objectives

    # print the table
    if opts.prolog is not None:
        interpolate(opts.prolog)
    else:
        print "<HTML>"

    if opts.describe:
        print "<UL>"
        for c in categories:
            print "    <LI> <STRONG>%s</STRONG>" % (c)
            interpolate(c + ".txt", 8)
            print "    </LI>"
        print "</UL>"

    obj.table(True)

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
