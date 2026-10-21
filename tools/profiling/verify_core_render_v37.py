"""Actual-ROM RP2A03 differentials for score/header work; initialized units."""
from pathlib import Path
import argparse, hashlib, importlib.util, itertools, json, random

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('native_unit',ROOT/'tools/audit/verify_native_relocation.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('before',type=Path);p.add_argument('after',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    b,B=native.load(a.before);c,C=native.load(a.after)
    assert all(C[n]==v for n,v in B.items() if v<0x8000 and n in C),'Unchanged RAM ABI'
    rng=random.Random(0x20237)
    stats={}
    def check(entry,bank,ram,rom_data,count,expected_top=None):
        result=[];clocks=[]
        for cpu,L in ((b,B),(c,C)):
            cpu.memory[:0x8000]=ram
            cpu.memory.switch(bank)
            cpu.memory[L['SMCCODE']:L['SMCCODE']+len(cpu.memory.smc)]=cpu.memory.smc
            for address,data in rom_data:cpu.memory[address:address+len(data)]=data
            cpu.a,cpu.x,cpu.y,cpu.p=(count*23)&255,(count*7)&255,(count*31)&255,count&255
            cpu.sp=0xfd;cpu.stPushWord(0x7eff);cpu.pc=L[entry];cpu.processorCycles=0
            steps=0
            while cpu.pc!=0x7f00:
                cpu.step();steps+=1
                assert steps<12000,(entry,count,hex(cpu.pc))
            if expected_top is not None:
                assert tuple(cpu.memory[L['TopScoreDisplay']:L['TopScoreDisplay']+6])==expected_top,(entry,count,'independent max')
            result.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,bytes(cpu.memory[:0x100])+bytes(cpu.memory[0x200:0x8000])))
            clocks.append(cpu.processorCycles)
        assert result[0]==result[1],{'entry':entry,'case':count,'registers':[r[:5]for r in result],
            'first_memory_differences':[(hex(i),b.memory[i],c.memory[i])for i in range(0x8000)if not 0x100<=i<0x200 and b.memory[i]!=c.memory[i]][:12]}
        delta=clocks[1]-clocks[0]
        st=stats.setdefault(entry,{'cases':0,'min_delta':10000,'max_delta':-10000})
        st['cases']+=1;st['min_delta']=min(st['min_delta'],delta);st['max_delta']=max(st['max_delta'],delta)

    score_cases=[]
    for value in (0,1,9,10,99,255):
        for triple in itertools.product((tuple([value]*6),tuple([0]*6),tuple([255]*6)),repeat=3):score_cases.append(triple)
    # First differing digit at each of six positions, including borrow edges.
    for digit,position,which in itertools.product((0,1,8,254),range(6),range(3)):
        triple=[[digit]*6 for _ in range(3)];triple[which][position]+=1
        score_cases.append(tuple(map(tuple,triple)))
    for i in range(1800):
        limit=10 if i%2==0 else 256
        score_cases.append(tuple(tuple(rng.randrange(limit)for _ in range(6))for _ in range(3)))
    for count,triple in enumerate(score_cases):
        ram=[0]*0x8000
        first,second,top=triple
        ram[B['PlayerScoreDisplay']:B['PlayerScoreDisplay']+12]=[*first,*second]
        ram[B['TopScoreDisplay']:B['TopScoreDisplay']+6]=top
        check('UpdateTopScore',3,ram,[],count,max(triple))

    render_cases=[]
    for header in range(256):render_cases.append((header,(header*13)&255,(header//4)%3-1,(header*29)&255,(header//7)%4,(header%64)*4,(header*7)&252,header%3))
    for header,edge,offset,rotation in itertools.product((4,8,12,28,64,124,128,252),
            ((0,0,0,0),(255,0,239,1),(127,255,255,0),(240,1,16,2)),(0,4,248,252),(0,4,252)):
        render_cases.append((header,*edge,offset,rotation,1))
    for _ in range(1000):render_cases.append((rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(64)*4,rng.randrange(64)*4,rng.randrange(2)))
    for count,(header,x,xhi,y,yhi,offset,rotation,active)in enumerate(render_cases):
        ram=[0]*0x8000
        for name,v in (('R0',0),('R1',0xc1),('R3',rng.randrange(256)),('R4',x),('R5',xhi),('R6',y),('R7',yhi),('CurrentOAMOffset',offset),('GuestOamRotationActive',active),('RgOamRotation',rotation),('GuestHudMixed',count&255)):
            if name in B:ram[B[name]]=v&255
        ram[B['Sprite_Data']:B['Sprite_Data']+256]=[rng.randrange(256)for _ in range(256)]
        record=[header]+[rng.randrange(256)for _ in range(256)]
        check('MetaspriteRenderLoop',4,ram,[(0xc100,record)],count)
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    report={'result':'passed','before_sha256':sha(a.before),'after_sha256':sha(a.after),
        'script_sha256':sha(Path(__file__)),'entries':stats,
        'compared':'A/X/Y/allP/SP and all bytes below8000 except discarded stack; independent score maximum',
        'scope':'Compiled RP2A03 initialized CPU/RAM/authored pose-data units, no interrupts/PPU/controller traversal',
        'limits':['Renderer units include all256 header bytes and signed positions, OAM exhaustion/rotation, software palette tags and both branches at128.','Real rendered pixels, IRQ/CHR timing and caller crowd effects require separate emulator tests.']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',stats)


if __name__=='__main__':main()
