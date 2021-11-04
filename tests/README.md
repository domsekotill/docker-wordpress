Behaviour Testing
=================

These behaviour tests use "Behave", a Python framework.


Requirements
------------

### Docker (>=18.09)

Docker is required for running the project; a minimum version of 18.09 is required to build 
the images.

### Python (>=3.9)

The tests are coordinated and run by "behave", a Python testing framework.  In order to 
check the correctness of the test code it has been written with the latest typing features 
of Python.


Installing
----------

There are a small number of Python package dependencies listed in [requirements.txt]() which 
must be installed; it is recommended that they are installed in a [virtual 
environment][venv]:

```bash
env=venv  # You may choose any directory name here
python -m venv $env
$env/bin/python -m pip install -r tests/requirements.txt
```

### OPTIONAL: Make `behave` runnable without a full path

The virtual environment's *bin/* directory (*Scripts/* for Windows builds of Python) can be 
added to the executable search variable "PATH".  This will make `behave` and other installed 
tools runnable without having to supply a full path to the executable.  The 'venv' tool 
supplies handy scripts for this purpose.

All the following example in this document assume this has been done; if not simply replace 
`behave` with `$env/bin/behave` where `$env` expands to the virtual environment created 
above.

For Bash and Zsh use the following, for other shells see the [venv][] documentation:

```bash
source $env/bin/activate
```

[venv]:
  https://docs.python.org/3/library/venv.html
  "Documentation for 'venv'"


Usage
-----

From the top directory of the project or the *tests* subdirectory, Behave can be called with 
no arguments to run all scenarios:

```bash
behave
```

Behave can be run with path arguments in which case it can be run from any directory.  
Feature files (matching `*.feature`) may be specified to run their scenarios, or if the path 
is a directory the tree will be searched for feature files.

```bash
behave tests  # Run scenarios for all features
behave tests/regression-*.feature  # Run regression scenarios
```
