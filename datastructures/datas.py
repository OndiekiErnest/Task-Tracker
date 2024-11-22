"""data structures"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass(slots=True, kw_only=True)
class TopicData:
    """topic attrs"""

    topic_id: int
    created: datetime
    title: str
    starts: datetime
    span: int
    enabled: bool
    ends: datetime = field(init=False)

    def __post_init__(self):
        self.ends = self.starts + timedelta(minutes=self.span)


@dataclass(slots=True, kw_only=True)
class ProblemData:
    """problem attrs"""

    problem_id: int
    created: datetime
    problem: str
    topic_id: int
    solved: bool
