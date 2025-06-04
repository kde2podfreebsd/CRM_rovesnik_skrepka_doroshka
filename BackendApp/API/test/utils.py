from BackendApp.API.test.scheme import *
from BackendApp.Database.Models.test_result_model import TestResult
from BackendApp.Database.Models.test_model import Test

def parse_test_result_into_format(test_res: TestResult) -> TestResultResponse:
    return TestResultResponse(
        id=test_res.id,
        chat_id=test_res.chat_id,
        test_id=test_res.test_id,
        correct_cnt=test_res.correct_cnt,
        total_cnt=test_res.total_cnt,
        get_reward=test_res.get_reward,
        is_first_try=test_res.is_first_try
    )
    
def parse_test_results_into_format(test_results) -> List[TestResultResponse]:
    return [parse_test_result_into_format(test_res) for test_res in test_results]

def parse_test_into_format(test: Test) -> TestResponse:
    return TestResponse(
        id=test.id,
        test_id=test.test_id,
        name=test.name,
        correct_cnt=test.correct_cnt,
        total_cnt=test.correct_cnt,
        description=test.description,
        promocode_type=test.promocode_type,
        bar_id=test.bar_id
    )
    
def parse_tests_into_format(tests) -> List[TestResponse]:
    return [parse_test_into_format(test) for test in tests]