import re
import shutil

import pytest

pytest_plugins = "pytester"

HELP_MESSAGE = "\\?\\:help"
VARIABLES_TABLE = "V\x1b\\[0;30;47mariables:"

# pudb/debugger.py:DebuggerUI#event_loop#WELCOME_LEVEL:2453
DEFAULT_CONFIG = """\
[pudb]
prompt_on_quit = False
seen_welcome = e999
"""


@pytest.fixture(autouse=True)
def pudb_xdg_home(tmp_path_factory, monkeypatch):
    configdir = tmp_path_factory.mktemp("pytest_pudb_testdir")
    monkeypatch.setenv("XDG_CONFIG_HOME", configdir)

    pudbconfig = configdir / "pudb" / "pudb.cfg"
    pudbconfig.parent.mkdir(exist_ok=True)

    with open(pudbconfig, "w", encoding="utf-8") as f:
        f.write(DEFAULT_CONFIG)

    yield

    shutil.rmtree(configdir, ignore_errors=True)


def test_pudb_interaction(testdir):
    p1 = testdir.makepyfile("""
        def test_1():
            assert 0 == 1
    """)
    child = testdir.spawn_pytest(f"--pudb {p1}")
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    # Check that traceback postmortem handled
    child.expect("PROCESSING EXCEPTION")
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_unittest_teardown_interaction(testdir):
    p1 = testdir.makepyfile("""
        import unittest
        class Blub(unittest.TestCase):
            def tearDown(self):
                self.a = False
            def test_false(self):
                self.a = True
                self.fail()
    """)
    child = testdir.spawn_pytest(f"--pudb {p1}")
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect("PROCESSING EXCEPTION")
    child.expect(VARIABLES_TABLE)
    child.send("V")  # Move to variables
    child.send("n")  # Add watch expression
    child.expect("Add Watch Expression")
    child.sendline("self.a")  # Set self.a
    child.expect("self.a: \x1b\\[0;30;42mTrue")
    child.sendeof()


def test_pudb_set_trace_integration(testdir):
    p1 = testdir.makepyfile("""
        def test_1():
            import pudb
            pudb.set_trace()
            assert 1
    """)
    child = testdir.spawn_pytest(p1)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pu_db_integration(testdir):
    p1 = testdir.makepyfile("""
        def test_1():
            import pudb
            pu.db
            assert 1
    """)
    child = testdir.spawn_pytest(p1)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_b_integration(testdir):
    p1 = testdir.makepyfile("""
        def test_1():
            import pudb.b
            assert 1
    """)
    child = testdir.spawn_pytest(p1)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_avoid_double_prologue(testdir):
    import pexpect

    from pytest_pudb import ENTER_MESSAGE

    p1 = testdir.makepyfile("""
        def test_1():
            test = []
            assert test[0]
    """)

    re_escape = re.escape(ENTER_MESSAGE).encode("utf-8")
    re_enter = re.compile(rb"\r\n>+ %s >+\r\n" % re_escape)  # \r\n instead of ^,$

    child = testdir.spawn_pytest(f"--pudb {p1}")
    child.expect(re_enter)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    # Check that traceback postmortem handled
    child.expect("PROCESSING EXCEPTION")
    child.expect(VARIABLES_TABLE)

    # Exit pudb
    child.write("q")
    ret = child.expect([re_enter, pexpect.EOF])

    if ret == 0:
        raise RuntimeError(f"pexpect found {re_enter!r} again!")
