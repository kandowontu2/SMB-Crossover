"""Observe the donor's real Peach hover paths using controller input only."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_smb3plus_kick_discovery_1031_v3 as P
from prepare_smb3plus_kick_discovery_1031_v1 import sha


def main():
    P.main()
    out=Path(sys.argv[sys.argv.index('--output')+1]).resolve()/'discovery'
    path=out/'controller.lua';text=path.read_text()
    needle=' emu.setInput(input,0)'
    assert text.count(needle)==1
    text=text.replace(needle," if frame>=3800 and frame<4200 then input.a=true end\n"+needle)
    text+='''
local floatFile=assert(io.open(OUTPUT..'float-boundaries.csv','w'))
floatFile:write('frame,bank,pc,character,form,held,fresh,Y,Yhi,VY,air,E4,E5,E6,E7,tile,sp\\n')
local floatCalls,seededFloat=0,false
local function floatTrace(bankId,pc)
 local mapped=emu.convertAddress(pc)
 if not mapped or mapped.address//8192~=bankId then return end
 floatCalls=floatCalls+1;assert(floatCalls<=8192,'Bounded float source observations')
 local s=emu.getState()
 floatFile:write(table.concat({frame,bankId,pc,read(0x119),read(0xed),read(0x17),read(0x18),
  read(0xa2),read(0x87),read(0xcf),read(0xd8),read(0x7ae4),read(0x7ae5),read(0x7ae6),
  read(0x7ae7),read(0xe5),s['cpu.sp']},',')..'\\n');floatFile:flush()
 if not seededFloat and bankId==31 and pc==0xbc4d and read(0x17)&128~=0 then
  seededFloat=true;dump('ram-float-entry.bin',32768,emu.memType.nesDebug)
  local f=assert(io.open(OUTPUT..'cpu-float-entry.txt','w'))
  for k,v in pairs(s)do if string.sub(k,1,4)=='cpu.'then f:write(k..'='..tostring(v)..'\\n')end end
  local cm=emu.convertAddress(0xc000)
  f:write('bankC='..tostring(cm.address//8192)..'\\n');f:close()
 end
end
for _,site in ipairs({{32,0xa003},{30,0xbac0},{30,0xb9f3},{31,0xb5ed},{31,0xbc4d},{31,0xbc66},{31,0xbb50}})do
 local b,pc=site[1],site[2]
 emu.addMemoryCallback(function()floatTrace(b,pc)end,emu.callbackType.exec,pc)
end
'''
    path.write_text(text,encoding='utf-8',newline='\n')
    ready=out/'ready.json';d=json.loads(ready.read_text())
    d.update(scope='Original Peach ground/air/hover call boundaries and native seed only. No host admission.',
        input_hold=dict(button='A',first_frame=3800,end_frame_exclusive=4200))
    for p in [Path(__file__),path]:d['bindings'][str(p)]=sha(p)
    ready.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(prepared=str(ready),sha256=sha(ready),native=False)))


if __name__=='__main__':main()
