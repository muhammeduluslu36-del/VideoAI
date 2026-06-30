from dataclasses import dataclass


@dataclass
class TimelineItem:
    start: float
    end: float
    type: str
    value: str | None = None


class Timeline:

    def __init__(self):
        self.items = []

    def add(self, item: TimelineItem):
        self.items.append(item)

    def duration(self):
        if not self.items:
            return 0

        return max(i.end for i in self.items)