"""Fixed-point unit vectors for the pinned 2.02 atan2/cos/sin steering."""
from pathlib import Path
import math

ROOT=Path(__file__).resolve().parents[2]
major=[round(256/math.hypot(1,i/256)) for i in range(256)]
minor=[round(i/math.hypot(1,i/256)) for i in range(256)]
# Zero represents an exact unit coefficient only for the major component.
major=[v%256 for v in major]
lines=['; Q0.8 cos/sin of atan(min/max); zero major at ratio0 means256.']
for name,values in [('Major',major),('Minor',minor)]:
 lines += [name+':']
 for i in range(0,256,16):lines += [' .byte '+','.join(map(str,values[i:i+16]))]
(ROOT/'src/sophia_vectors.inc').write_text('\n'.join(lines)+'\n')
