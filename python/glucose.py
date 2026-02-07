#!/usr/bin/python3
"""
    This is a utility to read a Lingo CGM download and
    translate it into a readily plot-able form:
"""

import sys
import csv

MINVAL = 70     # minimum recommended blood Glucose level
MAXVAL = 140    # maximum recommended blood Glucose level


def process(file):
    """
    produce a different version of the supplied file
        - rename columns to be reasonable for graph
        - change entry order from newest-first to oldest-first
        - chnage timestamps from  YYYY-MM-DDTHH:MM to MM/DD/YY HH:MM
        - add min/max columns (so they will show up as lines on the plot)

    parms:
        name of CSV file to be processed
    """

    # process every line in the CSV file
    with open(file, 'r', encoding='ascii') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        lines = []
        num_lines = 0

        # readn and convert all the samples
        for row in csv_reader:
            # all valid entries have two fields
            if len(row) != 2:
                continue

            # get date/time, change to spreadsheet format
            date = row[0]
            year = date[0:4]
            month = date[5:7]
            day = date[8:10]
            date_time = f"{month}/{day}/{year}"
            hour = date[11:13]
            mins = date[14:16]
            date_time += f" {hour}:{mins}"

            # add this record to our list
            lines.append((date_time, f"{row[1]:>3}"))
            num_lines += 1

        # write out the corrected samples
        print("Date/Time, Glucose, min, max")
        for i in range(num_lines - 1, 0, -1):
            print(f"{lines[i][0]}, {lines[i][1]}, {MINVAL:>3}, {MAXVAL:>3}")


def main():
    """
    process the supplied file
    """
    if len(sys.argv) < 2:
        print("Usage: python csv_to_vector.py csvfile")
    else:
        process(sys.argv[1])


if __name__ == "__main__":
    main()
