from typing import Union, List
import datetime as dt
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from .structs import Event

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_service(secrets_dir: Union[Path, str]) -> Resource:
    """
    Returns a Google Calendar resource object.
    Args:
        secrets_dir: Path to the directory containing the secrets.json file.
    Returns:
        A Google Calendar resource object.
    """
    secrets_dir = Path(secrets_dir)
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if (secrets_dir / 'token.json').exists():
        creds = Credentials.from_authorized_user_file(
            secrets_dir / 'token.json', SCOPES
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_dir / 'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(secrets_dir / 'token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    return service


def get_events(
    service: Resource,
    calendar_id: str = 'primary',
    num_events: int = 10,
    single_events: bool = True,
) -> List[Event]:
    """
    Returns a list of events from the Google Calendar API.
    Args:
        service: A Google Calendar resource object.
        calendar_id: The ID of the calendar to retrieve events from.
        num_events: The number of events to retrieve.
        single_events: Whether to retrieve single or recurring events.
    Returns:
        A list of events from the Google Calendar API
    """
    # Call the Calendar API
    now = dt.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_results = service.events().list(
        calendarId=calendar_id, timeMin=now,
        maxResults=num_events, singleEvents=single_events,
        orderBy='startTime'
    ).execute()
    events = events_results.get('items', [])

    if not events:
        print('No upcoming events found.')

    output_events = []
    for event in events:
        output_events.append(Event.from_dict(event))

    return output_events