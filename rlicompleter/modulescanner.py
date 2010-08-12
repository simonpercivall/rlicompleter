import sys
import os
import zipimport

try:
    set
except NameError:
    from sets import Set as set

from os import path
from rlicompleter.statfuncs import isdir

__all__ = ["get_completions", "subpackages"]

roots = set()
completions = set(sys.builtin_module_names)
packages = {}
zipmodules = {}

is_registered = False

def entry_listener(dist):
    """entry_listener(dist:pkg_resources.Distribution)
    """
    distpath = dist.location
    
    if isdir(distpath):
        roots.add((distpath, ""))
        completions.update(submodules(distpath, ""))

def register_entry_listener():
    global is_registered
    
    if not is_registered:
        import pkg_resources
        pkg_resources.add_activation_listener(entry_listener)
        is_registered = True

def add_zipped_module(path):
    pass

def get_completions(beginning):
    register_entry_listener()
    return [mod for mod in completions if mod.startswith(beginning)]

def subpackages(text):
    """subpackaes(text:str) : list

    Returns a list of possible completions for a
    hierarchy of packages and a partially spelled-out
    sub-package.
    """
    register_entry_listener()
    
    parts = text.split('.')
    
    # find the longest .-path that's already scanned
    for i in range(len(parts), 0, -1):
        basepack = ".".join(parts[:i])
        if basepack in packages:
            basepath = packages[basepack]
            break
    # and if we can't find even the top-module in packages, it's not real
    else:
        return []
    
    # now join all except the last, and check it's a real path
    basepath = reduce(path.join, [basepath] + parts[i:-1])
    if not isdir(basepath):
        return []

    basename = '.'.join(parts[:-1])
    completions = submodules(basepath, basename)
    return ['.'.join([basename, mod]) for mod in completions
                if mod.startswith(parts[-1])]

def submodules(dir, package):
    """submodules(dir:str, package:str) -> list[str]
    
    submodules() creates a list of strings, where 'package' is
    joined by a '.' with each module in 'dir'. 'package' can be
    an empty string.
    
    submodules() also updates the module-global dict 'packages'
    where each registered package refers to its filesystem path.
    """
    from rlicompleter.statfuncs import isfile
    

    _completions = []
    
    for fname in os.listdir(dir):
        # if it's reasonably certain that the file is a python
        # module, add it to the completions list
        if fname[-3:] in (".py", ".so"):
            if fname == "__init__.py":
                continue
            _completions.append(fname[:-3])
            continue
        if '.' in fname:
            continue
        
        # if we've got a directory, and it represents a package,
        # add it to the packages dict and to the completions list
        path = dir + '/' + fname
        if isfile(path+"/__init__.py"):
            if package:
                packages[package + "." + fname] = path
            # if this package name is already in the completions
            # list, that module will shadow this when
            # actually importing, so don't include this one
            elif fname not in completions:
                packages[fname] = path
            
            _completions.append(fname)
    return _completions

def update_top_level(seq):
    for path in seq:
        path = path or '.'
        if isdir(path):
            roots.add((path, ""))
            completions.update(submodules(path, ""))
        elif path in zipimport._zip_directory_cache:
            add_zipped_module(path)

# initialize the module. this should take only a tenth of a second.
update_top_level(sys.path)

# special-case _xmlcore
if "xmlcore" in packages:
    packages["xml"] = packages["xmlcore"]
