"""Ordinary side approach and post-pickup braking; no game state writes."""
from pathlib import Path
import sonic_natural_life_braked_policy_1327_1116 as Previous

PREVIOUS_SHA='3226b589d1b7c0baa090bf4b60a49e8db1d76687938211c773eb75dfd6b9c845'


def text():
    assert Previous.Prior.F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    source=Previous.text()
    a="if item then self.phase='collect';self.at=self.clock"
    b="if item then self.phase='side_align';self.at=self.clock"
    assert source.count(a)==1;source=source.replace(a,b)
    a=" elseif self.phase=='collect'then"
    b=""" elseif self.phase=='side_align'then
  local lo,hi=target-48,target-40
  bits=s.x<lo and 1 or s.x>hi and 2 or 0
  if s.x>=lo and s.x<=hi and math.abs(s.vx)>64 then bits=s.vx>0 and 2 or 1 end
  if s.x>=lo and s.x<=hi and math.abs(s.vx)<=64 and ready and self.clock-self.lastJump>24 and not self.lastA then
   self.phase='collect';self.at=self.clock;self.lastJump=self.clock;self.hold=self.clock+20;bits=1
  end
 elseif self.phase=='collect'then"""
    assert source.count(a)==1;source=source.replace(a,b)
    a="local dx=item.x-s.x;bits=dx>6 and 1 or dx< -6 and 2 or 0"
    b=a+"\n   if ready and self.clock-self.lastJump>24 and jumpReason(s)then self.lastJump=self.clock;self.hold=self.clock+20 end"
    assert source.count(a)==1;source=source.replace(a,b)
    a="  else bits=0 end"
    b="  else bits=s.vx>64 and 2 or s.vx< -64 and 1 or 0 end"
    assert source.count(a)==1;return source.replace(a,b)
