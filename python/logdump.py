#!/usr/bin/python3

"""
    This is a utility to read a Subsurface xml dive log and generate
    a more traditional looking list of dives.
"""

import xml.etree.ElementTree as ET


def to_feet(meters):
    """ utility function to convert meters to feet """
    return int((meters * 3.28084) + .5)


def to_far(centegrade):
    """ utility funciton to convert centegrade to farenheit """
    return int(32 + (centegrade * (212 - 32) / 100) + .5)


def to_viz(stars):
    """ utility function to convert my vis stars into feet """
    visabilities = (3, 5, 10, 20, 50, 100)
    return visabilities[stars]


class Statics:
    """
        We create one Logdump instance per input file, but there are
        a few parameters that should continue from one file to the
        next
    """
    # formatting parameters that are the same for all instances
    page_len = 0    # number of lines per page
    page_pad = 0    # header/footer padding

    # running counts that should carry from one instance to the next
    buddy_dives = 0  # if we are counting buddy's dives rather than mine
    line_count = 0   # (total) number of lines output so far


class Logdump:
    """
        digest SubSurface logs and output a simple line-per-dive summary

        the particular information to be included in the summary is
        what I wanted to see, and a few aspects of this output are tied
        to the way I encode info in my own log (e.g. how I encode viz)
    """
    # output columns
    FORMAT = "%6s  %8s %5s  %4s  %4s  %4s  %4s  %4s   %s"
    f_title = \
        ("  num", "date    ", "start", "depth", "time ", "temp", "viz",
         "rate", "location")
    f_lines = \
        ("-----", "--------", "-----", "-----", "-----", "----", "---",
         "----", "--------")

    # persistent instance state
    root = None         # root of the XML tree

    def __init__(self, file, statics):
        self.statics = statics
        tree = ET.parse(file)
        self.root = tree.getroot()
        self.sitemap = {}

    def dump_dive(self, dive, buddy):
        """
            print a record for a single dive

            args:
                dive:   XML Element for the dive
                buddy:  only print if buddy matches
                        (to enble me to track Lynnette's dives)

        """
        # see if we have to match a buddy
        if buddy is not None:
            this_buddy = dive.find('buddy')
            if this_buddy is None or this_buddy.text != buddy:
                return

        # see if we need to output a page footer
        if statics.page_len > 0:
            last = statics.page_len - statics.page_pad
            if statics.line_count >= last:
                while statics.line_count < statics.page_len:
                    print("")
                    statics.line_count += 1
                statics.line_count = 0

        # see if we need to output a new header
        if statics.line_count == 0:
            while statics.line_count < statics.page_pad:
                print("")
                statics.line_count += 1

            print(self.FORMAT % self.f_title)
            print(self.FORMAT % self.f_lines)
            statics.line_count += 2

        # dive number may be mine or buddy's
        if buddy is not None or statics.buddy_dives > 0:
            statics.buddy_dives = statics.buddy_dives + 1
            dive_num = statics.buddy_dives
        else:
            dive_num = dive.get('number')
        if dive_num is not None:
            num = f"{int(dive_num):5d}"
        else:
            num = "  ???"

        # get the basic info
        dive_date = dive.get('date')
        if dive_date is not None:
            (year, mon, day) = dive_date.split('-')
            date = f"{int(mon):02d}/{int(day):02d}/{int(year) % 100:02d}"
        else:
            date = "        "

        dive_time = dive.get('time')
        if dive_time is not None:
            (hr, mins, _) = dive_time.split(':')
            time = f"{int(hr):02d}:{int(mins):02d}"
        else:
            time = "     "

        dive_dur = dive.get('duration')
        if dive_dur is not None:
            (x, y) = dive_dur.split(' ')
            (m, s) = x.split(':')
            dur = f"{int(m):02d}:{int(s):02d}"
        else:
            dur = "   ??"

        dive_vis = dive.get('visibility')
        if dive_vis is not None:
            viz = f"{to_viz(int(dive_vis)):3d}'"
        else:
            viz = " "

        dive_rating = dive.get('rating')
        if dive_rating is not None:
            rate = f"{int(dive_rating):1d}*"
        else:
            rate = "  "

        # get the location name
        dive_loc = dive.get('location')
        uuid = dive.get('divesiteid')
        if dive_loc is not None:
            loc = dive_loc.text
        elif uuid is not None:
            loc = self.sitemap[uuid]
        else:
            loc = "???"

        # get the maximum depth
        feet = "??? "
        temp = "   "
        dive_comp = dive.find('divecomputer')
        if dive_comp is not None:
            # maximum depth
            dive_depth = dive_comp.find('depth')
            if dive_depth is not None:
                dive_max = dive_depth.get('max')
                if dive_max is not None:
                    (x, y) = dive_max.split(' ')
                    feet = f" {to_feet(float(x)):3d}"

            # get the water temperature
            dive_temp = dive_comp.find('temperature')
            if dive_temp is not None:
                x = dive_temp.get('water')
                (y, _) = x.split(' ')
                deg_f = to_far(float(y))
                temp = f"{deg_f:3d}F"

        # now print it all out
        print(self.FORMAT % (num, date, time, feet, dur, temp, viz, rate, loc))
        statics.line_count += 1

    def dump_log(self, buddy):
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
        num_trips = 0
        num_dives = 0

        # find and dump each contained dive (stand-alone or in a trip)
        dives = self.root.find('dives')
        for child in dives:
            if child.tag == 'dive':
                self.dump_dive(child, buddy)
                num_dives += 1
            elif child.tag == 'trip':
                for subchild in child:
                    if subchild.tag == 'dive':
                        self.dump_dive(subchild, buddy)
                        num_dives += 1
                num_trips += 1

        return (num_trips, num_dives)


#
# TODO
#     if I were cooler, when multiple file names were specified, I would
#     accumulate them and then re-sort (and re-number) based on date and time
#
if __name__ == '__main__':

    # parse the arguments
    import argparse
    parser = argparse.ArgumentParser(description='Subsurface Log Dump')
    parser.add_argument("filename", nargs='+', help="log-file-name")
    parser.add_argument("--page", type=int, default='0', help="lines/page")
    parser.add_argument("--pad", type=int, default='0', help="top/bot margins")
    parser.add_argument("--buddy", type=str, default=None, help="buddy name")
    parser.add_argument("--dives", type=int, default='0',
                        help="buddy's previous dives")
    args = parser.parse_args()

    # initialize the format parameters
    statics = Statics()
    if args.page != 0:
        statics.page_len = args.page
        statics.page_pad = 1 if args.pad == 0 else args.pad
    if args.dives is not None:
        statics.buddy_dives = args.dives

    # process each log file
    buddy = args.buddy
    for name in args.filename:
        # instantiate the dumper
        dumper = Logdump(name, statics)

        # generate the output
        (trips, dives) = dumper.dump_log(buddy)

        # Kinky - because of the way I use this program, I only want the
        #         buddy argument to be used for the first file (assumed
        #         to be mine.  The second file is dives I wasn't on, and
        #         so the buddy argument would be inappropriate.
        buddy = None
