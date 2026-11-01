"""Cold controller-only selection regression on the actual delivered nightly."""
from pathlib import Path
import argparse
from prepare_selected_native_packet_v1 import R, prepare, sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    rom=R/'build/kirby-owner-main-1101-v2/candidate.nes'
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(rom)==sha(installed)
    controller=r'''
local frame,age,phase,done=0,0,'title',false
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
emu.addEventCallback(function()
 local pad={}
 if age<4 then
  if phase=='open'or phase=='start'then pad.start=true
  elseif phase=='left'then pad.left=true elseif phase=='select'then pad.select=true end
 end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title'and frame>=100 then phase='open';age=0
 elseif phase=='open'and age>=50 then assert(r('CrossoverMenuState')==2);phase='left';age=0
 elseif phase=='left'and age>=30 then assert(r('CrossoverMenuIndex')==7);phase='select';age=0
 elseif phase=='select'and age>=30 then assert(r('SelectedCharacter')==34);shot('karnov-selected');phase='start';age=0
 elseif phase=='start'and age>=300 then
  shot('karnov-start-result')
  local selected=r('SelectedCharacter');local mode=r('OperMode');local task=r('OperMode_Task');local menu=r('CrossoverMenuState')
  local passed=selected==34 and mode==1 and task==3
  local f=assert(io.open(OUTPUT..'result.json','w'))
  f:write(string.format('{"passed":%s,"selected":%d,"mode":%d,"task":%d,"menu":%d,"frames":%d,"controller_only":true}\n',tostring(passed),selected,mode,task,menu,frame));f:close();done=true;emu.stop(passed and 0 or 1)
 end
 if frame>700 then error('Finite selection bound')end
end,emu.eventType.endFrame)
'''
    a.output.parent.mkdir(parents=True,exist_ok=True)
    prepare(a.output,rom,controller,[Path(__file__),installed],expected=sha(installed),timeout=60,scope='Actual installed-byte-equivalent cold title, Rygar Select, Karnov Start, native gameplay entry. Controller only; two PNGs.')

if __name__=='__main__':main()
