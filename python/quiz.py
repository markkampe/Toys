#!/usr/bin/python3
"""
This is a quiz utility that I wrote because I could not find the
old Unix "quiz" application for Linux.
"""
import argparse
import sys
from random import randrange
from os import getenv, path


# pylint: disable=invalid-name
verbose = False         # info about quiz
WIDTH = 14              # width of question column
SUBDIR = "Quizzes"      # default place (in $HOME) for quiz files
ENCODING = "Latin-1"    # European languages


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
                    # ignore blank and comment lines
                    if len(line) > 6 and line[0] != '#':
                        # make sure it has a reasonable number of fields
                        if line.count(':') != 1 or line.count('\t') == 0:
                            self.error(line_num, "not on colon/tab format")
                        else:
                            (cat, rest) = line.split(':')

                            # there might be multiple tabs and a comment
                            tab = rest.find("\t")
                            quest = rest[0:tab].strip()
                            ans = rest[tab+1:].strip()
                            if '#' in ans:
                                ans = ans.split('#')[0].strip()

                            # now we have the question and answer
                            entry = (cat, ans, quest) \
                                if reverse else (cat, quest, ans)

                            # one entry might be column headings
                            if cat == "Category":
                                self.col1 = entry[1]
                                self.bar1 = '-' * len(self.col1)
                                self.col2 = entry[2]
                                self.bar2 = '-' * len(self.col2)
                            elif not topics or cat in topics:
                                self.questions.append(entry)
                                # debugging encoding problems
                                # for i, c in enumerate(quest):
                                #     sys.stdout.write(f"{i:4d}: {c}," +
                                #     f"{hex(ord(c))}\n")
                    line_num += 1
            # file is automatically closed at end of with
        except IOError:
            sys.stderr.write(f"unable to read Quiz file {quizfile}\n")
            sys.exit(-1)

        if verbose:
            self.prologue(topics, reverse)

    def prologue(self, topics, reverse):
        """
        pylint says there are too many if statements in the above method
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
        # print out column headings
        sys.stdout.write(f"{self.col1:{WIDTH}}\t{self.col2}\n")
        sys.stdout.write(f"{self.bar1:{WIDTH}}\t{self.bar2}\n")

        # conduct the quiz until blank line or EOF
        asked = 0
        correct = 0
        available = len(self.questions)
        finished = [False] * len(self.questions)
        while correct < available:
            # choose a yet unanswered question
            choice = randrange(0, available)
            if finished[choice]:
                continue
            (_cat, question, answer) = self.questions[choice]

            # ask the question
            try:
                reply = input(f"{question+':':{WIDTH}}\t")
            except EOFError:
                sys.stdout.write("\n")
                break

            # check the answer
            ok = False
            if len(reply) > 0:
                # are there multiple correct answers
                answers = answer.split(',')
                for ans in answers:
                    if reply == ans.strip():
                        ok = True
                        correct += 1 if ok else 0
                        finished[choice] = ok

            if verbose or not ok:
                msg = "  CORRECT" if ok else "  INCORRECT"
                sys.stdout.write(f"{msg:{WIDTH}}\t{answer}\n")

            asked += 1

        sys.stdout.write("\n")
        return (correct, asked)


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
    (correct, total) = quiz.session()

    print(f"score: {correct}/{total}")
    sys.exit(0 if correct == total else 1)


if __name__ == '__main__':
    main()
