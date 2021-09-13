import os
import argparse
import sqlite3
from sqlite3.dbapi2 import Cursor
import csv

def activitycacheparser(input_db, output_folder):
    file_in = str(input_db)

    db = sqlite3.connect(file_in)
    cursor = db.cursor()

    print('[+] Extracting data from Activity Table')

    cursor.execute('''
        SELECT
	        datetime(Activity.LastModifiedTime,'unixepoch') AS 'Last Modified Time',
	        datetime(Activity.ExpirationTime, 'unixepoch') AS 'Expiration Time',
	        datetime(Activity.LastModifiedOnClient, 'unixepoch') AS 'Last Modification Time on Client',
	        datetime(Activity.StartTime, 'unixepoch') AS 'Start Time',
	        CASE
	        	WHEN Activity.CreatedInCloud == 0
	        	THEN ''
	        	ELSE datetime(Activity.CreatedInCloud, 'unixepoch')
	        END AS 'Created In Cloud',

	        Activity.ETag AS 'ETag',

	        CASE
	        	WHEN ActivityType in (2, 11, 12, 15, 16) THEN json_extract(Activity.AppId, '$[0].application') 
	        	WHEN ActivityType == 5 THEN json_extract(Activity.AppId, '$[1].application')
	        END AS 'Application',

	        CASE
	        	WHEN
	        		Activity.ActivityType == 5
	        	THEN
	        		json_extract(Activity.Payload, '$.appDisplayName')
	        END AS 'Display Name',

	        CASE
	        	WHEN
	        		Activity.ActivityType == 5
	        	THEN
	        		json_extract(Activity.Payload, '$.displayText')
	        END AS 'Display Text',

	        CASE
	        	WHEN ActivityType == 5 THEN 'User Opened app/file/page (5)'
	        	WHEN ActivityType == 6 THEN 'App in use/focus (6)'
	        	WHEN ActivityType in (11, 12, 15) THEN 'System ('||ActivityType||')'
	        	WHEN ActivityType == 16 THEN 'Copy/Paste (16)'
	        	ELSE ActivityType
	        END AS "Activity Type",

	        CASE
	        	WHEN ActivityStatus == 1 THEN 'Active'
	        	WHEN ActivityStatus == 2 THEN 'Updated'
	        	WHEN ActivityStatus == 3 THEN 'Deleted'
	        	WHEN ActivityStatus == 4 THEN 'Ignored'
	        END AS 'Activity Status',

	        Activity.Priority,
	        
            CASE
	        	WHEN Activity.IsLocalOnly == 0
	        	THEN 'No'
	        	ELSE 'Yes'
	        END AS 'Is Local Only',
	        
            CASE
	        	WHEN Activity.Tag NOT NULL
	        	THEN Activity.Tag
	        	ELSE ''
	        END AS 'Tag',
	        
            CASE
	        	WHEN Activity."Group" NOT NULL
	        	THEN Activity."Group"
	        	ELSE ''
	        END AS 'Group',
	        
            CASE
	        	WHEN Activity.MatchId NOT NULL
	        	THEN Activity.MatchId
	        	ELSE ''
	        END AS 'Match ID',
	        
            CASE
	        	WHEN json_extract(Activity.AppId,'$[0].platform') == 'afs_crossplatform'
	        	THEN json_extract(Activity.AppId,'$[1].platform')
	        	ELSE json_extract(Activity.AppId,'$[0].platform')
	        END AS 'Platform',
	        
            Activity.AppActivityId,
	        
            CASE
	        	WHEN hex(Activity.ParentActivityId) == '00000000000000000000000000000000'
	        	THEN ''
	        	ELSE hex(Activity.ParentActivityId)
	        END AS 'Parent Activity Id',

	        Activity.PlatformDeviceId AS 'Platform Device Id',

	        Activity.DdsDeviceId AS 'Dds Device Id',

	        CASE
	        	WHEN Activity.ActivityType == 16 THEN json_extract(Activity.Payload, '$.clipboardDataId')
	        	ELSE ''
	        END AS 'Clipboard Data ID',

	        CASE
	        	WHEN Activity.ActivityType == 10 THEN json_extract(Activity.ClipboardPayload, '$[0].content')
	        	ELSE ''
	        END AS 'Clipboard Data',

	        CASE
	        	WHEN Activity.ActivityType == 16 THEN json_extract(Activity.Payload, '$.gdprType')
	        	ELSE ''
	        END AS 'GDPR Type',

	        Activity.PackageIdHash,

	        Activity.Payload AS 'Original Payload'
	    FROM
	        Activity;
    ''')

    all_rows = cursor.fetchall()
    if(len(all_rows) > 0):
        generateReport(all_rows, output_folder, 'ActivityCache_Activity.csv')

    db.close()

def generateReport(results, output_folder, output_filename):
    print('[+] Starting Report generation')
    out = open(output_filename, 'w')
    csv_out = csv.writer(out, lineterminator='\n')
    csv_out.writerow(['Last Modification Time', 'Expiration Time', 'Last Modification Time on Client', 'Start Time', 'Time Created in Cloud', 'ETag', 'Application', 'Display Name', 'Display Text', 'Activity Type', 'Activity Status', 'Priority', 'Is Local Only', 'Tag', 'Group', 'Match ID', 'Platform', 'App Activity ID', 'Parent Activity ID', 'Platform Device ID', 'Dds Device ID', 'Clipboard Data ID', 'Clipboard Data', 'GDPR Type', 'Package ID Hash', 'Original Payload'])
    for row in results:
        csv_out.writerow(row)
    
    print('[+] Report Successfully generated and saved to ', output_filename)


def argparser():
    '''
    Argument Parser
    '''
    parser = argparse.ArgumentParser(description='Windows Activity Timeline cache Parser')
    parser.add_argument('-f', '--file', required=True, action="store", help='Path to input file/folder')
    parser.add_argument('-o','--output_file', required=False, action="store", help='Path to output file/folder')

    args = parser.parse_args()

    print('\nWindows Activity Timeline Parser by @_Nihith\n')

    if os.path.exists(args.file):
        activitycacheparser(args.file, args.output_file)
    else:
        print(parser.print_help())

argparser()