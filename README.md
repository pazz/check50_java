# check50_java

This is an extension for the [CS50 automarker check50][check50] that provides convenient wrappers around [`check50.run`][run] for directly compiling and interpreting Java source/byte code.

See also [check50_junit](https://github.com/pazz/check50_junit) and [check50_checkstyle](https://github.com/pazz/check50_checkstyle) for related utilities that make writing check50 checks for java less painful.


## Example Usage

All examples below assume that you're importing `check50` and `check50_java`.

### Compile Java source code

```python
@check50.check()
def someclass_compiles():
    check50_java.compile("SomeClass.java"
        classpaths=['your/classpaths',
                    'relative/to/the',
                    'pset/directory.jar']
    )
```
The classpaths argument defaults to `None` ~ `'.'`.

### Check that a class is executable (has well-formed main method)

```python
@check50.check(someclass_compiles)
def someclass_main_exists():
    """SomeClass is application class"""
    check50_java.checks.is_application_class("SomeClass")
```

### Execute an application class and check that its output is as expected

```python
@check50.check(someclass_main_exists)
def someclass_main_output():
    """SomeClass.main() output"""
    expected = "X"
    actual = check50_java.run("SomeClass").stdout()
    help_msg = "did you introduce training newline or whitespace characters?"
    if actual != expected:
        raise check50.Mismatch(expected, actual, help=help_msg)
```


[check50]: https://github.com/cs50/check50
[run]: https://cs50.readthedocs.io/projects/check50/en/latest/api/#check50.run
