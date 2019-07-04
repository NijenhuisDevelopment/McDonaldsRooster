import os
from datetime import datetime
import locale
import dateutil.parser
from flask import render_template, Blueprint, flash, redirect, url_for
import authentication
import application.gmail as mail
from application import kalendar
import copy
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


@main.route("/rooster/fetch")
def fetch_email():
    if authentication.is_logged_in():
        response, subject = mail.get_body_from_message()
        wd = prepare_events_for_calendar(subject, response)
        c = copy.deepcopy(wd)
        for w in c:
            locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')
            w.startTime = datetime.strftime(dateutil.parser.parse(w.startTime), "%A %e %B, %Y, %H:%M")
            w.endTime = datetime.strftime(dateutil.parser.parse(w.endTime), "%A %e %B, %Y, %H:%M")
            locale.setlocale(locale.LC_ALL, 'C')

        return render_template('summary.html', events=c, auth=True)
    else:
        return redirect(url_for('authentication.login'))


def prepare_events_for_calendar(subject, response):
    filepath = str(subject) + ".txt"
    kalendar.workdays = []

    if not os.path.isfile(filepath):
        file = open(filepath, "w+")
        file.write(response)
        file.close()
        kalendar.parse_file(filepath)
        workdays = kalendar.get_all_events()
        os.remove(filepath)

    return workdays


@main.route("/rooster/add")
def add_events_to_calendar():
    locale.setlocale(locale.LC_ALL, 'C')
    workdays = kalendar.get_all_events()
    service = authentication.build_calendar_api()

    for w in workdays:
        event = {
            'summary': 'Werken: ' + w.station,

            'start': {
                'dateTime': w.startTime,
            },
            'end': {
                'dateTime': w.endTime,
            },
            'reminders': {
                'useDefault': True,
            },
        }
        kalendar.create_event(event, service)
    flash("Rooster is toegevoegd", "info")
    return render_template('home.html', auth=True)
