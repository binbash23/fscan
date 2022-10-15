#
# 20220920 jens heine <binbash@gmx.net>
#
SQL_SET_IS_EXISTING_TO_1_WHEN_THEY_STILL_EXIST = """\
    UPDATE
	allfiles
    SET
	is_existing = 1
    WHERE
	id in 
    (
    SELECT
	a.id
    FROM
	allfiles_scan t,
	allfiles a
    WHERE
	t.path = a.path
	AND
	t.filename = a.filename
    )
"""
SQL_DELETE_NOT_EXISTING_ROWS = "delete from allfiles where is_existing = 0"
SQL_DELETE_CHANGED_FILE_ROWS = """\
    DELETE FROM
	allfiles
    WHERE
	id in 
    (
    SELECT
	a.id
    FROM
	allfiles_scan t,
	allfiles a
    WHERE
	t.path = a.path
	AND
	t.filename = a.filename
	AND
	(
	t.ctime <> a.ctime
	OR
	t.mtime <> a.mtime	
	OR
	t.filesize <> a.filesize
	)
    )
"""
SQL_INSERT_INTO_ALLFILES_NEW_FROM_ALLFILES_SCAN = """\
    INSERT INTO allfiles (path, filename, filesize, ctime, mtime, is_existing)
    SELECT
	path, filename, filesize, ctime, mtime, 1
    FROM
	allfiles_scan
    WHERE
	id not in (
    SELECT
	t.id
    FROM
	allfiles_scan t,
	allfiles a
    WHERE
	t.path = a.path and t.filename = a.filename
    )
"""
SQL_FIND_FILES_IN_ALLFILES_SCAN_THAT_ARE_NOT_IN_ALLFILES = """\
    SELECT
	path, filename
    FROM
	allfiles_scan
    WHERE
	id not in (
    SELECT
	t.id
    FROM
	allfiles_scan t,
	allfiles a
    WHERE
	t.path = a.path and t.filename = a.filename
    )
"""
SQL_FIND_CHANGED_FILES = """\
    SELECT
	path, filename
	FROM
	allfiles
    WHERE
	id in 
    (
    SELECT
	a.id
    FROM
	allfiles_scan t,
	allfiles a
    WHERE
	t.path = a.path
	AND
	t.filename = a.filename
	AND
	(
	t.ctime <> a.ctime
	OR
	t.mtime <> a.mtime	
--	OR
--	t.atime <> a.atime
	OR
	t.filesize <> a.filesize
	)
    )
"""
SQL_FIND_FILES_IN_ALLFILES_IS_EXISTING_FALSE = """\
    SELECT
	path, filename
    FROM
	allfiles
    WHERE
	is_existing = 0
"""
SQL_UPDATE_ALLFILES_CHANGED_WITH_NEW_FOUND_FILES_IN_SCAN = """\
	insert into allfiles_changed (
		allfiles_create_date,
		path, 
		filename,
		filesize,
		ctime,
		mtime,
		status
	)
    SELECT
		create_date as allfiles_create_date,
		path, 
		filename,
		filesize,
		ctime,
		mtime,
		"new"
    FROM
		allfiles_scan
    WHERE
		id not in (
		SELECT
			s.id
		FROM
			allfiles_scan s,
			allfiles a
		WHERE
			s.path = a.path and s.filename = a.filename
		)
"""
SQL_UPDATE_ALLFILES_CHANGED_WITH_CHANGED_FILES_AFTER_SCAN = """\
insert into allfiles_changed (
		allfiles_create_date,
		allfiles_last_update_date,
		path, 
		filename,
		filesize,
		filehash,
		hash_date,
		ctime,
		mtime,
		status
	)
    SELECT
		create_date as allfiles_create_date,
		last_update_date as allfiles_last_update_date,
		path, 
		filename,
		filesize,
		filehash,
		hash_date,
		ctime,
		mtime,
		"changed" 
	FROM
		allfiles
    WHERE
		id in 
		(
		SELECT
			a.id
		FROM
			allfiles_scan t,
			allfiles a
		WHERE
			t.path = a.path
			AND
			t.filename = a.filename
			AND
			(
			t.ctime <> a.ctime
			OR
			t.mtime <> a.mtime	
			OR
			t.filesize <> a.filesize
			)
		)	
"""
SQL_UPDATE_ALLFILES_CHANGED_WITH_DELETED_FILES_AFTER_SCAN = """\
insert into allfiles_changed (
		allfiles_create_date,
		allfiles_last_update_date,
		path, 
		filename,
		filesize,
		filehash,
		hash_date,
		ctime,
		mtime,
		status
	)
    SELECT
		create_date as allfiles_create_date,
		last_update_date as allfiles_last_update_date,
		path, 
		filename,
		filesize,
		filehash,
		hash_date,
		ctime,
		mtime,
		"deleted" 
	FROM
		allfiles
    WHERE
		is_existing = 0
"""

SQL_CREATE_DATABASE_SCHEMA = """\
CREATE TABLE IF NOT EXISTS "allfiles" (
	"id"	INTEGER,
	"create_date"	TEXT,
	"last_update_date"	TEXT,
	"path"	TEXT,
	"filename"	TEXT,
	"filesize"	INTEGER,
	"ctime_formatted" generate always as (strftime('%Y%m%d %H:%M:%S', datetime(ctime, 'unixepoch'))) VIRTUAL, 
	"mtime_formatted" generate always as (strftime('%Y%m%d %H:%M:%S', datetime(mtime, 'unixepoch'))) VIRTUAL,
	"hash_date"	TEXT, 
	"is_existing"	INTEGER DEFAULT 1,
	"filehash"	TEXT,
	"ctime"	TEXT,
	"mtime"	TEXT, mimetype text,
	UNIQUE("path","filename"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
--CREATE TABLE allfiles_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "allfiles_scan" (
	"id"	INTEGER,
	"create_date"	TEXT,
	"path"	TEXT,
	"filename"	TEXT,
	"filesize"	INT,
	"ctime_formatted" generate always as (strftime('%Y%m%d %H:%M:%S', datetime(ctime, 'unixepoch'))) VIRTUAL, 
	"mtime_formatted" generate always as (strftime('%Y%m%d %H:%M:%S', datetime(mtime, 'unixepoch'))) VIRTUAL,
	"ctime"	TEXT,
	"mtime"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "allfiles_changed" (
	"id"	INTEGER,
	"create_date"	TEXT,
	"allfiles_create_date"	TEXT,
	"allfiles_last_update_date"	TEXT,
	"path"	TEXT,
	"filename"	TEXT,
	"filesize"	INTEGER,
	"filehash"	TEXT,
	"hash_date"	TEXT, 
	"ctime_formatted" generate always as (strftime('%Y%m%d %H:%M:%S', datetime(ctime, 'unixepoch'))) VIRTUAL,
	"mtime_formatted" generate always as (strftime('%Y%m%d %H:%M:%S', datetime(mtime, 'unixepoch'))) VIRTUAL,
	"is_existing"	INTEGER DEFAULT 1,
	"ctime"	TEXT,
	"mtime"	TEXT,
	"status"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "configuration" (
	"property"	TEXT NOT NULL,
	"value"	TEXT, description TEXT,
	PRIMARY KEY("property")
);
CREATE TRIGGER t_allfiles_changed_create_date AFTER INSERT ON allfiles_changed
 BEGIN
  update allfiles_changed SET create_date = datetime('now', 'localtime') where id = new.id;
 END;
CREATE TRIGGER t_allfiles_scan_create_date AFTER INSERT ON allfiles_scan
 BEGIN
  update allfiles_scan SET create_date = datetime('now', 'localtime') where id = new.id;
 END;
CREATE VIEW allfiles_duplicates_stats as
SELECT
filehash,
count(*) as anzahl
FROM
allfiles
group by
filehash
having 
count(*)>1
order by 2 desc
/* allfiles_duplicates_stats(filehash,anzahl) */
/* allfiles_duplicates_stats(filehash,anzahl) */;
CREATE VIEW allfiles_bytes_hashed as
SELECT
ifnull(sum(filesize), 0) as bytes
FROM
allfiles
WHERE
filehash is not NULL
/* allfiles_bytes_hashed(bytes) */
/* allfiles_bytes_hashed(bytes) */;
CREATE VIEW allfiles_bytes_not_hashed as
SELECT
--round((sum(filesize)/1024/1024.0/1024), 3) as GB
ifnull(sum(filesize), 0) as bytes
FROM
allfiles
WHERE
filehash is NULL
/* allfiles_bytes_not_hashed(bytes) */
/* allfiles_bytes_not_hashed(bytes) */;
CREATE VIEW allfiles_sum_bytes as
SELECT
ifnull(sum(filesize), 0) as bytes
FROM
allfiles
/* allfiles_sum_bytes(bytes) */
/* allfiles_sum_bytes(bytes) */;
CREATE VIEW allfiles_duplicates_without_original as
SELECT
--DISTINCT
--a.id,
--a.filehash
a.*
FROM
allfiles a,
(
SELECT
filehash,
count(*) as anzahl
FROM
allfiles
group by
filehash
having 
count(*)>1
) as duplicates
WHERE
a.filehash = duplicates.filehash
AND
a.id not in 
(
SELECT
a.id as id
FROM
allfiles a,
(
SELECT
filehash,
min(ctime) as min_ctime,
count(*) as anzahl
FROM
allfiles
group by
filehash
having 
count(*)>1
) origs
WHERE
a.filehash = origs.filehash
AND
a.ctime = origs.min_ctime
)
order by 
filename, path
/* allfiles_duplicates_without_original(id,create_date,last_update_date,path,filename,filesize,ctime_formatted,mtime_formatted,hash_date,is_existing,filehash,ctime,mtime) */
/* allfiles_duplicates_without_original(id,create_date,last_update_date,path,filename,filesize,ctime_formatted,mtime_formatted,hash_date,is_existing,filehash,ctime,mtime,mimetype) */;
CREATE TRIGGER t_allfiles_create_date AFTER INSERT ON allfiles
 BEGIN
  update allfiles set create_date = datetime('now', 'localtime') where id = new.id;
 END;
CREATE TRIGGER t_allfiles_last_update_date AFTER UPDATE ON allfiles
 BEGIN
  update allfiles SET last_update_date = datetime('now', 'localtime') where id = new.id;
 END;
CREATE VIEW allfiles_mime_stats as
select
mimetype,
count(*)
from 
allfiles
group by
mimetype
order by
2 desc
/* allfiles_mime_stats(mimetype,"count(*)") */;
CREATE VIEW allfiles_duplicate_bytes as
SELECT
ifnull(sum(filesize),0) as bytes
FROM
allfiles_duplicates_without_original
/* allfiles_duplicate_bytes(bytes) */;
CREATE VIEW database_stats AS 
select
    Property,
    Value,
	Description
from
(
select
    10 as Id,
   'Workpath' as Property,
    value as Value,
	'Working directory in which the file scanner will search.' as Description
from
    configuration
where
    property ='workpath'
UNION
select
    20 as Id,
   'Filecount' as Property,
    count(*) as Value,
	'Total number of files in workpath.' as Description
from
    allfiles
UNION
select
    25 as Id,
   'Filecount 0 byte files' as Property,
    count(*) as Value,
	'Total number of files with zero byte size.' as Description
from
    allfiles where filesize = 0
UNION
select
    30 as Id,
   'Filesize' as Property,
    round(bytes/1024.0/1024/1024, 3) ||' GB' as Value,
	'Total size of all files in workpath.' as Description
from
    allfiles_sum_bytes
UNION
select
    40 as Id,
   'Files hashed / not hashed' as Property,
    h.hashed ||' / ' || n.not_hashed as Value,
	'Total number of files which have been hashed / not hashed (yet).' as Description
from
    (select count(*) as hashed from allfiles where filehash is not null) h,
    (select count(*) as not_hashed from allfiles where filehash is null and filesize > 0) n
UNION
select
    50 as Id,
   'Filesize hashed / not hashed' as Property,
    round(h.bytes/1024.0/1024/1024, 3) ||' GB / ' || round(nh.bytes/1024.0/1024/1024, 3) ||' GB' as Value,
	'Total size in bytes of files that have been hashed / not hashed (yet).' as Description
from
    allfiles_bytes_hashed h,
    allfiles_bytes_not_hashed nh
UNION
select
    55 as Id,
   'Percent bytes hashed' as Property,
    round( h.bytes/1024.0/1024/1024*100/(a.bytes/1024.0/1024/1024) , 2) ||' %' as Value,
	'Percentage of bytes that have been hashed.' as Description
from
    allfiles_bytes_hashed h,
    allfiles_sum_bytes a      
UNION
select
    60 as Id,
   'Duplicate files' as Property,
    count(*) as Value,
	'Total number of files that can be deleted from the workpath because they are duplicates.' as Description
from
    allfiles_duplicates_without_original
UNION
select
    70 as Id,
   'Duplicates filesize' as Property,
    round(bytes/1024.0/1024/1024, 3) ||' GB' as Value,
	'Total size in bytes of the duplicate files which can be safely deleted.' as Description
from
    allfiles_duplicate_bytes
UNION
select
    80 as Id,
   'Percent duplicate bytes' as Property,
    round( (d.bytes/1024.0/1024/1024)*100/(a.bytes/1024.0/1024/1024) , 2) ||' %' as Value,
	'Percentage of space from the workpath space usage that is used by duplicates.' as Description
from
    allfiles_duplicate_bytes d,
    allfiles_sum_bytes a
UNION
select
    90 as Id,
   'Different mime types' as Property,
     a.mimetype_count as Value,
	'Number of distinct mime types that have been found inside the workpath.' as Description
from
(
SELECT
count(
DISTINCT
mimetype) as mimetype_count
FROM
allfiles
) a
)
order by Id
/* database_stats(Property,Value,Description) */;
"""
SQL_CREATE_DEFAULT_CONFIGURATION = """\
INSERT INTO "main"."configuration" ("property", "value", "description") VALUES ('FILESCAN_COMMIT_BATCH_SIZE', '15000', 'The commit size for the file scanning process. Default is 50000.');
INSERT INTO "main"."configuration" ("property", "value", "description") VALUES ('WORKPATH', '/path_to/Pictures', 'The path where the filescanner will work.');
INSERT INTO "main"."configuration" ("property", "value", "description") VALUES ('FILEHASH_COMMIT_BATCH_SIZE', '100', 'The commit size for the process that calculates filehashes and mime types. Default is 50.');
INSERT INTO "main"."configuration" ("property", "value", "description") VALUES ('FILEHASH_BLOCK_SIZE', '1073741824', 'The block size that the hash calculator process will use. Default is 1073741824.');
INSERT INTO "main"."configuration" ("property", "value", "description") VALUES ('DUPLICATES_ARCHIVE_PATH', '/path_to/duplicates', 'The path where the duplicates will be stored. This path can be inside the WORKPATH');
INSERT INTO "main"."configuration" ("property","value","description") VALUES ('LOG_LEVEL','INFO','Loglevel of the application: CRITICAL, ERROR, WARN, INFO, DEBUG');
"""
SQL_SHOW_DUPLICATES = """\
select 
	'Filename' as filename,
	'MB' as MB,
	'Created' as created,
	'Modified' as modified,
	'Path' as path
UNION  
select 
	d.filename as filename,
	round(d.filesize / 1024.0 / 1024, 2) as MB,
	d.ctime_formatted as created,
	d.mtime_formatted as modified,
	d.path
from 
	allfiles_duplicates_without_original d
UNION
select
	'SUM MB' as filename,
	round(sum(z.filesize) / 1024.0 / 1024, 2) as MB,
	'' as created,
	'' as modified,
	'' as path
FROM
	allfiles_duplicates_without_original z
"""