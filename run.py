import argparse
from pathlib import Path
import json

from src import gcal, notion


def sync_events(
    database_id: str,
    gcal_service,
    notion_service,
):
    events = gcal.get_events(gcal_service)
    for event in events:
        notion.create_event(
            notion_service,
            database_id,
            event
        )


def main(secret_dir: Path):
    with open(secret_dir / 'notion_secrets.json', 'r') as buf:
        database_id = json.load(buf)['database_id']

    gcal_service = gcal.get_service(secret_dir)
    notion_service = notion.get_service(secret_dir)

    sync_events(database_id, gcal_service, notion_service)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--secret_dir', type=str, required=True)

    main(Path(args.parse_args().secret_dir))
