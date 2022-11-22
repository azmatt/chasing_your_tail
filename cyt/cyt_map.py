### GPS + Map functions to support Chasing Your Tail
### gcv-javier
### Released under the MIT License https://opensource.org/licenses/MIT
###


import time
from datetime import datetime, timedelta
import folium # to create a map with our position and tails positions
from gps import * # to get usb gps antenna data
from selenium import webdriver # to open and refreh the browser
from selenium.webdriver.chrome.options import Options # to use Chronium as browser
import requests # to call a free REST API to get the vendor of the mac addresses
import re # regex

###### To connect to the GPS antenna
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

###### Map variables
HTML_FILE = "cyt_map.html"
HTML_PATH = "/home/pi/Desktop/cyt/resources/"

###### REST API to get the mac vendor of the mac addresses
ENDPOINT = "https://macvendors.co/api/"
macs_map = {} # key-value pairs: mac->vendor

###### Current GPS position
def get_current_position(gps):
    try:
        nx = gpsd.next()
        # For a list of all supported classes and fields refer to:
        # https://gpsd.gitlab.io/gpsd/gpsd_json.html
        while nx is None or nx['class'] != 'TPV' or (latitude:= getattr(nx,'lat', "Unknown")) is None or (longitude := getattr(nx,'lon', "Unknown")) is None or latitude == "Unknown" or longitude == "Unknown":
             nx = gpsd.next()
             #if nx is not None:
             #    print ("Looking for GPS location: nx class: " + nx['class'] + ", lat: " + str(getattr(nx,'lat', "Unknown")) + ", lon: " + str(getattr(nx,'lon', "Unknown")))
             time.sleep(1.0)
        #print ("nx class: " + nx['class'])
        #print ("Your position: lon = " + str(longitude) + ", lat = " + str(latitude))
        center_coordinate = [latitude, longitude]
        #print("center_coordinate: " + str(center_coordinate[0]) + "," + str(center_coordinate[1]))
        return center_coordinate
    except:
        return get_current_position(gpsd) # gpsd.next() might throw and exception when decoding JSON

###### Paint map: open a browser with the cyt_map.html on full screen and refresh it every few seconds
def paint_map():
    #print ("Painting the map....")
    opts = Options()
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_argument("--start-fullscreen")

    driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', chrome_options=opts)

    #print ("HTML file location: " + html_path + html_file )
    driver.get("file:///" + HTML_PATH + HTML_FILE)

    while True:
        #print ("painting subprocess to sleep 5 seconds...")
        time.sleep(5) # TODO extract this 5 seconds to a GUI property
        #print ("painting subprocess awake, let's refresh")
        driver.refresh()
    driver.quit()


###### Get the mac vendor (the Internet is necessary to get the vendor for the mac addresses)
def get_mac_vendor(mac_input):
    try: 
        if macs_map[mac_input]:
            return mac_input + " " + macs_map[mac_input]
    except KeyError as ke:
        #print("macs map: " + str(macs_map))
        #print("mac not found in map: " + mac_input)
        try: 
            mac_prefix = mac_input[0 : 9]
            mac = mac_prefix + "00:00:00"
            #print ("mac parameter: " + mac)
            r = requests.get(ENDPOINT + mac) # only the first three values are necessary
            #print ("Json received: " + str(r.json()))
            #print ("Company: " + str(r.json()['result']['company']))
            # { "result": {"company": "Apple, Inc.", ......}}
            # { "result": {"error": "no result"}}
            if "error" in str(r.json()['result']):
                #print ("Error in json: " + str(r.json()['result']['error']))
                return mac_input # we could avoid this check and the next line would throw an exception
            else:
                macs_map[mac_input] = str(r.json()['result']['company']) # add the mac to the map so we don't need to call the mac vendor API
                return mac_input + " " + str(r.json()['result']['company']) 
        except Exception as e:
            #print ("Error calling " + ENDPOINT + ": " + str(e))
            return mac_input

###### To know if a string is a mac or not (it might be a ssid)
def is_mac(mac):
    #print ("Is a mac: " + mac + ": " + str("true" if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()) else "false"))
    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower())

###### Add marker into map
def add_marker_to_map(macSsidList, popupMessage, markerColor, map):
    #print("macSsidList length: " + str(len(macSsidList)))
    for row in macSsidList:
        #print ("Adding the marker: " + str(row))
        macOrSsid = str(row[0]).replace("(","").replace(")","").replace("'","").replace(",","")
        lat = str(row[1]).replace("(","").replace(")","").replace("'","").replace(",","")
        lon = str(row[2]).replace("(","").replace(")","").replace("'","").replace(",","")
        #print("mac/ssid: " + macOrSsid + ", lat: " + lat + ", lon: " + lon)
        if lat is not None and lat != 'None' and lon is not None and lat != 'None':
            folium.Marker(
                location = [lat, lon],
                popup = popupMessage,
                tooltip = get_mac_vendor(macOrSsid) if is_mac(macOrSsid) else macOrSsid,
                icon = folium.Icon(color=markerColor),
            ).add_to(map)

##### Update the html map constantly, to update our current position in the map
def update_map(matches_in_five_ten_min_ago_macs, matches_in_ten_fifteen_min_ago_macs, matches_in_fifteen_twenty_min_ago_macs, matches_in_five_ten_min_ago_ssids, matches_in_ten_fifteen_min_ago_ssids, matches_in_fifteen_twenty_min_ago_ssids):
#def update_map():
    while True:
        update_html(matches_in_five_ten_min_ago_macs, matches_in_ten_fifteen_min_ago_macs, matches_in_fifteen_twenty_min_ago_macs, matches_in_five_ten_min_ago_ssids, matches_in_ten_fifteen_min_ago_ssids, matches_in_fifteen_twenty_min_ago_ssids)
        #print ("update map subprocess to sleep 5 seconds")
        time.sleep(5) # TODO extract this 5 seconds to a GUI property

	
###### Update map: update the html file with our current position and the tails positions as markers
def update_html(matches_in_five_ten_min_ago_macs, matches_in_ten_fifteen_min_ago_macs, matches_in_fifteen_twenty_min_ago_macs, matches_in_five_ten_min_ago_ssids, matches_in_ten_fifteen_min_ago_ssids, matches_in_fifteen_twenty_min_ago_ssids):
    #print ("Updating the html....")

    center_coordinate = get_current_position(gpsd)
    # until we don't get the last current position the previous known position will be painted (with the date of the last update)

    if center_coordinate is not None and center_coordinate[0] is not None and center_coordinate[1] is not None and str(center_coordinate[0]) != 'Unkown' and str(center_coordinate[1]) != 'Unkown':                
        # map with our position as the center of the map (the Internet is necessary to get the map)
        myMap = folium.Map(
            location=center_coordinate,
            tiles='OpenStreetMap',
            zoom_start=15
            );
        # we paint the current time to know when the map was updated for the last time
        # datetime object containing current date and time
        now = datetime.now()
        htmlDiv = "<div class='text-center' style='z-index: 1000; position: absolute; font-size: 18pt; align-content: center; width: 525px; margin:0 auto; color: yellow; font-weight: bold; text-shadow: 2px 2px black'>" + now.strftime("%d/%m/%Y %H:%M:%S") + "</div>"		
        myMap.get_root().html.add_child(folium.Element(htmlDiv))
        # paint our position
        folium.Marker(
            center_coordinate, popup="<i>Me</i>", tooltip="Me"
        ).add_to(myMap)

        ## add marker for every tail, in different colour depending its list
        # macs lists
        # matches_in_five_ten_min_ago_macs
        add_marker_to_map(matches_in_five_ten_min_ago_macs, "5-10 minutes macs list", "green", myMap) # green #008000
        # matches_in_ten_fifteen_min_ago_macs
        add_marker_to_map(matches_in_ten_fifteen_min_ago_macs, "10-15 minutes macs list", "orange", myMap) # yellow #FFFF00
        # matches_in_fifteen_twenty_min_ago_macs
        add_marker_to_map(matches_in_fifteen_twenty_min_ago_macs, "15-20 minutes macs list", "red", myMap) # red #FF0000
                
        # ssids lists
        # matches_in_five_ten_min_ago_ssids
        add_marker_to_map(matches_in_five_ten_min_ago_ssids, "5-10 minutes ssids list", "green", myMap) # green #008000
        # matches_in_ten_fifteen_min_ago_ssids
        add_marker_to_map(matches_in_ten_fifteen_min_ago_ssids, "10-15 minutes ssids list", "orange", myMap) # yellow #FFFF00
        # matches_in_fifteen_twenty_min_ago_ssids
        add_marker_to_map(matches_in_fifteen_twenty_min_ago_ssids, "15-20 minutes ssids list", "red", myMap) # red #FF0000

        # Save an html with the map and the markers
        myMap.save(HTML_PATH + HTML_FILE)

        #print("At the end of updating the map...")
        




