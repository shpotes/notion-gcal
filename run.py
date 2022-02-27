import argparse
from pathlib import Path

from src import gcal, notion


def filter_old_events(
    notion_service,
    database_id,
    events
):
    notion_events = notion.get_events(notion_service, database_id)
    notion_ids = {event.gcal_id for event in notion_events}
    return [event for event in events if event.gcal_id not in notion_ids]


def sync_events(
    database_id: str,
    gcal_service,
    notion_service,
):
    events = gcal.get_events(gcal_service)
    new_events = filter_old_events(notion_service, database_id, events)
    for event in new_events:
        notion.create_event(
            notion_service,
            database_id,
            event
        )


def main(secret_dir: Path, database_id: str):
    gcal_service = gcal.get_service(secret_dir)
    notion_service = notion.get_service(secret_dir)

    sync_events(database_id, gcal_service, notion_service)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--secret_dir', type=str, required=True)
    args.add_argument('--database_id', type=str, required=True)

    parse_args = args.parse_args()
    main(Path(parse_args.secret_dir), parse_args.database_id)
