"""Match portable Gradius gear ownership against the real ROM's upgrade routines."""
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
    rom=O/'gear/smb-crossover-vic-gear.nes'
    base=[0]*65536;base[0x8000:]=raw[16:32784]
    old=NesMPU(memory=base);new,l=load(rom);new.memory.switch(75)
    fields=((0x35,'VvAutoFire'),(0x40,'VvSpeed'),(0x41,'VvMissile'),
            (0x42,'VvMeter'),(0x44,'VvGun'),(0x45,'VvOptions'),(0x46,'VvShield'))
    def execute(cpu,pc,original=False):
        cpu.a,cpu.x,cpu.y,cpu.p=0xa5,0x74,0x29,0x24
        cpu.sp=0xed;cpu.stPushWord(0x5aff);cpu.pc=pc
        events=[];steps=0
        while cpu.pc!=0x5b00:
            if original and cpu.pc in (0xec1e,0x8a30,0x8455,0x845b):
                events.append((cpu.pc,cpu.a));cpu.pc=cpu.stPopWord()+1
            else:cpu.step()
            steps+=1
            assert steps<1000,(hex(cpu.pc),pc)
        assert cpu.sp==0xed
        return events
    def reset(autofire,speed,missile,meter,gun,options,shield):
        old.memory[:2048]=[0]*2048;new.memory[0x5d00:0x5e00]=[0]*256
        for (address,name),value in zip(fields,(autofire,speed,missile,meter,gun,options,shield)):
            old.memory[address]=value;new.memory[l[name]]=value
    def compare(case):
        for address,name in fields:assert old.memory[address]==new.memory[l[name]],(case,name,old.memory[address],new.memory[l[name]])
    buys=0;refusals=0
    for alive,held,meter,speed,missile,gun,options,shield in itertools.product(
            (0,1,2),(0,0x40,0x80,0xc0),range(7),(0,13,254,255),(0,1),range(3),range(3),(0,1,5)):
        reset(20,speed,missile,meter,gun,options,shield)
        old.memory[0x100]=alive;new.memory[l['VvAlive']]=alive
        old.memory[7]=held;new.memory[l['VvHeld']]=held
        old.memory[0x18]=0
        events=execute(old,0x8974,True);execute(new,l['VvBuyUpgrade'])
        case=(alive,held,meter,speed,missile,gun,options,shield)
        compare(case)
        sounds=[v for pc,v in events if pc==0xec1e]
        assert new.memory[l['VvSfxEvent']]==(sounds[-1] if sounds else 0),(case,events)
        assert new.memory[l['VvHudDirty']]==int(any(pc==0x8a30 for pc,v in events)),case
        if alive==1 and held&0x40 and meter and not sounds:refusals+=1
        buys+=1
    pickups=0
    for meter,digit,autofire in itertools.product(range(7),range(256),(4,20)):
        reset(autofire,3,1,meter,2,2,5)
        old.memory[0x18]=0;old.memory[0x7e5]=digit
        new.memory[l['VvScoreDigit']]=digit
        events=execute(old,0x894b,True);execute(new,l['VvTakeCapsule'])
        compare((meter,digit,autofire))
        assert new.memory[l['VvSfxEvent']]==13
        assert new.memory[l['VvHudDirty']]==1
        bonus=int(any(pc==0x8455 and value==0x10 for pc,value in events))
        assert new.memory[l['VvScoreBonus']]==bonus,(meter,digit,events)
        assert sum(pc==0x845b for pc,value in events)==1,'Native per-capsule50 score event'
        pickups+=1
    report=dict(passed=True,upgrade_cases=buys,duplicate_refusals=refusals,pickup_cases=pickups,
        original_rom_sha256=hashlib.sha256(raw).hexdigest(),compiled_rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
        compared='Actual original$8974/$894B ownership/consumption/speedwrap/gunexclusion/2Options/5hitShield/rapidfire/capsulewrap plus sound/HUD/score events.',
        scope='CPU gear component. Original external audio/HUD/score calls observed as events; SMB pickup/drop/UI/native control wiring is still required.')
    (O/'gear-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
