"""
Sample application to show Chris how to read json (DnD character descriptions)
into python and write them back out again.
"""
import json
from optparse import OptionParser
from sys import stderr, exit

def read_characters(filename):
    """
    read an json format input file into a list

    @param filename: name of the input file
    @return the read in list
    """
    try:
        with open(filename, 'r') as infile:
            characters = json.load(infile)
            infile.close()
            return characters
    except Exception as e:
            stderr.write("ERROR: unable to read characters from file " + filename + "\n")
            stderr.write(e.message + "\n")
    return None


def write_characters(characters, filename):
    """
    write a list of character descriptions out to a json file

    @param characters: the list to be written
    @param filename: name of the file to which it should be written
    """
    try:
        with open(filename, 'w') as outfile:
            json.dump(characters, outfile, indent=4)
            outfile.write("\n")
            outfile.close()
    except Exception as e:
            stderr.write("ERROR: unable to write characters to file " + filename + "\n")
            stderr.write(e.message + "\n")


if __name__ == "__main__":

    # process the command line arguments
    msg = "usage: %prog [options] input_file output_file"
    parser = OptionParser(usage=msg)
    parser.add_option("-v", "--verboser", action="store_true", dest="verbose",
                      help="verboser output")
    (opts, files) = parser.parse_args()
    if len(files) < 2:
        stderr.write("ERROR: missing filename(s)\n")
        stderr.write(msg + "\n")
        exit(-1)

    # read the json descriptions
    npcs = read_characters(files[0])

    # print them out if requested
    if opts.verbose:
        print("Read " + str(len(npcs)) + " character from " + files[0])
        for c in npcs:
            print("{}: L{} {} {}, HP={}, XP={}".format(
                  c["name"], c["level"], c["race"], c["class"],
                  c["stats"]["hp"], c["stats"]["xp"]
                  ))

    # write them all out again to a new file
    write_characters(npcs, files[1])
