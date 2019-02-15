import json
import os
import time
from datetime import datetime
from typing import Tuple

import httplib2
from oauth2client import tools
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

APP_KEYS_FILE = 'app_keys.json'
USER_OAUTH_DATA_FILE = os.path.expanduser('~/.google-reminders-cli-oauth')

HTTP_OK = 200


def authenticate() -> httplib2.Http:
    """
    returns an Http instance that already contains the user credentials and is
    ready to make requests to alter user data.

    On the first time, this function will open the browser so that the user can
    grant it access to his data
    """
    with open(APP_KEYS_FILE) as f:
        app_keys = json.load(f)
    storage = Storage(USER_OAUTH_DATA_FILE)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(
            OAuth2WebServerFlow(
                client_id=app_keys['APP_CLIENT_ID'],
                client_secret=app_keys['APP_CLIENT_SECRET'],
                scope=['https://www.googleapis.com/auth/reminders'],
                user_agent='google reminders cli tool'),
            storage,
        )
    auth_http = credentials.authorize(httplib2.Http())
    return auth_http


def get_request_params(
    title: str, year: int, month: int, day: int, hour: int, minute: int,
) -> Tuple[dict, dict]:
    """
    get the headers and data needed for the request

    :return: (headers, data)
    """
    second = 00  # we always use 0 seconds
    headers = {
        'content-type': 'application/json+protobuf',
    }

    id = time.time()  # the reminder id is the unix time at which it was created
    reminder_id = f'cli-reminder-{id}'

    # The structure of the dictionary was extracted from a browser request to
    # create a new reminder. I didn't find any official documentation
    # for the request parameters.
    data = {
        "2": {
            "1": 7
        },
        "3": {
            "2": reminder_id
        },
        "4": {
            "1": {
                "2": reminder_id
            },
            "3": title,
            "5": {
                "1": year,
                "2": month,
                "3": day,
                "4": {
                    "1": hour,
                    "2": minute,
                    "3": second,
                }
            },
            "8": 0
        }
    }
    return headers, data


def parse_date(date_str: str) -> Tuple[int, int, int, int, int]:
    """
    extract the date and time from the given date representation string

    :return: (year, month, day, hour, minute)
    """
    supported_formats = [
        '%Y:%m:%d %H:%M', '%Y%m%d %H%M', '%Y%m%d %H:%M',
    ]
    for fmt in supported_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.year, dt.month, dt.day, dt.hour, dt.minute
        except ValueError:
            pass
    raise ValueError('Invalid date format')


def read_reminder_params():
    title = input('Enter reminder title: ')
    date_str = input('Enter time (yyyy:mm:dd HH:MM): ')
    year, month, day, hour, minute = parse_date(date_str)
    return get_request_params(title, year, month, day, hour, minute)


def main():
    auth_http = authenticate()
    headers, data = read_reminder_params()
    response, content = auth_http.request(
        uri='https://reminders-pa.clients6.google.com/v1internalOP/reminders/create',
        method='POST',
        body=json.dumps(data),
        headers=headers,
    )
    if response.status == HTTP_OK:
        print('Reminder set successfully')
    else:
        print('Error while trying to set a reminder:')
        print(f'    status code - {response.status}')
        print(f'    {content}')


if __name__ == '__main__':
    main()
