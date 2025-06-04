from pydantic import BaseModel
from typing import Optional, List
from BackendApp.Database.Models.promocode_types import _PromocodeType

class TestRequest(BaseModel):
    name: str
    correct_cnt: int
    total_cnt: int
    description: str
    test_id: int
    promocode_type: _PromocodeType
    bar_id: int
    
class Quiz(BaseModel):
    header: str
    answers: bytes
    answer_count: int
    correct_ans_id: int
    test_id: int
    
class CreateTestRequest(BaseModel):
    test: TestRequest
    quizes: List[Quiz]
    
class TestResultResponse(BaseModel):
    id: int
    chat_id: int
    test_id: int
    correct_cnt: int
    total_cnt: int
    get_reward: bool
    is_first_try: Optional[bool] = None
    

class TestUpdateRequest(BaseModel):
    test_id: int
    name: Optional[str] = None
    correct_cnt: Optional[int] = None
    total_cnt: Optional[int] = None
    description: Optional[str] = None
    promocode_type: Optional[_PromocodeType] = None
    bar_id: Optional[int] = None

class TestResponse(BaseModel):
    id: int
    test_id: int
    name: str
    correct_cnt: int
    total_cnt: int
    description: str
    promocode_type: _PromocodeType
    test_id: int
    bar_id: int