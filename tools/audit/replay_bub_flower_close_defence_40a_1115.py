"""Bub-only live close-threat handling at the second-pipe descent."""
from functools import lru_cache
from pathlib import Path
import inspect
import replay_bub_flower_combat_40a_1115 as Previous

R,ROM,W,N,B,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.B,Previous.PIN

DEFENCE=r'''
local closeFight=nil
local function closeRect(slot)
 local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
 local wx=slot==nil and full_x()or full_x(slot)
 local rel=(wx-camera)&255
 local at=slot==nil and Stock.ram.BoundingBox_UL_Corner or Stock.ram.EnemyBoundingBoxCoord+4*slot
 local a={};for i=0,3 do a[#a+1]=read(at+i)end
 a[1]=wx+((a[1]-rel+128)%256)-128;a[3]=wx+((a[3]-rel+128)%256)-128
 return a
end
local function closeThreat(q,actor,x,y,grounded)
 if x<600 or x>=720 or(full_index~=2 and full_index~=3)then return false end
 if full_part~='approach'and full_part~='jump'and full_part~='cross'then return false end
 local target=nil
 for i=0,5 do
  local flag=read(L.Enemy_Flag+i);local id=read(L.Enemy_ID+i)
  local dx=full_x(i)-x;local ey=read(L.Enemy_Y_Position+i)
  if flag>0 and flag<128 and(id==6 or id==0)and read(L.Enemy_State+i)&32==0
   and dx>0 and dx<=80 and math.abs(ey-y)<=48 and(not target or dx<target.dx)then
   target={slot=i,id=id,flag=flag,state=read(L.Enemy_State+i),dx=dx,x=full_x(i),y=ey,direction=read(L.Enemy_MovingDir+i),box=closeRect(i)}
  end
 end
 local body=closeRect(nil)
 if target and q.completed_Main~=flower.closeLast then
  flower.closeLast=q.completed_Main;flower.close_rows=flower.close_rows or{}
  local t=flower.close_rows;t[#t+1]={Main=q.completed_Main,x=x,y=y,native=r('Player_State'),selector=full_state(actor+3),part=full_part,index=full_index,
   held=full_state(0x301),saved=r('SavedJoypadBits'),body=body,target=target,cooldown=full_state(actor+8),pad=pad}
  if#t>20 then table.remove(t,6)end
 end
 if closeFight then
  local c=closeFight;local age=q.completed_Main-c.Main
  if q.captures>c.captures and q.pops>c.pops then
   flower.close_retired=flower.close_retired or{}
   flower.close_retired[#flower.close_retired+1]={Main=q.completed_Main,x=x,y=y,slot=c.slot,captures=q.captures-c.captures,pops=q.pops-c.pops}
   closeFight=nil;full_pad={};return true
  end
  assert(age<60,'Actual close-defence shot must trap and pop the threat')
  -- Stay clear while the projectile catches the real actor; approach only
  -- after actual source capture makes contact safe and needed for the pop.
  full_pad={right=q.captures>c.captures,b=age<4};return true
 end
 if not target or target.dx>48 then return false end
 local disjoint=body[3]<target.box[1]or body[1]>target.box[3]or body[4]<target.box[2]or body[2]>target.box[4]
 assert(disjoint,'Close-defence begins while actual native body/enemy boxes are disjoint')
 local aligned=math.abs(target.y-(y+8))<=8
 local ready=full_state(actor+8)==0 and full_state(0x301)&64==0
 if grounded and full_normal_jump_ready(actor)and aligned and ready and target.dx>=28 and target.dx<=40 then
  if full_state(0x102+(identity==1 and 8 or 0))&64==0 then full_pad={right=true};return true end
  closeFight={Main=q.completed_Main,slot=target.slot,captures=q.captures,pops=q.pops}
  flower.close_shots=flower.close_shots or{}
  flower.close_shots[#flower.close_shots+1]={Main=q.completed_Main,x=x,y=y,body=body,target=target,held=full_state(0x301),cooldown=full_state(actor+8)}
  full_pad={b=true};return true
 end
 -- Below the second-pipe lip the landing floor is real. Retire Right/A
 -- before touchdown and retreat while preserving a real safe landing foot.
 local safe=full_solid(x-8,208)and full_solid(x+7,208)
 full_pad={left=safe};return true
end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    text=Previous.controller(raw,identity,mode)
    if identity==1:return text
    once=Previous.Previous.Previous.Previous.Previous.once
    text=once(text,'local function full_tick_base(finish)',DEFENCE+'\nlocal function full_tick_base(finish)')
    marker=" if full_state(actor+3)&128~=0 or full_state(0x307)~=0 then full_fail('Fullstage source injury/death')end"
    text=once(text,marker,marker+'\n if closeThreat(q,actor,x,y,grounded)then return end')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def source_check(raw,identity=0):
    ns=dict(Previous.__dict__,controller=controller)
    exec(compile(inspect.getsource(Previous.source_check),str(Path(__file__))+':current-source-driver','exec'),ns)
    return ns['source_check'](raw,identity)
