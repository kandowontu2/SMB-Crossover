"""Cold controller-only selection regression on the actual delivered nightly."""
from pathlib import Path
import argparse
import json
import re
from prepare_selected_native_packet_v1 import R, prepare, sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--candidate',type=Path,help='Tested candidate matching the installed ROM and its labels')
    ap.add_argument('--installed-path',action='store_true');a=ap.parse_args()
    current=json.loads((R/'docs/qa/continuation-current.json').read_text())['installed_nightly']
    rom=a.candidate or Path(current['owning_candidate'])
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
    if a.installed_path:
        from nightly_patch_guard_v1 import check
        check(installed)
        # Run the Downloads file itself without copying debug files into Downloads.
        names={'CrossoverMenuState','CrossoverMenuIndex','SelectedCharacter','OperMode','OperMode_Task'}
        labels={m[2]:int(m[1],16) for line in rom.with_suffix('.lbl').read_text().splitlines()
                if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)',line)) and m[2] in names}
        assert labels.keys()==names
        controller='\n'.join(f'L[{json.dumps(n)}]={v}' for n,v in labels.items())+'\n'+controller
    a.output.parent.mkdir(parents=True,exist_ok=True)
    prepare(a.output,rom,controller,[Path(__file__),installed],expected=sha(installed),timeout=60,scope='Actual installed-byte-equivalent cold title, Rygar Select, Karnov Start, native gameplay entry. Controller only; two PNGs.')
    if a.installed_path:
        ready=a.output/'ready.json';q=json.loads(ready.read_text());q['ROM']=str(installed)
        q['scope']='Actual Downloads launch, no matching automatic patch; cold Karnov menu-to-gameplay. Controller only.'
        ready.write_text(json.dumps(q,indent=2)+'\n')

if __name__=='__main__':main()
