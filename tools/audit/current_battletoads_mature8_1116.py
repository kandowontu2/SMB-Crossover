"""Strict actual91dc model; exact6a3 inverse is reference only."""
from functools import lru_cache
from unittest.mock import patch
import compose_battletoads_mature8_1116 as C
import current_battletoads_stock_6a3_1116 as Previous

R,ROM,PIN,W,N,Frames=C.R,C.ROM,C.CANDIDATE,Previous.W,Previous.N,Previous.Frames
IDENTITIES=Previous.IDENTITIES

@lru_cache(maxsize=1)
def reference(raw):return C.inverse(raw)

@lru_cache(maxsize=1)
def bundle(raw):reference(raw);return dict(W.Symbols.bundle(),raw=raw)

def cold(raw,key='rash',report=False):
    reference(raw);name,cycle,variant=IDENTITIES[key];b=bundle(raw)
    expected=bytearray(raw[C.CACHE:C.CACHE+8192]);expected[0x1fe0:0x1ff0]=raw[C.COOKIE:C.COOKIE+16]
    assert C.digest(raw[C.CACHE:C.CACHE+8192])==C.lease()['payload']['new_SHA256']
    assert C.digest(raw[C.HEADER:C.HEADER+487])==C.lease()['payload']['new_native_header487_SHA256']
    entry=W.address(b,'BtConstruct');reads=[];base=N.NesMPU
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc==entry and m.rawtags[(entry-0x8000)//8192]==3 and not reads:
                assert bytes(m.ram[3])==expected,'Actual entire8192 newcache/full16cookie before constructor'
                reads.append(dict(PC=self.pc,SP=self.sp,bytes=8192,SHA256=C.digest(bytes(m.ram[3])),cookie=expected[0x1fe0:0x1ff0].hex()))
            return super().step()
    class Factory:
        @staticmethod
        def bindings(image,identity):
            assert image is raw and identity==key
            return dict(name=name,variant=variant,navigation=[2,4,4]+[32]*cycle)
    with patch.object(Previous.Cold,'Factory',Factory),patch.object(N,'NesMPU',CPU):m=Previous.Cold.cold(raw,key)
    assert reads and m.bundle['raw']is raw
    q=dict(actual_ROM_SHA256=PIN,identity=key,variant=variant,first_constructor_readback=reads[0],
        frontend='Real compiled menu/Select/Start/parser/constructor; no real title vblank in source bus',outputs=0,Mesen=False)
    m.bt_stock_opening=q
    return(m,q)if report else m

def preservation(raw):
    reference(raw)
    return dict(actual_execution_SHA256=PIN,parent_reference_SHA256=C.PIN,
        granted_spans=C.lease()['spans'],all_unowned_bytes_exact=True,old_factories_unchanged=True,outputs=0)
