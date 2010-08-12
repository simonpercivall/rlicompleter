#include <Python.h>
#include <sys/stat.h>

/* These functions are five times faster than their os.path
   equivalents. Read the module documentation for approximate
   timings. */

static PyObject *
statfuncs_isdir(PyObject *self, PyObject *args)
{
	char *path;
	struct stat statbuf;
	
	if (!PyArg_ParseTuple(args, "s", &path))
		return NULL;
	
	if (stat(path, &statbuf) == -1)
		return Py_INCREF(Py_False), Py_False;
	else
		return PyBool_FromLong(S_ISDIR(statbuf.st_mode));
}

PyDoc_STRVAR(isdir_doc,
"isdir(path:str) : bool\n\
\n\
Returns True if 'path' is a directory, otherwise False.");

static PyObject *
statfuncs_isfile(PyObject *self, PyObject *args)
{
	char *path;
	struct stat statbuf;
	
	if (!PyArg_ParseTuple(args, "s", &path))
		return NULL;
	
	if (stat(path, &statbuf) == -1)
		return Py_INCREF(Py_False), Py_False;
	else
		return PyBool_FromLong(S_ISREG(statbuf.st_mode));
}

PyDoc_STRVAR(isfile_doc,
"isdir(path:str) : bool\n\
\n\
Returns True if 'path' is a regular file, otherwise False.");

static PyMethodDef SpeedFuncsMethods[] = {
	{"isdir", statfuncs_isdir, METH_VARARGS, isdir_doc},
	{"isfile", statfuncs_isfile, METH_VARARGS, isfile_doc},
	{NULL, NULL, 0, NULL} /* Sentinel */
};

PyDoc_STRVAR(statfuncs_doc,
"This module provides functions for checking what type of file a\n\
path represents. The functions exported can check if a path\n\
represents a regular file or if it represents a directory.\n\
\n\
The functions provided by this module are each five times faster\n\
than the equivalent Python functions in the os.path module. This\n\
means a speedup of about 0.2 seconds per 1000 files.");

PyMODINIT_FUNC
initstatfuncs(void)
{
	(void)Py_InitModule3("statfuncs", SpeedFuncsMethods, statfuncs_doc);
}
