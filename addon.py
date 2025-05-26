"""
Module bootstrap.

This is used to bootstrap the module.  Otherwise relative imports would yield
the error: attempted relative import with no known parent package
"""

from metadata_myanimelist_tv import plugin_main

if __name__ == "__main__":
    plugin_main()
