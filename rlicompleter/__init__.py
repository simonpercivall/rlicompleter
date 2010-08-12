"""
rlicompleter is an extension to rlcompleter allowing completion
of import statements.

Importing rlicompleter binds its completion function to the
readline library. rlicompleter complete regular import
statements of packages and modules to any level as well as
from-import statements. For from-import statements the exact
behaviour of the completion function differs based on whether
the module to import from has already been imported into
the Python intepreter. If it has been imported (that is, has
an entry in sys.modules) the completion function completes
on data objects in the module as well as any sub-modules; if
it has not been imported the completion function completes
only on sub-modules.
"""
import __builtin__
import readline

import rlicompleter.completer
import rlicompleter.modulescanner
import rlicompleter.statfuncs


__all__ = ["completer", "modulescanner"]
__version__ = "3.1"
__date__ = "2004-07-23"
__author__ = "Simon Percivall"


#Set readline to complete with this completer.
if hasattr(__builtin__, "__IPYTHON__active"):
    # patch IPython's readline completer
    from IPython.completer import IPCompleter
    
    setattr(IPCompleter, "import_matches",
            rlicompleter.completer.Completer.__dict__["import_matches"])
    setattr(IPCompleter, "_import_matches",
            rlicompleter.completer.Completer.__dict__["_import_matches"])
    setattr(IPCompleter, "_from_matches",
            rlicompleter.completer.Completer.__dict__["_from_matches"])
    
    old_python_matches = IPCompleter.python_matches
    def python_matches(self, text):
        matches = self.import_matches(text)
        if matches:
            return matches
        else:
            return old_python_matches(self, text)
    IPCompleter.python_matches = python_matches
else:
    readline.set_completer(completer.Completer().complete)
