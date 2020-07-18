import xml.etree.ElementTree as ET  # for junit parser

import os
import re
import tempfile
import check50
from check50._api import Failure
from check50._api import Mismatch
from check50_java import compile as compile_raw
from check50_java import JAVAC, JAVA
from check50_java.util import _expand_classpaths

JUNIT_JAR = "junit-platform-console-standalone-1.6.2.jar"

JUNIT_JAR_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'lib',
    JUNIT_JAR)

JUNIT_DEAFAULT_ARGS = [
    '--disable-ansi-colors',
    '--disable-banner',
    '--details=none',
]
XML_REPORT = "TEST-junit-jupiter.xml"


def compile_test(*files, javac=JAVAC, **cflags):
    compile_raw(*files,
                javac=JAVAC,
                classpaths=[JUNIT_JAR_PATH],
                failhelp="make sure your methods have correct signatures",
                **cflags)


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
            inspect_testcase(case)

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


def run_and_interpret_test(java=JAVA, classpaths=None, args=None):
    """execute the junit5 CLI runner and interprets all resulting testcases."""
    report = run_test(java, classpaths, args)
    for case in report['testcases']:
        interpret_testcase(case)


def run_test(java=JAVA, classpaths=None, args=None):
    """execute the junit5 CLI and return a report."""

    # prepare classpath parameter
    classpaths = ['.'] + _expand_classpaths(classpaths)
    classpath = ":".join(classpaths)

    # command line arguments to the junit5 runner cmd
    args = args or []
    args = JUNIT_DEAFAULT_ARGS + args

    # make sure report is defined
    report = {'testcases': []}

    with tempfile.TemporaryDirectory() as report_dir:
        # prepare command line string
        cmd = [
            java,
            '-jar', JUNIT_JAR_PATH,
            '-cp', '"' + classpath + '"',
            f"--reports-dir={report_dir}",
        ] + args
        cmdline = " ".join(cmd)
        # check50._api.log(cmdline)

        # call subprocess and wait until it's done
        check50._api.run(cmdline).exit()

        # interpret XML report
        path = os.path.join(report_dir, XML_REPORT)
        report = read_xml_report(path, include_trace=True)

    return report


def interpret_testcase(case):
    """
    raises appropriate check50 exceptions
    if given testcase (from a junit report) fails.
    """
    if not case['pass']:
        msg = case['message']
        if case['exception'].endswith('AssertionFailedError'):
            r = r'^expected: \<(.+?)\> but was: \<(.+?)\>'
            m = re.match(r, msg)
            if m:
                expected, actual = m.groups()
                raise Mismatch(expected, actual)
            else:
                raise Failure(msg)
        raise Failure(msg)


def read_xml_report(path, include_trace=False):
    """Interpret JUnit5 XML report file."""
    tree = ET.parse(path)
    root = tree.getroot()

    s = {}
    s['testcases'] = []
    for case in root.findall('testcase'):
        c = case.attrib

        # remove trailing "()" on testcase names only when run with junit5
        if c['name'].endswith("()"):
            c['name'] = c['name'][:-2]

        c['pass'] = True
        for e in case.findall('error'):
            c['pass'] = False
            c['exception'] = e.get('type')
            c['message'] = e.get('message')
            etype = e.get('type')

            if etype == 'java.lang.NoSuchMethodError':
                r = r'^\'(\w+?) (\w+?)\.([a-zA-Z<>]+?)\((.*)\)\''
                m = re.match(r, c['message'])
                if m:
                    rtype, clazz, method, args = m.groups()
                    if method == "<init>":
                        msg = f"could not find constructor:  {clazz}({args})."
                    else:
                        msg = "could not find method:  " \
                            + f"{rtype} {clazz}.{method}({args})"
                    c['message'] = msg

        for f in case.findall('failure'):
            c['pass'] = False
            c['exception'] = f.get('type')
            c['message'] = f.get('message')
            if include_trace:
                c['trace'] = f.text
        s['testcases'].append(c)

    s['failures'] = int(root.attrib['failures'])
    s['tests'] = int(root.attrib['tests'])
    s['passed'] = s['tests'] - s['failures']
    return s
