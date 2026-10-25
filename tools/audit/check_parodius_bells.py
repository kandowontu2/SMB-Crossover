"""Compare extracted Bell/pickup instructions with the original cartridge CPU.

Palette packets, terrain and SMB enemy damage are explicit fixture callbacks;
this certifies native control state, not their host integration.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=module('pn_base_oracle',ROOT/'tools/audit/check_parodius_native.py')
bell=module('pn_bell_builder',ROOT/'tools/reference/build_parodius_bells.py')
from py65.devices.mpu6502 import MPU


def fixture(out,mapper):
    folder,_,_,_=base.compile_fixture(out,mapper);bell.generate(folder)
    if mapper=='mmc3':
        p=folder/'parodius_bell_native.s';p.write_text(re.sub(r'\$5d([0-9a-f]{2})',lambda m:f'${0x6100+int(m[1],16):04x}',p.read_text()))
    s=(folder/'fixture.s').read_text()
    s+='\nPARODIUS_CPU_FIXTURE=1\n.include "parodius_bell_native.s"\n.segment "PARODIUS_BELLS"\n'
    defined=set(base.builder.EXTERNALS.values())|set(base.builder.ENTRY.values())
    for target in sorted(set(bell.EXTERNALS.values())-defined):s+=target+':rts\n.export '+target+'\n'
    for name,_ in base.VIC.values():s+='.export '+name+'\n'
    (folder/'fixture.s').write_text(s)
    (folder/'fixture.cfg').write_text('MEMORY{A:start=$8000,size=$2000,type=ro,file=%O,fill=yes;B:start=$A000,size=$2000,type=ro,file=%O,fill=yes;C:start=$C000,size=$2000,type=ro,file=%O,fill=yes;}\nSEGMENTS{VIC_CORE:load=A,type=ro;PARODIUS_BELLS:load=B,type=ro;VIC_GFX:load=C,type=ro;}\n')
    compiler=ROOT/'tools/Windows/cc65/bin';logs=[]
    for command in [[str(compiler/'ca65.exe'),'-g','-o','fixture.o','fixture.s'],[str(compiler/'ld65.exe'),'-C','fixture.cfg','-Ln','fixture.lbl','-o','fixture.bin','fixture.o']]:
        r=subprocess.run(command,cwd=folder,capture_output=True,text=True);logs.append(r.stdout+r.stderr)
        assert r.returncode==0,'\n'.join(logs)
    (folder/'bell-compile.log').write_text('\n'.join(logs))
    labels={m[2]:int(m[1],16)for line in(folder/'fixture.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
    port=MPU();data=(folder/'fixture.bin').read_bytes();port.memory[0x8000:0xe000]=data
    _,symbols=base.builder.mappings();symbols.update({a:n for a,(n,_)in bell.EXTRA.items()})
    zero={'M0':0xa0,'M1':0xa1,'R0':0xa2,'R1':0xa3,'R4':0xa4,'R5':0xa5,'R6':0xa6,'R7':0xa7}
    addr={}
    for source,name in symbols.items():
        root,_,offset=name.partition('+')
        destination=zero[root]if root in zero else labels[root]
        addr[source]=destination+(int(offset)if offset else 0)
    return folder,port,labels,addr


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/verification/parodius-bells-nm/differential');a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
    report=dict(source_sha256=base.builder.SHA,scope=__doc__,mappers={})
    for mapper in ('mmc5','mmc3'):
        folder,port,labels,addr=fixture(out,mapper);_,original=base.builder.source_cpu()
        pairs={}
        for source in base.builder.ORIGINAL_FIELDS+[0x0640,0x6620,0x66b0]:
            count=128 if source==0x0640 else 28
            for i in range(count):pairs[source+i]=addr[source]+i
        for source in addr:
            if source<256 or source in (0x6590,0x65c0,0x65f0,0x65ab):pairs[source]=addr[source]
        # The mapper overlay uses independent source ZP addresses: poison all
        # unowned low RAM, while leaving return-stack writes legal.
        allowed=set(pairs.values())|set(range(0x100,0x200))
        events=[[],[]];steps=0;cases=[]
        callbacks=dict(base.builder.EXTERNALS);callbacks.update(bell.EXTERNALS)
        for source in (0xc977,0xc98a,0x9bba,0x97fc):callbacks.pop(source,None)
        cbport={labels[name]:name for name in callbacks.values()}
        def destination(source):
            if source in pairs:return pairs[source]
            raise AssertionError(hex(source))
        def seed(source,value):original.memory[source]=value&255;port.memory[destination(source)]=value&255
        def read(source):return original.memory[source]
        def clear(variant):
            original.memory[:0x8000]=[0]*0x8000;port.memory[:0x8000]=[0xa5]*0x8000
            for source,target in pairs.items():original.memory[source]=port.memory[target]=0
            seed(0x8f,variant);seed(0x87,variant);seed(0x6500,0x80);seed(0x6200,1);seed(0x63e0,1);seed(0x6260,80);seed(0x62c0,96)
            events[0].clear();events[1].clear();original.p=port.p=0x30
        def callback(cpu,name,index,terrain):
            def get(source):return cpu.memory[source if index==0 else destination(source)]
            def put(source,value):cpu.memory[source if index==0 else destination(source)]=value&255
            if name=='PnSoundEvent':events[index].append(('sfx',cpu.a))
            elif name=='PnTerrainQuery':cpu.a=terrain;cpu.FlagsNZ(cpu.a)
            elif name=='PnTerrainImpact':events[index].append(('terrain',get(0),get(2),get(3)))
            elif name=='PnBombPalettePrime':
                events[index].append(('palette-prime',get(0x64a0+27)))
                put(0x64d0+27,1 if get(0x26)>=16 else 0)
            elif name=='PnBombPaletteAdjust':
                events[index].append(('palette-adjust',get(0x64a0+27)))
                put(0x64d0+27,2 if get(0x26)>=16 else get(0x64d0+27)&253)
            elif name=='PnBombWorldDamage':events[index].append(('bomb',get(0x6500+27),get(0x64a0+27)))
            elif name=='PnBellGainLife':events[index].append(('1up',get(0x80)))
            elif name=='PnBellBonusContact':events[index].append(('bonus',cpu.y))
            cpu.pc=cpu.stPopWord()+1
        def run(cpu,entry,cb,index,terrain):
            nonlocal steps
            cpu.pc=entry;cpu.sp=0xfd;cpu.memory[0x1fe]=0xef;cpu.memory[0x1ff]=0x7f;cpu.x=0
            n=0
            while cpu.pc!=0x7ff0:
                if index==0 and cpu.pc in(0x8136,0x813a,0x814d):break
                if cpu.pc in cb:callback(cpu,cb[cpu.pc],index,terrain)
                else:cpu.step()
                n+=1;assert n<50000,hex(cpu.pc)
            steps+=n
        def execute(source,terrain=0):
            events[0].clear();events[1].clear();before=port.memory[:0x8000]
            run(original,source,callbacks,0,terrain);run(port,labels[bell.ENTRIES[source]],cbport,1,terrain)
            # Native animation scratch contains relocated ROM pointers. The
            # stable animation fields and resulting frame are compared; raw
            # pointer bytes cannot equal the cartridge's original addresses.
            different=[(hex(s),read(s),port.memory[t])for s,t in pairs.items()if s>=0x19 and read(s)!=port.memory[t]]
            assert not different,(mapper,hex(source),different[:12])
            assert events[0]==events[1],(mapper,events)
            bad=[hex(i)for i,(x,y)in enumerate(zip(before,port.memory))if i<0x8000 and x!=y and i not in allowed]
            assert not bad,('unowned writes',bad[:12])
        for variant in range(4):
            for kind in (4,5,6,7,8,9,10,23):
                for flags in (0,1,2,4,8,16,18,64):
                    clear(variant);seed(0x6230,kind);seed(0x7b,flags);seed(0x78,64);execute(0x80b5)
                    cases.append(dict(name='pickup',variant=variant,kind=kind,flags=flags))
            for kind in (1,4,8,16):
                clear(variant);seed(0x7b,kind);seed(0x80,9)
                maximum=0
                for tick in range(1100 if kind in(1,4)else 64):
                    seed(0x23,tick);seed(0x40,64 if tick%23==0 else 0)
                    seed(0x26,16 if tick%47<3 else 0);seed(0x6a,1);seed(0x6b,0)
                    execute(0x97fc,terrain=2 if tick%83==0 else 0)
                    maximum=max(maximum,read(0x6500+27))
                if kind in (1,4,8):assert read(0x7b)&kind==0,('Bell must finish',variant,kind,read(0x7b))
                cases.append(dict(name='bell-lifecycle',variant=variant,flags=kind,maximum_active=maximum))
        report['mappers'][mapper]=dict(passed=True,cases=cases,instructions=steps,compared_bytes=len(pairs),fixture_sha256=hashlib.sha256((folder/'fixture.bin').read_bytes()).hexdigest())
        (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',mapper,len(cases),'Bell/pickup cases',steps,'instructions',flush=True)


if __name__=='__main__':main()
