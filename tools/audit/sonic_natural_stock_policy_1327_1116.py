"""Ordinary input policy around the retained current SMS-stage sensors."""
from pathlib import Path
import audit_sonic_stock_foundation_1327_1116 as F

STAGE_SHA='2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee'


def text():
    path=F.R/'tools/playthroughs/sonic_original_full_stage_stdout_1110.lua'
    assert F.H(path.read_bytes())==STAGE_SHA
    source=path.read_text();sensors=source[source.index('local function solid('):source.index('local function drive()')]
    return r'''
local P={};P.__index=P
local r=SONIC_READ
local function read(at)return SONIC_MEMORY(at)end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
'''+sensors+r'''
function P.new(kind)
 assert(kind=='life'or kind=='star'or kind=='flower')
 return setmetatable({kind=kind,phase='route',clock=0,lastJump=-100,hold=-1,at=0,lastA=false},P)
end
function P:decide(s,actors)
 self.clock=s.motor
 local target=({life=1024,star=1616,flower=336})[self.kind]
 local ready=s.state==0 and s.source_flags&8~=0
 local item=nil;for _,a in ipairs(actors)do if a.flag~=0 and a.id==46 then item=a end end
 local bits=self.clock>3 and 1 or 0
 if self.phase=='route'then
  if s.x>=target-64 and ready and s.y==176 then self.phase='align';self.at=self.clock
  elseif ready and self.clock-self.lastJump>24 then
   local why=jumpReason(s)
   if why then self.lastJump=self.clock;self.hold=self.clock+20 end
  end
 end
 if self.phase=='align'then
  bits=s.x<target-11 and 1 or s.x>target and 2 or 0
  if s.x>=target-11 and s.x<=target and ready and self.clock-self.lastJump>24 then
   self.phase='head';self.at=self.clock;self.lastJump=self.clock;self.hold=self.clock+20
  end
 elseif self.phase=='head'then
  bits=s.x<target-11 and 1 or s.x>target and 2 or 0
  if item then self.phase='collect';self.at=self.clock
  elseif self.clock-self.at>60 and ready then self.phase='align'end
 elseif self.phase=='collect'then
  if item then
   local dx=item.x-s.x;bits=dx>6 and 1 or dx< -6 and 2 or 0
   if ready and self.clock-self.lastJump>24 and math.abs(dx)<=30 and item.y<s.y-12 then self.lastJump=self.clock;self.hold=self.clock+20 end
  else bits=0 end
 end
 if self.clock<self.hold then bits=bits|128 end
 self.lastA=bits&128~=0;return bits
end
return P
'''
