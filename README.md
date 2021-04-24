This is a collection of miscelaneous programs, (occasionally) useful to me,
and all to trivial to warrant their own repos.  The sub-directories are
(imginatively) named for the language in which the programs were written.

bash:
 - diary ... script I use to maintain my (monthly) diary files.
 - git_check ... script to tell me if I have anything to commit, push or pull
 - x2pdf.sh ... turn an ASCII text file into PDF (e.g. for upload to Gradescope)

c:
 - choose.c ... a tool to choose random numbers or one of a set of (potentially
   weighted) strings.
 - colsum.c ... a tool to read columnar data and compute a sum for any column
   that appears to be numeric.
 - lptest.c ... generate a file of pattern data to see how a printer handles
   pages of a certain width and length.

python:
 - LogDump.py ... utility to process an (XML) sub-surface dive log, and 
   produce (one-line-per-dive) summary pages (that I can show people).
 - quizsort.py ... utility to process Moodle (UCLA CS) quiz files, and
   organize them into categories or generate summaries.

investigations/prototypes:
 - c/interpose.c ... toy to test our ability to interpose our own routines
   in front of libC standards (like open, read, write).
 - c/key_lookup.c ...  toy to test key-rings to ascertain their persistence.
 - c/xterm-title.c ... toy to test the ability to decorate XTERMs from sent data.
 - leveldb/cpp_test.cpp ... simple program to prove I knew how to access a leveldb
 - leveldb/c_test.c ... the same program in c
 - python/blurr.py ... playing with Gaussian blurring (which I wanted to use for
   Java_Terrain Foundation exports)
 - python/DnD.py ... sample code (for Chris) for how to read a (JSON) character description
    - python/Daunsmouri.json ... test character description

obsolete/ephemera:
 - bash/create_files.sh, test_access.sh ... a pair of tools I created to test
   the ownership/access control being provided on a NTFS share that
   Pomona ITS was providing for use by the CS department.
 - c/check_access.c ... a program used by the above to ascertain what access
   I actually have to a particular file.
 - bash/jarup ... script to turn a (Pomona CS51 ObjectDraw) Jave demo into a 
   runnable appliaction.
 - explorer ... my thoughts on how to re-implement the Segue version of the
   Norton Disk Explorer using HTML.
 - perl/walker.pl ... a demo program I wrote (for Jenny?) to show how to walk
   a tree of file in a perl program
 - python/csv_to_vector.py ... program I wrote (for Jenny) to read CSV data and
   turn it into a more useful (to her) form.
 - python/ScoreScrape.py ... program I wrote for Pomona (CS51) to scrape 
   (SCORE grading) comments out of PDF files and compute scores from them.
   - test.txt ... sample score comments for testing
