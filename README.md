# check50_java

This is an extension, a collection of utility scripts, for the [CS50 automarker check50][check50].

It provides convenient wrappers around [`check50.run`][run], for compiling and interpreting Java source/byte code.
It also comes with functions to execute and interpret the results of [Junit5][junit] unit tests.


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

2. Move `BasketTest.class` somewhere into your pset directory, say under `tests/`.
3. Add a check as follows (I would usually have this depend on class exists, compiles, and can be instantiated checks).
    ```python
    @check50.check()
    def drink_getVolume():
        """Test Drink.getVolume()"""
        check50_java.junit5.run_and_interpret_test(
            classpaths=['tests/'],
            args=['--select-method', 'DrinkTest#getVolume'])
    ```
  This will run the precompiled unit test on the student submission, parse junit's XML report and raise any `check50.Failure`s as appropriate for the result. In this case it would raise a `check50.Mismatch` exception if the `assertEquals` within the unit test is thrown.



[check50]: https://github.com/cs50/check50
[run]: https://cs50.readthedocs.io/projects/check50/en/latest/api/#check50.run
[Junit5]: https://junit.org/junit5
[jcl]: https://junit.org/junit5/docs/current/user-guide/#running-tests-console-launcher
