import check50


def is_application_class(classname):
    """
    Try to run the main method in the given class and raise an
    appropriate Failure if unsuccessful.
    """
    process = check50.run(f"java {classname} 2>&1")
    stdout = process.stdout()
    exitcode = process.exitcode
    emsg = f"Main method not found in class {classname}"
    if exitcode != 0 and emsg in stdout:
        help = "Make sure to define a main method as:\n" \
            "\tpublic static void main(String[] args)"
        raise check50.Failure(emsg + ".", help)
