"""Bind the genuine block climb and standing hop after Prince's second pit."""

import argparse
from pathlib import Path
import sys

import check_prince_post_pit_cap_1110 as Cap
from deliver_helper_camera_render_1110 import bindings
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


R, Pair, Route = Cap.R, Cap.Pair, Cap.Route
V5 = Pair.V5
PROOF = Cap.PRIOR.with_name('cap.json')
PINS = {
    V5/'ready.json':'a62bc95830c3f9bcc24d698010eb7d87eb08dd55ef510e1471414d6d6886bc72',
    V5/'controller.lua':'47b622e73ff2c7040a6b922759c15aef74c2c821295fdcc1428c678df003f9fd',
    Cap.PRIOR:Cap.PRIOR_SHA,
    Cap.Early.PARENT:Cap.Early.PARENT_SHA,
}


GROUP = r'''
local postPit={births={}}
groupExec(groupHooks.begin,function(cpu)
 local left,right=currentEdges()
 assert(not postPit.begin and cpu['cpu.a']==0x37 and right>=1552,'Authored page6 Goomba group parser entry')
 postPit.begin={Main=admitted,frame=frame,world_x=wx(),camera_left=left,camera_right=right}
end,6,15)
groupExec(groupHooks.birth,function(cpu)
 local h=assert(postPit.begin,'Actual post-pit group entry precedes actor constructor')
 local n=#postPit.births
 local a=groupActor(cpu['cpu.x'])
 assert(n<2 and a.flag==1 and a.id==6 and a.x==h.camera_right+24*n,
  'Each post-pit Goomba comes from the authentic native group slots and X offsets')
 a.Main=admitted;a.frame=frame
 postPit.births[n+1]=a
end,6,15)

local function writePostPit(ok,why)
 if postPit.written then return end
 postPit.written=true
 writejson('post-pit-goombas.json',{passed=ok,reason=why,ROM_sha256=Q.ROM_sha256,
  controller_only=true,emulated_writes=false,group=postPit,route=route.post_pit,state=state(),frame=frame,
  initial_lives=initialLives,final_lives=r('NumberofLives')})
end
'''


CONTROL = r'''
local postPitPads={initial={'right'},['brake-right']={},left={'left'},['brake-left']={},['run-up']={'right'},
 ['brake-ledge']={},up={'up'},climb={'up'},['cap-A']={'a'},leap={'right'}}
local postPitBounds={initial=160,['brake-right']=100,left=130,['brake-left']=100,['run-up']=130,
 ['brake-ledge']=100,up=125,climb=100,['cap-A']=28,leap=145}
local function postPitTick(s,o,support)
 if route.index~=6 or not o or o.kind~='pit' or o.left~=2448 or postPit.clear then return false end
 if not route.post_pit then route.post_pit={stage='initial',Main=admitted,events={}}end
 local p=route.post_pit
 local stage=p.stage
 local x=s.world_x
 local left,right=currentEdges()
 local function change(name)
  p.stage=name;p.Main=admitted
  p.events[#p.events+1]={stage=name,Main=admitted,frame=frame,state=s,
    camera_left=left,camera_right=right,support=support,enemy_cursor=ram(0x73c)}
  route.pad=postPitPads[name]
  routeLog('post-pit-'..name)
 end
 if admitted-p.Main>postPitBounds[stage] then routeFail('Post-pit original '..stage..' exceeded its finite bound')end
 if x<1433 then routeFail('Post-pit turn retreated to the second gap')end
 route.pad=postPitPads[stage]
 if stage=='initial' and x>=1490 then change('brake-right')
 elseif stage=='brake-right' and idleReady(s) and support then change('left')
 elseif stage=='left' and x<=1477 and s.source_facing==0 then change('brake-left')
 elseif stage=='brake-left' and idleReady(s) and support then change('run-up')
 elseif stage=='run-up' then
  if x>=1470 and x<=1478 and right>=1541 and right<=1548 and ram(0x73c)==15
      and (s.phase&3)<=1 and support and runReady(s) and s.source_facing==255 then
   local solidBlock,tile=solid(1504,144)
   if not solidBlock or tile~=88 then routeFail('Expected actual authored high brick')end
   change('brake-ledge')
  elseif x>=1479 or right>=1552 then
   routeFail('Post-pit brick alignment passed its supported pre-birth window')
  end
 elseif stage=='brake-ledge' and idleReady(s) and support then
  if x<1486 or x>1502 or s.native_y~=176 then routeFail('Post-pit ground position is outside the original Up scan')end
  change('up')
 elseif stage=='up' and (s.source_mode==2 or s.source_mode==6 or s.source_action==10) then
  p.hang=s;change('climb')
 elseif stage=='climb' and s.source_action==10 and idleReady(s) and support and s.native_y>=111 and s.native_y<=115 then
  local a,t1=solid(x+2,144);local b,t2=solid(x+13,144)
  if not ((a and t1==88) or (b and t2==88)) then routeFail('Original climb lacked physical support on the actual high brick')end
  if #postPit.births~=2 then routeFail('High brick climb lacks both actual natural Goombas')end
  p.cap={state=s,actors={groupActor(postPit.births[1].slot),groupActor(postPit.births[2].slot)}}
  change('cap-A')
 elseif stage=='cap-A' and s.source_action==3 then
  p.admission=s;change('leap')
 elseif stage=='leap' and x>=1545 and s.native_y==176 and support then
  local a,b=groupActor(postPit.births[1].slot),groupActor(postPit.births[2].slot)
  if a.flag==1 and b.flag==1 and a.id==6 and b.id==6 and (a.state&32)==0 and (b.state&32)==0
      and a.x+13<x+2 and b.x+13<x+2 then
   postPit.clear={Main=admitted,frame=frame,player=s,actors={a,b}}
   writePostPit(true,'Actual original climb and supported standing A cleared both live post-pit Goombas')
   routeLog('post-pit-pair-behind')
   return false
  end
 end
 return true
end
'''


def controller():
    text = (V5/'controller.lua').read_text(encoding='utf-8')
    text = once(text,'local function groupExec(h,visit)','local function groupExec(h,visit,index,cursor)')
    text = once(text,"  if part~='full11' or route.index~=2 or not sourceActive() or r('GameEngineSubroutine')~=8 or ram(0x73c)~=7 then return end",
                "  if part~='full11' or route.index~=(index or 2) or not sourceActive() or r('GameEngineSubroutine')~=8\n"
                "      or ram(0x73c)~=(cursor or 7) then return end")
    text = once(text,'local function routeWrite(ok,why)',GROUP+'\nlocal function routeWrite(ok,why)\n'
                ' if not postPit.written then writePostPit(false,why) end')
    text = once(text,'local function fullTick(finish)',CONTROL+'\nlocal function fullTick(finish)')
    text = once(text,' if pitTurn(s,o,support) then return end',' if pitTurn(s,o,support) then return end\n'
                ' if postPitTick(s,o,support) then return end')
    text = once(text,'or not route.second_pit or not route.second_pit.far_ground then',
                'or not route.second_pit or not route.second_pit.far_ground or not postPit.clear then')
    assert text.count(Route.PIN)==1 and 'emu.write(' not in text
    sys.path.insert(0,str(Route.Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--proof-sha',required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(PROOF.parent) and out!=PROOF.parent and not out.exists()
    for path,digest in {**PINS,PROOF:args.proof_sha}.items():
        assert sha(path)==digest,path
    ready, proof = (Pair.Second.First.Pit.Current.read(p) for p in (V5/'ready.json',PROOF))
    assert ready['ROM_sha256']==proof['ROM_SHA256']==Route.PIN and not ready['emulated_writes']
    bindings(ready['bindings'])
    for p,digest in proof['bindings'].items():
        assert sha(R/p)==digest,p
    a = proof['standing_A']
    assert a['terminal']=='pair-behind' and a['admission']['action']==3 and not a['contacts']
    assert (a['start']['x'],a['start']['y'],a['start']['hp'],a['end']['y'],a['end']['hp'],a['end']['lives'])==(1491,112,4,176,4,2)
    refs = {Path(__file__),*PINS,PROOF,*map(Path,ready['bindings']),*(R/p for p in proof['bindings'])}
    prepare(out,Route.ROM,controller(),refs,expected=Route.PIN,timeout=ready['timeout'],
            allow_interactive=ready['allow_interactive'],
            scope='Original Up climbs the authored high brick and supported standing A clears both live post-pit Goombas. '
                  'Prior pipe, group, first- and second-pit witnesses remain in force.')
    assert sum(p.is_file() for p in out.rglob('*'))==3


if __name__=='__main__':
    main()
