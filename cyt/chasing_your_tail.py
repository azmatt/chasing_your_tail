### Chasing Your Tail V04_15_22
### @matt0177
### Released under the MIT License https://opensource.org/licenses/MIT
###

import sqlite3
import time
from datetime import datetime, timedelta
import glob
import os
import json
import pathlib


### Check for/make subdirectories for logs, ignore lists etc.
cyt_sub = pathlib.Path('/home/pi/Desktop/cyt/cyt_sub')
cyt_sub.mkdir(parents=True, exist_ok=True)

print ('Current Time: ' + time.strftime('%Y-%m-%d %H:%M:%S'))

### Create Log file

log_file_name = '/home/pi/Desktop/cyt/cyt_sub/cyt_log_' + time.strftime('%m%d%y_%H%M%S')

cyt_log = open(log_file_name,"w", buffering=1) 


#######Import ignore list and alert if not found

non_alert_ssid_list = []
try:
	from ignore_list_ssid import *
	#print (ignore_list)
except:
	pass
	
if non_alert_ssid_list:
	pass
else:
    print ("No Probed SSID Ignore List Found!")
    cyt_log.write("No Probed SSID Ignore List Found! \n")
    
probe_ignore_list = non_alert_ssid_list

ignore_list = []

try:
	from ignore_list import *
	#print (ignore_list)
except:
	pass
	
if ignore_list:
	pass
else:
    print ("No Ignore List Found!")
    cyt_log.write("No Ignore List Found! \n")
    
    
print ('{} MACs added to ignore list.'.format(len(ignore_list)))
print ('{} Probed SSIDs added to ignore list.'.format(len(probe_ignore_list)))
cyt_log.write ('{} MACs added to ignore list. \n'.format(len(ignore_list)))
cyt_log.write ('{} Probed SSIDs added to ignore list. \n'.format(len(probe_ignore_list)))

### Set Initial Variables
db_path = '/home/pi/kismet_logs/*.kismet'

###Initialize Lists
current_macs = []
five_ten_min_ago_macs = []
ten_fifteen_min_ago_macs = []
fifteen_twenty_min_ago_macs = []
current_ssids = []
five_ten_min_ago_ssids = []
ten_fifteen_min_ago_ssids = []
fifteen_twenty_min_ago_ssids = []

past_five_mins_macs = []
past_five_mins_ssids = []

### Calculate Time Variables
two_mins_ago = datetime.now() + timedelta(minutes=-2)  
unixtime_2_ago = time.mktime(two_mins_ago.timetuple())  ### Two Minute time used for current results
five_mins_ago = datetime.now() + timedelta(minutes=-5)
unixtime_5_ago = time.mktime(five_mins_ago.timetuple())
ten_mins_ago = datetime.now() + timedelta(minutes=-10)
unixtime_10_ago = time.mktime(ten_mins_ago.timetuple())
fifteen_mins_ago = datetime.now() + timedelta(minutes=-15)
unixtime_15_ago = time.mktime(fifteen_mins_ago.timetuple())
twenty_mins_ago = datetime.now() + timedelta(minutes=-20)
unixtime_20_ago = time.mktime(twenty_mins_ago.timetuple())

######Find Newest DB file
list_of_files = glob.glob(db_path)
latest_file = max(list_of_files, key=os.path.getctime)
print ("Pulling data from: {}".format(latest_file))
cyt_log.write ("Pulling data from: {} \n".format(latest_file))
con = sqlite3.connect(latest_file) ## kismet DB to point at

######Initialize macs past five minutes

def sql_fetch_past_5(con): 
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac FROM devices WHERE last_time >= {}".format(unixtime_5_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        #print(row)
        stripped_val = str(row).replace("(","").replace(")","").replace("'","").replace(",","")
        
        if stripped_val in ignore_list:
            pass
        else:
            #print ("new one!")
            past_five_mins_macs.append(stripped_val)

sql_fetch_past_5(con)

print ("{} MACS added to the within the past 5 mins list".format(len(past_five_mins_macs)))
cyt_log.write ("{} MACS added to the within the past 5 mins list \n".format(len(past_five_mins_macs)))
######Initialize macs five to ten minutes ago

def sql_fetch_5_to_10(con): 
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac FROM devices WHERE last_time <= {} AND last_time >= {} ".format(unixtime_5_ago, unixtime_10_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        #print(row)
        stripped_val = str(row).replace("(","").replace(")","").replace("'","").replace(",","")
        
        if stripped_val in ignore_list:
            pass
        else:
            #print ("new one!")
            five_ten_min_ago_macs.append(stripped_val)

sql_fetch_5_to_10(con)

print ("{} MACS added to the 5 to 10 mins ago list".format(len(five_ten_min_ago_macs)))
cyt_log.write ("{} MACS added to the 5 to 10 mins ago list \n".format(len(five_ten_min_ago_macs)))

######Initialize macs ten to fifteen minutes ago

def sql_fetch_10_to_15(con):
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac FROM devices WHERE last_time <= {} AND last_time >= {} ".format(unixtime_10_ago, unixtime_15_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        #print(row)
        stripped_val = str(row).replace("(","").replace(")","").replace("'","").replace(",","")
		        
        if stripped_val in ignore_list:
            pass
        else:
            #print ("new one!")
            ten_fifteen_min_ago_macs.append(stripped_val)
        

sql_fetch_10_to_15(con)

print ("{} MACS added to the 10 to 15 mins ago list".format(len(ten_fifteen_min_ago_macs)))
cyt_log.write ("{} MACS added to the 10 to 15 mins ago list \n".format(len(ten_fifteen_min_ago_macs)))

######Initialize macs fifteen to twenty minutes ago

def sql_fetch_15_to_20(con):
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac FROM devices WHERE last_time <= {} AND last_time >= {} ".format(unixtime_15_ago, unixtime_20_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        #print(row)
        stripped_val = str(row).replace("(","").replace(")","").replace("'","").replace(",","")
		
        if stripped_val in ignore_list:
            pass
        else:
            #print ("new one!")
            fifteen_twenty_min_ago_macs.append(stripped_val)
        

sql_fetch_15_to_20(con)

print ("{} MACS added to the 15 to 20 mins ago list".format(len(fifteen_twenty_min_ago_macs)))
cyt_log.write("{} MACS added to the 15 to 20 mins ago list \n".format(len(fifteen_twenty_min_ago_macs)))

######Initialize probe requests past 5 minutes

def probe_request_sql_fetch_past_5(con): 
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac, type, device FROM devices WHERE last_time >= {}".format(unixtime_5_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        raw_device_json = json.loads(str(row[2], errors='ignore'))
        if 'dot11.probedssid.ssid' in str(row):
            ssid_probed_for = raw_device_json["dot11.device"]["dot11.device.last_probed_ssid_record"]["dot11.probedssid.ssid"] ### Grabbed SSID Probed for
            #print ('in 5 mins list with {}'.format(ssid_probed_for))
            #print (row)
            if ssid_probed_for == '':
                pass
            elif ssid_probed_for in probe_ignore_list:
                pass
            else:
                past_five_mins_ssids.append(ssid_probed_for)

probe_request_sql_fetch_past_5(con)

print ("{} Probed SSIDs added to the within the past 5 minutes list".format(len(past_five_mins_ssids)))
cyt_log.write ("{} Probed SSIDs added to the within the past 5 minutes list \n".format(len(past_five_mins_ssids)))

######Initialize probe requests five to ten minutes ago

def probe_request_sql_fetch_5_to_10(con): 
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac, type, device FROM devices WHERE last_time <= {} AND last_time >= {} ".format(unixtime_5_ago, unixtime_10_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        raw_device_json = json.loads(str(row[2], errors='ignore'))
        if 'dot11.probedssid.ssid' in str(row):
            ssid_probed_for = raw_device_json["dot11.device"]["dot11.device.last_probed_ssid_record"]["dot11.probedssid.ssid"] ### Grabbed SSID Probed for
            #print ('in 5 mins list with {}'.format(ssid_probed_for))
            #print (row)
            if ssid_probed_for == '':
                pass
            elif ssid_probed_for in probe_ignore_list:
                pass
            else:
                five_ten_min_ago_ssids.append(ssid_probed_for)

probe_request_sql_fetch_5_to_10(con)

print ("{} Probed SSIDs added to the 5 to 10 mins ago list".format(len(five_ten_min_ago_ssids)))
cyt_log.write("{} Probed SSIDs added to the 5 to 10 mins ago list \n".format(len(five_ten_min_ago_ssids)))

######Initialize probe requests ten to fifteen minutes ago

def probe_request_sql_fetch_10_to_15(con): 
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac, type, device FROM devices WHERE last_time <= {} AND last_time >= {} ".format(unixtime_10_ago, unixtime_15_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        raw_device_json = json.loads(str(row[2], errors='ignore'))
        if 'dot11.probedssid.ssid' in str(row):
            ssid_probed_for = raw_device_json["dot11.device"]["dot11.device.last_probed_ssid_record"]["dot11.probedssid.ssid"] ### Grabbed SSID Probed for
            #print ('in 10 mins list with {}'.format(ssid_probed_for))
            if ssid_probed_for == '':
                pass
            elif ssid_probed_for in probe_ignore_list:
                pass
            else:
                ten_fifteen_min_ago_ssids.append(ssid_probed_for)

probe_request_sql_fetch_10_to_15(con)

print ("{} Probed SSIDs added to the 10 to 15 mins ago list".format(len(ten_fifteen_min_ago_ssids)))
cyt_log.write ("{} Probed SSIDs added to the 10 to 15 mins ago list \n".format(len(ten_fifteen_min_ago_ssids)))

######Initialize probe requests fifteem to twenty minutes ago

def probe_request_sql_fetch_15_to_20(con): 
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac, type, device FROM devices WHERE last_time <= {} AND last_time >= {} ".format(unixtime_15_ago, unixtime_20_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        raw_device_json = json.loads(str(row[2], errors='ignore'))
        if 'dot11.probedssid.ssid' in str(row):
            ssid_probed_for = raw_device_json["dot11.device"]["dot11.device.last_probed_ssid_record"]["dot11.probedssid.ssid"] ### Grabbed SSID Probed for
            #print ('in 15 mins list with {}'.format(ssid_probed_for))
            if ssid_probed_for == '':
                pass
            elif ssid_probed_for in probe_ignore_list:
                pass
            else:
                fifteen_twenty_min_ago_ssids.append(ssid_probed_for)

probe_request_sql_fetch_15_to_20(con)

print ("{} Probed SSIDs added to the 15 to 20 mins ago list".format(len(fifteen_twenty_min_ago_ssids)))
cyt_log.write("{} Probed SSIDs added to the 15 to 20 mins ago list \n".format(len(fifteen_twenty_min_ago_ssids)))

#### Define main logic

def sql_fetch_current(con):
    two_mins_ago = datetime.now() + timedelta(minutes=-2)  
    unixtime_2_ago = time.mktime(two_mins_ago.timetuple())
    cursorObj = con.cursor()
    cursorObj.execute("SELECT devmac, type, device FROM devices WHERE last_time >= {}".format(unixtime_2_ago)) 
    rows = cursorObj.fetchall()
    for row in rows:
        raw_device_json = json.loads(str(row[2], errors='ignore'))
        if 'dot11.probedssid.ssid' in str(row):
            ssid_probed_for = raw_device_json["dot11.device"]["dot11.device.last_probed_ssid_record"]["dot11.probedssid.ssid"] ### Grabbed SSID Probed for
            if ssid_probed_for == '':
                pass
            else:
                #print ('Found a probe!: {}'.format(ssid_probed_for))
                cyt_log.write ('Found a probe!: {} \n'.format(ssid_probed_for))
                #### New
                if ssid_probed_for in five_ten_min_ago_ssids:
                    print ("Probe for {} in 5 to 10 mins list".format(ssid_probed_for))
                    cyt_log.write ("Probe for {} in 5 to 10 mins list \n".format(ssid_probed_for))
                else:
                    pass
                if ssid_probed_for in ten_fifteen_min_ago_ssids:
                    print ("Probe for {}  10 to 15 mins list".format(ssid_probed_for))
                    cyt_log.write ("Probe for {}  10 to 15 mins list \n".format(ssid_probed_for))
                else:
                    pass
                if ssid_probed_for in fifteen_twenty_min_ago_ssids:
                    print ("Probe for {} in 15 to 20 mins list".format(ssid_probed_for))
                    cyt_log.write ("Probe for {} in 15 to 20 mins list \n".format(ssid_probed_for))
                else:
                    pass
                ##### End New
        else:
            pass
        stripped_val = str(row).replace("(","").replace(")","").replace("'","").replace(",","").split(" ")[0]
        #print (stripped_val)
        if stripped_val in ignore_list:
            pass
        else:
            if stripped_val in five_ten_min_ago_macs:
                print("{} {} in 5 to 10 mins list".format(row[0], row[1]))
                cyt_log.write("{} {} in 5 to 10 mins list \n".format(row[0], row[1]))
            else:
                pass
            if stripped_val in ten_fifteen_min_ago_macs:
                print("{} {} in 10 to 15 mins list".format(row[0], row[1]))
                cyt_log.write("{} {} in 10 to 15 mins list \n".format(row[0], row[1]))
            else:
                pass
            if stripped_val in fifteen_twenty_min_ago_macs:
                print("{} {} in 15 to 20 mins list".format(row[0], row[1]))
                cyt_log.write("{} {} in 15 to 20 mins list \n".format(row[0], row[1]))
            else:
                pass
## End sql_fetch_current



#### Begin Time Loop

time_count = 0

while True:
    time_count = time_count + 1
    sql_fetch_current(con)
    if time_count % 5 == 0:
        ##Update Lists
        fifteen_twenty_min_ago_macs = ten_fifteen_min_ago_macs
        ten_fifteen_min_ago_macs = five_ten_min_ago_macs
        print ("{} MACs moved to the 15-20 Min list".format(len(fifteen_twenty_min_ago_macs)))
        print ("{} MACs moved to the 10-15 Min list".format(len(ten_fifteen_min_ago_macs)))
        cyt_log.write ("{} MACs moved to the 15-20 Min list \n".format(len(fifteen_twenty_min_ago_macs)))
        cyt_log.write ("{} MACs moved to the 10-15 Min list \n".format(len(ten_fifteen_min_ago_macs)))
        
        fifteen_twenty_min_ago_ssids = ten_fifteen_min_ago_ssids
        ten_fifteen_min_ago_ssids = five_ten_min_ago_ssids
        print ("{} Probed SSIDs moved to the 15 to 20 mins ago list".format(len(fifteen_twenty_min_ago_ssids)))
        print ("{} Probed SSIDs moved to the 10 to 15 mins ago list".format(len(ten_fifteen_min_ago_ssids)))
        cyt_log.write ("{} Probed SSIDs moved to the 15 to 20 mins ago list \n".format(len(fifteen_twenty_min_ago_ssids)))
        cyt_log.write ("{} Probed SSIDs moved to the 10 to 15 mins ago list \n".format(len(ten_fifteen_min_ago_ssids)))
        
        ###Update time variables
        five_mins_ago = datetime.now() + timedelta(minutes=-5)
        unixtime_5_ago = time.mktime(five_mins_ago.timetuple())
        ten_mins_ago = datetime.now() + timedelta(minutes=-10)
        unixtime_10_ago = time.mktime(ten_mins_ago.timetuple())
        
        ###Clear recent lists
        five_ten_min_ago_macs = []
        five_ten_min_ago_ssids = []
        
        ### Move the past 5 check from 5 mins ago into the past 5-10 list
        #sql_fetch_5_to_10(con)
        five_ten_min_ago_macs = past_five_mins_macs
        print ("{} MACs moved to the 5 to 10 mins ago list".format(len(five_ten_min_ago_macs)))
        cyt_log.write ("{} MACs moved to the 5 to 10 mins ago list \n".format(len(five_ten_min_ago_macs)))
        five_ten_min_ago_ssids = past_five_mins_ssids
        print ("{} Probed SSIDs moved to the 5 to 10 mins ago list".format(len(five_ten_min_ago_ssids)))
        cyt_log.write ("{} Probed SSIDs moved to the 5 to 10 mins ago list \n".format(len(five_ten_min_ago_ssids)))
        
        ### Update past 5 min check to have them ready for 5 mins from now
        past_five_mins_macs = []
        past_five_mins_ssids = []
        
        sql_fetch_past_5(con)
        probe_request_sql_fetch_past_5(con)
        #print ("{} MACs seen within the past 5 minutes".format(len(past_five_mins_macs)))
        #past_five_mins_ssids
        
    time.sleep(60)
