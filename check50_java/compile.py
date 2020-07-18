import re
import check50
from check50._api import Failure
from check50._api import log
from check50_java import JAVAC, JAVA
from check50_java.util import _expand_classpaths


#: Default CFLAGS for :func:`check50.c.compile`
CFLAGS = {}  # {"std": "c11", "ggdb": True, "lm": True}
TIMEOUT = 10


def compile(*files, javac=JAVAC, classpaths=None, failhelp=None, **cflags):
    """
    Compile C source files.

    :param files: filenames to be compiled
    :param cc: compiler to use (:data:`check50.c.CC` by default)
    :param classpaths: list of paths (e.g. individual jars) to add to classpath
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

    process = check50._api.run(f"{javac} -classpath \"{classpath}\" {flags} {files}")

    # Strip out ANSI codes
    stdout = process.stdout(timeout=TIMEOUT)

    if process.exitcode != 0:
        for line in stdout.splitlines():
            log(line)
        raise Failure("code failed to compile", help=failhelp)


def run(mainclass, java=JAVA, classpaths=None, failhelp=None, args=None):
    """
    Call the java interpreter
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
    log(cmdline)

    # call subprocess and wait until it's done
    return check50._api.run(cmdline)
