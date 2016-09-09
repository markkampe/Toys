#
#
# this is used by the exam.py utility
#
#   a pager filters all of the output that goes into an exm,
#   doing word-wrapping and page-padding to a specified page size.
#


class pager:

    def __init__(self, outfile, linewid, pagelen):
        self.output = outfile   # output file
        self.width = linewid    # line width
        self.length = pagelen   # page length
        self.hang = 0           # hanging indent

        self.thisline = ""      # accumulated line
        self.question = []      # accumulated question
        self.page = []          # accumulated page

        self.prevBlank = False  # not in blank area
        self.fill = True        # filling enabled
        self.drop = 0           # no leading spaces

    # set the hanging indent
    def setHang(self, hang=0):
        self.hang = hang

    #
    # buffer another line to be output at end of page
    #
    # (1) handle <PRE></PRE> to disable/enable filling
    # (2) handle <SPACE> for non-paddable blank lines
    # (3) every other stretch of blank lines is paddable
    # (4) if filling is enabled, we fill to line width
    #
    def addLine(self, line=None):

        # see if this is a PRE directive
        stripped = line.strip()
        if stripped == "<PRE>" or stripped == "<pre>":
            self.lineBreak()
            self.fill = False
            return
        elif stripped == "</PRE>" or stripped == "</pre>":
            self.fill = True
            return
        elif stripped == "<BR>" or stripped == "<br>":
            self.lineBreak()
            return
        elif stripped == "<SPACE>" or stripped == "<space>":
            self.lineBreak()
            self.question.append("\n")
            self.prevBlank = False
            return

        # see if this is a padding point
        isBlank = (len(stripped) == 0) and self.fill
        if isBlank:
            self.lineBreak()
        if isBlank and not self.prevBlank:
            self.question.append(None)
        self.prevBlank = isBlank

        # and finally, process the line
        if self.fill:
            if isBlank:
                self.question.append('\n')
            else:
                self.lineFill(line)
        else:
            self.question.append(line + '\n')

    #
    # accumulate more text to fill
    #
    #   This works pretty well, but handles only a hanging indent.
    #   It would be cooler if it could infer desired indent from
    #   the input ... but this only works if the input lines are
    #   shorter than the output lines.  Otherwise we won't have seen
    #   the next line by the time we need its indent.
    #
    def lineFill(self, line):

        # no whitespace for a new question
        if len(self.question) == 0 and len(self.thisline) == 0:
            self.drop = 0

        words = line.split(' ')
        for w in words:
            linelen = len(self.thisline)
            wordlen = len(w)
            if wordlen == 0:
                continue

            # have we filled the current line?
            if (linelen + self.drop + wordlen) > self.width:
                self.lineBreak()

            # add this word to the line
            self.thisline += (self.drop * ' ') + w

            # figure out how much space goes after this word
            #   NOTE: this botches "e.g."
            if w.endswith(".") or w.endswith("?"):
                self.drop = 2
            else:
                self.drop = 1

    #
    # force out the accumulated line
    #
    def lineBreak(self):
        if self.thisline:
            self.question.append(self.thisline + '\n')
        self.thisline = ""
        self.drop = self.hang

    #
    # flush out the accumulated question out to the current
    # page, forcing out the page if it is full or we are done
    #
    def flush(self, force=False):
        # force out the current line
        self.lineBreak()

        # see if we need to skip to a new page
        Plen = len(self.page)
        Qlen = len(self.question)
        if Plen + Qlen > self.length:
            self.force()

        # append this question to the page
        self.page.extend(self.question)
        self.question = []
        self.prevBlank = False

        # see if we need to force it out
        if force:
            self.force()

        # and tell them how large this line was
        return Qlen

    #
    # force out the current page
    #
    #   A page may include multiple padding points,
    #   indicated by None lines.  When we flush the
    #   page out, we will divide any remaining lines
    #   evenly among the padding points.
    #
    def force(self):

        # how many excess lines and padding points
        padPoints = 0
        lines = 0
        for l in self.page:
            if l is None:
                padPoints += 1
            else:
                lines += 1
        if padPoints == 0:
            padPoints = 1
        excess = self.length - lines

        # force out the buffered questions
        lines = 0
        for l in self.page:
            if l is not None:
                # normal lines
                self.output.write(l)
                lines += 1
            else:
                # padding points
                x = int(excess / padPoints)
                while x > 0:
                    self.output.write('\n')
                    lines += 1
                    excess -= 1
                    x -= 1
                padPoints -= 1

        # pad us out to a page boundary
        while lines < self.length:
            self.output.write('\n')
            lines += 1

        # and reset the buffered page
        self.page = []
