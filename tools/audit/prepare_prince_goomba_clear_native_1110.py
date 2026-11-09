"""Stage a controller-only third-pipe and two-Goomba replay on private 4699."""

import argparse
import json
from pathlib import Path
import sys

from check_prince_goomba_recovery_1110 import Route
from deliver_helper_camera_render_1110 import bindings
from observe_chip_committed_write import lua
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


R, Current = Route.R, Route.Current
V3 = Route.ROOT/'native'
HANDOFF = R/'build/prince-goomba-recovery-1110/handoff.json'
PINS = {
    V3/'controller.lua':'5e4fc351ef7519066d4986a9d04a2747126d29ffad61bc0334af2448621332eb',
    V3/'ready.json':'d0ef89372c80abb7d3df922f8b2652a2b343d7a2365a078791294bbe4888b57c',
    V3/'capture/third-pipe.json':'9ec9472d480b21c6fd421b09f90b7f52033936fe688e5d8f6c36c73141a1cd7b',
    V3/'capture/binding.json':'b7e2d84631d71edf626dc312d2db9eb606c73e0c216b9313dbd0582a2fed05f5',
    V3/'capture/full11.json':'7ecfd6263ec5e52e8fce77689003dc0c57308cf8e04b6424d295f01a255b27a2',
    HANDOFF:'28651e37f3f3927cd4d57a2d9d2b47cffa143fbd46ae5c51bb1cd6e8e9137cd8',
}


GROUP = r'''
local thirdGroup={births={}}
local groupHooks=BOUND_GROUP_HOOKS
local function groupActor(slot)
 return {slot=slot,id=ram(L.Enemy_ID+slot),flag=ram(L.Enemy_Flag+slot),
         x=ram(L.Enemy_X_Position+slot)+256*ram(L.Enemy_PageLoc+slot),
         y=ram(L.Enemy_Y_Position+slot),state=ram(L.Enemy_State+slot),
         direction=ram(0x53f+slot)}
end
local function groupExec(h,visit)
 emu.addMemoryCallback(function()
  if part~='full11' or route.index~=2 or not sourceActive() or r('GameEngineSubroutine')~=8 or ram(0x73c)~=7 then return end
  local m=emu.convertAddress(h.pc)
  if not m or m.memType~=emu.memType.nesPrgRom or m.address~=h.physical then return end
  equal(bytes(h.pc,#h.bytes),h.bytes,'Exact native group parser opcode')
  visit(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
groupExec(groupHooks.begin,function(cpu)
 local left,right=currentEdges()
 assert(not thirdGroup.begin and cpu['cpu.a']==0x37 and right>=816,'Authored page3 Goomba group parser entry')
 thirdGroup.begin={Main=admitted,frame=frame,world_x=wx(),camera_left=left,camera_right=right,entry=cpu['cpu.a']}
end)
groupExec(groupHooks.birth,function(cpu)
 local h=thirdGroup.begin
 if not h then return end
 local n=#thirdGroup.births
 local actor=groupActor(cpu['cpu.x'])
 assert(n<2 and actor.flag==1 and actor.id==6 and actor.x==h.camera_right+24*n,
  'Each natural Goomba comes from the authentic group slots and X offsets')
 actor.frame=frame;actor.Main=admitted
 thirdGroup.births[n+1]=actor
end)
local function writeThirdGroup(ok,why)
 if thirdGroup.written then return end
 thirdGroup.written=true
 writejson('third-goombas.json',{passed=ok,reason=why,ROM_sha256=Q.ROM_sha256,controller_only=true,
  emulated_writes=false,group=thirdGroup,camera_route=route.third_camera,terminal=state(),
  initial_lives=initialLives,final_lives=r('NumberofLives')})
end
local function thirdGroupTick(s,support)
 if thirdGroup.written or #thirdGroup.births~=2 or route.index<3 or s.world_x<872
   or s.native_y~=176 or not support then return end
 local a,b=groupActor(thirdGroup.births[1].slot),groupActor(thirdGroup.births[2].slot)
 if a.flag==1 and b.flag==1 and a.id==6 and b.id==6 and (a.state&32)==0 and (b.state&32)==0
   and a.x+13<s.world_x+2 and b.x+13<s.world_x+2 then
  thirdGroup.clear={Main=admitted,frame=frame,player=s,actors={a,b}}
  writeThirdGroup(true,'Actual original third-pipe jump and real far-side ground beyond both live Goombas')
 end
end
'''


CORRIDOR = r'''
local function thirdCameraRoute(s,o,support)
 if not o or o.left~=736 then return false end
 local x=s.world_x
 if not route.third_camera and route.mode=='approach' and 676<=x and x<698 and s.native_y==176 and support then
  local left,right=currentEdges()
  route.third_camera={start=s,Main=admitted,left=left,right=right,events={}}
  routeMode('third-cam-right',{'right'})
 end
 local c=route.third_camera
 if not c or c.done then return false end
 local mode=route.mode
 local left,right=currentEdges()
 local idle=s.source_frame==15 and s.source_mode==0 and s.source_A_lock==0 and s.native_y==176
  and 208<=s.physical_foot and s.physical_foot<=211 and (solid(x+2,208) or solid(x+13,208))
 local function change(next,pad)
  assert(#c.events<30,'Bounded camera-route transitions')
  c.events[#c.events+1]={from=mode,to=next,player=s,Main=admitted,frame=frame,left=left,right=right}
  routeMode(next,pad)
 end
 if mode=='third-cam-right' and x>=698 then
  change('third-cam-brake-right',{})
 elseif mode=='third-cam-left' and x<=699 then
  change('third-cam-brake-left',{})
 elseif mode=='third-cam-brake-right' and idle then
  if right>=803 then change('third-cam-nudge',{'right'}) else change('third-cam-left',{'left'}) end
 elseif mode=='third-cam-brake-left' and idle then
  change('third-cam-right',{'right'})
 elseif mode=='third-cam-nudge' and x>=709 then
  change('third-cam-settle',{})
 elseif mode=='third-cam-settle' and idle and s.source_facing==255 then
  change('third-cam-ledge',{'up'})
 elseif mode=='third-cam-ledge' and (s.source_mode==2 or s.source_mode==6 or s.source_action==10) then
  route.hang=s
  routeLog('actual-original-ledge-hang')
  change('third-cam-climb',{'up'})
 elseif mode=='third-cam-climb' and s.source_action==10 and s.physical_foot<=147 then
  c.done=true
  change('pipe-cross',{'right'})
 end
 if mode~='third-cam-ledge' and mode~='third-cam-climb' and
    (x<656 or x>723 or s.native_y<172 or s.native_y>182) then
  routeFail('Original brake and nudge left the supported corridor')
 end
 if admitted-c.Main>600 or admitted-route.changed>150 then
  routeFail('Original camera and Up handoff exceeded its finite bound')
 end
 return true
end
'''


def controller(raw):
    hooks = {}
    for name,pc,expected in (('begin',0xa7a3,b'\xa0\x00\x38\xe9\x37'),
                             ('birth',0xa804,b'\x8d\x6a\x01\xa9\x27')):
        physical=2*8192+pc-0xa000
        assert raw[16+physical:16+physical+len(expected)]==expected
        hooks[name]=dict(pc=pc,physical=physical,bytes=list(expected))
    stream=bytes.fromhex('1ec2006b068b8663b70f05030623064bb7bb005bb7fb373bb70f0b1b37ff')
    assert raw[19023:19023+len(stream)]==stream and stream[7:9]==bytes.fromhex('63b7')
    source=(V3/'controller.lua').read_text(encoding='utf-8')
    anchor='local function routeWrite(ok,why)'
    source=once(source,anchor,once(GROUP,'BOUND_GROUP_HOOKS',lua(hooks))+'\n'+anchor+
                '\n if not thirdGroup.written then writeThirdGroup(false,why) end')
    anchor='local function roofJump(s,o,support)'
    source=once(source,anchor,CORRIDOR+'\n'+anchor)
    anchor=' local age=admitted-(route.changed or route.start)'
    source=once(source,anchor,anchor+'\n thirdGroupTick(s,support)\n if thirdCameraRoute(s,o,support) then return end')
    source=once(source,'  if #route.clears~=6 or route.max_x<3100 or not route.flag then',
                '  if #route.clears~=6 or route.max_x<3100 or not route.flag or not thirdGroup.clear then')
    assert source.count(Route.PIN)==1 and 'emu.write(' not in source
    sys.path.insert(0,str(Route.Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    return source


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    for path,pin in PINS.items():
        assert sha(path)==pin,path
    assert sha(Route.ROM)==Route.PIN
    ready,old,third,full,cpu=(Current.read(path) for path in (V3/'ready.json',V3/'capture/binding.json',
        V3/'capture/third-pipe.json',V3/'capture/full11.json',HANDOFF))
    assert ready['ROM_sha256']==old['ROM_sha256']==third['ROM_sha256']==full['ROM_sha256']==cpu['ROM_SHA256']==Route.PIN
    assert old['ready_sha256']==PINS[V3/'ready.json'] and old['exit_code']!=0 and not ready['emulated_writes']
    assert third['passed'] and not full['passed'] and full['HP']==0
    bindings(ready['bindings'])
    for name,pin in cpu['bindings'].items():
        assert sha(R/name)==pin,name
    positives=[q for q in cpu['results'] if q['terminal']=='cleared' and q['nudge']==709]
    assert [q['camera_right_initial'] for q in positives]==[748,760]
    for q in positives:
        assert q['goal']==803 and q['ledge_pad']==8 and q['group_birth']['camera_right']==816
        assert q['far_ground']['x']==891 and q['end']['hp']==5 and q['end']['lives']==2
        assert all(actor['x']+13<q['end']['x']+2 for actor in q['end']['actors'])
    source=controller(Route.ROM.read_bytes())
    refs={Path(__file__),*PINS,*map(Path,ready['bindings']),*(R/name for name in cpu['bindings'])}
    prepare(out,Route.ROM,source,refs,expected=Route.PIN,timeout=ready['timeout'],
            scope='Genuine camera travel, short Right nudge, neutral donor stance, Up ledge and original running A. '
                  'Third pipe, both live Goombas, and full-stage results are separate.',
            allow_interactive=ready['allow_interactive'])
    assert len(list(out.iterdir()))==3


if __name__=='__main__':
    main()
