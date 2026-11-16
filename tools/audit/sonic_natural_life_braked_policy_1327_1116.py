"""Controller-only braked launch after the retained moving-target negative."""
from pathlib import Path
import sonic_natural_stock_policy_1327_1116 as Prior

PRIOR_SHA='e1891238461f31a7211460f1eb232f9a868769f8404760e87f2e7698ef9fd73b'


def text():
    assert Prior.F.H(Path(Prior.__file__).read_bytes())==PRIOR_SHA
    s=Prior.text()
    old="  if s.x>=target-11 and s.x<=target and ready and self.clock-self.lastJump>24 then"
    new="  if s.x>=target-11 and s.x<=target and math.abs(s.vx)>64 then bits=s.vx>0 and 2 or 1 end\n  if s.x>=target-11 and s.x<=target and math.abs(s.vx)<=64 and ready and self.clock-self.lastJump>24 then"
    assert s.count(old)==1;s=s.replace(old,new)
    old=" elseif self.phase=='head'then\n  bits=s.x<target-11 and 1 or s.x>target and 2 or 0"
    new=" elseif self.phase=='head'then\n  bits=0"
    assert s.count(old)==1;return s.replace(old,new)
