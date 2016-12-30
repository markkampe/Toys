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
    parser.add_option("-s", "--summary", dest="summarize", action="store_true",
                      default=False)
    (opts, files) = parser.parse_args()
    for f in files:
        if opts.summarize:
            summarize(f)
        else:
            process(f)
    sys.exit(0)
