import requests
import json
import time
from datetime import datetime, timedelta

from utils import str_to_timestamp

from config import FETCH_OFFSET_DAYS


def fetch_events():
    start_time_five_days_from_now = datetime.utcnow() + timedelta(days=FETCH_OFFSET_DAYS)
    
    start_time_midnight = start_time_five_days_from_now.replace(hour=0, minute=0, second=0, microsecond=0)
   
    start_time_unix = int(start_time_midnight.timestamp())
    finish_time_unix = start_time_unix + (10 * 24 * 60 * 60) - 1

    ctftime_response = requests.get(f'https://ctftime.org/api/v1/events/?limit=1000&start={start_time_unix}&finish={finish_time_unix}')

    events = json.loads(ctftime_response.text)
    return events


def filter_fetched_events():
    events = fetch_events()

    start_time_five_days_from_now = datetime.utcnow() + timedelta(days=FETCH_OFFSET_DAYS+1)
    start_time_midnight = start_time_five_days_from_now.replace(hour=0, minute=0, second=0, microsecond=0)
    finish_time_unix = int(start_time_midnight.timestamp()) - 1

    filtered_events = []

    for event in events:
        event_unix_time = str_to_timestamp(event['start'])
        if (event_unix_time < finish_time_unix):
            filtered_events.append({'id':event['id'], 'title':event['title'], 'start':event['start'], 'finish': event['finish'] ,'url':event['url'] })
    
    return filtered_events


def more_about_event(id):
    response = requests.get(f"https://ctftime.org/api/v1/events/{id}/")
    event_info = json.loads(response.text)
    return event_info