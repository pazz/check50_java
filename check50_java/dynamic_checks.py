# Copyright (C) 2020  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

import check50

from check50_java.junit import run_test
from check50_java.junit import interpret_testcase


def checks_from_testclass(testclass, dependency=None, classpaths=None):
    """
    Create check50 checks for every testcase that junit5 finds
    the given test class.

    This will create one check which runs the junit cli on the given testclass
    and several child checks, one for every testcase reported by junit.
    The parent check depends on the given dependency (a check50 check).
    It is the only one that interacts with junit5. All other checks depend on
    this parent check, and only relay the results of their (junit) testcase.

    :param testclass: the name of the junit test class
    :type testclass: str
    :param dependency: the check that all generated checks depends on
    :type dependency: function
    :param classpaths: a list of paths that together will form the classpath
                       parameter for the underlying `java` command.
                       Each element is a string containing a path to a
                       directory or jar file. relative paths are interpreted
                       relative to the problem set.
    :type classpaths: list(str)
    :type timeout: list(str)


    Example usage::

        @check50.check() # Mark 'exists' as a check
        def exists():
            \"""hello.c exists\"""
            check50.exists("hello.c")


    """
    checks = []  # we will collect checks here

    # The main check, which runs all unit tests and passes on a report
    @check50.check(dependency)
    def run_tests():
        f"""Inspect {testclass}"""
        report = run_test(classpaths=classpaths,
                          args=['--select-class', '"' + testclass+'"'])

        return report

    checks.append(run_tests)

    # A function to create a sub-check for the i^th testcase in the report.
    # It will simply look up and pass on the results from the report.
    # testclass and testmethod are only used to derive a readable name.
    # TODO: read those off the report.
    def _create_check(testclass, testmethod, i):
        def check(rep):
            case = rep['testcases'][i]
            interpret_testcase(case)

        check_id = f"{i}:{testclass}.{testmethod}"
        check.__name__ = check_id
        check.__doc__ = check_id
        return check

    # run junit once to generate report and extract test cases
    report = run_test(classpaths=classpaths,
                      args=['--select-class', testclass])

    i = 0
    for case in report['testcases']:
        testmethod = case['name']

        check = _create_check(testclass, testmethod, i)
        i += 1

        # Register the check with check50
        check = check50.check(run_tests)(check)

        checks.append(check)
    return checks
