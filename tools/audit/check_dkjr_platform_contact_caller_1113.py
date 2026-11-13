"""Current native caller A/NZCV liveness differential; no ROM modification."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_descending_contact_1113 as C

N,W,L,P,H=C.N,C.W,C.L,C.P,C.H


def run(seed,slot,timer,taint=None):
    C.SLOT=slot;m=C.setup(seed)
    N.put(m,TimerControl=timer,ObjectOffset=slot)
    Base=N.NesMPU;hits=0
    class Probe(Base):
        def step(self):
            nonlocal hits
            if self.pc==0xb442 and self.memory.rawtags[1]==128:
                hits+=1
                if taint is not None:
                    self.a=taint[0]
                    self.p=(self.p&~0xc3)|taint[1]
            return Base.step(self)
    with patch.object(N,'NesMPU',Probe):
        result=N.invoke(m,'RunLargePlatform',a=85,x=slot,y=91,p=0x31)
    assert hits==1,(slot,timer,hits)
    return m,result


def digest(m,result):
    native=bytearray(m[:0x800]);native[0x100:0x1df]=bytes(223)
    return (bytes(native),tuple(bytes(r)for r in m.ram),tuple(m.rawtags),
        bytes(m.vram),tuple(m.chr_latches),tuple(result[k]for k in('A','X','Y','P')))


def main():
    from compose_dkjr_platform_contact_1113 import load_parent
    raw=load_parent()
    assert sha256(raw).hexdigest()==P.PRINCE_PROPOSAL
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    cases=0
    for slot,timer in product((0,3,5),(0,1)):
        baseline=digest(*run(seed,slot,timer))
        for a,flags in product((0,1,40,255),range(16)):
            p=(flags&3)|((flags&4)<<4)|((flags&8)<<4)
            got=digest(*run(seed,slot,timer,(a,p)))
            assert got==baseline,(slot,timer,a,hex(p),[i for i,(x,y)in enumerate(zip(got,baseline))if x!=y])
            cases+=1
    print('DKJR_PLATFORM_CALLER '+json.dumps(dict(passed=True,ROM_SHA256=sha256(raw).hexdigest(),
        checker_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        actual_native_post_dispatch_address=0xb442,A_NZCV_taint_cases=cases,
        source_WRAM_native_fields_maps_graphics_return_AXYP_equal=True,
        excluded='Only dead foreground hardware-stack bytes0100..01DE; live return stack is exact.',
        ROM_written=False,outputs_written=0,
        scope='Declared current DK component fixture, actual unchanged RunLargePlatform suffix. No new candidate, foreign-owner or complete-Main claim.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
