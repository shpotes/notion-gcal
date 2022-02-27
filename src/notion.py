from typing import Union, List
import json
from pathlib import Path

from notion_client import Client

from .structs import Event


def get_service(secrets_dir: Union[Path, str]) -> Client:
    """
    Returns a Notion client object.
    Args:
        secrets_dir: Path to the directory containing the secrets.json file.
    Returns:
        A Notion client object.
    """
    secrets_dir = Path(secrets_dir)
    # Get the notion token
    with open(secrets_dir / 'notion_secrets.json', 'r') as buf:
        notion_secrets = json.load(buf)
        token = notion_secrets['token']
    # Create the client
    client = Client(auth=token)

    return client


def create_event(
    service: Client,
    database_id: str,
    event: Event
) -> dict:
    """
    Creates a new event in a given Notion database.
    """
    service.pages.create(
        parent={
            "database_id": database_id
        },
        **event.to_notion_page()
    )


def get_events(
    service: Client,
    database_id: str,
) -> List[Event]:
    response = service.databases.query(database_id)
    return [Event.from_notion_response(res) for res in response["results"]]
