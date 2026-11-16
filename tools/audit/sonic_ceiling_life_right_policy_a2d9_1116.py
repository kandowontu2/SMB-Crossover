"""Meet the right-moving native1UP from the safe right side of its block."""
from pathlib import Path
import sonic_ceiling_life_side_policy_a2d9_1116 as Previous

PREVIOUS_SHA='c691caa725d5c326ef710794c06dd746bedc27dce193644b66e66a9f0ad06322'


def text():
    assert Previous.Previous.Prior.F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    s=Previous.text()
    for a,b in(('local lo,hi=target-48,target-40','local lo,hi=target+24,target+32'),
        ("self.phase='collect';self.at=self.clock;self.lastJump=self.clock;self.hold=self.clock+20;bits=1",
         "self.phase='collect';self.at=self.clock;self.lastJump=self.clock;self.hold=self.clock+20;bits=2")):
        assert s.count(a)==1;s=s.replace(a,b)
    return s
