# check50_java

This is an extension, a collection of utility scripts, for the [CS50 automarker check50][check50].

It provides convenient wrappers around [`check50.run`][run], for compiling and interpreting Java source/byte code.
It also comes with functions to execute and interpret the results of [Junit5][junit] unit tests
and [checkstyle][checkstyle] warnings.


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

### Turning Junit tests into check50 checks

This module ships with [Junit5's stand-alone console launcher][jcl], which can be used to compile and run unit checks. What seems to work quite well is to add compiled java bytecode for junit test classes to the pset,
and run them during checks. The resulting XML report file will reflect things like undefined classes or when method signatures in student code are incompatible with the model solution against which the unit tests were compiled.
A full example follows.

1. Write your model solution and unit test classes and manually compile them.

    ```java
    public class Drink {
        private final int volume;

        public Drink(int v) {
            volume = v;
        }

        int getVolume() {
            return volume;
        }
    ```

    ```java
    import static org.junit.jupiter.api.Assertions.*;
    import org.junit.jupiter.api.Test;

    class DrinkTest {
      @Test
      public void getVolume() {
        Drink d = new Drink(200);
        assertEquals(200, d.getVolume());
      }
    }
    ```

2.  Move `BasketTest.class` somewhere into your pset directory, say under `tests/`.
3.  Add a check as follows (I would usually have this depend on class exists, compiles, and can be instantiated checks).
    ```python
    @check50.check()
    def drink_getVolume():
        """Test Drink.getVolume()"""
        check50_java.junit5.run_and_interpret_test(
            classpaths=['tests/'],
            args=['--select-method', 'DrinkTest#getVolume'])
    ```
    This will run the precompiled unit test on the student submission, parse junit's XML report and raise any `check50.Failure`s as appropriate for the result. In this case it would raise a `check50.Mismatch` exception if the `assertEquals` within the unit test is thrown.

4. Make sure to add `check50-java` as a dependency in your pset's `.cs50.yml`:
    ```yml
    check50:
      dependencies:
        - check50-java
      files:
        - !exclude "*"
        - !include "*.java"
    ```

### Raising checkstyle warnings

Checkstyle let's you complain about style issues in java code beyond what [style50][style50] (astyle) can do.
For instance you can flag if identifiers don't adhere to Java's camelCase code conventions, or javadocs are missing.

Since the checkstyle stand-alone CLI application is too large (~12M), we ship only wrapper code that can call, and interpret its XML reports.

To use this, you need to add two things to your pset
1. a stand-alone jar file, e.g. `checkstyle-8.35-all.jar` available [here](https://github.com/checkstyle/checkstyle/releases/)
2. an xml file with checks to include (You can pick the sub or google style files in the jar and delete what you don't like).

Let's assume you have these two files under `checkstyle/` in your pset.
Then you add a check50 check as follows. The target can be more specific of course.

```python
@check50.check(exists)
def checkstyle():
    """style police"""
    check50.include("checkstyle/")
    check50_java.checkstyle.run_and_interpret_checkstyle(
        jar='checkstyle/checkstyle-8.35-all.jar',
        checks_file='checkstyle/checks.xml',
        target='*.java')
```

This will dump all warnings into the log (because check50 hard-codes its html template).
Example output:

```
:( style police
    stylistic issues found
    running java -jar checkstyle/checkstyle-8.35-all.jar -c checkstyle/checks.xml -f xml *.java...
    Issues found:
    - In Basket.java(line 2, char 1): Wrong lexicographical order for 'java.util.ArrayList' import. Should be before 'java.util.List'.
    - In Basket.java(line 19, char 5): Missing a Javadoc comment.
    - In Basket.java(line 27, char 5): Missing a Javadoc comment.
    - In Basket.java(line 35, char 5): Missing a Javadoc comment.
    - In Basket.java(line 47): First sentence of Javadoc is missing an ending period.
    - In Item.java(line 27): Line is longer than 100 characters (found 102).
    - In Item.java(line 53, char 40): 'typecast' is not followed by whitespace.
    - In Snack.java(line 20, char 5): Missing a Javadoc comment.
```



[checkstyle]: https://checkstyle.sourceforge.io/
[check50]: https://github.com/cs50/check50
[run]: https://cs50.readthedocs.io/projects/check50/en/latest/api/#check50.run
[junit]: https://junit.org/junit5
[jcl]: https://junit.org/junit5/docs/current/user-guide/#running-tests-console-launcher
[style50]: https://cs50.readthedocs.io/style50/
