"""

"""


def raise_for_result(func):
    def wrapper(*args, **kwargs):
        success, result = func(*args, **kwargs)
        if success:
            return result
        else:
            raise Exception("Command failed")
