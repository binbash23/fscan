#
# 20220920 jens heine <binbash@gmx.net>
#
import logging
import sqlite3
import os
import sys
from sqlstatements import *  # All sql statements properly formatted
from configloader import *

#
# VARIABLES
#
databaseFilename = 'filedatabase.db'
WORKPATH = None
FILESCAN_COMMIT_BATCH_SIZE = 50000
DUPLICATES_ARCHIVE_PATH = None


#
# FUNCTIONS
#
def getLogger():
    #_log = logging.getLogger("filescanner.fscan")
    _log = logging.getLogger()
    #console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #console_handler.setFormatter(formatter)
    #_log.addHandler(console_handler)
    # _log.setLevel(logging.DEBUG)
    _log.handlers[0].setFormatter(formatter)
    _log.setLevel(getPropertyValue("LOG_LEVEL"))
    return _log


def startscanning():
    log = getLogger()
    #log.setLevel(getPropertyValue("LOG_LEVEL"))
    FILESCAN_COMMIT_BATCH_SIZE = int(getPropertyValue("FILESCAN_COMMIT_BATCH_SIZE"))
    DUPLICATES_ARCHIVE_PATH = getPropertyValue("DUPLICATES_ARCHIVE_PATH")
    WORKPATH = getPropertyValue("WORKPATH")
    log.debug("Opening file database...")
    conn = sqlite3.connect(databaseFilename)
    cursor = conn.cursor()

    # First delete tmp table
    try:
        log.debug("Clearing table allfiles_scan...")
        cursor.execute("delete from allfiles_scan")
    except Exception as e:
        log.error(e)

    # Collect all files and insert them into database temp table
    log.info("Collecting files and file information from : " + WORKPATH + "...")
    if WORKPATH == "/path_to/Pictures":
        log.warning("Maybe you have to set the WORKPATH first.")
        log.warning("Try: fscan.py -p 'WORKPATH' -v '/home/<myusername>/Bilder'")
    fileCount = 0
    rowsInserted = 0
    for path, currentDirectory, files in os.walk(WORKPATH):
        if path.startswith(DUPLICATES_ARCHIVE_PATH):
            log.debug("Skipping path " + path + " because it is used to archive duplicates!")
            continue
        for file in files:
            fileCount += 1
            try:
                # print(fileCount + os.path.join(path, file))
                fileStats = os.stat(os.path.join(path, file))
                fileSize = fileStats.st_size
                ctime = fileStats.st_ctime
                mtime = fileStats.st_mtime
            except KeyboardInterrupt as ke:
                print("Canceled by user.")
                sys.exit(0)
            except Exception as e:
                log.error(e)
                continue
            try:
                cursor.execute(
                    "insert into allfiles_scan (path, filename, filesize, ctime, mtime) values (? , ? , ?, ?, ?)",
                    (path, file, fileSize, ctime, mtime))
                rowsInserted += 1
            except KeyboardInterrupt as ke:
                print("Canceled by user.")
                sys.exit(0)
            except Exception as e:
                log.error(fileCount, " : Error inserting file record:", e)
            if fileCount % FILESCAN_COMMIT_BATCH_SIZE == 0:
                log.debug("Committing batch (" + str(FILESCAN_COMMIT_BATCH_SIZE) + "/" + str(rowsInserted) + ") ...")
                conn.commit()

    log.info("Found " + str(fileCount) + " files in workdir: " + WORKPATH)
    log.info("Inserted " + str(rowsInserted) + " files into database")

    #
    # SQL Operations
    #
    log.debug("Setting is_existing flag in allfiles to 0...")
    try:
        cursor.execute("UPDATE	allfiles SET is_existing = 0")
        conn.commit()
    except Exception as e:
        log.error(e)

    log.debug("Find files that are new in the working directory...")
    try:
        cursor.execute(SQL_FIND_FILES_IN_ALLFILES_SCAN_THAT_ARE_NOT_IN_ALLFILES)
        resultset = cursor.fetchall()
        for row in resultset:
            log.info("NEW FILE >>> " + row[0] + os.path.sep + row[1])
        log.debug("Update allfiles_changed tables with new found files...")
        cursor.execute(SQL_UPDATE_ALLFILES_CHANGED_WITH_NEW_FOUND_FILES_IN_SCAN)
        conn.commit()
    except Exception as e:
        log.error(e)

    log.debug("Insert new files into allfiles table...")
    try:
        cursor.execute(SQL_INSERT_INTO_ALLFILES_NEW_FROM_ALLFILES_SCAN)
        conn.commit()
    except Exception as e:
        log.error(e)

    log.debug("Mark all already existing files with is_existing = 1 ...")
    try:
        cursor.execute(
            "UPDATE allfiles SET is_existing = 1 WHERE id in ( SELECT a.id FROM allfiles_scan t,	allfiles a WHERE t.path = a.path AND t.filename = a.filename)")
        conn.commit()
    except Exception as e:
        log.error(e)

    log.debug("Find files that have changed since last scan...")
    try:
        cursor.execute(SQL_FIND_CHANGED_FILES)
        resultset = cursor.fetchall()
        for row in resultset:
            log.info("CHANGED FILE >>> " + row[0] + os.path.sep + row[1])
        log.debug("Update allfiles_changed tables with changed files after scan...")
        cursor.execute(SQL_UPDATE_ALLFILES_CHANGED_WITH_CHANGED_FILES_AFTER_SCAN)
        conn.commit()
    except Exception as e:
        log.error(e)

    """
    Markiere alle dateien in allfiles, die auch in allfiles_scan vorhanden sind und
    wo sich aber ctime, mtime oder filesize unterscheiden und setze filehash = NULL
    """
    log.debug("Invalidate filehashes and update attributes from files that have changed...")
    try:
        cursor.execute(SQL_DELETE_CHANGED_FILE_ROWS)
        cursor.execute(SQL_INSERT_INTO_ALLFILES_NEW_FROM_ALLFILES_SCAN)
        conn.commit()
    except Exception as e:
        log.error(e)

    log.debug("Find files that are missing since last scan...")
    try:
        cursor.execute(SQL_FIND_FILES_IN_ALLFILES_IS_EXISTING_FALSE)
        resultset = cursor.fetchall()
        for row in resultset:
            log.info("MISSING FILE >>> " + row[0] + os.path.sep + row[1])
        log.debug("Update allfiles_changed tables with deleted files after scan...")
        cursor.execute(SQL_UPDATE_ALLFILES_CHANGED_WITH_DELETED_FILES_AFTER_SCAN)
        conn.commit()
    except Exception as e:
        log.error(e)

    """
    Lösche alle file Zeilen, die nicht mehr aktuell existieren
    """
    log.debug("Clean allfiles table and delete rows with files that do not exist anymore...")
    try:
        cursor.execute(SQL_DELETE_NOT_EXISTING_ROWS)
        conn.commit()
    except Exception as e:
        log.error(e)

    conn.commit()
    conn.close()


def main():
    log.debug("staaaarting")

    startscanning()


if __name__ == '__main__':
    main()
