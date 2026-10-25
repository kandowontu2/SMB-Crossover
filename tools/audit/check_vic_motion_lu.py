"""Execute the real Gradius ROM and linked retargeted motion in matched CPU arenas."""
from pathlib import Path
import hashlib
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
sys.path.insert(0,str(R/'tools/audit'))
from verify_native_relocation import load,NesMPU

O=R/'build/verification/vic-viper-lq'


def main():
    raw=Path('C:/NES/Gradius (USA).nes').read_bytes()
    rom=O/'smb-crossover-vic-motion.nes'
    manifest=json.loads((O/'motion-retarget.json').read_text())
    a=manifest['aliases']
    base=[0]*65536;base[0x8000:]=raw[16:32784]
    old=NesMPU(memory=base)
    new,l=load(rom);new.memory.switch(75)
    assert all(l[k]==v for k,v in a.items()),'Compiled ExRAM ABI differs from allocation'
    count=0;cycles=[]
    slots=((0x320,a['VvObjY'],32),(0x340,a['VvObjYF'],32),
           (0x360,a['VvObjX'],32),(0x380,a['VvObjXF'],32),
           (0x120,a['VvObjAnim'],3),(0x140,a['VvObjTimer'],3),
           (0x7a0,a['VvRingX'],24),(0x7c0,a['VvRingY'],24),
           (0x160,a['VvRingCursor'],1),(0x98,a['VvStepLo'],1),
           (0x99,a['VvStepHi'],1),(0x9b,a['VvTilt'],1))
    for held,speed,options,x,y,fraction in itertools.product(range(16),(0,1,4,13,14,254,255),
            range(3),(16,17,80,239,240),(15,16,17,191,192),(0,255)):
        old.memory[:2048]=[0]*2048
        new.memory[0x5d00:0x5e00]=[0]*256
        for source,target,size in slots:
            for i in range(size):
                value=(i*37+count*13)&255
                old.memory[source+i]=value;new.memory[target+i]=value
        def setfield(source,target,value):
            old.memory[source]=value;new.memory[a[target]]=value
        for source,target,value in (
            (0x7,'VvHeld',held),(0x18,'VvPlayer',0),(0x40,'VvSpeed',speed),
            (0x45,'VvOptions',options),(0x360,'VvObjX',x),(0x320,'VvObjY',y),
            (0x340,'VvObjYF',fraction),(0x380,'VvObjXF',fraction),
            (0x160,'VvRingCursor',count%24),(0x140,'VvObjTimer',(0,7,127,255)[count%4])):
            setfield(source,target,value)
        for cpu,pc,exit_pc in ((old,0xa006,0xa0e9),(new,l['VvNativeMotion'],0x5b00)):
            cpu.a,cpu.x,cpu.y,cpu.p=0xa5,0x74,0x29,0x24
            cpu.sp=0xed
            if cpu is new:cpu.stPushWord(exit_pc-1)
            cpu.pc=pc;cpu.processorCycles=0;steps=0
            while cpu.pc!=exit_pc:
                cpu.step();steps+=1
                assert steps<1500,(count,hex(cpu.pc))
        state=(held,speed,options,x,y,fraction)
        for source,target,size in slots:
            assert old.memory[source:source+size]==new.memory[target:target+size],(
                state,hex(source),old.memory[source:source+size],new.memory[target:target+size])
        assert (old.a,old.x,old.y,old.p,old.sp)==(new.a,new.x,new.y,new.p,new.sp),(
            state,'registers',(old.a,old.x,old.y,old.p,old.sp),(new.a,new.x,new.y,new.p,new.sp))
        cycles.append(new.processorCycles-old.processorCycles);count+=1
    # Negative control: an altered original horizontal clamp must fail on the
    # actual RIGHT+wall arena, making this independent of the generated mapping.
    assert old.memory[0xa02d]==0xf0
    old.memory[0xa02d]=0xe0
    for cpu,pc,exit_pc in ((old,0xa006,0xa0e9),(new,l['VvNativeMotion'],0x5b00)):
        if cpu is old:
            cpu.memory[7]=1;cpu.memory[0x18]=0;cpu.memory[0x40]=0;cpu.memory[0x45]=0;cpu.memory[0x360]=239
        else:
            for k,v in (('VvHeld',1),('VvPlayer',0),('VvSpeed',0),('VvOptions',0),('VvObjX',239)):cpu.memory[a[k]]=v
        cpu.sp=0xed
        if cpu is new:cpu.stPushWord(exit_pc-1)
        cpu.pc=pc
        while cpu.pc!=exit_pc:cpu.step()
    assert old.memory[0x360]!=new.memory[a['VvObjX']],'Wrong original clamp must be detected'
    report=dict(passed=True,cases=count,original_rom_sha256=hashlib.sha256(raw).hexdigest(),
        compiled_rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
        compared='Actual original instructions vs linked retarget: AXYP/SP; all four32B coordinate arrays,3animation/timer states,48ring bytes,ring cursor,step/tilt.',
        cycle_delta_min=min(cycles),cycle_delta_max=max(cycles),negative_control_detected=True,
        scope='CPU motion/Option-ring/tilt component only; no SMB camera, projectile, native gameplay or controller-route claim.')
    (O/'motion-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
