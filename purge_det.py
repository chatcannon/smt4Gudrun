#!/usr/bin/python2

"""purge_det.py - run purge_det under Sumatra

* Reads in parameters from purge_det.dat
* Tells Sumatra what the input files are and where the output files will be
* Runs purge_det

Copyright (C) 2013 Christopher Kerr
This file is free software, you may use it under the terms of the GNU General
Public License (GPL) version 3 or, at your option, any later version.
"""

import sys
import os
import os.path
import subprocess

import sumatra
from sumatra import projects, launch

from gudrunParameters import PurgeDetParameterSet
    

print "Loading parameters from purge_det.dat..."
parameters = PurgeDetParameterSet('purge_det.dat')

output_dir = parameters.get_param(1, 'Gudrun input file directory')
rawdata_dir = parameters.get_param(2, 'Data file directory')
calib_file = parameters.get_param(3, 'Detector calibration file name')
groups_file = parameters.get_param(4, 'Groups file name')

output_dir = os.path.abspath(output_dir)
if os.getcwd() != output_dir:
    raise RuntimeError("""purge_det not started from 'Gudrun input file directory'...
        Exiting in case Sumatra gets confused""")

input_files = [#os.path.abspath('purge_det.dat'), 
               calib_file, groups_file]

subprocess.check_call(['git', 'add', 'purge_det.dat'])
if subprocess.call(['git', 'diff', '--staged', '--quiet', 'purge_det.dat']):
    print "Committing purge_det.dat to git..."
    subprocess.check_call(['git', 'reset'])
    subprocess.check_call(['git', 'add', 'purge_det.dat'])
    subprocess.check_call(['git', 'commit', '-m', 'Autocommit of purge_det.dat by smt_purge_det.py'])

for data, comment in parameters.parsed_lines[10:]:
    basename, one = data.split()
    input_files.append(os.path.join(rawdata_dir, basename))

print "Loading project..."
project = projects.load_project()
project.data_store.root = output_dir

subdir = os.path.relpath(output_dir, project.path)

print "Generating input keys..."
common_prefix = os.path.commonprefix(input_files)
if not common_prefix.endswith(os.sep):
    common_prefix = os.path.dirname(common_prefix)
project.input_datastore.path = common_prefix
input_keys = project.input_datastore.generate_keys(*input_files)

print "Creating 'executable' object..."
# Need to pass a version otherwise it will run the program with --version to get the version...
purge_det = sumatra.programs.Executable(path='/opt/Gudrun4/bin/purge_det', name='purge_det',
                                        version=4, options='')
print "Creating 'launch_mode' object..."
serial_mode = launch.SerialLaunchMode(working_directory=output_dir)

print "Launching purge_det..."
run_label = project.launch(parameters, input_keys, script_args="",
                           executable=purge_det, main_file='purge_det.dat',
                           launch_mode=serial_mode)

print "Tagging with subdir"
project.add_tag(run_label, subdir)