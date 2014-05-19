#!/usr/bin/env python2

import os
import sys

dir_of_executable = os.path.dirname(__file__)
path_to_project_root = os.path.abspath(os.path.join(dir_of_executable, '..'))

sys.path.insert(0, path_to_project_root)

from orapplet.main import main
main()
