smt4Gudrun
==========

Helper scripts for using Sumatra with Gudrun GUI

Why this project is helpful
---------------------------

[Sumatra](http://neuralensemble.org/sumatra/) is "a tool for managing and tracking projects based on numerical simulation or analysis, with the aim of supporting reproducible research".
[Gudrun](http://disordmat.moonfruit.com/) is "a data analysis package that allows the user to go from the raw scattering data obtained in neutron and x-ray scattering experiments to Differential Scattering Cross Section (DCS) and then to Pair Distribution Function (PDF)".

Running Gudrun directly with `smt run` does not work, and in any case when using the GUI it is impossible to set the command line.
smt4Gudrun contains helper scripts to set up the environment to make GudrunGUI run all its purge\_det and gudrun\_dcs runs under Sumatra.

How to use
----------

1. Make sure Gudrun is installed in /opt/Gudrun4, or alternatively edit the /path/to/smt4Gudrun/gudrunGUI.sh script.
2. Create a Sumatra repository in an empty directory with `git init` and `smt init`.
3. Run `sh /path/to/smt4Gudrun/gudrunGUI.sh` from within the Sumatra repository. Use the Gudrun GUI as you would normally.
4. Use `smt web` or the Sumatra command line tools to compare your results.

