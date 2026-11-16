"""Explicit6a3 candidate cold transport and owning-reference boundary."""
from functools import lru_cache
from unittest.mock import patch
import compose_bowser_life_gain_signed_1116 as C

R,ROM,PIN,W,N,Frames=C.R,C.ROM,C.CANDIDATE,C.Current.W,C.Current.N,C.Current.Frames
digest=C.digest

def bundle(raw):C.inverse(raw);return dict(W.Symbols.bundle(),raw=raw)

@lru_cache(maxsize=1)
def image(raw):
    parent=C.inverse(raw);_,_,after,_=C.Plan.proposal(parent);assert digest(after)==C.lease()['payload']['proposed_SHA256'];return after

def cold(raw,key='smb3',report=False):
    b=bundle(raw);identity={'smb3':0,'smb1':1}[key];expected=bytearray(image(raw));cookie=bytes.fromhex(C.lease()['cookie_views']['new_hex'])
    expected[0x1fe0:0x1ff0]=cookie;base=N.NesMPU;reads=[];entry=W.address(b,'BwConstruct')
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc==entry and m.rawtags[1]==3 and not reads:
                assert bytes(m.ram[3])==expected,'Actual complete8192B load +full16cookie before first constructor'
                reads.append(dict(PC=self.pc,SP=self.sp,bytes=8192,cookie=cookie.hex(),payload_SHA256=digest(bytes(m.ram[3]))))
            return super().step()
    with patch.object(N,'NesMPU',CPU):m,opening=C.Current.Historical.cold(raw,identity)
    assert reads and bytes(m.ram[3][:2615])==image(raw)[:2615]
    assert bytes(m.ram[3][0x1fe0:0x1ff0])==cookie
    assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    q=dict(opening=opening,first_actual_constructor_readback=reads[0],executable2615_SHA256=digest(bytes(m.ram[3][:2615])),
        ROM_SHA256=PIN,source_frontend='Compiled actual grid/Select/Start/parser; source bus lacks real title vblank',outputs=0,Mesen=False)
    m.bowser_life_opening=q
    return(m,q)if report else m
