# Copyright (C) 2020  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

import xml.etree.ElementTree as ET  # for junit parser

import os
import check50

from check50._api import Failure
from check50_java import JAVA


##########################

class CheckstyleWarning:
    """A single checkstyle error"""

    def __init__(self, **kwargs):
        self.data = kwargs

    def location(self):
        l = None
        if 'filename' in self.data:
            l = self.data['filename']
            if 'line' in self.data:
                prec = "line " + self.data['line']
                if 'column' in self.data:
                    prec += ", char " + self.data['column']
                l += "(" + prec + ")"
        return l

    def __str__(self):
        return "In " + self.location() + ": " + self.data['message']


def run_and_interpret_checkstyle(**kwargs):
    """
    Execute the checkstyle CLI runner, interpret and log all resulting warnings
    and raise check50 Failure if there were warnings.

    Ideally, this would be replaced by a special check50.Failure subclass
    that encapsulates all warnings and is rendered nicely into html by check50.
    The problem is that check50 hard-codes its html template.

    All parameters are as for :func:`run_checkstyle`.
    """
    report = run_checkstyle(**kwargs)
    if report:
        check50.log("Issues found:")
        for w in report:
            check50.log("- " + str(w))
        raise Failure(rationale="stylistic issues found")


def run_checkstyle(jar=None, checks_file=None, target=None,
                   java=JAVA, timeout=None):
    """
    Execute the Checkstyle CLI and return a report.

    java and timeout parameters are as for :func:`check50_java.run`.
    The junit5 standalone jar file will be added to the classpath.

    :param str jar: The (relative) path to the checkstyle-all jar file that can
                    be executed on the command line.
    :param str checks_file: the path to the checks xml file to be used
    :param str target: the path to those files checkstyle should inspect

    The return value is a list of CheckstyleWarning, each of which represents
    a complaint, as read from the XML report produced by checkstyle.
    """

    cmd = [
        java,
        '-jar', jar,
        '-c', checks_file,
        '-f xml',
        target
    ]
    cmdline = " ".join(cmd)

    # call subprocess and wait until it's done
    report = check50._api.run(cmdline).stdout(timeout=timeout)

    return read_checkstyle_xml(report)


def read_checkstyle_xml(report, remove_path_prefix=''):
    """turn checkstyle XML report string into a list of CheckstyleWarning """
    root = ET.fromstring(report)

    report = []
    for file in root.findall('file'):
        f = file.attrib
        filename = os.path.basename(f['name'])
        f['errors'] = []
        for error in file.findall('error'):
            e = error.attrib
            # show only relative path to not expose the system checks run on
            e['filename'] = filename

            report.append(CheckstyleWarning(**e))
    return report
