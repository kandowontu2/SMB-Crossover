"""Controller-only retry when a moving lift is missed; retain all clear checks."""
import argparse
from pathlib import Path
import subprocess
import sys
from prepare_selected_native_packet_v1 import prepare,sha

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--rom',type=Path,required=True)
ap.add_argument('--source',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
source=args.source.read_text()
old=' if row.departed then return end\n local slot = ram(0xc30b)-1'
new=''' if row.departed then return end
 -- A faster game can put the lift above the first boarding jump. Return to
 -- its edge and release A, then retry with ordinary controller inputs.
 if not row.boarded and x>left+26 and x<obstacle.left then
  return {left=true,b=true}
 end
 local slot = ram(0xc30b)-1'''
assert source.count(old)==1
source=source.replace(old,new)
old='''  if x>=left-23 and x<=left+26 then
   if floor then
    if top>=166 and s.held&128==0 then return {right=true,b=true,a=true} end'''
new='''  if x>=left-23 and x<=left+26 then
   -- Keep the initial press through the donor's queued jump entry, just as
   -- departure does; releasing during its windup can cancel boarding.
   if row.boarding_press and s.queued==12 then return {right=x<left+5,b=true,a=true} end
   if floor then
    if top>=166 and s.held&128==0 then row.boarding_press=true; return {right=true,b=true,a=true} end'''
assert source.count(old)==1
source=source.replace(old,new)
prepare(args.output,args.rom,source,{args.source,Path(__file__)},expected=sha(args.rom),
        timeout=180,allow_interactive=True,
        scope='Controller-only full 1-1 with missed-lift approach recovery. All original lives, jumps, three actual board/departures, and active1-2 assertions retained.')
subprocess.run([sys.executable,'-B',str(args.output/'run.py')],check=True)
