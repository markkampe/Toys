import sys
import csv


def process(file, fields):
    """
    read the specified CSV file, producing static initializations for
    vectors with the specified names.
    parms:
        name of CSV file to be processed
        number of interesting fields per line
    """

    # start out with empty lists for each expected field
    data = []
    for i in range(fields):
        data.append([])

    # process every line in the CSV file, dividing it into columns
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line = 1
        for row in csv_reader:
            if len(row) < fields:
                # if it has too few lines, ignore it
                print("ignoring line " + str(line) + ": only " +
                      str(len(row)) + " fields")
            else:
                # make sure all fields are non-empty
                good = True
                for col in range(fields):
                    if row[col] == "":
                        # print("Ignoring line " + str(line) + ": field " +
                        #       str(col) + " is empty")
                        good = False
                        break

                # copy each column into the appropriate vector
                if good:
                    for col in range(fields):
                        data[col].append(row[col])
            line = line + 1

        # print out each column as a separate vector initialization
        for col in range(fields):
            output = "col" + str(col) + " = ["
            fields = 0
            for field in data[col]:
                if fields != 0:
                    output = output + ","
                if len(output) >= 72:
                    print(output)
                    output = "\t"
                output += ' ' + field
                fields += 1

            output += " ]"
            print(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python csv_to_vector.py csvfile")
    else:
        process(sys.argv[1], 4)


if __name__ == "__main__":
    main()
