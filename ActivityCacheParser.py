import os
import argparse
import sqlite3
import csv

# Known GUIDs - https://docs.microsoft.com/en-us/dotnet/desktop/winforms/controls/known-folder-guids-for-file-dialog-custom-places
# ProgramFilesX64 6D809377-6AF0-444B-8957-A3773F02200E
# ProgramFilesX86 7C5A40EF-A0FB-4BFC-874A-C0F2E0B9FA8E
# System 1AC14E77-02E7-4E5D-B744-2EB1AE5198B7
# SystemX86 D65231B0-B2F1-4857-A4CE-A8E7C6EA7D27
# Windows F38BF404-1D43-42F2-9305-67DE0B28FC23

def get_activity(cursor):
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
                WHEN json_extract(Activity.AppId, '$[0].platform') == 'afs_crossplatform' THEN json_extract(Activity.AppId, '$[1].application') ELSE json_extract(Activity.AppId, '$[0].application')
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
            CASE 
		        WHEN Activity.ActivityType==5 THEN json_extract(Activity.Payload, '$.description') 
		        ELSE '' 
	        END AS 'Description',
        	CASE
    		    WHEN Activity.ActivityType==5 THEN json_extract(Activity.Payload, '$.contentUri') 
    		    ELSE '' 
	        END AS 'Content Uri',
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
            Activity
        ORDER BY 
            Activity.ETag;
    ''')

    all_rows = cursor.fetchall()
    return all_rows

def get_activityOperation(cursor):
    print('[+] Extracting data from ActivityOperation Table')

    cursor.execute('''
        SELECT
	        datetime(ActivityOperation.CreatedTime, 'unixepoch') AS 'Created Time',
	        datetime(ActivityOperation.LastModifiedTime,'unixepoch') AS 'Last Modified Time',
	        datetime(ActivityOperation.LastModifiedOnClient, 'unixepoch') AS 'Last Modification Time on Client',
	        datetime(ActivityOperation.ExpirationTime, 'unixepoch') AS 'Expiration Time',
	        datetime(ActivityOperation.OperationExpirationTime, 'unixepoch') AS 'Operation Expiration Time',
	        datetime(ActivityOperation.StartTime, 'unixepoch') AS 'Start Time',
	        CASE
	        	WHEN ActivityOperation.EndTime == 0
	        	THEN ''
	        	ELSE datetime(ActivityOperation.EndTime, 'unixepoch')
	        END AS 'End Time',
	        CASE
	        	WHEN ActivityOperation.CreatedInCloud == 0 THEN ''
	        	ELSE datetime(ActivityOperation.CreatedInCloud, 'unixepoch')
	        END AS 'Created In Cloud',
	        ActivityOperation.ETag AS 'ETag',
	        CASE
	        	WHEN ActivityType in (2, 11, 12, 15, 16) THEN json_extract(ActivityOperation.AppId, '$[0].application')
	        	WHEN json_extract(ActivityOperation.AppId, '$[0].platform') == 'afs_crossplatform' THEN json_extract(ActivityOperation.AppId, '$[1].application') ELSE json_extract(ActivityOperation.AppId, '$[0].application')
	        END AS 'Application',
	        CASE
	        	WHEN ActivityType == 5
	        	THEN json_extract(ActivityOperation.Payload, '$.displayText')
	        END AS 'Display Text',
	        CASE
	        	WHEN ActivityType == 5 
	        	THEN json_extract(ActivityOperation.Payload, '$.appDisplayName')
	        END AS 'App Display Name',
	        CASE
	        	WHEN ActivityType == 5 THEN 'User Opened app/file/page (5)'
                WHEN ActivityType == 6 THEN 'App in use/focus (6)'
                WHEN ActivityType in (11, 12, 15) THEN 'System ('||ActivityType||')'
                WHEN ActivityType == 16 THEN 'Copy/Paste (16)'
                ELSE ActivityType
	        END AS "Activity Type",
	        CASE
	        	WHEN ActivityOperation.ActivityType == 6
	        	THEN time(json_extract(ActivityOperation.Payload,'$.activeDurationSeconds'),'unixepoch')
	        	ELSE ''
	        END AS 'Active Duration',
	        CASE
	        	WHEN ActivityOperation.ActivityType == 6 and ((ActivityOperation.EndTime - ActivityOperation.StartTime) > 0)
	        	THEN time((ActivityOperation.EndTime - ActivityOperation.StartTime), 'unixepoch')
	        	ELSE ''
	        END AS 'Calculated Active Duration',
	        ActivityOperation.Priority,
	        CASE
	        	WHEN ActivityOperation.OperationType == 1 THEN 'Active'
	        	WHEN ActivityOperation.OperationType == 2 THEN 'Updated'
	        	WHEN ActivityOperation.OperationType == 3 THEN 'Deleted'
	        	WHEN ActivityOperation.OperationType == 4 THEN 'Ignored'
	        END AS 'Operation Type',
	        CASE
	        	WHEN ActivityOperation.ActivityType == 6
	        	THEN json_extract(ActivityOperation.Payload,'$.userTimezone')
	        	ELSE ''
	        END AS 'User Engaged Timezone',
	        CASE 
	        	WHEN ActivityOperation.ActivityType==5 THEN json_extract(ActivityOperation.Payload, '$.description') 
	        	ELSE '' 
	        END AS 'Description',
	        CASE
	        	WHEN ActivityOperation.ActivityType==5 THEN json_extract(ActivityOperation.Payload, '$.contentUri') 
	        	ELSE '' 
	        END AS 'Content Uri',
	        hex(ActivityOperation.Id) AS 'ID',
	        ActivityOperation.Tag AS 'Tag',
	        ActivityOperation.MatchId AS 'Match ID',
	        CASE
	        	WHEN ActivityOperation.ActivityType in (2,11,12,15) 
	        	then ''
	        	else coalesce(json_extract(ActivityOperation.Payload, '$.activationUri'),json_extract(ActivityOperation.Payload, '$.reportingApp')) 
	        end as 'App/Uri',
	        ActivityOperation."Group",
	        ActivityOperation.AppActivityId,
	        CASE 
	        	WHEN hex(ActivityOperation.ParentActivityId) == '00000000000000000000000000000000'
	        	THEN ''
	        	ELSE hex(ActivityOperation.ParentActivityId)
            END AS 'Parent Activity Id',
	        ActivityOperation.PlatformDeviceId AS 'Platform Device Id',
	        ActivityOperation.DdsDeviceId AS 'Dds Device Id',
	        ActivityOperation.GroupAppActivityId AS 'Group App Activity Id',
	        ActivityOperation.EnterpriseId AS 'EnterpriseId',
	        ActivityOperation.PackageIdHash AS 'Package Id Hash',
	        ActivityOperation.Payload AS 'Orignal Payload'
	    FROM
	        ActivityOperation
	    ORDER BY ActivityOperation.ETag;
    ''')

    all_rows = cursor.fetchall()
    return all_rows

def get_packageID(cursor):
    print('[+] Extracting data from Activity_PackageID Table')
    cursor.execute('''
        SELECT
	        hex(ActivityId), 
        	Platform, 
	        PackageName, 
        	datetime(ExpirationTime, 'unixepoch') 
	    FROM 
	        Activity_PackageId;
    ''')
    all_rows = cursor.fetchall()
    return all_rows

def activitycacheparser(input_db, output_folder):
    file_in = str(input_db)
    db = sqlite3.connect(input_db)
    cursor = db.cursor()

    activityTable = get_activity(cursor)
    if(len(activityTable) > 0):
        generateReport(activityTable, output_folder, 'ActivityCache_Activity.csv')
    else:
        print('[+] No data found in Activity table')

    operationTable = get_activityOperation(cursor)
    if(len(operationTable) > 0):
        generateReport(operationTable, output_folder, 'ActivityCache_ActivityOperation.csv')
    else:
        print('[+] No data found in Operation table')

    packageID = get_packageID(cursor)
    if(len(packageID) > 0):
        generateReport(packageID, output_folder, 'ActivityCache_ActivityPackageID.csv')
    else:
        print('[+] No data found in Operation table')

def generateReport(results, output_folder, output_filename):
    '''
    Generates CSV Reports
    '''
    print('[+] Starting Report generation')
    out = open(output_filename, 'w', encoding="utf-8")
    csv_out = csv.writer(out, lineterminator='\n')
    if(output_filename == 'ActivityCache_Activity.csv'):
        csv_out.writerow(['Last Modification Time', 'Expiration Time', 'Last Modification Time on Client', 'Start Time', 'Time Created in Cloud', 'ETag', 'Application', 'Display Name', 'Display Text', 'Activity Type', 'Activity Status', 'Priority', 'Is Local Only', 'Tag', 'Group', 'Match ID', 'Platform', 'Description', 'Content Uri', 'App Activity ID', 'Parent Activity ID', 'Platform Device ID', 'Dds Device ID', 'Clipboard Data ID', 'Clipboard Data', 'GDPR Type', 'Package ID Hash', 'Original Payload'])
    elif(output_filename == 'ActivityCache_ActivityOperation.csv'):
        csv_out.writerow(['Created Time', 'Last Modification Time', 'Last Modification Time on Client', 'Expiration Time', 'Operation Expiration Time', 'Start Time', 'End Time', 'Created In Cloud', 'ETag', 'Application', 'Display Text', 'App Display Name', 'Activity Type', 'Active Duration', 'Calculated Active Duration', 'Priority', 'Operation Type', 'User Engaged Type', 'Description', 'Content Uri', 'ID', 'Tag', 'Match ID', 'Activation Uri/Reporting App', 'Group', 'App Activity ID', 'Parent Activity ID', 'Platform Device ID', 'Dds Device ID', 'Group App Activity ID', 'Enterprise ID', 'Package Id Hash', 'Original Payload'])
    elif(output_filename == 'ActivityCache_ActivityPackageID.csv'):
        csv_out.writerow(['Activity ID', 'Platform', 'Package Name', 'Expiration Time'])
    for row in results:
        csv_out.writerow(row)
    if(os.path.exists(output_filename)):
        print(f'[+] Report Successfully generated and saved to {output_filename}\n')
    else:
        print('[+] Report generation Failed')

def argparser():
    '''
    Argument Parser
    '''
    parser = argparse.ArgumentParser(description='Windows Activity Timeline cache Parser')
    parser.add_argument('-f', '--file', required=True, action="store", help='Path to input file/folder')
    parser.add_argument('-o','--output_file', required=False, action="store", help='Path to output file/folder')

    args = parser.parse_args()

    print('\nWindows Activity Timeline Parser\n')

    if os.path.exists(args.file):
        activitycacheparser(args.file, args.output_file)
    else:
        print(parser.print_help())

argparser()