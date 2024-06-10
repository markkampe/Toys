#!/usr/bin/python
#
#   This is a program to process exported moodle quiz files, putting
#   them into per-category files (for editing and organization).
#   It also has a -s (--summary) option that generates a list of
#   question names.
#

import sys
import os.path
from optparse import OptionParser


#
# parse a category line to get the category
#
def category(line):
    """ strip off the prefix and suffix to get the initial category """
    start = line.find('<text>')
    end = line.rfind('</text>')
    full = line[start+6:end].rstrip().lstrip()
    return full


#
# process a category line to come up with a file name
#
def catFile(category):
    # find the last pathname component
    lastslash = category.rfind('/')
    if lastslash < 0:
        sys.stderr.write("Category name w/o final slash: %s\n" % line)
        sys.exit(-1)

    # no embedded blanks in file names
    name = category[lastslash + 1:].replace(' ', '_') + ".xml"
    return name


#
# extract text from the wrapper Moodle puts around it
#
def rawText(line):
    # strip off enclosing angle-brackets
    if line.startswith('<') and line.endswith('>'):
        line = line[1:-1]

    # strip off CDATA encapsulation
    if line.startswith('![CDATA[') and line.endswith(']]'):
        line = line[8:-2]

    # strip off HTML paragraph markers
    if line.startswith('<p>') and line.endswith('</p>'):
        line = line[3:-4]

    # strip off any final HTML break
    if line.endswith('<br>'):
        line = line[0:-4]

    return line


#
# there are several different feedback types, and any text in
# them is not a question or answer
#
feedback = ["feedback", "correctfeedback", "incorrectfeedback",
            "partiallycorrectfeedback"]


def isOpenFeedback(line):
    """ see if this line begins a feedback section """
    for token in feedback:
        if '<' + token in line:
            return True
    return False


def isCloseFeedback(line):
    """ see if this line begins a feedback section """
    for token in feedback:
        if '</' + token in line:
            return True
    return False


#
# input processing state machine
#   looks for categories and questions
#   processes the categories, copies the questions
#
def process(file):
    """ process an input file """
    output = None
    input = open(file, 'rb')
    inCategory = False
    inQuestion = False
    for line in input:
        if inQuestion:
            output.write(line)
            if '</question>' in line:
                output.write('\n')
                inQuestion = False
        elif inCategory:
            if '<text>$course$' in line:
                if output is not None:
                    output.close()
                catName = category(line)
                fileName = catFile(catName)

                if os.path.isfile(fileName):
                    # append to the existing file for this category
                    output = open(fileName, 'a')
                else:
                    # create a new file for this category
                    output = open(fileName, 'wb')
                    output.write('<!-- question: 0 -->\n')
                    output.write('  <question type="category">\n')
                    output.write('    <category>\n')
                    output.write('      <text>%s</text>\n' % (catName))
                    output.write('    </category>\n')
                    output.write('  </question>\n')
                    output.write('\n')
            elif '</question>' in line:
                inCategory = False
        else:
            if '<!-- question: 0' in line:
                inCategory = True
            elif '<!-- question:' in line:
                if output is not None:
                    output.write(line)
                inQuestion = True
            # else:
                # random input to be ignored

    # close the output and input files
    if output is not None:
        output.close()
    input.close()


#
# process a question text line and generate a one line summary
#
def list(line):
    """ print out the text of a question """
    # pull out the text
    start = line.find('<text>')
    end = line.rfind('</text>')
    text = line[start+6:end].lstrip()

    # pull out the CDATA
    start = text.find('[CDATA[')
    end = text.rfind(']]')
    body = text[start+7:end].rstrip()

    # pull out the paragraph (if any)
    start = body.find('<p>')
    if start >= 0:
        end = body.rfind('</p>')
        body = body[start + 3:end]

    # pull out a trailing break (if any)
    end = body.rfind('<br>')
    if end >= 0:
        body = body[0:end]

    # print it out
    if body != "":
        print body


#
# input processing state machine
#   print out simple ASCII summaries of questions and answers
#
def simpleText(file, tags):
    """ print questions and answers in straight text """

    qType = None
    qName = None
    cName = None
    inCategory = False
    inQuestion = False
    inSubquestion = False
    inName = False
    inAnswer = False
    inFeedback = False
    choiceNum = 0
    choices = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)",
               "(h)", "(i)", "(j)"]

    input = open(file, 'rb')
    for line in input:
        if qType is None:
            if '<question ' in line:
                start = line.find('type="')
                if start > 0:
                    rest = line[start+6:]
                    end = rest.find('"')
                    if end > 0:
                        qType = rest[0:end]
                    else:
                        qType = '!!!'
                else:
                    qType = '???'

        # in a question and we have its name
        elif '<name>' in line:
            inName = True
        elif '</name>' in line:
            inName = False
        elif inName and '<text>' in line:
            start = line.find('<text>')
            end = line.find('</text>')
            if end > 0:
                qName = line[start+6:end]

        # in a question and we have its text
        elif '<questiontext' in line:
            inQuestion = True
        elif '</questiontext' in line:
            inQuestion = False
        elif inQuestion and '<text>' in line:
            start = line.find('<text>')
            end = line.find('</text>')
            if end > 0:
                question = rawText(line[start+6:end])
            if cName is not None:
                print(cName)
            print(qType + ": " + qName)
            print("    " + question)

        # in a sub-question and we have its text
        elif '<subquestion' in line:
            inSubquestion = True
            print
        elif '</subquestion' in line:
            inSubquestion = False
        elif inSubquestion and '<text>' in line:
            start = line.find('<text>')
            end = line.find('</text>')
            if end > 0:
                question = rawText(line[start+6:end])
            print("    " + question)

        # in a feedback section
        elif isOpenFeedback(line):
            inFeedback = True
        elif isCloseFeedback(line):
            inFeedback = False

        # in a question and we have an answer
        elif '<answer' in line:
            inAnswer = True
        elif '</answer>' in line:
            inAnswer = False
        elif inAnswer and not inFeedback and '<text>' in line:
            start = line.find('<text>')
            end = line.find('</text>')
            if end > 0:
                answer = rawText(line[start+6:end])
            if qType != "matching":
                if tags:
                    print("\n        " + choices[choiceNum] + ' ' + answer)
                else:
                    print("\n        " + answer)
                choiceNum += 1
            else:
                print("        " + answer)

        # in category section
        elif '<category' in line:
            inCategory = True
        elif '</category' in line:
            inCategory = False
        elif inCategory and '<text>' in line:
            # find the last pathname component
            cat = category(line)
            lastslash = cat.rfind('/')
            if lastslash > 0:
                cName = cat[lastslash + 1:]

        # we have reached the end of a question
        elif '</question>' in line:
            # end of question
            qType = None
            qName = None
            inQuestion = False
            inName = False
            inAnswer = False
            inFeedback = False
            choiceNum = 0
            print("\n")


#
# input processing state machine
#   look for questions, and list them
#
def summarize(file):
    """ print out a list of included questions """

    input = open(file, 'rb')
    inQuestion = False

    for line in input:
        if inQuestion:
            if '</questiontext>' in line:
                inQuestion = False
            else:
                list(line)
        elif '<questiontext' in line:
            inQuestion = True


#
# main loop - parameter and file processing
#
if __name__ == '__main__':
    """ process specified input files, or test data """

    # process arguments to get input file names
    umsg = "usage: %prog [options] READINGS.csv"
    parser = OptionParser(usage=umsg)
    parser.add_option("-a", "--ascii", dest="ascii", action="store_true",
                      default=False)
    parser.add_option("-s", "--summary", dest="summarize", action="store_true",
                      default=False)
    parser.add_option("-t", "--tags", dest="tags", action="store_true",
                      default=False)
    (opts, files) = parser.parse_args()
    for f in files:
        if opts.summarize:
            summarize(f)
        elif opts.ascii:
            simpleText(f, opts.tags)
        else:
            process(f)
    sys.exit(0)
