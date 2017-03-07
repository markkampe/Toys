#
# this is used by the exam.py utility
#
#   The question class understands the format of the question information
#   files, and knows how to output that information as:
#       summary
#       exam question
#       exam solution
#       grading rubric
#
import sys
import os.path


class question:

    def __init__(self, qname, role=None, number=None, dir=None):
        """ instantiate a question """

        # see if we can find the file
        file = dir + "/" + qname if dir else qname
        if not os.path.exists(file):
            sys.stderr.write("ERROR: unable to open exam file " + file + "\n")
            self.input = None
        else:
            self.input = open(file, 'rb')

        # default attributes
        self.name = qname
        self.number = number
        self.status = role
        self.descr = None
        self.text = None
        self.lect = None
        self.difficulty = "  "
        self.result = None
        self.priority = 0
        self.lines = 1
        self.time = 0
        self.head = "sts Q-ID  P,DN Description                        Lecture      Reading"
        self.dash = "--- ----  ---- ------------                       -------      -------"
        self.format = "%3s %-5s %d,%s %-31.31s    %-10.10s   %s"

    def close(self):
        self.input.close()

    def heading(self, lines=False):
        return self.dash if lines else self.head

    def summary(self, output=None):
        """ read the summary and return the description """

        if self.input is None:
            return "ERROR"

        # process attribute=value lines until we hit the question
        self.input.seek(0)
        for line in self.input:
            if "===QUESTION===" in line:
                args = (self.status, self.name, self.priority, self.difficulty,
                        self.descr, self.lect, self.text)
                return self.format % args
            else:
                name, var = line.partition("=")[::2]
                if name == "descr":
                    self.descr = var.rstrip()
                elif name == "text" and var.rstrip() != "":
                    self.text = var.rstrip()
                elif name == "lect" and var.rstrip() != "":
                    self.lect = var.rstrip()
                elif name == "status" and var.rstrip() != "":
                    self.status = var.rstrip()
                elif name == "diff" and var.rstrip() != "":
                    self.difficulty = var.rstrip()
                elif name == "lines" and var.rstrip() != "":
                    self.lines = int(var)
                elif name == "pri" and var.rstrip() != "":
                    self.priority = int(var)
                elif name == "time" and var.rstrip() != "":
                    self.time = int(var)
                elif name == "result" and var.rstrip() != "":
                    self.result = var.rstrip()

    def printExam(self, pager):
        """ print out the exam question """
        if self.input is None:
            return

        # set the hanging indent
        pager.setHang(len(self.number) + 2)

        # seek to the question
        inSection = False
        firstLine = False
        self.input.seek(0)
        for line in self.input:
            if "===ANSWER===" in line:
                break
            elif "===QUESTION===" in line:
                inSection = True
                firstLine = True
            elif inSection:
                if firstLine:
                    prefix = "%s: " % (self.number)
                    pager.addLine(prefix + line.rstrip())
                    firstLine = False
                else:
                    pager.addLine(line.rstrip())

        # see if we owe any padding lines
        l = self.lines
        while l > 0:
            pager.addLine('\n')
            l -= 1

        # flush the output and note the line count
        return pager.flush()

    def printSolution(self, output):
        """ print out problem solution  """
        if self.input is None:
            return

        # seek to the question
        inSection = False
        firstLine = False
        self.input.seek(0)
        for line in self.input:
            if "===RUBRIC===" in line:
                output.write('\n')
                break
            elif "===ANSWER===" in line:
                inSection = True
                firstLine = True
            elif inSection:
                if firstLine:
                    self.solnIntro(output)
                    firstLine = False
                output.write("    " + line)

    def printRubric(self, output):
        """ print out problem rubric  """
        if self.input is None:
            return

        # seek to the question
        inSection = False
        firstLine = False
        self.input.seek(0)
        for line in self.input:
            if "===NOTES===" in line:
                output.write('\n')
                break
            elif "===RUBRIC===" in line:
                inSection = True
                firstLine = True
            elif inSection:
                if firstLine:
                    title = "%s(%s): %s\n" % \
                            (self.number, self.name, self.descr)
                    output.write(title)
                    firstLine = False
                output.write("\t" + line)

    def solnIntro(self, output):
        """ print out the start of a solution """

        title = "<H2>%s. %s</H2>\n" % (self.number, self.descr)
        output.write(title)

        if self.text or self.lect:
            refmsg = "This was discussed in %s section(s) %s<br>\n"
            output.write("<P>\n")
            if self.text:
                output.write(refmsg % ("reading", self.text))
            if self.lect:
                output.write(refmsg % ("lecture", self.lect))
            output.write("</P>\n")
