"""Native powered Tank walk with and without B, using a bounded observer."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
R=Path(__file__).resolve().parents[2];O=R/'build/tank-walk-modes-1101-v32'

def main():
 O.mkdir(exist_ok=True);source=R/'build/tank-walk-review-1101-v30/native/controller.lua'
 t=source.read_text().replace("if phase=='walk' then pad.right=true;pad.b=true end", "if phase=='walk' then pad.right=true;pad.b=age>=36 end")
 start=t.index('  if age==1 or age==25 or age==49 then');end=t.index('  local bytes={}',start)
 t=t[:start]+"""  if age==1 then
   emu.write(L['PlayerStatus'],2,emu.memType.nesDebug)
   emu.write(L['PlayerSize'],0,emu.memType.nesDebug)
  end
"""+t[end:]
 rom=R/'build/mario-tank-visible-host-1101-v5/candidate.nes'
 prepare(O/'native',rom,t,[Path(__file__),source],expected=sha(rom),timeout=90,scope='Cold selection with explicit powered state. Walk72frames, first36 without B, last36 with B; compact OAM/pose trace and three PNGs. Diagnostic, not full-stage proof.')
if __name__=='__main__':main()
