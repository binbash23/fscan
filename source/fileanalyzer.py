#
# 20220920 jens heine <binbash@gmx.net>
#
# import sqlite3
import os
# import sys
import hashlib
import magic
from configloader import *
import logging
import progressbar

#
# VARIABLES
#
databaseFilename = 'filedatabase.db'
FILEHASH_BLOCK_SIZE = 1073741824
FILEHASH_COMMIT_BATCH_SIZE = 100


#
# FUNCTIONS
#
def getLogger():
    # _log = log.getLogger("filescanner.fscan")
    _log = logging.getLogger()
    # console_handler = log.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # console_handler.setFormatter(formatter)
    # _log.addHandler(console_handler)
    # _log.setLevel(log.DEBUG)
    _log.handlers[0].setFormatter(formatter)
    _log.setLevel(getPropertyValue("LOG_LEVEL"))
    return _log


def calculateFilehash(filename):
    filehash = hashlib.sha3_256()
    #    filehash = hashlib.md5()
    with open(filename, 'rb') as file:
        fileblock = file.read(FILEHASH_BLOCK_SIZE)
        while len(fileblock) > 0:
            filehash.update(fileblock)
            fileblock = file.read(FILEHASH_BLOCK_SIZE)
    return filehash.hexdigest()


def startanalyzing():
    log = getLogger()
    FILEHASH_BLOCK_SIZE = int(getPropertyValue("FILEHASH_BLOCK_SIZE"))
    FILEHASH_COMMIT_BATCH_SIZE = int(getPropertyValue("FILEHASH_COMMIT_BATCH_SIZE"))
    log.debug("Opening file database...")
    conn = sqlite3.connect(databaseFilename)
    cursor = conn.cursor()

    # Collect all files and insert them into database
    log.info("Calculating file hashes...")
    # start hashing files that have no hashvalue yet and which have more than 0 bytes filesize beginning with the latest ones
    cursor.execute(
        "select path, filename from allfiles where (filehash is null or filehash = '') and filesize > 0 order by ctime desc")
    sqlresult = cursor.fetchall()
    filesToHash = len(sqlresult)
    filesHashed = 0
    bar = progressbar.ProgressBar(max_value=filesToHash).start()
    bar.start()
    for row in sqlresult:
        log.debug("Files left (calculation hash value) : " + str(filesToHash))
        path = row[0]
        filename = row[1]
        # print(os.path.join(path, filename))
        try:
            log.debug("Calculating filehash for: " + filename)
            hashvalue = calculateFilehash(os.path.join(path, filename))
            log.debug("Hash is: " + str(hashvalue))
        except Exception as e:
            log.error(e)
            # log.error("Error calculating filehash for file: " + filename + sys.exc_info())
            hashvalue = None
        if hashvalue is None:
            updatestring = "update allfiles set filehash = NULL where path = ? and filename = ?"
        else:
            updatestring = "update allfiles set filehash = '" + hashvalue + "', hash_date = datetime('now', 'localtime') where path = ? and filename = ?"
        values = (path, filename)
        try:
            cursor.execute(updatestring, values)
            filesHashed += 1
            bar.update(filesHashed)
        except Exception as e:
            log.error(e)
        filesToHash -= 1
        if filesToHash % FILEHASH_COMMIT_BATCH_SIZE == 0:
            log.debug("Committing updates...")
            conn.commit()
    bar.finish()
    log.info("Ready: " + str(filesHashed) + " files processed.")
    conn.commit()

    #
    # Start analyzing mime types
    #
    log.info("Analyzing mime types...")
    # start hashing files that have no hashvalue yet and which have more than 0 bytes filesize beginning with the latest ones
    cursor.execute("select path, filename from allfiles where mimetype is null and filesize > 0 order by ctime desc")
    sqlresult = cursor.fetchall()
    filesToAnalyze = len(sqlresult)
    filesAnalyzed = 0
    bar2 = progressbar.ProgressBar(max_value=filesToAnalyze).start()
    bar2.start()
    for row in sqlresult:
        log.debug("Files left (mime type detection) : " + str(filesToAnalyze))
        path = row[0]
        filename = row[1]
        # print(os.path.join(path, filename))
        try:
            log.debug("Analyzing file: " + filename)
            # mimetype = calculateFilehash(os.path.join(path, filename))   ###
            mimetype = magic.from_file(os.path.join(path, filename), mime=True)
            log.debug("Mime type is: " + mimetype)
        except Exception as e:
            # log.error("Error analyzing file: " + filename + " " + sys.exc_info())
            log.error(e)
            mimetype = None
        if mimetype is None:
            updatestring = "update allfiles set mimetype = NULL where path = ? and filename = ?"
        else:
            updatestring = "update allfiles set mimetype = '" + mimetype + "' where path = ? and filename = ?"
        values = (path, filename)
        try:
            cursor.execute(updatestring, values)
            filesAnalyzed += 1
        except Exception as e:
            log.error(e)
        filesToAnalyze -= 1
        bar2.update(filesAnalyzed)
        if filesToAnalyze % FILEHASH_COMMIT_BATCH_SIZE == 0:
            log.debug("Committing updates...")
            conn.commit()
    bar2.finish()
    log.info("Ready: " + str(filesAnalyzed) + " files processed.")
    conn.commit()

    conn.close()
