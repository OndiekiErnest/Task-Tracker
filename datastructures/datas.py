"""data structures"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class TopicData:
    """topic attrs"""

    topic_id: int
    created: datetime
    title: str
    starts: datetime
    enabled: bool
    ends: datetime


@dataclass(slots=True, kw_only=True)
class ProblemData:
    """problem attrs"""

    problem_id: int
    created: datetime
    problem: str
    topic_id: int
    solved: bool
