
from api.app import check_loading


def test_check_loading():
    first_check = check_loading()
    print(first_check)
    assert not first_check["loaded"]
    assert not first_check["max_try_passed"]
    for i in range(6):
        check_loading()

    later_check = check_loading()
    print(later_check)
    assert not later_check["loaded"]
    assert later_check["max_try_passed"]
