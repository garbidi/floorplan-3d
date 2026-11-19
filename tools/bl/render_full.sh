#!/bin/bash
# usage: render_full.sh script.py out.png samples  -> renders 4 bands (borders) at 100% and stitches
S=$1; OUT=$2; N=$3
for i in 0 1 2 3; do
  y0=$(python3 -c "print(1-($i+1)/4)"); y1=$(python3 -c "print(1-$i/4)")
  powershell.exe -NoProfile -Command "\$env:BLPCT='100'; \$env:BLBORDER='0,1,$y0,$y1'; & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup --python 'C:\Projects\3d_visual\tools\bl\\$S' -- 'C:/Projects/3d_visual/tools/tmp/band$i.png' $N 2>&1 | Select-String -Pattern 'RENDERED|Error   ' | Select-Object -First 3"
done
python3 - "$OUT" <<'P'
import sys; from PIL import Image
ims=[Image.open(f'/mnt/c/Projects/3d_visual/tools/tmp/band{i}.png').convert('RGBA') for i in range(4)]
W=ims[0].width; H=sum(i.height for i in ims); c=Image.new('RGBA',(W,H)); y=0
for i in ims: c.paste(i,(0,y)); y+=i.height
c.save('/mnt/c/Projects/3d_visual/'+sys.argv[1]); print('stitched',c.size)
P
