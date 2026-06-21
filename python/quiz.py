#!/usr/bin/python3
"""
This is a quiz utility that I wrote because I could not find the
old Unix "quiz" application for Linux.
"""
import argparse
import sys
import math
import unicodedata
from random import randrange
from os import getenv, path


# pylint: disable=invalid-name
verbose = False         # info about quiz
WIDTH = 14              # min width of question column
TAB_STOP = 4            # tab stop width
SUBDIR = "Quizzes"      # default place (in $HOME) for quiz files
ENCODING = "Latin-1"    # European languages
HARD = "NEEDSWORK"      # tag for stuff I need to work on
MINLINE = 5             # word, colon, tab, word, newline


class Quiz:
    """
    Read a file of quiz questions, and conduct a session of question promts
    and answer checking.
    """
    def __init__(self, quizfile, topics, reverse=False):
        """
        Digest the specified quiz file
        :param quizfile (string): name of quiz file
        :param topics ([string, ...]): topics to be quizzed on
        :param reverse (bool): prompt with answers rather than questions
        """
        self.quizfile = quizfile
        self.questions = []
        self.col1 = "Question"
        self.bar1 = "--------"
        self.col2 = "Answer"
        self.bar2 = "------"
        self.width = WIDTH

        # make sure we can write the characters we read
        sys.stdout.reconfigure(encoding=ENCODING)
        # report on what quiz will cover
        if verbose:
            sys.stdout.write(f"Quiz: {quizfile} ... ")

        # read the file, parsing out the categories, questions, and answers
        line_num = 1
        try:
            with open(quizfile, 'rt', encoding=ENCODING) as instream:
                for line in instream:
                    # separate the text form any comment
                    (cat, q, a, cmt) = self.parse(line, line_num, reverse)
                    if cat and q and a:
                        entry = (cat, q, a)

                        # figure out good column widths
                        if len(entry[1]) > self.width:
                            self.width = self.tab_stop(len(entry[1]))

                        # one entry might be column headings
                        if cat == "Category":
                            self.col1 = entry[1]
                            self.bar1 = '-' * len(self.col1)
                            self.col2 = entry[2]
                            self.bar2 = '-' * len(self.col2)
                        elif not topics or cat in topics:
                            self.questions.append(entry)
                        elif HARD in topics and HARD in cmt:
                            self.questions.append(entry)

                    line_num += 1
            # file is automatically closed at end of with
        except IOError:
            sys.stderr.write(f"unable to read Quiz file {quizfile}\n")
            sys.exit(-1)

        if verbose:
            self.prologue(topics, reverse)

    def parse(self, line, linenum, reverse):
        """
        pylint says there are too many if statements in the above constructor
        :param line (string): to be parsed
        :param linenum (int): line number for error messages
        :param reverse (bool): reverse questions and answers
        :return (cat, question, answer, comment)
        """
        # separate out any comment
        if line.count('#') > 0:
            (text, comment) = line.split('#')
        else:
            text = line
            comment = ""

        # see if we have a question and answer
        if len(text) < MINLINE:
            return (None, None, None, None)
        if text.count(':') != 1 or text.count('\t') == 0:
            self.error(linenum, "not in colon/tab format")
            return (None, None, None, None)

        # lex off the category, question, and answer
        (cat, rest) = text.split(':')
        tab = rest.find("\t")
        quest = rest[0:tab].strip()
        ans = rest[tab+1:].strip()

        if reverse:
            return (cat, ans, quest, comment)
        return (cat, quest, ans, comment)

    def prologue(self, topics, reverse):
        """
        pylint says there are too many if statements in the above constructor
        :param topics ([string]): topics to be included
        :param reverse (bool): reverse questions and answers
        """
        sys.stdout.write(f"{len(self.questions)} ")
        if reverse:
            sys.stdout.write("(reversed) ")
        sys.stdout.write("questions\n")
        sys.stdout.write("\tusing")

        if not topics:
            sys.stdout.write(" all topics")
        else:
            sys.stdout.write(" topics [")
            for i, t in enumerate(topics):
                if i != 0:
                    sys.stdout.write(", ")
                sys.stdout.write(t)
            sys.stdout.write("]")
        sys.stdout.write("\n")

    def error(self, line, msg):
        """
        log an error message about the quiz file
        :param line (int): line nunber
        :param msg (string): complaint
        """
        sys.stderr.write("ERROR " + self.quizfile + " ")
        if line > 0:
            sys.stderr.write(f"line {line}")
        sys.stderr.write(f": {msg}\n")

    def session(self):
        """
        prompt with questions, read answers, and check results
        :return score (int, int): correct out of total
        """
        # conduct the quiz until blank line or EOF
        available = len(self.questions)
        asked = 0
        correct = 0
        finished = [False] * len(self.questions)

        # print out column headings
        sys.stdout.write(f"{self.col1:{self.width}}\t{self.col2}\n")
        sys.stdout.write(f"{self.bar1:{self.width}}\t{self.bar2}\n")
        while correct < available:
            # choose a yet unanswered question
            choice = randrange(0, available)
            if finished[choice]:
                continue
            (_cat, question, answer) = self.questions[choice]

            # ask the question
            try:
                reply = input(f"{question+':':{self.width}}\t").strip()
            except EOFError:
                sys.stdout.write("\n")
                break

            # check the answer
            if len(reply) > 0:
                ok = self.check(reply, choice)
                if ok:
                    correct += 1
                    finished[choice] = True
            else:
                ok = False

            if verbose or not ok:
                msg = "  CORRECT" if ok else "  INCORRECT"
                sys.stdout.write(f"{msg:{self.width}}\t{answer}\n")

            asked += 1

        sys.stdout.write("\n")
        return (correct, asked)

    def check(self, answer, choice):
        """
        check the correctess of an answer
        :param answer (string): given answer
        :param choice (int): question number
        :return: boolean
        """
        # compare given answer with all correct ones
        (_cat, _question, correct) = self.questions[choice]
        possibilities = correct.split(',')
        for ans in possibilities:
            if answer == ans.strip():
                return True

            # user may not be able to enter accents
            simpler = strip_accents(ans.strip())
            # print out what it should have been
            if answer == simpler:
                sys.stdout.write(f"{' ':{self.width}}\t{ans.strip()}\n")
                return True

        return False

    def tab_stop(self, number):
        """
        round a number to a multiple of another (even tabs)
        :param number (int): to be rounded
        :param multiple (int): number to be a multiple of
        """
        return math.ceil(number / TAB_STOP) * TAB_STOP


def strip_accents(string):
    """
    replace non-ASCII characters with their closest ASCII equivalents
    :param string: to be translated
    return (string) ASCII equivalent
    """

    # separate accents from characters
    nfd_form = unicodedata.normalize('NFD', string)
    # keep only the non-accent characters
    return "".join([c for c in nfd_form if not unicodedata.combining(c)])


def quizFile(name):
    """
    Figure out whether or not this names a quiz file
    :param name (string): suspected quiz file name
    :return (string): full path to quiz file, or None
    """
    # is it the name of an existing file
    if path.isfile(name):
        return name

    # is it the name of a file in a Quiz directory
    quizdir = getenv("QUIZDIR")
    if quizdir is None:
        quizdir = getenv("HOME") + "/" + SUBDIR
    maybe = quizdir + '/' + name
    if path.isfile(maybe):
        return maybe

    return None


def main():
    """
    process the arguments, read the quiz file, and conduct the quiz

    Usage: quiz.py [-v] [-r] [quiz] [topics ...]
        -r  prompt w/answers, expect question
        -v  verboser output
    environment:
        QUIZFILE    default quiz file if none specified on CLI
        QUIZDIR     directory to look in for quizzes
    """

    # parse the arguments
    parser = argparse.ArgumentParser(
             description="question/answer review program",
             epilog="environment variables: QUIZDIR, QUIZFILE")
    parser.add_argument("names", nargs='*', type=str,
                        help="quiz-file [topic ...]")
    parser.add_argument("-r", "--reverse", action='store_true',
                        help="reverse questions/answers")
    parser.add_argument("-v", "--verbose", action='store_true')

    args = parser.parse_args()

    # process the string arguments
    topics = []
    quiz_file_name = None
    for i, name in enumerate(args.names):
        # first argument might be a quiz file name
        if i == 0:
            quiz_file_name = quizFile(name)
            if quiz_file_name is not None:
                continue
            # perhaps the QUIZFILE environment variable
            maybe = getenv("QUIZFILE")
            if maybe is not None:
                quiz_file_name = quizFile(maybe)
                if quiz_file_name is None:
                    sys.stderr.write(f"Cannot open QUIZFILE={maybe}\n")
                    sys.exit(-1)

        # name wasn't quiz, must have been a topic
        topics.append(name)

    # if no args, look for a default quiz file
    if quiz_file_name is None:
        sys.stderr.write("No quiz name specified, no QUIZFILE in env\n")
        sys.exit(-1)

    # pylint: disable=global-statement
    global verbose
    verbose = args.verbose
    quiz = Quiz(quiz_file_name, topics, args.reverse)

    # make sure we have digested some questions
    if len(quiz.questions) == 0:
        sys.stderr.write("Quiz file " + quiz_file_name + " contains ")
        sys.stderr.write("no questions")
        if len(topics) > 0:
            sys.stderr.write(" in categories:")
            for t in topics:
                sys.stderr.write(' ' + t)
        sys.stderr.write('\n')
        sys.exit(2)

    # run the quiz
    (correct, total) = quiz.session()
    print(f"score: {correct}/{total}")
    sys.exit(0 if correct == total else 1)


if __name__ == '__main__':
    main()
