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

def run() -> None:
    '''hypertrace-instrument Entry point'''
    args = parse_args()

    python_path = environ.get("PYTHONPATH")

    if not python_path:
        python_path = []

    else:
        python_path = python_path.split(pathsep)

    cwd_path = getcwd()

    if cwd_path not in python_path:
        python_path.insert(0, cwd_path)

    filedir_path = dirname(abspath(__file__))

    python_path = [path for path in python_path if path != filedir_path]

    python_path.insert(0, filedir_path)
    environ["PYTHONPATH"] = pathsep.join(python_path)

    executable = which(args.command)
    execl(executable, executable, *args.command_args)

run()
