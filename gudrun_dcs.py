#!/usr/bin/python2

"""gudrun_dcs.py - run gudrun_dcs under Sumatra

* Reads in parameters from gudrun_dcs.dat
* Tells Sumatra what the input files are and where the output files will be
* Runs gudrun_dcs
* Tags the resulting Sumatra record with the sample(s) and container(s) used

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

from gudrunParameters import GudrunParameterSet
    

print "Loading parameters from gudrun_dcs.dat..."
parameters = GudrunParameterSet('gudrun_dcs.dat')

output_dir = parameters.get_param(0, 1, 'INSTRUMENT', 'Gudrun input file directory')
rawdata_dir = parameters.get_param(0, 2, 'INSTRUMENT', 'Data file directory')
calib_file = parameters.get_param(0, 4, 'INSTRUMENT', 'Detector calibration file name')
groups_file = parameters.get_param(0, 6, 'INSTRUMENT', 'Groups file name')
deadtime_file = parameters.get_param(0, 7, 'INSTRUMENT', 'Deadtime constants file name')
if deadtime_file == '*':
    deadtime_file = os.path.join(output_dir, 'deadtime.cor')
scattering_params_file = parameters.get_param(0, 25, 'INSTRUMENT', 'Neutron scattering parameters file')
start_dir = parameters.get_param(0, 28, 'INSTRUMENT', 'Folder where Gudrun started')
startup_file_dir = parameters.get_param(0, 29, 'INSTRUMENT', 'Folder containing the startup file')
beam_params_file = parameters.get_param(1, 7, 'BEAM', 'Filename containing incident beam spectrum parameters')

output_dir = os.path.abspath(output_dir)
if os.getcwd() != output_dir:
    raise RuntimeError("""gudrun_dcs not started from 'Gudrun input file directory'...
        Exiting in case Sumatra gets confused""")

print "Truncating gudrun_dcs.dat at the END marker..."
with open('gudrun_dcs.dat', 'r+') as fid:
    fid.truncate(parameters.end)

subprocess.check_call(['git', 'add', 'gudrun_dcs.dat'])
if subprocess.call(['git', 'diff', '--staged', '--quiet', 'gudrun_dcs.dat']):
    print "Committing gudrun_dcs.dat to git..."
    subprocess.check_call(['git', 'reset'])
    subprocess.check_call(['git', 'add', 'gudrun_dcs.dat'])
    subprocess.check_call(['git', 'commit', '-m', 'Autocommit of gudrun_dcs.dat by smt_gudrun_dcs.py'])

input_files = [calib_file, groups_file,
               deadtime_file, scattering_params_file, beam_params_file]

input_files.extend([os.path.join(rawdata_dir, data_file) for data_file in parameters.get_data_files()])

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
gudrun_dcs = sumatra.programs.Executable(path='/opt/Gudrun4/bin/gudrun_dcs', name='gudrun_dcs',
                                        version=4, options='')
print "Creating 'launch_mode' object..."
serial_mode = launch.SerialLaunchMode(working_directory=output_dir)

print "Launching gudrun_dcs..."
run_label = project.launch(parameters, input_keys, script_args="",
                           executable=gudrun_dcs, main_file='gudrun_dcs.dat',
                           launch_mode=serial_mode)

print "Tagging with subdir"
project.add_tag(run_label, subdir)

print "Tagging with sample and container"
for name, parsed_lines, line_dict in parameters.sections_or_go:
    if name.startswith('SAMPLE ') and (name != 'SAMPLE BACKGROUND'):
        project.add_tag(run_label, name)
    elif name.startswith('CONTAINER '):
        project.add_tag(run_label, name)
