"""Exact first constructor-tail writer in retained5cfa cold negative."""
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_sword_tier2_earned_1115 as Test

C,N,W=Test.C,Test.N,Test.W

def run(parent):
    raw,_=C.proposal(parent);current=None;writes=[];cuts=[];base=W.ControllerBus;cpu=N.NesMPU
    class Bus(base):
        def __setitem__(self,at,value):
            if isinstance(at,int)and 0xc0f6<=at<0xc100 and current is not None and current.memory is self and self.rawtags[2]==2:
                old=self[at]
                if value!=old:
                    assert len(writes)<128
                    writes.append(dict(address=at,before=old,after=value,PC=current.before_PC,SP=current.sp,maps=list(self.rawtags)))
            return super().__setitem__(at,value)
    class CPU(cpu):
        def step(self):
            nonlocal current
            current=self;self.before_PC=self.pc
            if self.pc in(0xc0b0,0xc0f6)and self.memory.rawtags[2]==2:
                cuts.append(dict(PC=self.pc,SP=self.sp,tail=bytes(self.memory[0xc0f0:0xc100]).hex()))
            return super().step()
    try:
        with patch.object(W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU):Test.cold(raw)
    except AssertionError as error:
        return dict(passed=False,retained_negative=True,candidate_SHA256=C.CANDIDATE,error=repr(error),writes=writes,cuts=cuts,outputs=0,Mesen=False)
    raise AssertionError('Expected retained constructor-tail negative')

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Cold negative trace attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
