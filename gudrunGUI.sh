#!/bin/sh

SMT4GUDRUN_ROOT="$(dirname $0)"
GUDRUN_ROOT="/opt/Gudrun4"
DATADIR="$(pwd)"

## GudrunGUI.sysparN always needs to be in the current directory, 
## even if $DATADIR is different, because GudrunGUI will look for 
## it in the current directory
cat - > GudrunGUI.sysparN <<END
${SMT4GUDRUN_ROOT}/gudrun_dcs.py;
${SMT4GUDRUN_ROOT}/purge_det.py;
${GUDRUN_ROOT}/rungnuplot.sh;
${GUDRUN_ROOT}/rungnuplotplot.sh;
${DATADIR}/GEMstartup.txt;
;
END

java -Duser.language=en -classpath "${GUDRUN_ROOT}/GudrunGUI" -jar "${GUDRUN_ROOT}/GudrunGUI/GudrunGUI_4.jar" N
