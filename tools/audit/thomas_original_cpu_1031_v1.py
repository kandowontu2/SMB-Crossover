"""Original Kung Fu CPU oracle with explicitly untimed PPU/controller services.

This executes the donor's reset, NMI, parser and gameplay instructions. PPU
status supplies vblank/sprite-zero readiness, not a raster/timing simulation.
"""
from pathlib import Path
import hashlib,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_native_relocation import NesMPU

DONOR=Path('C:/NES/Kung Fu (Japan, USA) (En).nes')
EXPECTED='2275213352411a23df7428496ad03991348ddee3034ac6db83d2d16f0d1f8554'

class Bus(list):
    def __init__(self,rom):
        super().__init__([0]*65536);super().__setitem__(slice(0x8000,0x10000),rom[16:0x8010])
        self.ppu=bytearray(0x4000);self.ppu[:8192]=rom[0x8010:]
        self.oam=bytearray(256);self.ctrl=0;self.mask=0;self.v=0;self.w=0;self.hi=0;self.buffer=0;self.oamaddr=0
        self.pad=[0,0];self.serial=[0,0];self.strobe=0
        self.apu=[];self.writes=[];self.ppuwrites=[]
    def pa(self,a):
        a&=0x3fff
        if 0x3000<=a<0x3f00:a-=0x1000
        if 0x2000<=a<0x3000:a=0x2000+((a-0x2000)&0x7ff) # original vertical mirroring
        if a>=0x3f00:
            a=0x3f00+(a&31)
            if a in [0x3f10,0x3f14,0x3f18,0x3f1c]:a-=16
        return a
    def __getitem__(self,a):
        if isinstance(a,slice):return super().__getitem__(a)
        a&=65535
        if a<0x2000:return super().__getitem__(a&0x7ff)
        if 0x2000<=a<0x4000:
            reg=a&7
            if reg==2:self.w=0;return 0xc0
            if reg==4:return self.oam[self.oamaddr]
            if reg==7:
                at=self.pa(self.v);v=self.ppu[at];old=self.buffer;self.buffer=v;self.v=(self.v+(32 if self.ctrl&4 else 1))&0x7fff
                return v if at>=0x3f00 else old
            return 0
        if a in [0x4016,0x4017]:
            p=a-0x4016;i=min(self.serial[p],8);v=(self.pad[p]>>(7-i))&1 if i<8 else 1
            if not self.strobe:self.serial[p]+=1
            return v
        return super().__getitem__(a)
    def __setitem__(self,a,value):
        if isinstance(a,slice):return super().__setitem__(a,value)
        a&=65535;value&=255
        if a<0x2000:
            a&=0x7ff;super().__setitem__(a,value);self.writes.append((a,value));return
        if 0x2000<=a<0x4000:
            reg=a&7
            if reg==0:self.ctrl=value
            elif reg==1:self.mask=value
            elif reg==3:self.oamaddr=value
            elif reg==4:self.oam[self.oamaddr]=value;self.oamaddr=(self.oamaddr+1)&255
            elif reg==5:self.w^=1
            elif reg==6:
                if self.w:self.v=(self.hi<<8)|value
                else:self.hi=value&0x3f
                self.w^=1
            elif reg==7:
                at=self.pa(self.v)
                if at>=8192:self.ppu[at]=value
                self.ppuwrites.append((at,value));self.v=(self.v+(32 if self.ctrl&4 else 1))&0x7fff
            return
        if a==0x4014:
            self.oam[:]=bytes(self[(value<<8)+i]for i in range(256));return
        if a==0x4016:self.strobe=value&1;self.serial=[0,0];return
        if 0x4000<=a<=0x4017:self.apu.append((a,value));return
        if a<0x8000:super().__setitem__(a,value)

def donor():
    r=DONOR.read_bytes();assert hashlib.sha256(r).hexdigest()==EXPECTED;return r

def labels(path):
    out={}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        m=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line)
        if m:out[m[2]]=int(m[1],16)
    return out

def machine(rom=None):
    bus=Bus(rom or donor());c=NesMPU(memory=bus,pc=None);return c

def until_idle(c,limit=120000):
    steps=0
    while c.pc!=0x82d3:
        c.step();steps+=1
        assert steps<limit,(hex(c.pc),c.sp)
    return steps

def boot():
    c=machine();until_idle(c);return c

def frame(c,pad=0,pad2=0):
    c.memory.pad=[pad,pad2];c.memory.writes=[];c.memory.apu=[];c.memory.ppuwrites=[]
    c.nmi();return until_idle(c)

def run(c,pc,a=0,x=0,y=0,p=0x20,limit=15000):
    c.a,c.x,c.y,c.p,c.sp=a,x,y,p,0xfd;c.stPushWord(0x5ffe);c.pc=pc
    c.memory.writes=[];c.memory.apu=[];c.memory.ppuwrites=[]
    n=0;cycles=c.processorCycles
    while c.pc!=0x5fff:
        c.step();n+=1;assert n<limit,(hex(pc),hex(c.pc))
    return (c.a,c.x,c.y,c.p,c.sp,c.processorCycles-cycles)

if __name__=='__main__':
    c=boot();states=[]
    for f in range(650):
        frame(c,0x10 if 120<=f<125 else 0)
        if f%50==0:states.append(dict(frame=f,mode=c.memory[0x50],scene=c.memory[0x51],state=c.memory[0x69],counter=c.memory[0x68],hp=c.memory[0x4a6]))
    print(json.dumps(states))
