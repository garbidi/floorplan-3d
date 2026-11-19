#!/bin/bash
# usage: queue.sh key1 key2 ... ; waits for any running batch_gen, then runs sequentially
cd /mnt/c/Projects/3d_visual
for k in "$@"; do
  while pgrep -f "batch_gen.py" >/dev/null; do sleep 20; done
  python3 tools/batch_gen.py $k 2 > tools/tmp/gen_$k.log 2>&1
  grep BEST tools/tmp/gen_$k.log >> tools/tmp/queue_results.log
done
