from unittest import TestCase
from cv_ostf_adapter.controllers import root
import mock
from tests.test_functional import TestRootController


class TestUnits(TestCase):
    def test_start_async(self):
        tests = TestRootController
        root.start_async(tests)