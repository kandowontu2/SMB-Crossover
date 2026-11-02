"""Bounded native checks of the composed nightly successor."""
import argparse
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 ref=R/'build/shinobi-rotation-trace-1101-v25/native/controller.lua'
 t=ref.read_text()
 # Preserve the existing physical-frame observation and require alignment at
 # every write, rather than accepting a screenshot alone as sprite integrity.
 t=t.replace("if name=='CurrentOAMOffset' and v%4==0 then return end", "assert(v%4==0,'OAM count/rotation must remain a multiple of four: '..name..' '..v);if name=='CurrentOAMOffset' then return end")
 assert "assert(v%4==0" in t
 a.output.parent.mkdir(exist_ok=True)
 prepare(a.output,a.rom,t,[Path(__file__),ref],expected=sha(a.rom),timeout=90,scope='Combined candidate real cold Shinobi selection, idle/walk and actual OAM cursor/rotation alignment at every write. Three screenshots, no emulated RAM writes. Not full1-1.')
if __name__=='__main__':main()
