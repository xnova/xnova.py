"""
Testing utilities.
"""

from __future__ import with_statement

from django.template import Template, Context, RequestContext
from django.test.testcases import TestCase


def run_tests():
    """
    Use the Django test runner to run the tests.
    Sets the return code to the number of failed tests.
    """
    import sys
    import django
    try:
        django.setup()
    except AttributeError:
        pass
    try:
        from django.test.runner import DiscoverRunner as TestRunner
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner as TestRunner
    runner = TestRunner()
    sys.exit(runner.run_tests(["xnova"]))
