import os

def pytest_generate_tests(metafunc):
        os.environ['ALLOWED_ISS'] = "test"
