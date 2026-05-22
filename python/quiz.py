#!/usr/bin/python3
"""
This is a quiz utility that I wrote because I could not find the
old Unix "quiz" application for Linux.
"""
# TODO handling ISO latin-1 files, output, input
import argparse
import sys
from random import randrange
from os import getenv, path


# pylint: disable=invalid-name
verbose = False     # info about quiz
WIDTH = 14          # width of question column
SUBDIR = "Quizzes"  # default place for quiz files


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

        # report on what quiz will cover
        if verbose:
            sys.stdout.write(f"Quiz: {quizfile} ... ")

        # read the file, parsing out the categories, questions, and answers
        line_num = 1
        try:
            with open(quizfile, 'rt', encoding='Latin-1') as instream:
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


def main():
    """
    process the arguments, read the quiz file, and conduct the quiz
    """

    # parse the arguments
    parser = argparse.ArgumentParser(
             description = "question/answer review program",
             epilog = "environment variables: QUIZDIR, QUIZFILE")
    parser.add_argument("names", nargs='*', type=str,
                        help="quiz-file [topic ...]")
    parser.add_argument("-r", "--reverse", action='store_true',
                        help="reverse questions/answers")
    parser.add_argument("-v", "--verbose", action='store_true')

    args = parser.parse_args()

    # process the string arguments
    quizname = None
    topics = []
    for name in args.names:
        if quizname is None:
            quizname = name
        else:
            topics.append(name)

    # if no args, look for a default quiz file
    if quizname is None:
        quizname = getenv("QUIZFILE")
        if quizname is None:
            sys.stderr.write("No quiz name or QUIZFILE in env\n")
            sys.exit(-1)

    # make sure that file exists
    if path.isfile(quizname):
        quiz_file_name = quizname
    else:
        # perhaps it is in user's Quiz directory
        quiz_dir = getenv("QUIZDIR")
        if quiz_dir is None:
            quiz_dir = getenv("HOME") + '/' + SUBDIR
        quiz_file_name = quiz_dir + '/' + quizname
        if not path.isfile(quiz_file_name):
            sys.stderr.write(f"Unable to access Quiz file {quiz_file_name}\n")
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
