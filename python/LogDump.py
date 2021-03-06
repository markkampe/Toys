#!/usr/bin/python

import xml.etree.ElementTree as ET

def toFeet(meters):
    """ utility function to convert meters to feet """
    return int((meters * 3.28084) + .5)


def toFar(centegrade):
    """ utility funciton to convert centegrade to farenheit """
    return int(32 + (centegrade * (212 - 32) / 100) + .5)


def toViz(stars):
    """ utility function to convert my vis stars into feet """
    visabilities = (3, 5, 10, 20, 50, 100)
    return visabilities[stars]


class LogDump:
    """
        digest SubSurface logs and output a simple line-per-dive summary

        the particular information to be included in the summary is
        what I wanted to see, and a few aspects of this output are tied
        to the way I encode info in my own log (e.g. how I encode viz)
    """

    buddyDives = 0  # if we are counting buddy's dives rather than mine

    # output columns
    FORMAT = "%6s  %8s %5s  %4s  %4s  %4s  %4s  %4s   %s"
    f_title = \
        ("  num", "date    ", "start", "depth", "time ", "temp", "viz",
         "rate", "location")
    f_lines = \
        ("-----", "--------", "-----", "-----", "-----", "----", "---",
         "----", "--------")

    # persistent instance state
    linecount = 0       # lines we have already printed (on this page)
    root = None         # root of the XML tree

    # formatting parameters
    page_len = 0        # number of lines per page
    page_pad = 0        # header/footer padding

    def __init__(self, file):
        tree = ET.parse(file)
        self.root = tree.getroot()
        self.sitemap = {}

    def dumpDive(self, dive, buddy):
        """
            print a record for a single dive

            args:
                dive:   XML Element for the dive
                buddy:  only print if buddy matches
                        (to enble me to track Lynnette's dives)

        """

        # see if we have to match a buddy
        if buddy is not None:
            thisBuddy = dive.find('buddy')
            if thisBuddy is None or thisBuddy.text != buddy:
                return

        # see if we need to output a page footer
        if self.page_len > 0:
            last = self.page_len - self.page_pad
            if self.linecount >= last:
                while self.linecount < self.page_len:
                    print
                    self.linecount += 1
                self.linecount = 0

        # see if we need to output a new header
        if self.linecount == 0:
            while self.linecount < self.page_pad:
                print
                self.linecount += 1

            print self.FORMAT % self.f_title
            print self.FORMAT % self.f_lines
            self.linecount += 2

        # dive number may be mine or buddy's
        if buddy is not None:
            global buddyDives
            buddyDives = buddyDives + 1
            diveNum = buddyDives
        else:
            diveNum = dive.get('number')
        if diveNum is not None:
            num = "%5d" % int(diveNum)
        else:
            num = "  ???"

        # get the basic info
        diveDate = dive.get('date')
        if diveDate is not None:
            (year, mon, day) = diveDate.split('-')
            date = "%02d/%02d/%02d" % (int(mon), int(day), int(year) % 100)
        else:
            date = "        "

        diveTime = dive.get('time')
        if diveTime is not None:
            (hr, min, sec) = diveTime.split(':')
            time = "%02d:%02d" % (int(hr), int(min))
        else:
            time = "     "

        diveDur = dive.get('duration')
        if diveDur is not None:
            (x, y) = diveDur.split(' ')
            (m, s) = x.split(':')
            dur = "%02d:%02d" % (int(m), int(s))
        else:
            dur = "   ??"

        diveVis = dive.get('visibility')
        if diveVis is not None:
            viz = "%3d'" % toViz(int(diveVis))
        else:
            viz = " "

        diveRating = dive.get('rating')
        if diveRating is not None:
            rate = "%1d*" % int(diveRating)
        else:
            rate = "  "

        # get the location name
        diveLoc = dive.get('location')
        uuid = dive.get('divesiteid')
        if diveLoc is not None:
            loc = diveLoc.text
        elif uuid is not None:
            loc = self.sitemap[uuid]
        else:
            loc = "???"

        # get the maximum depth
        feet = "??? "
        temp = "   "
        diveComp = dive.find('divecomputer')
        if diveComp is not None:
            # maximum depth
            diveDepth = diveComp.find('depth')
            if diveDepth is not None:
                diveMax = diveDepth.get('max')
                if diveMax is not None:
                    (x, y) = diveMax.split(' ')
                    feet = " %3d'" % (toFeet(float(x)))

            # get the water temperature
            diveTemp = diveComp.find('temperature')
            if diveTemp is not None:
                x = diveTemp.get('water')
                (y, z) = x.split(' ')
                degF = toFar(float(y))
                temp = "%3dF" % degF

        # now print it all out
        print self.FORMAT % (num, date, time, feet, dur, temp, viz, rate, loc)
        self.linecount += 1

    def dumpLog(self, buddy):
        """
            enumerate and list all the dives in this log
            args buddy name (optional), only list matching dives
        """


        # build up a divesite map
        sites = self.root.find('divesites')
        for child in sites:
            if child.tag == 'site':
                sitename = child.get('name')
                uuid = child.get('uuid')
                if sitename is not None and uuid is not None:
                    self.sitemap[uuid] = sitename

        # print header, initialize counters
        numTrips = 0
        numDives = 0

        # find and dump each contained dive (stand-alone or in a trip)
        dives = self.root.find('dives')
        for child in dives:
            if child.tag == 'dive':
                self.dumpDive(child, buddy)
                numDives += 1
            elif child.tag == 'trip':
                for subchild in child:
                    if subchild.tag == 'dive':
                        self.dumpDive(subchild, buddy)
                        numDives += 1
                numTrips += 1

        return (numTrips, numDives)


if __name__ == '__main__':

    # parse the arguments
    import argparse
    parser = argparse.ArgumentParser(description='Subsurface Log Dump')
    parser.add_argument("filename", help="log-file-name")
    parser.add_argument("--page", type=int, default='0', help="lines/page")
    parser.add_argument("--pad", type=int, default='0', help="top/bot margins")
    parser.add_argument("--buddy", type=str, default=None, help="buddy name")
    parser.add_argument("--dives", type=int, default='0', help="buddy's previous dives")
    args = parser.parse_args()

    # instantiate the dumper
    dumper = LogDump(args.filename)
    if args.page != 0:
        dumper.page_len = args.page
        dumper.page_pad = 1 if args.pad == 0 else args.pad

    # generate the output
    buddyDives = args.dives
    (trips, dives) = dumper.dumpLog(args.buddy)
