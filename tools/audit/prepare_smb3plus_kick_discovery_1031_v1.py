"""Observe the donor's real kick call boundary with controller-only input."""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=Path(sys.argv[sys.argv.index('--output')+1]).resolve()/'discovery'
    assert not out.exists()
    base=R/'tools/audit/prepare_smb3plus_donor_native_1030_v4.py'
    source=base.read_text()
    assert source.count('end<=3600')==1
    source=source.replace('end<=3600','end<=4800')
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_kick_discovery_base'}
    exec(compile(source,str(base),'exec'),ns)
    ns['main']()
    script=out/'controller.lua';text=script.read_text()
    assert text.count('    emu.setInput(input, 0, 0)')==1
    text=text.replace('    emu.setInput(input, 0, 0)','')
    text+='''
local kick=assert(io.open(OUTPUT..'kick-boundaries.csv','w'))
kick:write('frame,bank,pc,character,form,held,fresh,timer,pose,sp,return_stack\\n')
local entries=0
local function trace(pc)
 local mapped=emu.convertAddress(pc)
 if not mapped or mapped.address//8192~=38 then return end
 entries=entries+1;assert(entries<=2048,'Bounded donor kick observations')
 local s=emu.getState();local stack={}
 for i=1,8 do stack[#stack+1]=string.format('%02x',read(0x100+((s['cpu.sp']+i)&255)))end
 kick:write(table.concat({frame,38,pc,read(0x119),read(0xed),read(0x17),read(0x18),
  read(0x517),read(0xee),s['cpu.sp'],table.concat(stack,'')},',')..'\\n');kick:flush()
end
emu.addMemoryCallback(function()trace(0xac82)end,emu.callbackType.exec,0xac82)
emu.addMemoryCallback(function()trace(0xac79)end,emu.callbackType.exec,0xac79)
emu.addEventCallback(function()
 local input={}
 for _,pulse in ipairs(PULSES)do
  if frame>=pulse[1]and frame<pulse[1]+4 then input[string.lower(pulse[2])]=true end
 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
'''
    script.write_text(text,encoding='utf-8',newline='\n')
    ready=out/'ready.json';d=json.loads(ready.read_text())
    d.update(input_application='inputPolled',scope='Original kick entry/continuation and controller-only small-Toad observations; no port/readiness claim.')
    for p in [base,Path(__file__).resolve(),script]:d['bindings'][str(p)]=sha(p)
    ready.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(prepared=str(ready),sha256=sha(ready),native=False)))


if __name__=='__main__':main()
