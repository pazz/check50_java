# Copyright (C) 2020  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

JAVAC = "javac"
JAVA = "java"

from . compile import compile, run
from . junit5 import compile_test
from . checks import is_application_class
