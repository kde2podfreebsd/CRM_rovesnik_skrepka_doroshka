from pydantic import BaseModel
from typing import Optional, List
    
class CreateQuizRequest(BaseModel):
    header: str
    answers: List[str]
    answer_cnt: int
    correct_ans_id: int
    test_id: int
    

class QuizResponse(BaseModel):
    id: int
    header: str
    answers: List[str]
    answer_count: int
    correct_ans_id: int
    test_id: int
    
class UpdateQuizRequest(BaseModel):
    id: int
    header: str = None
    answers: List[str] = None
    answer_count: int = None
    correct_ans_id: int = None
    test_id: int = None
    