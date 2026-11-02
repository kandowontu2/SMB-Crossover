"""Bounded native checks of the composed nightly successor."""
import argparse
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--route',action='store_true');a=ap.parse_args()
 ref=R/('build/shinobi-crouch-route-1101-v23/native/controller.lua' if a.route else 'build/shinobi-rotation-trace-1101-v25/native/controller.lua')
 t=ref.read_text()
 # Preserve the existing physical-frame observation and require alignment at
 # every write, rather than accepting a screenshot alone as sprite integrity.
 if a.route:
  t=t.replace('local starts={410,560,688,864}','local starts={410,560,692,868}')
 else:
  t=t.replace("if name=='CurrentOAMOffset' and v%4==0 then return end", "assert(v%4==0,'OAM count/rotation must remain a multiple of four: '..name..' '..v);if name=='CurrentOAMOffset' then return end")
  assert "assert(v%4==0" in t
 a.output.parent.mkdir(exist_ok=True)
 prepare(a.output,a.rom,t,[Path(__file__),ref],expected=sha(a.rom),timeout=150 if a.route else 90,scope='Combined candidate real cold Shinobi selection and '+('opening Goomba/four pipes; source-proven tallpipe takeoff692/868; four PNG maximum.' if a.route else 'idle/walk and actual OAM cursor/rotation alignment at every write. Three screenshots.')+' No emulated RAM writes. Not full1-1.')
if __name__=='__main__':main()
