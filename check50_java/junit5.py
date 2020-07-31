# Copyright (C) 2020  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

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


##########################
JUNIT_JAR = "junit-platform-console-standalone-1.6.2.jar"

JUNIT_JAR_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'lib',
    JUNIT_JAR)

JUNIT_DEFAULT_ARGS = [
    '--disable-ansi-colors',
    '--disable-banner',
    '--details=none',
]
XML_REPORT = "TEST-junit-jupiter.xml"


def compile_test(*files, javac=JAVAC, classpaths=None, **cflags):
    """
    Compile given source files but make sure that the junit jar
    is added to the classpath when calling the compiler.

    All parameters are as for :func:`check50_java.run`.
    The junit5 standalone jar file will be added to the classpath.
    """
    cp = classpaths or []
    cp.append(JUNIT_JAR_PATH)
    compile_raw(*files,
                javac=javac,
                classpaths=cp,
                failhelp="make sure your methods have correct signatures",
                **cflags)


def run_and_interpret_test(**kwargs):
    """
    Execute the Junit5 CLI runner and interprets all resulting testcases.

    This will run the CLI test runner with the given arguments (to select the
    testclass or filter the list of tests to execute), then read the resulting
    XML report and raise check50.Failure's for every failure or error
    found in the report.

    All parameters are as for :func:`check50_java.run`.
    The junit5 standalone jar file will be added to the classpath.

    """
    report = run_test(**kwargs)
    for case in report['testcases']:
        interpret_testcase(case)


def run_test(java=JAVA, classpaths=None, timeout=None, args=None):
    """
    Execute the Junit5 CLI and return a report.

    All parameters are as for :func:`check50_java.run`.
    The junit5 standalone jar file will be added to the classpath.

    The return value is a python dict that summarizes relevant testcases
    and their execution info, as read from the Junit XML report file.
    """

    # prepare classpath parameter
    classpaths = ['.'] + _expand_classpaths(classpaths)
    classpath = ":".join(classpaths)

    # command line arguments to the junit5 runner cmd
    args = args or []
    args = JUNIT_DEFAULT_ARGS + args

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
        check50._api.run(cmdline).exit(timeout=timeout)

        # supress log message introduced in previous command
        # which logs the full shell command (java -cp ..)
        check50._api._log.clear()

        # interpret XML report
        path = os.path.join(report_dir, XML_REPORT)
        report = read_xml_report(path, include_trace=True)

    return report


def interpret_testcase(case):
    """
    Inspect the given testcase result and raise an appropriate check50.Failure
    if the testcase was unsuccessful.
    """
    if not case['pass']:
        msg = case['message']
        if case['exception'].endswith('AssertionFailedError'):
            r = r'^expected: \<(.+?)\> but was: \<(.+?)\>'
            m = re.match(r, msg, re.MULTILINE)
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
                # highlight if default constructor missing
                r = r'^(\w+?): method \'void <init>\(\)\' not found'
                m = re.match(r, c['message'])
                if m:
                    clazz = m.groups()[0]
                    c['message'] = f"no constructor: '{clazz}()'."
                else:
                    # highlight other missing methods
                    r = r'^\'(\w+?) (\w+?)\.([a-zA-Z<>]+?)\((.*)\)\''
                    m = re.match(r, c['message'])
                    if m:
                        rtype, clazz, method, args = m.groups()
                        if method == "<init>":
                            msg = f"no constructor: '{clazz}({args})'."
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
