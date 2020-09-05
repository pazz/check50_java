# Copyright (C) 2020  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

import check50

#TODO: This is buggy and reports false positives!
def is_application_class(classname):
    """
    Try to run the main method in the given class and raise an
    appropriate Failure if unsuccessful.

    :param classname: name of class to check
    :type classname: str
    """
    process = check50.run(f"java {classname} 2>&1")
    stdout = process.stdout()
    exitcode = process.exitcode
    emsg = f"Main method not found in class {classname}"
    if exitcode != 0 and emsg in stdout:
        helpmsg = "Make sure to define a main method as:\n" \
            "\tpublic static void main(String[] args)"
        raise check50.Failure(emsg + ".", help=helpmsg)
