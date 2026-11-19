#!/bin/bash
O=$1; shift
powershell.exe -NoProfile -Command "\$env:NOHANGER='$NOHANGER'; \$env:GROT='$GROT'; & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup --python 'C:\Projects\3d_visual\tools\bl\gar_view.py' -- C:/Projects/3d_visual/tools/tmp/$O.png $* 2>&1 | Select-String 'RENDERED|Error   |Error:|line [0-9]|Traceback'"
