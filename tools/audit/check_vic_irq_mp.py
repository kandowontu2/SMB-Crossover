"""Compare actual linked IRQ PPU write cycles and interrupted register state."""
from pathlib import Path
import hashlib
import json
import random
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
sys.path.insert(0,str(R/'tools/audit'))
from verify_native_relocation import NesMPU

O=R/'build/verification/vic-adoption-mp'


class Memory(list):
    def __setitem__(self,key,value):
        if isinstance(key,int) and key in (0x2005,0x2006,0x5128):
            self.writes.append((key,value,self.cpu.processorCycles))
        super().__setitem__(key,value)


def labels(path):
    result={}
    for line in path.with_suffix('.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line)
        if m:result[m[2]]=int(m[1],16)
    return result


def run(path,params):
    raw=path.read_bytes();l=labels(path)
    m=Memory([0]*65536)
    m[0x8000:0xa000]=raw[16+126*8192:16+127*8192]
    m[l['IrqNewScroll']]=params['scroll']
    m[l['IrqPPUCTRL']]=params['page']
    m[0]=params['scratch']
    cpu=NesMPU(memory=m);m.cpu=cpu;m.writes=[]
    cpu.pc=l['IrqScrollSplit'];cpu.a=params['a'];cpu.x=params['x'];cpu.y=params['y'];cpu.p=0x24;cpu.sp=0xef
    cpu.stPushWord(0x5b00);cpu.stPush(0x24)
    steps=0
    while cpu.pc!=0x5b00:
        cpu.step();steps+=1
        assert steps<100
    assert (cpu.a,cpu.x,cpu.y,cpu.sp)==(params['a'],params['x'],params['y'],0xef)
    return m.writes,m[l['IrqNewScroll']],cpu.p


def main():
    old=R/'build/checkpoints/tmnt-roster-mn/build/smb-crossover-mmc5-expanded.nes'
    new=O/'vic-composed-final.nes'
    rng=random.Random(0x47524144)
    count=0
    for scroll in range(256):
        for page in (0,1):
            p=dict(scroll=scroll,page=page,scratch=rng.randrange(256),a=rng.randrange(256),x=rng.randrange(256),y=rng.randrange(256))
            a,ashadow,ap=run(old,p);b,bshadow,bp=run(new,p)
            aw=[v for v in a if v[0]!=0x5128];bw=[v for v in b if v[0]!=0x5128]
            assert [v[:2] for v in aw]==[v[:2] for v in bw],(p,aw,bw)
            assert aw[0]==bw[0] and aw[-2:]==bw[-2:],(p,aw,bw)
            assert ashadow==bshadow and ap==bp
            font=[v for v in b if v[0]==0x5128]
            assert len(font)==1 and font[0][1]==0 and font[0][2]<bw[-2][2]
            count+=1
    report=dict(passed=True,linked_IRQ_cases=count,PPU_page_and_scroll_values_exact=True,
                first_page_write_and_last_two_scroll_write_CPU_cycles_exact=True,
                interrupted_A_X_Y_P_and_stack_exact=True,world_font_precedes_scroll_latch=True,
                old_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),new_sha256=hashlib.sha256(new.read_bytes()).hexdigest())
    (O/'irq-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
