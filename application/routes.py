import itertools
import os
from datetime import datetime
import locale
import dateutil.parser
from flask import render_template, Blueprint, flash, redirect, url_for, session
import authentication
import application.gmail as mail
from application import kalendar
import copy
from application.forms import AddEventsForm
import requests

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    global authenticated
    try:
        if authentication.get_user_info() is not None:
            authenticated = True
    except Exception:
        authenticated = False
    finally:
        return render_template('home.html', auth=authenticated)


def add_to_session(event_list):
    json_list = []
    for item in event_list:
        json_item = item.to_json()
        json_list.append(json_item)
    session['event_list'] = json_list


@main.route("/rooster/summary")
def event_summary():
    # form = AddEventsForm()
    return render_template("summary.html", auth=True)


@main.route("/rooster/fetch/all")
def fetch_all_mail():
    if authentication.is_logged_in():

        response, subject = mail.get_body_from_messages()
        wd = prepare_events_for_calendar_all(subject, response)
        copied = copy.deepcopy(wd)
        copied.sort(key=lambda r: r.start_time)
        for workday in copied:
            # print(workday.start_time)
            locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')
            workday.start_time = datetime.strftime(dateutil.parser.parse(workday.start_time), "%A %e %B, %Y, %H:%M")
            workday.end_time = datetime.strftime(dateutil.parser.parse(workday.end_time), "%A %e %B, %Y, %H:%M")
            locale.setlocale(locale.LC_ALL, 'C')  # print(workday.start_time)
        return render_template('summary.html', events=copied, auth=True)
    else:
        return redirect(url_for('authentication.login'))


@main.route("/rooster/fetch/latest")
def fetch_latest_mail():
    if authentication.is_logged_in():
        response, subject = mail.get_body_from_single_message()
        wd = prepare_events_for_calendar(subject, response)
        copied = copy.deepcopy(wd)
        copied.sort(key=lambda r: r.start_time)
        for workday in copied:
            locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')
            workday.start_time = datetime.strftime(dateutil.parser.parse(workday.start_time), "%A %e %B, %Y, %H:%M")
            workday.end_time = datetime.strftime(dateutil.parser.parse(workday.end_time), "%A %e %B, %Y, %H:%M")
            locale.setlocale(locale.LC_ALL, 'C')

        return render_template('summary.html', events=copied, auth=True)
    else:
        return redirect(url_for('authentication.login'))


def prepare_events_for_calendar_all(subject, response):
    kalendar.workdays = []
    for email, resp in zip(range(len(subject)), range(len(response))):
        filepath = str(email) + ".txt"

        if not os.path.isfile(filepath):
            file = open(filepath, "w+")
            file.write(response[resp])
            file.close()
            kalendar.parse_file(filepath)
            os.remove(filepath)

    return kalendar.get_all_events()


def prepare_events_for_calendar(subject, response):
    filepath = str(subject) + ".txt"
    kalendar.workdays = []

    if not os.path.isfile(filepath):
        file = open(filepath, "w+")
        file.write(response)
        file.close()
        kalendar.parse_file(filepath)
        os.remove(filepath)

    return kalendar.get_all_events()


@main.route("/rooster/add", methods=["POST"])
def add_events_to_calendar():
    locale.setlocale(locale.LC_ALL, 'C')
    workdays = kalendar.get_all_events()
    service = authentication.build_calendar_api()


    for w in workdays:
        event = {
            'summary': 'Werken: ' + w.station,
            'start': {'dateTime': w.start_time, },
            'end': {'dateTime': w.end_time, },
            'reminders': {'useDefault': True, },
        }
        # kalendar.create_event(event, service)
    flash("Rooster is toegevoegd", "info")
    return render_template('home.html', auth=True)
