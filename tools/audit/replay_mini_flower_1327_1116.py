"""Strict actual1327 M then natural Flower, original helpers and pickup path."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_manual_ctor_1327_1116 as Previous
import replay_mini_mushroom_1327_1116 as Mushroom
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='455c7b479efcbfea5460439effb72902c0b37783d2e445a446c94d76367047a5'

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Previous.bindings(raw));c.update(kind='flower',stock_type=1,target_x=1248,target_y=144);return c

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower' and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw).split('\n',1)
    body=once(body,"if item.phase=='travel'and x<960 then","if item.phase=='travel'and x<C.target_x-72 then")
    start=body.index("  if item.phase=='travel'then item.phase='align-support';item.since=steps end")
    end=body.index('\n  return\n end',start)
    new="""  if item.phase=='travel'then item.phase='align-head';item.since=steps end
  assert(steps-item.since<1000,'One natural Flower/support episode')
  if a and not item.mature then item.phase='wait-flower'end
  if item.phase=='align-head'then
   buttons={right=x<C.target_x-1,left=x>C.target_x+1}
   if supported(s)and s.vx==0 and math.abs(x-C.target_x)<=2 and s.held&128==0 then item.settle=(item.settle or 0)+1 else item.settle=0 end
   if item.settle>=6 then item.phase='bump';item.takeoff=state();item.jump_since=steps;buttons={a=true}end
  elseif item.phase=='bump'then
   buttons={a=steps-item.jump_since<36};assert(steps-item.jump_since<120,'Real original Flower head bump')
  elseif item.phase=='wait-flower'then
   buttons={}
   if item.mature then
    local left=C.target_x
    for _=1,8 do if not solid(left-8,C.target_y+1)then break end;left=left-16 end
    assert(not solid(left-8,C.target_y+1),'Finite actual authored brick row')
    item.brick_row={left=left,y=C.target_y,clear_column=left-16,cells={}}
    for xx=left-16,C.target_x+32,16 do
     local at=0x300+((xx//256)&1)*0xd0+(C.target_y&240)-32+((xx&255)//16)
     item.brick_row.cells[#item.brick_row.cells+1]={x=xx,y=C.target_y,cell=at,raw=read(at),flags=work(0xd300+read(at))}
    end
    item.phase='clear-column';item.settle=0
   end
  elseif item.phase=='clear-column'then
   local aim=item.brick_row.clear_column;buttons={left=x>aim+1,right=x<aim-1}
   if supported(s)and s.vx==0 and math.abs(x-aim)<=2 and s.held&128==0 then item.settle=item.settle+1 else item.settle=0 end
   if item.settle>=6 then item.phase='summon';item.summon_since=steps;item.summon_request=state();buttons={up=true,select=true}end
  elseif item.phase=='summon'then
   buttons={};assert(steps-item.summon_since<120,'Actual existing Flower support constructor')
   if item.manual_birth then item.phase='rise-flower'end
  elseif item.phase=='rise-flower'then
   buttons={};local e=actor(item.manual_birth.slot)
   assert(e.flag==1 and e.id==37 and e.x==item.manual_birth.initial_left,'Keep existing actual Flower support')
   if work(0xc30d)==e.slot+1 and supported(s)and s.y<=C.target_y-40 then item.departure=state();item.phase='collect'end
  elseif item.phase=='collect'then buttons=a and{right=x<a.x+1,left=x>a.x+7}or{}end"""
    body=body[:start]+new+body[end:]
    body=once(body,"r('FloateyNum_Control',5)==(M.scope_passed and 11 or 6)","r('FloateyNum_Control',5)==6")
    start=body.index('stockEndpoint=function()\n');end=body.index("\nhook('LifeBefore'",start)
    original=Mushroom.TEMPLATE.read_text();a=original.index('local function endpoint()\n')+len('local function endpoint()\n');z=original.index("\nhook('GameLoop'",a)
    endpoint=original[a:z]
    endpoint=endpoint.replace("r('PlayerStatus')==1","r('PlayerStatus')==2").replace('work(0xc244)==1','work(0xc244)==2')
    endpoint=endpoint.replace('Natural Mini mature Mushroom/wholeC1/1000/60growth/25 real MiniStep+public returns','Natural Mini M then matureFlower/wholeC1/1000/60growth/25 original+public returns')
    body=body[:start]+'stockEndpoint=function()\n'+endpoint+body[end:]
    body=once(body,"r('GuestPowerupActive')==0 and r('PlayerStatus')==1 and r('GameEngineSubroutine')==8","r('GuestPowerupActive')==0 and r('PlayerStatus')==(M.scope_passed and 2 or 1)and r('GameEngineSubroutine')==8")
    body=once(body,"frame<14000 and mainEntries<4200,'Bounded natural Mini M/hidden1UP'","frame<16000 and mainEntries<5000,'Bounded natural Mini M/Flower'")
    body=once(body,"if qx<960 or qx>=1072 then return end","if qx<1184 or qx>=1296 then return end")
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='flower'):
    assert key=='flower';q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),parent_manual_ctor_SHA256=BASE_SHA,scope='Actual1327 frozen M/guarded three lifts, ordinary first pit, real matureFlower, existing clear-column UpSelect support if needed, wholeC1/native1/1000/60/+25 returned MiniStep/public; shot scope separate');return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
