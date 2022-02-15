import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import time

headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
url = "https://reslife.ucla.edu/reserve"
session = requests.Session()



def format_data(room_name, data, date):
    my_str = data.replace("0", "🟥").replace("1", "🟩")
        
    return f"""{room_name}{date}\n00:00 {my_str[0:6]}|{my_str[6:12]}\n06:00 {my_str[12:18]}|{my_str[18:24]}\n12:00 {my_str[24:30]}|{my_str[30:36]}\n18:00 {my_str[36:42]}|{my_str[42:48]}\n"""

def get_data(roomtype, date, duration = "30"):
    r = session.get(url, headers = headers, params={'type':roomtype, 'duration': duration, 'date': date})
    bsObj = BeautifulSoup(r.content, "html.parser")
    
    results = bsObj.find(id = "results")
    if not results:
        print(f"oops, there was a problem getting the results at https://reslife.ucla.edu/reserve?type={roomtype}&duration={duration}&date={date}")
        return
    tags = results.findAll(class_ = "col-md-8 col-sm-8 col-xs-8")
    if not tags:    
        print(f"oops, there was a problem getting the results at https://reslife.ucla.edu/reserve?type={roomtype}&duration={duration}&date={date}")
        return

    rooms = {}
    for tag in tags: #each tag is a single row corresponding to a single timeslot
        #print(tag)
        #print("---------------------------")
        room = tag.find(class_ = "col-md-6").get_text().strip()
        time = tag.find(class_ = "col-md-6").find_next_sibling().get_text().strip()
        #print(room, time)
        if room not in rooms.keys():
            rooms[room] = [time]
        else:
            rooms[room].append(time)
   
    #print(rooms)
    rooms = {k.split('(')[0]:v for k, v in rooms.items()}
    rooms = {k:[clean_time_data(_) for _ in v] for k, v in rooms.items()}
    rooms = {k:condense_time_data(v) for k, v in rooms.items()}

    return rooms

def condense_time_data(time_list):
    #this function takes in a list of datetime objects and returns a string
    #it is assumed that time_list contains datetime objects from the same day,, and that the times are all multiples of 30 minutes from midnight
    #the output of this function will be a string of 1's and 0's, with 48 of them.
    if not time_list:
        return "0" * 48

    beginning_time = datetime(time_list[0].year, time_list[0].month, time_list[0].day)
    time_list = [(t - beginning_time).seconds//1800 for t in time_list]

    l = ["1" if x in time_list else "0" for x in range(48)]

    return "".join(l)

def get_roomtypes():
    r = session.get(url, headers = headers)
    bsObj = BeautifulSoup(r.content, "html.parser")
    string_of_roomtypes = bsObj.find(id = "room-type")["data-durations"]
    string_of_roomtypes = string_of_roomtypes.replace("30 minutes", "30").replace("1 hour", "60").replace("2 hours", "120")
    return json.loads(string_of_roomtypes)


def clean_time_data(td, interval_length = 30, year = 2022): #td stands for timedata, expecting an input string
    #we shall assume the year is always 2022
    #we will use the end-time of the interval, combined with the interval length to calculate the start time of the interval. this is easier than reading the starttime since there is inconsistent formatting with am and pm.
    td = td.replace('midnight', '12:00am')
    
    date = re.findall(r'[A-Z][a-z][a-z] \d\d', td)[0] #E.g. "Jan 04"
    time = re.findall(r'-\d{1,2}:\d\d(?:am|pm)', td)[0].strip("-").upper()  #E.g. "12:00AM" or "9:00PM"
    
    dt = datetime.strptime(f"{year} {date} {time}", "%Y %b %d %I:%M%p")
    dt += timedelta(minutes = -interval_length)
    #print(date, time)
    return dt

def find_available_days(roomtype):
    r = session.get(url, headers = headers, params = {"type":roomtype, "duration": "30"})
    bsObj = BeautifulSoup(r.content, "html.parser")
    calendar = bsObj.find(id = "date")
    dates = []
    
    for tag in calendar.findAll(class_ = "calendar-today calendar-available calendar-label"):
        #print(tag)
        date_str = tag['aria-label'] #E.g. "Tuesday, January 4"
        dates.append(datetime.strptime(f"2022 {date_str}", "%Y %A, %B %d"))
    for tag in calendar.findAll(class_ = "calendar-available calendar-label"):
        date_str = tag['aria-label'] #E.g. "Tuesday, January 4"
        dates.append(datetime.strptime(f"2022 {date_str}", "%Y %A, %B %d"))
    
    return [_.isoformat().split("T")[0] for _ in dates]


roomtypes = list(get_roomtypes().keys()) # roomtypes should be equal to {'meditation', 'rieber', 'sproulmusic', 'music', 'sproulstudy', 'movement', 'hedrick', 'hedrickstudy', 'hitch', 'hedrickmusic'}
assert set(roomtypes) == {'meditation', 'rieber', 'sproulmusic', 'music', 'sproulstudy', 'hedrick', 'hedrickstudy', 'hitch', 'hedrickmusic', 'deneve'}

# for r in roomtypes:
#     print(find_available_days(r))
#     for day in find_available_days(r):

#         print(get_data(r, day))
#         time.sleep(3)

# num_requests = 1

# while True:
#     for r in roomtypes:
#         days = find_available_days(r); num_requests += 1
#         print(days)
#         for day in days:

#             print(get_data(r, day)); num_requests += 1
#             time.sleep(3)

#             print(f"done {num_requests} requests so far")




print('reservation_checker done running')