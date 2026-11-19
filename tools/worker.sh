#!/bin/bash
# single worker: takes keys from tools/tmp/queue.txt one by one (flock-protected, only one worker at a time)
cd /mnt/c/Projects/3d_visual
exec 9>tools/tmp/worker.lock
flock -n 9 || { echo "worker already running"; exit 0; }
while pgrep -f "batch_gen.py" >/dev/null; do sleep 15; done
while true; do
  k=$(head -n1 tools/tmp/queue.txt 2>/dev/null)
  [ -z "$k" ] && break
  sed -i '1d' tools/tmp/queue.txt
  python3 tools/batch_gen.py $k 2 > tools/tmp/gen_$k.log 2>&1
  grep BEST tools/tmp/gen_$k.log >> tools/tmp/queue_results.log
done
echo "QUEUE EMPTY $(date +%H:%M)" >> tools/tmp/queue_results.log
