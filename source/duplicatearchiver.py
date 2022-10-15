#
# 20221002 jens heine <binbash@gmx.net>
#
import sqlite3
import sys
import os
from configloader import *
from datetime import datetime
from datetime import date
import shutil
from pathlib import Path
import logging

#
# variables
#
databaseFilename = 'filedatabase.db'
DUPLICATES_ARCHIVE_PATH = None

#
# functions
#
def getLogger():
    #_log = log.getLogger("filescanner.fscan")
    _log = logging.getLogger()
    #console_handler = log.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #console_handler.setFormatter(formatter)
    #_log.addHandler(console_handler)
    # _log.setLevel(log.DEBUG)
    _log.handlers[0].setFormatter(formatter)
    _log.setLevel(getPropertyValue("LOG_LEVEL"))
    return _log


def archiveDuplicateFiles():
    log = getLogger()
    DUPLICATES_ARCHIVE_PATH = getPropertyValue("DUPLICATES_ARCHIVE_PATH")
    conn = sqlite3.connect(databaseFilename)
    cursor = conn.cursor()
    cursor.execute("select sum(bytes) as sum_bytes from allfiles_duplicate_bytes")
    result = cursor.fetchone()
    totalbytestomove = result[0]
    totalbytestomoveformatted = round(totalbytestomove / 1024.0 / 1024 / 1024, 3)
    sqlstring = "select path, filename, filesize from allfiles_duplicates_without_original"
    cursor.execute(sqlstring)
    result = cursor.fetchall()
    numberofduplicatefiles = len(result)
    log.info("Found " + str(numberofduplicatefiles) + " duplicate files.")
    if numberofduplicatefiles == 0:
        return
    Path(DUPLICATES_ARCHIVE_PATH).mkdir(parents=True, exist_ok=True)
    timestampfolder = datetime.now().strftime('%Y%m%d-%H%M%S')
    log.info("Moving files to archive directory: " + DUPLICATES_ARCHIVE_PATH)
    filenumber = 0
    bytesmoved = 0
    for path, file, filesize in result:
        filenumber += 1
        sourcefile = os.path.join(path, file)
        destinationfile = os.path.join(DUPLICATES_ARCHIVE_PATH + os.path.sep + timestampfolder + path, file)
        Path(DUPLICATES_ARCHIVE_PATH + os.path.sep + timestampfolder + path).mkdir(parents=True, exist_ok=True)
        bytesmovedformatted = round(bytesmoved / 1024.0 / 1024 / 1024, 3)
        percentdone = round((bytesmoved / 1024.0 / 1024 / 1024 * 100) / totalbytestomove, 2)
        log.debug(str(filenumber) + "/" + str(numberofduplicatefiles) + "-" + str(bytesmovedformatted) + "GB / " +
              str(totalbytestomoveformatted) + "GB -" + str(percentdone) + "%")
        log.debug("Archiving :" + sourcefile)
        log.debug("To        :" + destinationfile)
        try:
            shutil.move(sourcefile, destinationfile)
        except Exception as e:
            log.error(e)
        bytesmoved += filesize
        #if filenumber >= 100:
        #    break
    conn.close()


#
# main
#
#archiveDuplicateFiles()






















