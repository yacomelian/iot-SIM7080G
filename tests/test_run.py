"""
Unit test for the program
"""

import run


class TestRun:

    def test_1(self):
        run.load_config()
        assert 1 == 1

    def test_2(self):
        run.load_config()
        assert 2 == 2
