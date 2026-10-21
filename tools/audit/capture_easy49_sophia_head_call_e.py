"""Capture entire real resident head calls on ordinary C-candidate inputs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-sophia-head-axis-c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    mapper=sys.argv[1]
    assert mapper in ['mmc3','mmc5']
    spec=importlib.util.spec_from_file_location('head_image_e',V/'agent49k-samus-water-up-direction-component-a/image.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    im=m.Image(D/f'source/build/smb-crossover-{mapper}.nes')
    binding=D/f'native-head-e-{mapper}.json'
    assert not binding.exists()
    entry=im.hook('CrossoverHeadProbe')
    interrupts=[im.hook(n)for n in ['NonMaskableInterrupt','IrqScrollSplit']]
    core=r'''dofile(IDENTITY)
local H=ENTRY
local INTS=INTERRUPTS
local f,id=0,0
local active=nil
local returns={}
local out=assert(io.open(ROSTER_CONFIG.out..'head-calls-e.jsonl','w'))
local ram=assert(io.open(ROSTER_CONFIG.out..'head-calls-e.ram','wb'))
local writes=assert(io.open(ROSTER_CONFIG.out..'head-writes-e.csv','w'))
writes:write('id,address,value\n')
local offset=0
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function bank(a)local z=emu.convertAddress(a);return z and z.memType==emu.memType.nesPrgRom and z.address//8192 or -1 end
local function guard(h)
 if bank(h.address)~=h.physical_bank then return false end
 for i,b in ipairs(h.bytes)do assert(r(h.address+i-1)==b,'Head native physical eight bytes')end
 return true
end
local function snapshot(kind,pc)
 local s=emu.getState();local b={}
 for a=0,2047 do b[#b+1]=string.char(r(a))end
 for a=0x6000,0x7fff do b[#b+1]=string.char(r(a))end
 ram:write(table.concat(b));ram:flush()
 local v={active.id,kind,f,s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps'],s['cpu.sp'],pc,s['cpu.cycleCount'],offset,bank(0x8000),bank(0xa000),bank(0xc000),bank(0xe000),active.interrupts}
 out:write('[')
 for i,n in ipairs(v)do if i>1 then out:write(',')end;if type(n)=='string'then out:write(string.format('%q',n))else out:write(n)end end
 out:write(']\n');out:flush();offset=offset+10240
end
for _,h in ipairs(INTS)do emu.addMemoryCallback(function()if active and guard(h)then active.interrupts=active.interrupts+1 end end,emu.callbackType.exec,h.address)end
emu.addMemoryCallback(function()
 if f<915 or f>970 or not guard(H)then return end
 assert(not active,'Resident head call is not recursive')
 local s=emu.getState();local sp=s['cpu.sp']
 local ret=(r(0x100+(sp+1)%256)+256*r(0x100+(sp+2)%256)+1)%65536
 id=id+1;active={id=id,ret=ret,sp=(sp+2)%256,interrupts=0,retbank=bank(ret)}
 snapshot('entry',H.address)
 if not returns[ret]then
  returns[ret]=true
  emu.addMemoryCallback(function()
   if active and active.ret==ret and emu.getState()['cpu.sp']==active.sp and bank(ret)==active.retbank then
    snapshot('return',ret);active=nil
   end
  end,emu.callbackType.exec,ret)
 end
end,emu.callbackType.exec,H.address)
emu.addMemoryCallback(function(a,v)if active then writes:write(active.id..','..a..','..v..'\n');writes:flush()end end,emu.callbackType.write,0,0xffff)
emu.addEventCallback(function()f=f+1 end,emu.eventType.endFrame)
return function()return{}end
'''
    core=core.replace('IDENTITY',json.dumps((V/'root49-current-c-transfers-a/identity.lua').as_posix()))
    core=core.replace('INTERRUPTS',m.lua(interrupts)).replace('ENTRY',m.lua(entry))
    policy=D/f'native-head-e-{mapper}.lua';policy.write_text(core)
    parent=R/f'build/roster-through-2-2/root49-sophia-head-axis-b-11-v0-{mapper}/inputs.csv'
    record=dict(status='PREPARED_PASSIVE_WHOLE_RESIDENT_HEAD_CAPTURE',script_sha256=sha(__file__),ROM=im.metadata(),
                entry=entry,interrupts=interrupts,policy_sha256=sha(policy),input_sha256=sha(parent),
                input_parent=parent.relative_to(R).as_posix(),capture_frames=[915,970],
                columns='id,event,frame,A,X,Y,P,SP,PC,cycles,RAMoffset,bank8000,bankA000,bankC000,bankE000,interrupts'.split(','),
                emulated_writes=False,state_loads=False,phase_cap_bytes=500000000,final_reserve_bytes=50000000,global_cap_bytes=70000000000)
    binding.write_text(json.dumps(record,indent=2)+'\n')
    print('Prepared passive whole-head capture '+mapper)


if __name__=='__main__':main()
