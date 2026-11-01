"""Metal Storm donor CPU oracle; PPU readiness is untimed, not native proof."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tools/audit')]
from verify_native_relocation import NesMPU

ROM=Path('C:/NES/Metal Storm (USA).nes')
EXPECTED='22e7576958e842c564153bf799293cedf90c6a0aaee302b73ec8af88a7481d87'

def donor():
    b=ROM.read_bytes();assert hashlib.sha256(b).hexdigest()==EXPECTED
    return b

class Bus(bytearray):
    def __init__(self,rom=None):
        super().__init__(65536)
        b=rom or donor();self.prg=b[16:16+131072];self.chr=b[16+131072:]
        self.regs=[0]*8;self.select=0;self.mirror=0
        self.ppu=bytearray(0x4000);self.oam=bytearray(256)
        self.ctrl=0;self.mask=0;self.v=0;self.w=0;self.hi=0;self.buffer=0;self.oamaddr=0
        self.pad=[0,0];self.serial=[0,0];self.strobe=0
        self.apu=[];self.writes=[];self.ppuwrites=[];self.mapperwrites=[]
        self.map()
    def map(self):
        banks=[self.regs[6]&15,self.regs[7]&15,14,15]
        if self.select&64:banks[0],banks[2]=banks[2],banks[0]
        self.banks=banks
        for i,b in enumerate(banks):super().__setitem__(slice(0x8000+i*8192,0xa000+i*8192),self.prg[b*8192:(b+1)*8192])
    def ca(self,a):
        r=self.regs
        banks=[r[0]&254,(r[0]&254)+1,r[1]&254,(r[1]&254)+1,r[2],r[3],r[4],r[5]]
        if self.select&128:banks=banks[4:]+banks[:4]
        return (banks[a//1024]*1024+(a&1023))%len(self.chr)
    def pa(self,a):
        a&=0x3fff
        if 0x3000<=a<0x3f00:a-=0x1000
        if 0x2000<=a<0x3000:
            n=(a-0x2000)//1024
            n=n//2 if self.mirror else n&1
            a=0x2000+n*1024+(a&1023)
        if a>=0x3f00:
            a=0x3f00+(a&31)
            if a in [0x3f10,0x3f14,0x3f18,0x3f1c]:a-=16
        return a
    def ppuread(self,a):
        a=self.pa(a)
        return self.chr[self.ca(a)]if a<8192 else self.ppu[a]
    def __getitem__(self,a):
        if isinstance(a,slice):return super().__getitem__(a)
        a&=65535
        if a<0x2000:return super().__getitem__(a&0x7ff)
        if 0x2000<=a<0x4000:
            reg=a&7
            if reg==2:self.w=0;return 0xc0
            if reg==4:return self.oam[self.oamaddr]
            if reg==7:
                at=self.pa(self.v);v=self.ppuread(at);old=self.buffer;self.buffer=v;self.v=(self.v+(32 if self.ctrl&4 else 1))&0x7fff
                return v if at>=0x3f00 else old
            return 0
        if a in [0x4016,0x4017]:
            p=a-0x4016;i=min(self.serial[p],8);v=(self.pad[p]>>(7-i))&1 if i<8 else 1
            if not self.strobe:self.serial[p]+=1
            return v
        return super().__getitem__(a)
    def __setitem__(self,a,v):
        if isinstance(a,slice):return super().__setitem__(a,v)
        a&=65535;v&=255
        if a<0x2000:
            a&=0x7ff;super().__setitem__(a,v);self.writes.append((a,v));return
        if 0x2000<=a<0x4000:
            reg=a&7
            if reg==0:self.ctrl=v
            elif reg==1:self.mask=v
            elif reg==3:self.oamaddr=v
            elif reg==4:self.oam[self.oamaddr]=v;self.oamaddr=(self.oamaddr+1)&255
            elif reg==5:self.w^=1
            elif reg==6:
                if self.w:self.v=(self.hi<<8)|v
                else:self.hi=v&0x3f
                self.w^=1
            elif reg==7:
                at=self.pa(self.v)
                if at>=8192:self.ppu[at]=v
                self.ppuwrites.append((at,v));self.v=(self.v+(32 if self.ctrl&4 else 1))&0x7fff
            return
        if a==0x4014:self.oam[:]=bytes(self[(v<<8)+i]for i in range(256));return
        if a==0x4016:self.strobe=v&1;self.serial=[0,0];return
        if 0x4000<=a<=0x4017:self.apu.append((a,v));return
        if a>=0x8000:
            self.mapperwrites.append((a,v))
            if a&0xe001==0x8000:self.select=v;self.map()
            elif a&0xe001==0x8001:self.regs[self.select&7]=v;self.map()
            elif a&0xe001==0xa000:self.mirror=v&1
            return
        super().__setitem__(a,v)
    def physical(self,a):return self.banks[(a-0x8000)//8192]*8192+(a&8191)

def machine():return NesMPU(memory=Bus(),pc=None)

def until_idle(c,limit=150000,coverage=None,trace=None):
    n=0
    while c.pc!=0xfcba:
        if coverage is not None and c.pc>=0x8000:coverage.add(c.memory.physical(c.pc))
        if trace is not None:trace(c)
        assert c.memory[c.pc]!=0,('BRK',hex(c.pc),c.memory.banks)
        c.step();n+=1
        assert n<limit,('bound',hex(c.pc),c.memory.banks,c.sp)
    return n

def boot():
    c=machine();until_idle(c);return c

def frame(c,pad=0,coverage=None,trace=None):
    c.memory.pad=[pad,0];c.memory.writes=[];c.memory.ppuwrites=[];c.memory.apu=[];c.memory.mapperwrites=[]
    c.nmi();return until_idle(c,coverage=coverage,trace=trace)

def call(c,pc,a=0,x=0,y=0,p=0x30,limit=20000,trace=None):
    c.pc,c.a,c.x,c.y,c.p,c.sp=pc,a,x,y,p,0xf0;c.stPushWord(0x5ffe);n=0;cycles=c.processorCycles
    c.memory.writes=[];c.memory.apu=[]
    while c.pc!=0x5fff:
        if trace is not None:trace(c)
        assert c.memory[c.pc]!=0,('BRK',hex(c.pc));c.step();n+=1
        assert n<limit,('bound',hex(c.pc),c.memory.banks,c.sp)
    assert c.sp==0xf0
    return(c.a,c.x,c.y,c.p,c.sp,c.processorCycles-cycles)

def main():
    out=ROOT/'build/metal-storm-component-1101-v2';out.mkdir(exist_ok=True)
    c=boot();cov=set();maxsteps=0
    for tick in range(1000):
        pad=0x10 if tick in [120,121,300,301,480,481]else 0
        maxsteps=max(maxsteps,frame(c,pad,coverage=cov))
    result=dict(passed=True,CPU_untimed=True,native=False,installed=False,ROM_sha256=EXPECTED,frames=1000,maxsteps=maxsteps,executed_instruction_addresses=len(cov),final_PRG_banks=c.memory.banks)
    (out/'discovery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(frames=1000,maxsteps=maxsteps,instructions=len(cov),banks=c.memory.banks)))

if __name__=='__main__':main()
