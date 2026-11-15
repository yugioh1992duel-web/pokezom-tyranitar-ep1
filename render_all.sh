#!/bin/bash
# Detach from the launching shell so the first hyperframes child is not
# killed when the launcher session exits (render_cancelled_parent_exited).
if [ "$(ps -o sid= -p $$ | tr -d ' ')" != "$$" ]; then
  exec setsid "$(readlink -f "$0")" "$@"
fi
export TMPDIR=/home/hatch/workspace/.tmp_hf
# Segmented capture: each run banks finished segments so a VM kill only
# costs the in-flight segment, not the whole section.
export HF_SEGMENTED_CAPTURE=true
cd ~/workspace/pokezom_tyranitar_build/segments
valid() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1" 2>/dev/null | grep -qE '^[0-9.]+$'; }
# Any valid render counts (old corrupt partials must not shadow a good one).
has_valid() { local f; for f in $1/renders/*/video-only.mp4; do [ -f "$f" ] && valid "$f" && return 0; done; return 1; }
for s in s0 s1 s2 s3 s4 s5 s6 s7 s8; do
  if has_valid "$s"; then echo "$(date +%H:%M:%S) $s already rendered, skip"; continue; fi
  echo "$(date +%H:%M:%S) rendering $s ..."
  (cd $s && npx --yes hyperframes@0.8.217 render --resume > render.log 2>&1)
  if has_valid "$s"; then echo "$(date +%H:%M:%S) $s DONE"; else echo "$(date +%H:%M:%S) $s FAILED (see render.log)"; fi
done
echo "$(date +%H:%M:%S) ALL SEGMENTS PROCESSED"
