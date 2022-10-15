#
# 20220930 jens heine <binbash@gmx.net>
#
import os.path
import sqlite3
import sys
import logging
from sqlstatements import *
from configloader import *

#
# variables
#
databaseFilename = 'filedatabase.db'


#
# functions
#
def showDatabaseStats():
    try:
        conn = sqlite3.connect(databaseFilename)
        cursor = conn.cursor()
        sqlstring = "select * from database_stats"
        sqlresult = cursor.execute(sqlstring)
        result = sqlresult.fetchall()
        for row in result:
            print(str(row[0]).ljust(28), str(row[1]).ljust(30), str(row[2]).ljust(30))
    except Exception as e:
        logging.error(e)
    finally:
        conn.close()


def showDuplicates():
    try:
        conn = sqlite3.connect(databaseFilename)
        cursor = conn.cursor()
        #sqlstring = "select * from allfiles_duplicates_without_original"
        sqlresult = cursor.execute(SQL_SHOW_DUPLICATES)
        result = sqlresult.fetchall()
        i = 0
        for row in result:
            print(i, '-', row)
            i += 1
        #print("Found", len(result), "duplicates.")
    except Exception as e:
        logging.error(e)
    finally:
        conn.close()


def showMimeStats():
    try:
        conn = sqlite3.connect(databaseFilename)
        cursor = conn.cursor()
        sqlstring = "select * from allfiles_mime_stats"
        sqlresult = cursor.execute(sqlstring)
        result = sqlresult.fetchall()
        for row in result:
            print(str(row[0]).ljust(60), str(row[1]).ljust(10))
        print("Found", len(result), "mime types.")
    except Exception as e:
        logging.error(e)
    finally:
        conn.close()


def createInitialDatabase():
    try:
        conn = sqlite3.connect(databaseFilename)
        cursor = conn.cursor()
        logging.debug("Setting PRAGMA journal_mode = WAL for database.")
        cursor.execute("PRAGMA journal_mode = WAL")
        conn.commit()
        sqlstring = "select value from configuration where property = 'WORKPATH'"
        sqlresult = cursor.execute(sqlstring)
        value = sqlresult.fetchone()[0]
        if value is not None:
            return
    except:
        1 == 1
        #  do nothing
    try:
        #print("Creating initial database...")
        logging.info("Creating initial database...")
        conn = sqlite3.connect(databaseFilename)
        cursor = conn.cursor()
        cursor.executescript(SQL_CREATE_DATABASE_SCHEMA)
        cursor.executescript(SQL_CREATE_DEFAULT_CONFIGURATION)
    except Exception as e:
        logging.error(e)
    finally:
        conn.close()

# showDuplicates()
createInitialDatabase()
