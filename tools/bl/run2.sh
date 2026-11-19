#!/bin/bash
# usage: run2.sh script.py args...   (prints errors / RENDERED lines)
S=$1; shift
powershell.exe -NoProfile -Command "& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup --python 'C:\Projects\3d_visual\tools\bl\\$S' -- $* 2>&1 | Select-String -Pattern 'RENDERED|Error|Traceback|line [0-9]|Exception' | Select-Object -First 15"
