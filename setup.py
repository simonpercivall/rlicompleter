import sys
from distutils.core import setup
from distutils.extension import Extension
from distutils.command.build_ext import build_ext


exts = [Extension("rlicompleter.statfuncs",
                  ["rlicompleter/statfuncsmodule.c"])]

setup(name="rlicompleter",
      version="3.1",
      author="Simon Percivall",
      
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: C',
        'Topic :: Software Development :: Interpreters',
      ],
      
      packages=["rlicompleter"],
      ext_modules=exts,
      cmdclass={'build_ext': build_ext}
)

if "install" in sys.argv:
    print (
"""
\033[1mUsage Notes\033[0m
To use this module for completing the command line in the interactive
Python interpreter, add:

    import rlicompleter

to your .pythonrc file.

When you start the Python interpreter all modules in sys.path will be
catalogued. This should take less than 0.2 seconds and you shouldn't
even notice the slight delay as you start the Python interpreter.""")
