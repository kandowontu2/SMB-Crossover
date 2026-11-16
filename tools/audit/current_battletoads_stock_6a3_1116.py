"""Strict actual6a3 Battletoads stock boundary; inverse is reference only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import compose_bowser_life_gain_signed_1116 as Life
import replay_battletoads_stair_progress_1115 as Frozen
import check_battletoads_full11_current_1114 as Cold

R,ROM,PIN,W,N=Life.R,Life.ROM,Life.CANDIDATE,Frozen.W,Frozen.N
Frames=Cold.Runner.Frames
digest=Life.digest
CACHE=1989648
HEADER=16+93*8192+0xdc0
COOKIE=765863
FROZEN_SHA='fd22928a899457c1ce0d2b6c5e16c891eef735e47fc92d34d655dbfcbf37b752'
LIFE_SHA='2b5d81f056991636bf2498d4871645ea1cd80b003d2d986504b46b89d8b013b7'
IDENTITIES={'rash':('RASH',0,0),'zitz':('ZITZ',1,32)}

@lru_cache(maxsize=1)
def reference(raw):
    assert digest(Path(Life.__file__).read_bytes())==LIFE_SHA
    assert digest(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Exact current6a3 required'
    parent=Life.inverse(raw);assert digest(parent)==Life.PIN
    assert raw[CACHE:CACHE+8192]==parent[CACHE:CACHE+8192]
    assert raw[HEADER:HEADER+487]==parent[HEADER:HEADER+487]
    return parent

@lru_cache(maxsize=1)
def preservation(raw):
    parent=reference(raw);rows=[]
    spans=[('Bt private cache',CACHE,8192),('Bt native loader/services/header',HEADER,487),
           ('Hot drawing classifier',Frozen.C.FILE,Frozen.C.SIZE)]
    spans += [('Carry owned span '+str(i),at,len(bytes.fromhex(h)))for i,(at,h)in enumerate(Frozen.C.Carry.PREIMAGES)]
    for name,at,size in spans:
        assert raw[at:at+size]==parent[at:at+size]
        rows.append(dict(name=name,file=at,bytes=size,SHA256=digest(raw[at:at+size])))
    return dict(actual_execution_SHA256=PIN,reference_bc5_SHA256=digest(parent),
        boundary='Strict signed Bowser inverse for reference only; actual6a3 CPU',
        exact_current_BT_extents=rows,full16_Bt_cookie=raw[COOKIE:COOKIE+16].hex(),
        Bowser72_owned_bytes_preserved_in_execution=True,game_bytes_changed=0,outputs=0)

@lru_cache(maxsize=1)
def bundle(raw):reference(raw);return dict(W.Symbols.bundle(),raw=raw)

def cold(raw,key='rash',report=False):
    preservation(raw);name,cycle,variant=IDENTITIES[key];b=bundle(raw)
    expected=bytearray(raw[CACHE:CACHE+8192]);expected[0x1fe0:0x1ff0]=raw[COOKIE:COOKIE+16]
    entry=W.address(b,'BtConstruct');reads=[];base=N.NesMPU
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc==entry and m.rawtags[(entry-0x8000)//8192]==3 and not reads:
                assert bytes(m.ram[3])==expected,'Actual8192-byte BT cold load and full16 cookie before constructor'
                reads.append(dict(PC=self.pc,SP=self.sp,bytes=8192,SHA256=digest(bytes(m.ram[3])),cookie=expected[0x1fe0:0x1ff0].hex()))
            return super().step()
    class Factory:
        @staticmethod
        def bindings(image,identity):
            assert image is raw and identity==key
            return dict(name=name,variant=variant,navigation=[2,4,4]+[32]*cycle)
    with patch.object(Cold,'Factory',Factory),patch.object(N,'NesMPU',CPU):m=Cold.cold(raw,key)
    assert reads and m.bundle['raw']is raw
    assert N.get(m,'CrossoverMenuIndex')==23 and N.get(m,'SelectedCharacter')==33
    assert N.get(m,'FmGroups')==64+variant and N.get(m,'CrossoverBehaviorVersion')==0
    q=dict(actual_ROM_SHA256=PIN,identity=key,variant=variant,first_constructor_readback=reads[0],
        frontend='Actual compiled Left/Down/Down/Select/Start/parser/constructor; source bus lacks real title vblank',
        gameplay_seeds=0,outputs=0,Mesen=False)
    m.bt_stock_opening=q
    return(m,q)if report else m
