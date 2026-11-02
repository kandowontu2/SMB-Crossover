"""Original Prince NES UxROM CPU oracle with explicitly untimed peripherals.

This is an instruction oracle, not a Mesen/raster/audio qualification. Original
reset, controller, NMI, bank writes, CHR-RAM uploads and foreground code execute.
PPUSTATUS readiness alternates; NMI is delivered at the original F2FC wait.
"""
from pathlib import Path
import hashlib,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import thomas_original_cpu_1031_v1 as T
DONOR=Path('C:/NES/Prince of Persia (USA).nes')
SHA='5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4'
IDLE=0xf2fc


class Bus(T.Bus):
 def __init__(self,rom):
  assert len(rom)==131088 and rom[4:6]==bytes([8,0])
  self.rom=rom;self.bank=0;self.mapper_writes=[];self.status_reads=0
  super().__init__(rom[:16]+rom[16:16400]+rom[-16384:])
  self.ppu=bytearray(0x4000)
  self.switch(0)
 def switch(self,bank):
  self.bank=bank&7
  list.__setitem__(self,slice(0x8000,0xc000),self.rom[16+self.bank*16384:16+(self.bank+1)*16384])
 def __getitem__(self,a):
  if not isinstance(a,slice) and 0x2000<=a<0x4000 and a&7==2:
   self.w=0;self.status_reads+=1
   return 0xc0 if self.status_reads&1 else 0
  return super().__getitem__(a)
 def __setitem__(self,a,value):
  if isinstance(a,int):
   a&=65535;value&=255
   if a>=0x8000:
    # Original bank writes use the fixed FFF0..FFF7 value table; retain the
    # physical bus-conflict AND as well as the selected 16KB bank.
    effective=value&list.__getitem__(self,a)
    self.mapper_writes.append((a,value,effective&7));self.switch(effective);return
   if 0x2000<=a<0x4000 and a&7==7:self.ppu[self.pa(self.v)]=value
  return super().__setitem__(a,value)


def donor():
 raw=DONOR.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA;return raw


def machine():return T.NesMPU(memory=Bus(donor()),pc=None)


def until(c,pc=IDLE,*,sp=None,limit=800000,trace=None):
 n=0
 while c.pc!=pc or(sp is not None and c.sp!=sp):
  if trace is not None:trace(c)
  assert c.memory[c.pc]!=0,('Unexpected original BRK',c.memory.bank,hex(c.pc),c.sp)
  c.step();n+=1
  assert n<limit,('Original execution bound',c.memory.bank,hex(c.pc),c.sp)
 return n


def boot(trace=None):
 c=machine();until(c,trace=trace);return c


def frame(c,pad=0,trace=None):
 m=c.memory;m.pad=[pad,0];m.writes=[];m.apu=[];m.ppuwrites=[];m.mapper_writes=[]
 sp=c.sp;c.nmi();n=until(c,sp=sp,trace=trace)
 if trace is not None:trace(c)
 c.step();return n+until(c,trace=trace)


def call(c,pc,**kw):return T.run(c,pc,**kw)
