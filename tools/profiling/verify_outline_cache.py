"""Actual compiled helper versus independent filtering, explicit CPU/RAM cases."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import random

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('native_unit',ROOT/'tools/audit/verify_native_relocation.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    cpu,L=native.load(a.rom);cpu.memory.switch(10)
    rng=random.Random(0x20236);count=0;rows=[]
    base=L['OutlinePoseBuffer']
    for n in ('OutlineSourceHi','OutlineTinyNext','OutlineTinyLast'):
        cpu.memory[L[n]]=0
    for i in range(4):cpu.memory[L['OutlineTinyHi']+i]=0
    def record(parts,mask,seed):
        rand=random.Random(seed);out=[parts*4]
        for i in range(parts):out.extend((rand.randrange(256),(rand.randrange(256)&~4)|(4 if mask(i) else 0),rand.randrange(256),rand.randrange(256)))
        return out
    allowed=set(range(base,base+129))
    for name,sz in (('OutlineBytesLeft',1),('OutlineSourceLo',1),('OutlineSourceHi',1),('OutlineSourceBank',1),
                    ('OutlineTinyLo',4),('OutlineTinyHi',4),('OutlineTinyBank',4),('OutlineTinyNext',1),('OutlineTinyLast',1),('OutlineTinyOffset',1)):
        allowed.update(range(L[name],L[name]+sz))
    def run(address,data,bank,kind):
        nonlocal count
        cpu.memory[address:address+len(data)]=data
        cpu.memory[L['CurrentBankC']]=bank
        cpu.memory[L['R0']]=address&255;cpu.memory[L['R1']]=address>>8
        for i in range(2,8):cpu.memory[L['R0']+i]=rng.randrange(256)
        before=list(cpu.memory[0:0x8000])
        valid=0<data[0]<=128 and data[0]%4==0
        expected=[]
        if valid:
            for i in range(1,data[0]+1,4):
                if not data[i+1]&4:expected.extend(data[i:i+4])
        cpu.a,cpu.x,cpu.y,cpu.p=count&255,(count*13)&255,(count*29)&255,(count*73)&255
        cpu.sp=0xfd;cpu.stPushWord(0x7eff);cpu.pc=L['PlayerRemoveOutlines'];cpu.processorCycles=0
        steps=0
        while cpu.pc!=0x7f00:
            if cpu.memory[cpu.pc]==0x9d:
                target=cpu.memory[cpu.pc+1]+256*cpu.memory[cpu.pc+2]
                if target==base+1:
                    assert target+cpu.x<=base+128,(count,kind,'output store exceeds reservation')
            cpu.step();steps+=1;assert steps<10000,(count,hex(cpu.pc))
        pointer=cpu.memory[L['R0']]+256*cpu.memory[L['R1']]
        if valid:
            assert base<=pointer<=base+128 and pointer+len(expected)<=base+128,(count,kind,pointer,len(expected))
            assert cpu.memory[pointer:pointer+len(expected)+1]==[len(expected),*expected],(count,kind,'independent bytes')
        else:assert pointer==address,(count,kind,'invalid header pointer')
        for i in range(0x8000):
            if i in (L['R0'],L['R1']) or i in allowed or 0x100<=i<0x200:continue
            assert cpu.memory[i]==before[i],(count,kind,'out-of-contract write',hex(i))
        if address<0xc000 and valid:
            assert cpu.memory[L['OutlineSourceHi']]==0
            assert all(cpu.memory[L['OutlineTinyHi']+i]==0 for i in range(4))
        rows.append({'case':count,'kind':kind,'source':address,'bank':bank,'source_bytes':data[0],
                     'filtered_bytes':len(expected) if valid else None,'cycles':cpu.processorCycles,'pointer':pointer})
        count+=1
    # Four immutable poses repeatedly alternate; a fifth forces replacement.
    small=[record(11,lambda i:i>=5,100+i) for i in range(5)]
    for _ in range(5):
        for i in range(4):run(0xc100+128*i,small[i],20,'four-pose-cycle')
    for i in (4,0,1,2,3,4,2,4,2):run(0xc100+128*i,small[i],20,'fifth-pose-eviction')
    # The same address in different banks must never alias.
    for _ in range(4):
        for bank in (21,22,23,24):run(0xc100,record(11,lambda i:i>=5,1000+bank),bank,'bank-key')
    # Every legal length, all/no/alternating/random tags, fresh immutable keys.
    for parts in range(1,33):
        for mode in range(4):
            for repeat in range(2):
                b=30+parts*4+mode
                run(0xc100,record(parts,lambda i: mode==1 or mode==2 and i%2==0 or mode==3 and (i*7+parts)%5<2,parts*10+mode),b,'length-mask-repeat')
    # Full output overlaps all four slots; alternate full and small paths.
    for i in range(20):
        run(0xc000,record(32,lambda _:False,2000+i%2),180+i%2,'full128')
        run(0xc400,small[i%5],190+i%5,'small-after-full')
    # RAM input aliases a former small-cache slot, then changes in place.
    for i in range(30):
        run(base+96,record(3,lambda j:j==1,3000+i),0,'mutable-RAM-alias')
        run(0xc100,small[0],20,'immutable-after-RAM')
    for header in (0,1,2,3,5,127,129,255):run(0xc800,[header,*([0]*255)],200,'invalid-header')
    # Independent varied immutable keys and lengths retain bounded writes.
    for i in range(500):
        parts=rng.randrange(1,33);seed=4000+i
        run(0xc000+(i%16)*256,record(parts,lambda j:(j*11+seed)%7<3,seed),i%256,'varied-key')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report={'result':'passed','scope':'Compiled helper unit, authored CPU/RAM/ROM-data arenas; no emulator traversal',
            'rom_sha256':sha(a.rom),'script_sha256':sha(Path(__file__)),'cases':count,
            'compared':'Independent filtered record bytes, returned pointer bounds, all native/SRAM outside explicit work fields; R2..R7 preserved',
            'rows':rows,'limits':['No interrupts/PPU; real caller, OAM/pixels and matched crowd packets are separate.','Synthetic immutable keys are not real art/source-parity evidence.']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',count,'bounded independent filter/cache cases')


if __name__=='__main__':main()
