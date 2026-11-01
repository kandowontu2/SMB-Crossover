"""Untimed original Excitebike NROM CPU oracle; no host/emulator claim.

PPUSTATUS alternates ready/not-ready to satisfy original explicit vblank waits.
It does not model raster timing, sprite-zero location or acoustic output.
"""
from pathlib import Path
import hashlib, sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import thomas_original_cpu_1031_v1 as T

DONOR=Path('C:/NES/Excitebike (Japan, USA) (En).nes')
SHA='4eac85fdf79ffb931103d910d6f9ae3b0db0affd1df833d5e2511055a5698489'
IDLE=0xc1d8

class Bus(T.Bus):
    def __init__(self,rom):
        assert len(rom)==24592 and rom[4:6]==bytes([1,1])
        # Thomas' reusable bus expects a32KB PRG image. NROM128 mirrors16KB.
        super().__init__(rom[:16]+rom[16:16400]*2+rom[16400:])
        self.status_reads=0
    def __getitem__(self,a):
        if not isinstance(a,slice) and 0x2000<=a<0x4000 and a&7==2:
            self.w=0;self.status_reads+=1
            return 0xc0 if self.status_reads&1 else 0
        return super().__getitem__(a)

def donor():
    raw=DONOR.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA;return raw

def machine():
    return T.NesMPU(memory=Bus(donor()),pc=None)

def until(c,pc=IDLE,limit=150000,trace=None):
    n=0
    while c.pc!=pc:
        if trace is not None:trace(c)
        assert c.memory[c.pc]!=0,('Unexpected donor BRK',hex(c.pc))
        c.step();n+=1
        assert n<limit,('Original execution bound',hex(c.pc),c.sp)
    return n

def boot():
    c=machine();until(c);return c

def frame(c,pad=0,trace=None):
    c.memory.pad=[pad,0];c.memory.writes=[];c.memory.apu=[];c.memory.ppuwrites=[]
    c.nmi()
    # Finish the genuine NMI, including its original RTI, before foreground.
    until(c,IDLE,trace=trace)
    c.step()
    return until(c,IDLE,trace=trace)

def call(c,pc,a=0,x=0,y=0,p=0x20,limit=30000):
    return T.run(c,pc,a,x,y,p,limit)
