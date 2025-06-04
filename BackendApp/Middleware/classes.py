from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from BackendApp.Database.Models.promocode_types import _PromocodeType
from uuid import UUID


@dataclass
class QuizForAPI:
    id: int
    header: str
    answer_cnt: int
    answers: List[str]
    correct_ans_id: int
    test_id: int

@dataclass
class Quiz:
    header: str
    answer_cnt: int
    answers: List[str]
    correct_ans_id: int
    test_id: int


@dataclass
class Test:
    name: str
    correct_cnt: int
    total_cnt: int
    description: str
    test_id: int
    promocode_type: _PromocodeType
    bar_id: int
    
    
@dataclass
class AffilatePromotion:
    channel_link: str
    promotion_text: str
    promocode_type: _PromocodeType
    short_name: str
    bar_id: int
    sub_chat_id: List[str] = None
    id: Optional[int] = None
