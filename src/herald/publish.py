import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from herald.repo import EventRepository
from herald.targets import Target
from herald import templating

logger = logging.getLogger(__name__)


@dataclass
class TargetEntry:
    target: Target
    template: str


class Publisher:
    def __init__(self, source: str, entries: list[TargetEntry], lookahead: timedelta):
        """
        :param source: Path or URL to the iCal source file
        :param entries: List of targets to publish
        :param lookahead: Time period to include
        :param template: Path to jinja2 template file
        """

        self.source = source
        self.entries = entries
        self.lookahead = lookahead
        self.repo = EventRepository(source=self.source)

    def publish(self):
        now = datetime.now()
        events = self.repo.list(start=now, end=now + self.lookahead)

        if not events:
            logger.info("No events found in the lookahead window")
            return

        for entry in self.entries:
            message = templating.render(entry.template, events)
            entry.target.publish(message)
