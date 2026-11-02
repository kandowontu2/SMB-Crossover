"""Authenticated DK Jr NROM128 instruction oracle, with untimed PPU services.

This is not a native NES timing test. The original reset/NMI/controller/game
instructions execute. PPUSTATUS reports ready, and one original foreground
random-number iteration runs between supplied NMI epochs.
"""
from pathlib import Path
import hashlib,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import thomas_original_cpu_1031_v1 as T
DONOR=Path('C:/NES/Donkey Kong Jr. (World) (Rev 1).nes')
SHA='1bc7fdc98c29b2c51438c3ce92ca37fac61b939a7cf100c644fed37206cf2cf6'
IDLE=0xc6b0

def donor():
    b=DONOR.read_bytes()
    assert len(b)==24592 and b[4:6]==bytes([1,1])
    assert hashlib.sha256(b).hexdigest()==SHA
    return b

class Bus(T.Bus):
    def __init__(self,raw=None):
        b=raw or donor()
        super().__init__(b[:16]+b[16:16400]*2+b[16400:])

def until(c,pc=IDLE,limit=150000,trace=None):
    n=0
    while c.pc!=pc:
        if trace:trace(c)
        assert c.memory[c.pc]!=0,('Unexpected BRK',hex(c.pc))
        c.step();n+=1
        assert n<limit,('Instruction bound',hex(c.pc),c.sp)
    return n

def boot():
    c=T.NesMPU(memory=Bus(),pc=None);until(c);return c

def frame(c,pad=0,trace=None):
    m=c.memory;m.pad=[pad,0];m.writes=[];m.apu=[];m.ppuwrites=[]
    c.nmi();n=until(c,trace=trace)
    c.step();return n+until(c,trace=trace)

def active():
    c=boot()
    for f in range(600):
        frame(c,0x10 if 20<=f<22 else 0)
        if c.memory[0x46]==1 and c.memory[0x6b]==1:return c,f+1
    raise AssertionError('Original first scene did not activate')

def state(c):
    m=c.memory
    return dict(x=m[0x213],y=m[0x210],state=m[0x6b],previous=m[0x6c],
                facing=m[0x6d],pose=m[0x211],held=m[0x14],sample=m[0x15],
                direction=m[0x54],vine_grip=m[0x71],air_epoch=m[0x7e],
                hfrac=m[0x56],vfrac=m[0x7f],gravity_lo=m[0x82],gravity_hi=m[0x83])
