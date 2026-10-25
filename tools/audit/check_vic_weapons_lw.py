"""Differential CPU arenas for original Gradius guns/missiles with declared query fixtures."""
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
    rom=O/'weapons/smb-crossover-vic-weapons.nes'
    base=[0]*65536;base[0x8000:]=raw[16:32784]
    old=NesMPU(memory=base);new,l=load(rom);new.memory.switch(75)
    arrays=((0x320,l['VvObjY'],32),(0x340,l['VvObjYF'],32),
            (0x360,l['VvObjX'],32),(0x380,l['VvObjXF'],32),
            (0x120,l['VvObjAnim'],12),(0x163,l['VvObjSub']+3,9),
            (0x3a3,l['VvFireTimer'],6))
    scratch=json.loads((O/'weapon-retarget.json').read_text())['ram_map']
    scratch=[(int(a),v['address']) for a,v in scratch.items() if int(a) in (0x98,0x99,0x9a,0x9b,0x9c,0xa4,0xa5,0xa8)]
    count=0;cohorts={};query_counts={0xc3af:0,0xc3d3:0};sound_events=0
    # Every owner count, gun, press/hold combination, live/free shot pattern,
    # terrain fly/crawl/wall branch, and the original stage5 probe bypass.
    for entry,gun,options,press,held,pattern,under,side,stage in itertools.product(
            ('all','dead','shots'),range(3),range(3),(0,128),(0,128),
            range(5),(0,1),(0,1),(0,4)):
        old.memory[:2048]=[0]*2048;new.memory[0x5d00:0x5e00]=[0]*256
        for address,target,size in arrays:
            for i in range(size):
                value=(i*37+count*13)&255
                old.memory[address+i]=value;new.memory[target+i]=value
        for address,target in scratch:old.memory[address]=new.memory[target]=(count*17+address)&255
        values=((7,'VvHeld',held),(5,'VvFresh',press),(0x18,'VvPlayer',0),
                (0x19,'VvStage',stage),(0x35,'VvAutoFire',(4,20)[count&1]),
                (0x41,'VvMissile',int(pattern&1)),(0x44,'VvGun',gun),(0x45,'VvOptions',options))
        for address,name,value in values:old.memory[address]=value;new.memory[l[name]]=value
        for i in range(12):
            for source,name,value in (
                (0x320,'VvObjY',(16,17,96,197,199)[(i+count)%5]),
                (0x360,'VvObjX',(16,80,236,240,247)[(i+count)%5]),
                (0x120,'VvObjAnim',(0,6,7,8,10)[(i+pattern)%5])):
                old.memory[source+i]=value;new.memory[l[name]+i]=value
        for i in range(9):
            sub=0 if old.memory[0x123+i]==0 else (i+pattern)%4
            old.memory[0x163+i]=sub;new.memory[l['VvObjSub']+3+i]=sub
            if i<6:
                delay=(0,1,4,20,255)[(i+count)%5]
                old.memory[0x3a3+i]=delay;new.memory[l['VvFireTimer']+i]=delay
        new.memory[l['VvTestTerrainUnder']]=under;new.memory[l['VvTestTerrainSide']]=side
        sound=[]
        for cpu,pc,original in (
                (old,{'all':0xa0e9,'dead':0xa16f,'shots':0xa1e6}[entry],True),
                (new,l[{'all':'VvNativeWeapons','dead':'VvNativeMissiles','shots':'VvNativeShots'}[entry]],False)):
            cpu.a,cpu.x,cpu.y,cpu.p=0xa5,0x74,0x29,0x24
            cpu.sp=0xed;cpu.stPushWord(0x5aff);cpu.pc=pc;steps=0
            while cpu.pc!=0x5b00:
                if original and cpu.pc in (0xc3af,0xc3d3,0xec1e):
                    if cpu.pc==0xec1e:sound.append(cpu.a)
                    else:
                        query_counts[cpu.pc]+=1
                        cpu.a=under if cpu.pc==0xc3af else side;cpu.FlagsNZ(cpu.a)
                    cpu.pc=cpu.stPopWord()+1
                else:cpu.step()
                steps+=1;assert steps<4000,(count,hex(cpu.pc))
        case=(entry,gun,options,press,held,pattern,under,side,stage)
        for address,target,size in arrays:
            assert old.memory[address:address+size]==new.memory[target:target+size],(
                case,hex(address),old.memory[address:address+size],new.memory[target:target+size])
        for address,target in scratch:assert old.memory[address]==new.memory[target],(case,hex(address),old.memory[address],new.memory[target])
        assert new.memory[l['VvSfxEvent']]==(sound[-1] if sound else 0),(case,sound)
        assert (old.a,old.x,old.y,old.p,old.sp)==(new.a,new.x,new.y,new.p,new.sp),(case,'registers')
        sound_events+=len(sound);count+=1;cohorts[entry]=cohorts.get(entry,0)+1
    report=dict(passed=True,cases=count,cohorts=cohorts,query_counts=query_counts,sound_events=sound_events,
        original_rom_sha256=hashlib.sha256(raw).hexdigest(),compiled_rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
        compared='Native firing timers/slot limits/crossreload; sixshot and threemissile movement including crawl/wall/expiry; AXYP/SP; coordinate/shot/timer/scratch fields; last sound event.',
        scope=__doc__,playable=False,
        limitations='Terrain query and sound-request callees are explicit deterministic CPU fixture callbacks, not the original world/audio drivers or an SMB game adapter.')
    (O/'weapon-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
