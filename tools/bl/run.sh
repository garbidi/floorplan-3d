#!/bin/bash
# usage: run.sh script.py out.png samples pct
powershell.exe -NoProfile -Command "\$env:BLPCT='$4'; & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup --python 'C:\Projects\3d_visual\tools\bl\\$1' -- 'C:/Projects/3d_visual/$2' $3 2>&1 | Select-String -Pattern 'RENDERED|Error|Traceback|line ' | Select-Object -First 12"
