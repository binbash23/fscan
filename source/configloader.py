#
# 20220930 jens heine <binbash@gmx.net>
#
import sqlite3
import sys
import logging

#
# variables
#
databaseFilename = 'filedatabase.db'


#
# functions
#
def showConfiguration():
    try:
        conn = sqlite3.connect(databaseFilename)
        cursor = conn.cursor()
        sqlstring = "select * from configuration"
        sqlresult = cursor.execute(sqlstring)
        result = sqlresult.fetchall()
        for row in result:
            print(row[0].ljust(28), row[1].ljust(30), row[2].ljust(30))
    except:
        logging.error(sys.exc_info())
    finally:
        conn.close()


def getPropertyValue(property):
    value = None
    try:
        conn = sqlite3.connect(databaseFilename)
        cursor = conn.cursor()
        sqlstring = "select value from configuration where property = '" + property + "'"
        sqlresult = cursor.execute(sqlstring)
        value = sqlresult.fetchone()[0]
        #conn.commit()
    except:
        logging.error(sys.exc_info())
    finally:
        conn.close()
    #print("Found value for property " + property + " = " + value)
    return value


def setPropertyValue(property, value):
    if property is None or value is None or property == "" or value == "":
        raise ValueError("Property and value must not be empty or None!")
    try:
        conn = sqlite3.connect(databaseFilename)
        cursor = conn.cursor()
        sqlstring = "update configuration set value = '" + value + "' where property = '" + property + "'"
        #        print(property)
        #        print(value)
        #        print(sqlstring)
        cursor.execute(sqlstring)
        conn.commit()
    except:
        logging.error(sys.exc_info())
        return False
    finally:
        conn.close()
    #print("Set value for property " + property + " = " + value)
    return True

#
# main
#
# getPropertyValue("workpath")

# setPropertyValue("FILEHASH_COMMIT_BATCH_SIZE", "220")

# setPropertyValue("workpath", "/home/melvin/Bilder/")

# setPropertyValue("FILEHASH_COMMIT_BATCH_SIZE", "")
