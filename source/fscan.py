#!/usr/bin/python3
#
# 20221002 jens heine <binbash@gmx.net>
#

# import logging
import optparse
# from configloader import *
from database import *
from filescanner import *
from fileanalyzer import *
from duplicatearchiver import *
from optparse import OptionGroup

VERSION = "fscan by Jens Heine <binbash@gmx.net> version: 20221016"
#
# main
#
def main():
    parser = optparse.OptionParser()
    parser.add_option("-s", "--scan", action="store_true", dest="scan", default=False, help="Start filesystem scan")
    parser.add_option("-a", "--analyze", action="store_true", dest="analyze", default=False,
                      help="Start filesystem analysis (hashing and mime type detection)")
    parser.add_option("-m", "--moveduplicates", action="store_true", dest="moveduplicates", default=False,
                      help="Move duplicate files to archive folder")
    parser.add_option("-c", "--config", action="store_true", dest="config", default=False,
                      help="Show configuration")
    parser.add_option("-M", "--mimetypes", action="store_true", dest="mimetypes", default=False,
                      help="Show mime type statistics")
    parser.add_option("-d", "--duplicates", action="store_true", dest="duplicates", default=False,
                      help="Show duplicate files")
    parser.add_option("-S", "--stats", action="store_true", dest="stats", default=False,
                      help="Show database statistics")
    parser.add_option("-l", "--loglevel", action="store", dest="loglevel",
                      help="Set loglevel (DEBUG, INFO, WARN, ERROR, CRITICAL)")
    parser.add_option("-V", "--version", action="store_true", dest="version", default=False,
                      help="Show fscan version info")
    group = OptionGroup(parser, "Set configuration parameter")
    group.add_option("-p", "--property", action="store", dest="property", help="Set property")
    group.add_option("-v", "--value", action="store", dest="value", help="Set value")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    #print("->", options.loglevel.upper())
    if options.loglevel is not None:
        loglevel_int = getattr(logging, options.loglevel.upper(), None)
        if not isinstance(loglevel_int, int):
            raise ValueError("Invalid log level: %s" % loglevel_int)
        setPropertyValue("LOG_LEVEL", options.loglevel.upper())

    createInitialDatabase()

    if options.scan == True:
        startscanning()
    if options.analyze == True:
        startanalyzing()
    if options.moveduplicates == True:
        archiveDuplicateFiles()
    if options.config == True:
        showConfiguration()
    if options.duplicates == True:
        showDuplicates()
    if options.mimetypes == True:
        showMimeStats()
    if options.stats == True:
        showDatabaseStats()
    if options.property is not None and options.value is not None:
        setPropertyValue(options.property, options.value)
    if options.version == True:
        print(VERSION)

if __name__ == '__main__':
    main()
