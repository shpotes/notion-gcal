from typing import Optional, Union, List
from dataclasses import dataclass


def notion_text(text: Optional[str]) -> dict:
    """
    Returns a Notion-friendly version of the text.
    Args:
        text: The text to be formatted.
    Returns:
        A Notion-friendly version of the text.
    """
    content = '' if text is None else text

    return {
        "rich_text": [{
            "text": {
                "content": content
            }
        }]
    }


def notion_url(url: Optional[str]) -> dict:
    """
    Returns a Notion-friendly version of the URL.
    Args:
        url: The URL to be formatted.
    Returns:
        A Notion-friendly version of the URL.
    """
    content = '' if url is None else url

    return {
        "url": content
    }


def notion_block(type: Union[str, List[str]], text_dict: dict) -> dict:
    """
    Returns a Notion-friendly version of a block.
    Args:
        type: The type of the block.
        text_dict: The text to be formatted.
    Returns:
        A Notion-friendly version of the block.
    """
    if isinstance(text_dict["content"], str):
        output_dict = {
            "object": "block",
            "type": type,
            type: {
                "text": [{
                    "type": "text",
                    "text": text_dict
                }]
            }
        }
    else:
        output_dict = {
            "object": "block",
            "type": type,
            type: {
                "text": [
                    {"type": "text", "text": text_chunk}
                    for text_chunk in text_dict["content"]
                ]
            }
        }

    return output_dict


@dataclass
class Event:
    start: str
    end: str
    title: str
    location: Optional[str] = None
    gcal_id: Optional[str] = None

    def _get_notion_page_title(self) -> dict:
        return {
            "title": [
                {
                    "text": {
                        "content": self.title
                    }
                }
            ]
        }

    def _get_notion_date(self):
        return {
            "date": {
                "start": self.start[:-6]+"Z",
                "end": self.end[:-6]+"Z"
            }
        }

    def to_notion_page(self) -> dict:
        """
        Returns a dict representing a Notion page.
        """
        properties = {}
        properties["Event"] = self._get_notion_page_title()
        properties["Date"] = self._get_notion_date()
        properties["gcal_id"] = notion_text(self.gcal_id)

        if self.location:
            properties["Meeting"] = notion_url(self.location)

        return {
            "properties": properties,
        }

    @classmethod
    def from_gdict(cls, event: dict) -> 'Event':
        start_date = event['start'].get('dateTime', event['start'].get('date'))
        end_date = event['end'].get('dateTime', event['end'].get('date'))
        if 'hangoutLink' in event:
            location = event['hangoutLink']
        elif 'conferenceData' in event:
            location = event['conferenceData']['entryPoints'][0]['uri']
        else:
            location = ""

        return cls(
            start=start_date,
            end=end_date,
            title=event['summary'],
            location=location,
            gcal_id=event['id']
        )

    @classmethod
    def from_notion_response(cls, response: dict) -> 'Event':
        info = response["properties"]

        return cls(
            start=info["Date"]["date"]["start"],
            end=info["Date"]["date"]["end"],
            title=info["Event"]["title"][0]["text"]["content"],
            location=info["Meeting"]["url"] if "Meeting" in info else None,
            gcal_id=info["gcal_id"]["rich_text"][0]["plain_text"]
        )
