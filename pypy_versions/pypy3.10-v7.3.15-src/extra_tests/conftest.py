import sys
import pytest

def get_marker(item, name):
    try:
        return item.get_closest_marker(name=name)
    except AttributeError:
        # pytest < 3.6
        return item.get_marker(name=name)


def pytest_runtest_setup(item):
    if get_marker(item, name='pypy_only'):
        if '__pypy__' not in sys.builtin_module_names:
            pytest.skip('PyPy-specific test')


def pytest_configure(config):
    config.addinivalue_line("markers", "pypy_only: PyPy-specific test")

# This needs to be in the top-level conftest.py, it is copied from the one
# in hpy_tests/_vendored See the note at
# https://docs.pytest.org/en/7.1.x/reference/reference.html#initialization-hooks
def pytest_addoption(parser):
    parser.addoption(
        "--compiler-v", action="store_true",
        help="Print to stdout the commands used to invoke the compiler")
    parser.addoption(
        "--subprocess-v", action="store_true",
        help="Print to stdout the stdout and stderr of Python subprocesses"
             "executed via run_python_subprocess")
    parser.addoption(
        "--dump-dir",
        help="Enables dump mode and specifies where to write generated test "
             "sources. This will then only generate the sources and skip "
             "evaluation of the tests.")

def pytest_collection_modifyitems(config, items):
    skip1 = pytest.mark.skip(reason="PyPy does not warn")
    skip2 = pytest.mark.skip(reason="PyPy does not report a traceback")
    for item in items:
        if item.name == "test_more_buffer_warning":
            item.add_marker(skip1)
        if item.name == "test_callback_exception":
            item.add_marker(skip2)

