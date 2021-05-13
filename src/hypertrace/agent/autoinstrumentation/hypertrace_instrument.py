# Based upon the OTel autoinstrumentation feature
'''This module implements a CLI command that be used to
autoinstrument existing pythong programs that use supported
modules.'''
import argparse
from logging import getLogger
from os import environ, execl, getcwd
from os.path import abspath, dirname, pathsep
from shutil import which

logger = getLogger(__file__)

def parse_args():
    '''Parse CLI arguments.'''
    parser = argparse.ArgumentParser(
        description="""
        hypertrace-instrument automatically instruments a Python
        program and runs the program
        """
    )

    parser.add_argument("command", help="Your Python application.")

    parser.add_argument(
        "command_args",
        help="Arguments for your application.",
        nargs=argparse.REMAINDER,
    )

    return parser.parse_args()

def update_python_path() -> None:
    '''Retrieve existing PYTHONPATH'''
    python_path = environ.get("PYTHONPATH")

    # Split the paths
    if not python_path:
        python_path = []
    else:
        python_path = python_path.split(pathsep)

    # Get the current working directory
    cwd_path = getcwd()

    # If this directory is already in python_path, remove it.
    python_path = [path for path in python_path if path != cwd_path]

    # Add CWD to the front.
    python_path.insert(0, cwd_path)

    # What is the directory containing this python file?
    filedir_path = dirname(abspath(__file__))

    # If this directory is already in python_path, remove it.
    python_path = [path for path in python_path if path != filedir_path]

    # Add this directory to the front
    python_path.insert(0, filedir_path)

    # Reset PYTHONPATH environment variable
    environ["PYTHONPATH"] = pathsep.join(python_path)

def run() -> None:
    '''hypertrace-instrument Entry point'''
    args = parse_args()

    # update PYTHONPATH env var
    update_python_path()

    # Get full path to the command that was passed in as an
    # argument
    executable = which(args.command)

    # Execute the app
    execl(executable, executable, *args.command_args)

if __name__ == '__main__':
    run()
