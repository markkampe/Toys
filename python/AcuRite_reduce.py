"""
This program reads (csv) AcuRite downloads, and reduces them to daily
max and min temperatures and humidities (for a specified sensor)

usage:  python3 accurite_reduce.py -s sensor [-v] rawdata.csv
"""
import sys
import os.path
from optparse import OptionParser
import csv

# AcuRite (input) column headings
hSense = "Sensor Name"
hTime = "Timestamp"
hTemp = "Temperature ( F )"
hHum = "Humidity ( RH )"

# my (output) headings
hDate = "Date"
hTmax = "max Temperature ( F )"
hTmin = "min Temperature ( F )"
hHmax = "max Humidity ( RH )"


def analyze(row):
    """ analyze the first line of a CSV file to find needed columns """
    columns = {}

    for c in range(len(row)):
        s = row[c]
        if s == hSense:
            columns["sensor"] = c
        elif s == hTime:
            columns["time"] = c
        elif s == hTemp:
            columns["temp"] = c
        elif s == hHum:
            columns["humidity"] = c

    return columns


if __name__ == "__main__":
    """ argument processing and main loop """

    # process the command line arguments
    msg = "usage: %prog [options] input_file"
    parser = OptionParser(usage=msg)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose output")
    parser.add_option("-s", "--sensor", dest="sensor", metavar="STRING",
                      default="*")

    (opts, files) = parser.parse_args()
    if len(files) < 1:
        sys.stderr.write("ERROR: missing filename(s)\n")
        exit(-1)

    # we will accumulate temp/humidity range for each sensor/day
    readings = {}   # readings[sensor_date] = [Tmin, Tmax, Hmax]

    # process each input file for the specified sensor
    for file in files:
        # process every line in the CSV file, dividing it into columns
        with open(file) as csv_file:
            if opts.verbose:
                sys.stderr.write("Processing file " + file +
                                 ", sensor=" + opts.sensor + "\n")

            csv_reader = csv.reader(csv_file, delimiter=',')
            line = 0
            for row in csv_reader:
                line += 1
                if line == 1:       # find desired input columns
                    cols = analyze(row)
                    cSense = cols["sensor"]
                    cTime = cols["time"]
                    cTemp = cols["temp"]
                    cHum = cols["humidity"]
                else:               # process a sensor reading
                    sensor = row[cSense]
                    # look for lines from chosen sensor
                    if opts.sensor == "*" or sensor == opts.sensor:
                        timestamp = row[cTime]
                        date = timestamp.split()[0]
                        temp = float(row[cTemp])
                        hum = float(row[cHum])

                        key = sensor + "_" + date
                        if key in readings:
                            current = readings[key]
                            Tmin = temp if temp < current[0] else current[0]
                            Tmax = temp if temp > current[1] else current[1]
                            Hmax = hum if temp > current[2] else current[2]
                            readings[key] = [Tmin, Tmax, Hmax]
                        else:       # first reading is highest and lowest
                            readings[key] = [temp, temp, hum]

        # print out all the accumulated sensor/date values
        print(hSense + "," + hDate + "," + hTmin + "," + hTmax + "," + hHmax)
        for key in readings:
            values = readings[key]
            fields = key.split("_")
            sensor = fields[0]
            date = fields[1]
            Tmin = str(values[0])
            Tmax = str(values[1])
            Hmax = str(values[2])
            print(sensor + "," + date + "," + Tmin + "," + Tmax + "," + Hmax)
