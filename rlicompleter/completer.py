import sys
import re
import readline
import keyword

import __main__
import __builtin__

from rlicompleter import modulescanner


__all__ = ["Completer"]


class StopMatching(Exception):
    pass

class Completer(object):
    """Completer mainly defines a completion function for
    completing global names, attribute names and import statements.
    
    Completer instances should be used as the completion mechanism
    of readline via the set_completer function:
    
    readline.set_completer(Completer(namespace).complete)
    """

    def __init__(self, namespace=None):
        """__init__(namespace:dict) : None
        
        Create a Completer instance. If the optional namespace
        parameter is given: bind to that namespace as the global
        namespace to complete on; else bind __main__.__dict__.
        """
        if namespace and not isinstance(namespace, dict):
            raise TypeError("namespace must be a dictionary")
        
        # Don't bind to namespace quite yet, but flag whether the user wants a
        # specific namespace or to use __main__.__dict__. This will allow us
        # to bind to __main__.__dict__ at completion time, not now.
        if namespace is None:
            self.use_main_ns = True
        else:
            self.use_main_ns = False
            self.namespace = namespace
        
        self.matchers = [self.import_matches,
                         self.attr_matches,
                         self.global_matches]

    def complete(self, text, state):
        """complete(text:str, state:int) : list
        
        Return the next possible completion for 'text'.

        This is called successively with state == 0, 1, 2, ... until it
        returns None.  The completion should begin with 'text'.

        """
        if self.use_main_ns:
            self.namespace = __main__.__dict__
        line = readline.get_line_buffer()

        try:
            if state == 0:
                for matcher in self.matchers:
                    self.matches = sorted(matcher(text))
                    if self.matches:
                        break
        except StopMatching:
            self.matches = []

        try:
            return self.matches[state]
        except IndexError:
            return None
    
    def global_matches(self, text):
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in functions and names currently
        defined in self.namespace that match.
        """
        matches = []
        n = len(text)
        for list in [keyword.kwlist,
                     __builtin__.__dict__,
                     self.namespace]:
            for word in list:
                if word[:n] == text:
                    matches.append(word)
        return matches

    def attr_matches(self, text):
        """Compute matches when text contains a dot.

        Assuming the text is of the form NAME.NAME....[NAME], and is
        evaluatable in self.namespace, it will be evaluated and its attributes
        (as revealed by dir()) are used as possible completions.  (For class
        instances, class members are also considered.)

        WARNING: this can still invoke arbitrary C code, if an object
        with a __getattr__ hook is evaluated.

        """
        m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
        if not m:
            return []
        expr, attr = m.group(1, 3)
        object = eval(expr, self.namespace)
        words = dir(object)
        if hasattr(object,'__class__'):
            words.append('__class__')
            words = words + get_class_members(object.__class__)
        matches = []
        n = len(attr)
        for word in words:
            if word[:n] == attr:
                matches.append("%s.%s" % (expr, word))
        return matches
    
    def import_matches(self, text):
        line = readline.get_line_buffer()
        
        return self._import_matches(line, text)

    def _import_matches(self, line, text):
        """import_matches(line:str, text:str) : list
        
        Returns a list of possible completions for an
        import statement and a partially spelled-out
        package/module name.
        
        Raises StopMatching when we know we're in the correct
        matcher, but there are no matches.
        """
        basic_match = re.compile(r"\s*(from|import)\b")
        import_stmt = re.compile(r"\s*(from|import)\s+([\w_\.]+)?$")
        from_stmt = re.compile(r"\s*from [\w_\.]+ ([\w_\.]*)$")
        
        if not basic_match.match(line):
            return []
        
        import_match = import_stmt.search(line)
        if import_match:
            match = re.search(r"from ([\w_.]+) import", line)
            if match:
                if '.' in text:
                    raise StopMatching()
                
                matches = self._from_matches(match.group(1), text)
                if not matches:
                    raise StopMatching()
                else:
                    return matches
            if '.' in text:
                matches = modulescanner.subpackages(text)
                if not matches:
                    raise StopMatching()
                else:
                    return matches
        
            matches = modulescanner.get_completions(text)
            if not matches:
                raise StopMatching()
            else:
                return matches
        
        from_match = from_stmt.match(line)
        if from_match:
            if text != "" and not "import".startswith(text):
                raise StopMatching()
            else:
                return ["import"]
        
        raise StopMatching()
    
    def _from_matches(self, module, text):
        """from_matches(module:str, text:str) : list
        
        Create a list of completions for 'text' in the namespace
        of 'module'. If 'module' is imported: complete on
        attributes and possible sub-modules; else complete only
        sub-modules.
        """
        
        fullname = ".".join([module, text])
        completions = []
        
        subpkgs = modulescanner.subpackages(fullname)
        
        if not self.use_main_ns:
            temp_ns = self.namespace
        self.namespace = sys.modules
        
        try:
            subobjs = self.attr_matches(fullname)
        except NameError:
            subobjs = None
        
        if not self.use_main_ns:
            self.namespace = temp_ns
        
        
        if subpkgs:
            completions.extend([pkg.split('.')[-1] for pkg in subpkgs])
        if subobjs:
            completions.extend([obj.split('.')[-1] for obj in subobjs])
        
        return completions


# Python < 2.4 hasn't got the sorted function
try:
    sorted
except NameError:
    def sorted(seq):
        """sorted(seq:iterable) : list
        
        Sorts a copy of the given sequence. Leaves the original alone.
        """
        copy = list(seq)
        copy.sort()
        
        return copy

def get_class_members(klass):
    ret = dir(klass)
    if hasattr(klass,'__bases__'):
        for base in klass.__bases__:
            ret = ret + get_class_members(base)
    return ret
