# Copyright (C) 2020  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

import os
import check50


def _full_path(path):
    """turns `path` into an absolute path by prepending check_dir"""
    if not os.path.isabs(path):
        path = os.path.join(check50.internal.check_dir, path)
    return path


def _expand_classpaths(classpaths=None):
    """
    prepare list of strings for interpretation as java classpath.

    This is guaranteed to return a list of absolute paths to directories/jars
    to be included in the java classpath for compilation/interpretation.
    """
    if classpaths is None:
        classpaths = []
    else:
        classpaths = [_full_path(path) for path in classpaths]
    return classpaths
