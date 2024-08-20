"""data structures"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass(slots=True, kw_only=True)
class TopicData:
    """topic attrs"""

    title: str
    starts: datetime
    span: int
    enabled: bool
    ends: datetime = field(init=False)

    def __post_init__(self):
        self.ends = self.starts + timedelta(minutes=self.span)


@dataclass(frozen=True)
class Key:
    """singleton key"""

    obj: object
    args: tuple
    kwargs: frozenset
