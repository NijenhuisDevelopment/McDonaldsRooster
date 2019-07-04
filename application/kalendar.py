from __future__ import print_function
from datetime import datetime, timedelta
import re
import json

class Workday:
    def __init__(self, start_time, end_time, station, add_event):
        self.start_time = start_time
        self.end_time = end_time
        self.station = station
        self.add_event = add_event

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def create_event(event, service):
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


def parse_file(text_file):
    with open(text_file, 'r') as infile:
        filedata = infile.readlines()
        out = []

        workday_regex = ".*(?= - )"
        end_day_regex = " -([^,]+)"
        station_regex = ", ..."

        start_date = []
        end_time = []
        station = []

        for l in filedata:
            line = l.rstrip().lstrip()
            reg0 = re.search(workday_regex, line)
            if reg0:
                found0 = reg0.group(0)
                start_date.append(found0)
                out.append(found0)

                reg1 = re.search(end_day_regex, line)
                if reg1:
                    found1 = reg1.group(0)
                    end_time.append(found1.strip(' - '))

                    reg2 = re.search(station_regex, line)
                    if reg2:
                        found2 = reg2.group(0)
                        station.append(found2.strip(', '))

    for i in range(len(end_time)):
        date = start_date[i]
        regex = "\\S*$"
        t = re.sub(regex, "", date)
        end_time[i] = (t + end_time[i])

    translate(start_date)
    translate(end_time)

    for i in range(len(start_date)):
        prepare_events(start_date[i], end_time[i], station[i])


workdays = []


def get_all_events():
    return workdays


def prepare_events(start_date, end_time, station):
    start = datetime.strptime(start_date, "%A %d %B %Y %H:%M")
    end = datetime.strptime(end_time, "%A %d %B %Y %H:%M")

    if end.hour < start.hour:
        end = end + timedelta(days=1)

    s = str(start.date()) + "T" + str(start.time()) + "+02:00"
    e = str(end.date()) + "T" + str(end.time()) + "+02:00"

    w = Workday(s, e, station, True)
    workdays.append(w)
    return workdays


def translate(l):
    for i in range(len(l)):
        l[i] = l[i].replace("maandag", "Monday")
        l[i] = l[i].replace("dinsdag", "Tuesday")
        l[i] = l[i].replace("woensdag", "Wednesday")
        l[i] = l[i].replace("donderdag", "Thursday")
        l[i] = l[i].replace("vrijdag", "Friday")
        l[i] = l[i].replace("zaterdag", "Saturday")
        l[i] = l[i].replace("zondag", "Sunday")

        l[i] = l[i].replace("januari", "January")
        l[i] = l[i].replace("februari", "February")
        l[i] = l[i].replace("maart", "March")
        l[i] = l[i].replace("april", "April")
        l[i] = l[i].replace("mei", "May")
        l[i] = l[i].replace("juni", "June")
        l[i] = l[i].replace("juli", "July")
        l[i] = l[i].replace("augustus", "August")
        l[i] = l[i].replace("september", "September")
        l[i] = l[i].replace("oktober", "October")
        l[i] = l[i].replace("november", "November")
        l[i] = l[i].replace("december", "December")
    return l
