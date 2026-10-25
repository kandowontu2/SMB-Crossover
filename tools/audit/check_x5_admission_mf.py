"""Check linked palette compatibility and fresh-game menu variant retention."""
from pathlib import Path
import hashlib
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
sys.path.insert(0,str(R/'tools/audit'))
from verify_native_relocation import load

O=R/'build/verification/kirby-adoption-me'


def reset(cpu,labels):
    cpu.memory[:2048]=[0]*2048
    cpu.memory[0x5c00:0x8000]=[0]*0x2400
    start=labels['__SMCCODE_RUN__']
    cpu.memory[start:start+len(cpu.memory.smc)]=cpu.memory.smc
    cpu.memory[labels['CurrentBank']]=0x83
    cpu.memory[labels['CurrentBankC']]=0x84
    cpu.memory.switch(3)


def call(cpu,labels,name):
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=0xa5,0x67,0x89,0x24,0xed
    cpu.stPushWord(0x5aff);cpu.pc=labels[name]
    count=0
    while cpu.pc!=0x5b00:
        cpu.step();count+=1
        assert count<100000,(name,hex(cpu.pc))
    assert cpu.sp==0xed


def main():
    oldrom=R/'build/checkpoints/darkwing-zelda2-md/build/smb-crossover-mmc5-expanded.nes'
    newrom=O/'smb-crossover-mmc5-kirby-final.nes'
    old,ol=load(oldrom);new,nl=load(newrom)
    assert ol['GetPlayerColors']==nl['GetPlayerColors']
    count=0
    for char,power,area,bill,behavior in itertools.product(range(13),range(3),range(4),range(2),range(2)):
        outputs=[]
        for cpu,labels in ((old,ol),(new,nl)):
            reset(cpu,labels)
            for name,value in (('SelectedCharacter',char),('PlayerStatus',power),('AreaType',area),
                               ('BillVariant',bill),('CrossoverBehaviorVersion',behavior),('VRAM_Buffer1_Offset',0)):
                cpu.memory[labels[name]]=value
            call(cpu,labels,'GetPlayerColors')
            offset=cpu.memory[labels['VRAM_Buffer1_Offset']]
            outputs.append((offset,bytes(cpu.memory[labels['VRAM_Buffer1']:labels['VRAM_Buffer1']+offset+1])))
        assert outputs[0]==outputs[1],(char,power,area,bill,behavior,outputs)
        count+=1
    reset(new,nl);new.memory[nl['SelectedCharacter']]=13
    call(new,nl,'GetPlayerColors')
    size=new.memory[nl['VRAM_Buffer1_Offset']]
    data=bytes(new.memory[nl['VRAM_Buffer1']:nl['VRAM_Buffer1']+size])
    assert data[-6:]==bytes((0x3f,0x11,3,0x35,0x25,0x0f)),data.hex()
    assert bytes((0x3f,0x19,3,0x16,0x30,0x27)) in data
    variants=0
    for seed in range(16):
        reset(new,nl)
        new.memory[0x5c00:0x6000]=[0x85]*1024
        chosen=[(seed+i*17)&255 for i in range(16)]
        new.memory[0x5fe0:0x5ff0]=chosen
        new.memory.switch(78);new.memory[nl['CurrentBank']]=0xce
        call(new,nl,'X5InventoryInit')
        assert new.memory[0x5fe0:0x5ff0]==chosen
        assert not any(new.memory[0x5c00:0x5fe0]+new.memory[0x5ff0:0x6000])
        variants+=1
    report=dict(passed=True,legacy_palette_cases=count,new_Kirby_palette=True,
        world2_palette_unchanged=True,menu_variant_retention_cases=variants,
        reset_gameplay_bytes_per_case=1008,original_palette_entry_PC_unchanged=True,
        old_sha256=hashlib.sha256(oldrom.read_bytes()).hexdigest(),
        new_sha256=hashlib.sha256(newrom.read_bytes()).hexdigest(),
        scope='Linked CPU arenas; actual controller/NMI evidence is separate.')
    (O/'admission-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
