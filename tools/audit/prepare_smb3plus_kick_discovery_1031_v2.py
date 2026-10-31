"""Capture the genuine controller boundary, including a native B-edge seed."""
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_smb3plus_kick_discovery_1031_v1 as P


def main():
    P.main()
    out=Path(sys.argv[sys.argv.index('--output')+1]).resolve()/'discovery'
    script=out/'controller.lua';text=script.read_text()
    text+='''
local ctl=assert(io.open(OUTPUT..'controller-boundaries.csv','w'))
ctl:write('frame,character,form,held,fresh,timer,pose,in_air,Y,bankC,sp\\n')
local ctlEntries,seeded=0,false
emu.addMemoryCallback(function()
 local mapped=emu.convertAddress(0xa6bb)
 if not mapped or mapped.address//8192~=8 then return end
 ctlEntries=ctlEntries+1;assert(ctlEntries<=1024,'Bounded original controller entries')
 local s=emu.getState();local cm=emu.convertAddress(0xc000)
 ctl:write(table.concat({frame,read(0x119),read(0xed),read(0x17),read(0x18),read(0x517),
  read(0xee),read(0xd8),read(0xa2),cm.address//8192,s['cpu.sp']},',')..'\\n');ctl:flush()
 if not seeded and read(0x18)&64~=0 then
  seeded=true;dump('ram-B-entry.bin',32768,emu.memType.nesDebug)
  local f=assert(io.open(OUTPUT..'cpu-B-entry.txt','w'))
  for k,v in pairs(s)do if string.sub(k,1,4)=='cpu.'then f:write(k..'='..tostring(v)..'\\n')end end
  f:write('bankC='..cm.address//8192..'\\n');f:close()
 end
end,emu.callbackType.exec,0xa6bb)
'''
    script.write_text(text,encoding='utf-8',newline='\n')
    ready=out/'ready.json';d=json.loads(ready.read_text())
    for p in [Path(__file__).resolve(),script]:d['bindings'][str(p)]=P.sha(p)
    ready.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(ready=str(ready),sha256=P.sha(ready),native=False)))


if __name__=='__main__':main()
