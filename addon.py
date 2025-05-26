"""
Module bootstrap.

This is used to bootstrap the module.  Otherwise relative imports would yield
the error: attempted relative import with no known parent package
"""

import os
import sys
import importlib

base = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(base, "resources", "lib"))

if __name__ == "__main__":
    pkg = importlib.import_module("metadata_myanimelist_tv")
    pkg.plugin_main()
