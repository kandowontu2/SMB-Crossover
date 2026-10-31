"""Prepare a bounded, controller-only trace of the original WWF action VM."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B

O = R/'build/wwf-action-donor-native-1031-v1/discovery'
P = R/'build/wwf-roster-source-review-v1/handoff.json'
ROM = Path('C:/NES/WWF WrestleMania (USA).nes')
EXPECTED = '0d294769d55984684f8fe3299f47b7f4da8667b1dabb94ab8e4c620750bf7f87'

POLICY = r'''-- Original donor: controller inputs and read-only observations only.
local f,age,done=0,nil,false
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function mode()return r(0x27)+256*r(0x28)end
local function native()return r(0x0c)==0 end
local trace=assert(io.open(OUTPUT..'frames.csv','w'))
trace:write('frame,age,mode,actor0_identity,actor1_identity,action0,action1,requested0,requested1,cursor0,cursor1,group0,group1,pose0,pose1,x0,x1,y0,y1,held0,fresh0\n')
local commands=assert(io.open(OUTPUT..'script-dispatch.csv','w'))
commands:write('frame,age,actor,action,cursor,pointer,opcode,x,y,sp,stack\n')
local dispatches,snaps,shots,seen=0,0,0,{}
local function binary(name,first,last)
 local o=assert(io.open(OUTPUT..name,'wb'))
 for a=first,last do o:write(string.char(r(a)))end
 o:close()
end
local function screen(name)
 shots=shots+1;assert(shots<=4,'Four whole screenshots maximum')
 local o=assert(io.open(OUTPUT..name..'.png','wb'));o:write(emu.takeScreenshot());o:close()
end
emu.addMemoryCallback(function()
 if native()and mode()==0xabff and not age then
  age=0;binary('ram-match-entry.bin',0,0x7ff)
 end
end,emu.callbackType.exec,0xabff)
emu.addMemoryCallback(function()
 if not age or not native()then return end
 dispatches=dispatches+1;assert(dispatches<=4096,'Bounded original script observations')
 local s=emu.getState();local x,y=s['cpu.x'],s['cpu.y']
 assert(x==0 or x==1,'Actual native actor selector')
 local ptr=r(0x21)+256*r(0x22);local op=r((ptr+y)&65535)
 local stack={}
 for k=1,6 do stack[#stack+1]=string.format('%02x',r(0x100+((s['cpu.sp']+k)&255)))end
 commands:write(table.concat({f,age,x,r(0x3c+x),r(0x40+x),ptr,op,r(0x2c+x),r(0x2e+x),s['cpu.sp'],table.concat(stack)},',')..'\n');commands:flush()
 local key=x..':'..r(0x3c+x)
 if not seen[key]and snaps<4 and r(0x3c+x)>=5 then
  seen[key]=true;snaps=snaps+1
  binary('ram-action-'..snaps..'.bin',0,0x7ff)
 end
end,emu.callbackType.exec,0xe385)
emu.addEventCallback(function()
 if done then return end
 local p,q={},{}
 if age then
  if age<24 then p.left=true
  elseif age>=64 and age<180 then p.a=age%32==0
  elseif age>=200 and age<320 then p.b=age%32==8
  elseif age>=340 and age<420 then p.up=true;p.b=age%32==0 end
 else
  local m=mode()
  if m==0x846f then
   if r(0x12c)~=0 then p.select=f%8==1 else p.start=f%8==3 end
  elseif m==0xd911 then
   if r(0x6e)%2==0 then p.a=f%8==3 else q.a=f%8==3 end
  elseif m==0x87db then
   local i=r(0x6e)+1;if r(0x12b)==255 then i=2 end
   local target=({5,0,5,0,5,0})[i]or 0
   if r(0x18)&127==1 then
    local pad=r(0x6e)%2==0 and p or q
    if r(0x6d)~=target then pad.down=f%8==1 else pad.a=f%8==3 end
   end
  elseif m~=0xabff and m~=0xa038 then p.start=f%60==5 end
 end
 emu.setInput(p,0);emu.setInput(q,1)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end
 f=f+1;assert(f<6000,'Original donor boot/controller bound')
 if age then
  trace:write(table.concat({f,age,mode(),r(0x2a),r(0x2b),r(0x3c),r(0x3d),r(0x3e),r(0x3f),r(0x40),r(0x41),r(0x32),r(0x33),r(0x34),r(0x35),r(0x2c),r(0x2d),r(0x2e),r(0x2f),r(0x0d),r(0x0e)},',')..'\n');trace:flush()
  if age==2 then screen('match-entry')elseif age==100 then screen('kick')elseif age==235 then screen('punch')elseif age==390 then screen('directional')end
  if age>=440 then
   assert(dispatches>50 and snaps>0,'Actual original action interpreter observed')
   trace:close();commands:close()
   local o=assert(io.open(OUTPUT..'result.json','w'))
   o:write('{"passed":true,"controller_only":true,"RAM_writes":false,"frames":'..f..',"match_frames":'..age..',"dispatches":'..dispatches..',"snapshots":'..snaps..',"screenshots":'..shots..'}\n');o:close()
   done=true;print('PASS original WWF action VM trace');emu.stop(0);return
  end
  age=age+1
 end
end,emu.eventType.endFrame)
'''


def main():
    assert not O.exists()
    assert B.sha(P) == '94d8411e26fe5cc7aeec01441e553dc16ddca00dd024a73af0b9aa7bc246cc23'
    h = json.loads(B.read(P))
    # The unrelated older Mario-in-WWF project has since been rebuilt. Keep
    # that failed transitive check visible, rather than rewriting its frozen
    # receipt or treating its current host artifacts as original-game proof.
    drift = [p for p, digest in h['bindings'].items()
             if not Path(p).is_file() or B.sha(p) != digest]
    for name in ['wrestlers.json', 'native-action-directories-scripts.bin', 'native-descriptors.bin']:
        required = P.parent/name
        assert B.sha(required) == h['bindings'][str(required)], required
    assert B.sha(ROM) == EXPECTED
    O.mkdir(parents=True)
    B.write(O/'controller.lua', POLICY)
    # Same process-isolation/budget/unchanged-source runner as the current
    # controller-only checks. It refuses to disturb an existing Mesen.
    runner = R/'build/current68-benj-peach-native-1031-v1/peach/run.py'
    B.write(O/'run.py', B.read(runner))
    paths = [Path(__file__), P, ROM, O/'controller.lua', O/'run.py', runner,
             R/'tools/run_mesen.py', R/'tools/audit/capture_budget.py', Path('C:/mesen2/Mesen.exe')]
    out = dict(prepared=True, native=False, ROM=str(ROM), ROM_sha256=EXPECTED,
               host_timeout_seconds=60, run_cap_bytes=536870912, max_files=64, max_PNGs=4,
               limits='Original donor observation only; no host changes or admission. Physical A/B/direction inputs; at most four2KiB RAM snapshots and four whole PNGs, no video.',
               historical_reference_binding_drift=drift,
               original_game_authority='Exact original USA ROM SHA; old Mario-port build artifacts are not used by this native run.',
               bindings={str(p.resolve()): B.sha(p) for p in paths})
    B.write(O/'ready.json', json.dumps(out, indent=2)+'\n')
    print(json.dumps(dict(prepared=True, ready=str(O/'ready.json'), ready_sha256=B.sha(O/'ready.json'))))


if __name__ == '__main__':
    main()
