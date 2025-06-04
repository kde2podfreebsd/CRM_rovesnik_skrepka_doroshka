from BackendApp.API.test.scheme import *


def parse_test_result_into_format(test_res) -> TestResultResponse:
    return TestResultResponse(
        id=test_res.id,
        chat_id=test_res.chat_id,
        test_id=test_res.test_id,
        correct_cnt=test_res.correct_cnt,
        total_cnt=test_res.total_cnt,
        get_reward=test_res.get_reward,
        promo=test_res.promo,
        is_first_try=test_res.is_first_try
    )
    
def parse_test_results_into_format(test_results) -> List[TestResultResponse]:
    return [parse_test_result_into_format(test_res) for test_res in test_results]


def parse_test_into_format(test) -> TestResponse:
    return TestResponse(
        id=test.id,
        test_id=test.test_id,
        name=test.name,
        correct_cnt=test.correct_cnt,
        total_cnt=test.correct_cnt,
        description=test.description,
        percent_to_add=test.percent_to_add
    )
    
    
def parse_tests_into_format(tests) -> List[TestResponse]:
    return [parse_test_into_format(test) for test in tests]