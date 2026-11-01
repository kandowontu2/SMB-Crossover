"""Bounded controller-only selection and walking smoke test for Mario the Tank."""
from pathlib import Path
import json
from prepare_mario_tank_visible_1101_v5 import O,P
from prepare_selected_native_packet_v1 import prepare,sha
def main():
    rom=O/'candidate.nes';q=json.loads((O/'candidate-patches.json').read_text())
    assert sha(rom)==q['private_candidate_sha256']
    # Retain the baseline host symbol bundle for successor audits. Private
    # worker symbols remain in visible.lbl/graft.lbl, not this host bundle.
    rom.with_suffix('.lbl').write_bytes((P/'candidate.lbl').read_bytes())
    rom.with_suffix('.dbg').write_bytes((P/'candidate.dbg').read_bytes())
    controller=r'''
local frame,age,phase,done,cycles=0,0,'title',false,0
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
emu.addEventCallback(function()
 local pad={}
 if age<4 then
  if phase=='open' or phase=='start' then pad.start=true
  elseif phase=='select' then pad.select=true end
 end
 if phase=='walk' then pad.right=true;pad.b=true end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title' and frame>=100 then phase='open';age=0
 elseif phase=='open' and age>=50 then assert(r('CrossoverMenuState')==2);phase='select';age=0
 elseif phase=='select' and age>=30 then
  cycles=cycles+1
  if cycles==7 then assert(r('MarioVariant')==7);shot('selected');phase='start';age=0 else age=0 end
 elseif phase=='start' and age>=300 then
  assert(r('SelectedCharacter')==0 and r('MarioVariant')==7 and r('OperMode')==1 and r('OperMode_Task')==3)
  shot('gameplay-entry');phase='walk';age=0
 elseif phase=='walk' and age>=36 then
  shot('walking');local x=r('Player_PageLoc')*256+r('Player_X_Position')
  local passed=x>40 and r('MarioVariant')==7 and r('GameEngineSubroutine')==8
  local f=assert(io.open(OUTPUT..'result.json','w'))
  f:write(string.format('{"passed":%s,"controller_only":true,"frames":%d,"world_x":%d,"variant":%d,"full_stage":false}\n',tostring(passed),frame,x,r('MarioVariant')));f:close();done=true;emu.stop(passed and 0 or 1)
 end
 if frame>900 then error('Finite selection bound')end
end,emu.eventType.endFrame)
'''
    prepare(O/'native-final-smoke',rom,controller,[Path(__file__),P/'candidate.lbl',P/'candidate.dbg'],expected=sha(rom),timeout=90,scope='Cold title, Mario Select seven times, Start, gameplay entry and36 controller walking frames. Three PNGs. No RAM writes, no powerup or stage-clear claim.')
if __name__=='__main__':main()
