# Copyright (C) 2020  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

import check50
from check50._api import Failure
from check50._api import log
from check50_java import JAVAC, JAVA
from check50_java.util import _expand_classpaths


#: Default CFLAGS for :func:`check50_java.compile`
CFLAGS = {}


def compile(*files, javac=JAVAC, classpaths=None, failhelp=None,
            timeout=10, **cflags):
    """
    Compile Java source files.

    :param files: filenames to be compiled
    :param cc: compiler to use (:data:`check50_java.JAVAC` by default)
    :param classpaths: list of paths that together will form the classpath
                       parameter for the underlying `java` command.
                       Each element is a string containing a path to a
                       directory or jar file. relative paths are interpreted
                       relative to the problem set.
    :type classpaths: list(str)
    :param failhelp: help string used in Failure if unsuccessful
    :param timeout: number of seconds after which to time out and fail
    :param cflags: additional flags to pass to the compiler
    :raises check50.Failure: if compilation failed (i.e., if the compiler
            returns a non-zero exit status).
    :raises RuntimeError: if no filenames are specified

    Additional CFLAGS may be passed as keyword arguments just as for
    `check50.c.compile`
    """
    files = " ".join(files)

    # assemble CLASSPATH
    classpaths = ['.'] + _expand_classpaths(classpaths)
    classpath = ":".join(classpaths)

    flags = CFLAGS.copy()
    flags.update(cflags)
    flags = " ".join((f"-{flag}" +
                      (f"={value}" if value is not True else "")).replace(
                          "_", "-") for flag, value in flags.items() if value)

    cmdline = f"{javac} -classpath \"{classpath}\" {flags} {files}"
    process = check50._api.run(cmdline)
    stdout = process.stdout(timeout=timeout)

    if process.exitcode != 0:
        for line in stdout.splitlines():
            log(line)
        raise Failure("code failed to compile", help=failhelp)


def run(mainclass, java=JAVA, classpaths=None, failhelp=None, args=None):
    """
    Call the java interpreter.

    :param mainclass: name of application class to interpret
    :param java: interpreter to use (:data:`check50_java.JAVA` by default)
    :param classpaths: list of paths that together will form the classpath
                       parameter for the underlying `java` command.
                       Each element is a string containing a path to a
                       directory or jar file. relative paths are interpreted
                       relative to the problem set.
    :type classpaths: list(str)
    :param failhelp: help string used in Failure if unsuccessful
    :param args: additional commandline arguments (list of str)
                 to pass to the intepreter
    """

    # prepare classpath parameter
    classpaths = ['.'] + _expand_classpaths(classpaths)
    classpath = ";".join(classpaths)

    # command line arguments
    args = args or []

    # prepare command line string
    cmd = [
        java,
        '-cp', '"' + classpath + '"',
        mainclass
    ] + args
    cmdline = " ".join(cmd)

    # call subprocess
    return check50._api.run(cmdline)
