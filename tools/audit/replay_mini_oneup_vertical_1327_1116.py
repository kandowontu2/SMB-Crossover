"""Existing Up+Select support and ordinary fresh A for genuine hidden1UP."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_head_query_1327_1116 as Previous
import replay_mini_oneup_retained_lifts_1327_1116 as Bound
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='3e606f490a99f027506bab24f37018058408e7ef38ab58a0c4a4994c22dd2c7a'


@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Bound.bindings(raw));b=Current.bindings(raw)['bundle']
    for n in('Enemy_X_Speed','Enemy_MovingDir','Player_Y_Speed'):c['ram'][n]=W.address(b,n)
    at=16+84*8192+(0xb43e&8191);c['hooks']['NativeMiniHead']=dict(pc=0xb43e,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+84*8192:16+85*8192]))
    at=Current.CODE_AT+0xcbf;c['hooks']['MiniNativeTile']=dict(pc=0xacbf,offset=3*8192+0xcbf,work=True,bytes=list(raw[at:at+4]));return c


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw).split('\n',1)
    start=body.index("  if item.phase=='travel'then item.phase='brake';item.since=steps end")
    end=body.index('\n  return\n end',start)
    new="""  if item.phase=='travel'then item.phase='align-support';item.since=steps end
  assert(steps-item.since<600,'One existing manual support/hidden item episode')
  if a then item.phase=a.state<128 and 'wait-mature'or'collect'end
  if item.phase=='align-support'then
   buttons={right=x<C.target_x-1,left=x>C.target_x+1}
   if supported(s)and s.vx==0 and math.abs(x-C.target_x)<=2 and s.held&128==0 then item.settle=(item.settle or 0)+1 else item.settle=0 end
   if item.settle>=6 then item.phase='summon';item.summon_since=steps;item.summon_request=state();buttons={up=true,select=true}end
  elseif item.phase=='summon'then
   buttons={};assert(steps-item.summon_since<120,'Real native manual platform constructor')
   if item.manual_birth then item.phase='rise'end
  elseif item.phase=='rise'then
   buttons={};local e=actor(item.manual_birth.slot)
   assert(e.flag==1 and e.id==37 and e.x==item.manual_birth.initial_left,'Keep real summoned vertical actor')
   if work(0xc30d)==e.slot+1 and supported(s)and s.y<=160 and s.held&128==0 then
    item.phase='bump';item.takeoff=state();item.support_takeoff={actor=e,source_foot=s.sourceY16/16+7};item.jump_since=steps;buttons={a=true}
   end
  elseif item.phase=='bump'then
   buttons={a=steps-item.jump_since<36};assert(steps-item.jump_since<120,'One real raised-support head jump')
  elseif item.phase=='wait-mature'then
   local away=C.target_x-24;buttons={left=x>away+1,right=x<away-1}
  elseif item.phase=='collect'then buttons=a and{right=x<a.x+1,left=x>a.x+7}or{}end"""
    body=body[:start]+new+body[end:]
    old=" if a.id~=37 or(a.x~=560 and a.x~=688 and a.x~=864)then return end"
    assert body.count(old)==1;body=body.replace(old," if a.id~=37 then return end",1)
    old="route.births[#route.births+1]=row;camera_lift_spawns[a.x]={top=a.y,frame=frame,relative_x=a.x-pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc')}"
    new="""route.births[#route.births+1]=row;camera_lift_spawns[a.x]={top=a.y,frame=frame,relative_x=a.x-pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc')}
 if item.summon_request and not item.manual_birth and a.x~=560 and a.x~=688 and a.x~=864 then
  assert(a.x==math.max(0,row.state.x-12)and a.y==row.state.y+32,'Actual native existing vertical constructor formula');row.manual_vertical=true;item.manual_birth=row
 end"""
    assert body.count(old)==1;body=body.replace(old,new,1)
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw).encode()),parent_query_factory_SHA256=BASE_SHA,
        scope='Actual1327 genuine M/guarded fixed-lift prefix; existing ordinary Up+Select real vertical constructor+carry then freshA from raised support to authoredhiddenL, maturewholeC1/INC/cue64/+25 unchanged',
        existing_manual_vertical_inputs=True,native_head_bank84_SHA256=bindings(raw)['hooks']['NativeMiniHead']['bank_SHA256'])
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
