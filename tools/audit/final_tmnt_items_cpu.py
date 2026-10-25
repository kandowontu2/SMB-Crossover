"""Bound current turtle pickup leaves and original uncapped boomerang refunds.

Direct CPU controls use explicit RAM. They do not certify physical acquisition,
input timing, native frame/PPU/audio behavior or any prepared profile as passed.
"""
from pathlib import Path
import argparse
import hashlib
import json
from py65.devices.mpu6502 import MPU
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load

TARGET='52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
ORIGINAL='15e112c3790add361157dfa42854c3159c956f72e6acd8fabc518615f1ce8525'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def original_cpu(raw):
    c=MPU()
    c.memory[0x8000:0xc000]=raw[16+6*16384:16+7*16384]
    c.memory[0xc000:]=raw[16+7*16384:16+8*16384]
    return c


def original_run(c,pc,x=0,stop=0xfff0):
    c.pc,c.sp,c.x,c.y=pc,0xfd,x,0
    c.memory[0x1fe],c.memory[0x1ff]=0xef,0xff
    for _ in range(20000):
        if c.pc==stop:return
        c.step()
    raise AssertionError(('Original routine timeout',hex(c.pc)))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--original',type=Path,default=Path('C:/NES/Teenage Mutant Ninja Turtles (USA).nes'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert sha(a.rom)==TARGET and sha(a.original)==ORIGINAL
    a.output.mkdir(parents=True,exist_ok=False)
    b=scoped_load(a.rom);rows=[]
    for variant in range(4):
        for old in range(5):
            for gear in range(1,5):
                for ammo in [0,19,20,80,99,102]:
                    for selected in [0,1]:
                        q=Arena(b,19);q.set('TnVariant',variant)
                        for i in range(4):
                            q.set('TnEquipment',i+1,i);q.set('TnAmmo',30+i,i)
                        q.set('TnEquipment',old,variant);q.set('TnAmmo',ammo,variant);q.set('TnGearSelected',selected)
                        q.invoke('TnGiveEquipment',a=gear)
                        expected=min(99,ammo+20) if old==gear else 20
                        assert(q.get('TnEquipment',variant),q.get('TnAmmo',variant),q.get('TnGearSelected'))==(gear,expected,selected if old==gear else 1)
                        assert all((q.get('TnEquipment',i),q.get('TnAmmo',i))==(i+1,30+i)for i in range(4)if i!=variant)
                        rows.append(dict(case='current_gear_leaf',variant=variant,old=old,gear=gear,ammo=ammo,selected=selected,result=expected))
        for hp in range(129):
            for kind in [0,1]:
                for food in [0,1]:
                    q=Arena(b,19);q.set('TnVariant',variant);q.set('TnHealth',hp,variant);q.set('TnFood',food)
                    q.invoke('TnHeal',a=kind)
                    assert(q.get('TnHealth',variant),q.get('TnFood'))==(min(128,hp+(32 if kind==0 else 64)),food^1)
                    rows.append(dict(case='current_food_leaf',variant=variant,hp=hp,kind=kind,food=food,result=q.get('TnHealth',variant)))
    raw=a.original.read_bytes();original=[]
    for variant in range(4):
        c=original_cpu(raw)
        for at,value in [(0x67,variant),(0x73+variant,3),(0xa8+variant,98),(0x442,7),(0x480,80),(0x460,100)]:c.memory[at]=value
        original_run(c,0x96e3,x=2,stop=0xcef0)
        assert c.memory[0xa8+variant]==99
        values=[]
        for actor in [2,3,4]:
            c.memory[0x440+actor]=0x27;c.memory[0x480+actor]=80;c.memory[0x460+actor]=100
            original_run(c,0xfdc8,x=actor);values.append(c.memory[0xa8+variant])
        assert values==[100,101,102]
        q=Arena(b,19);q.set('TnVariant',variant);q.set('TnEquipment',3,variant);q.set('TnAmmo',98,variant)
        q.invoke('TnGiveEquipment',a=3);assert q.get('TnAmmo',variant)==99
        port=[]
        for _ in range(3):q.invoke('TnRestoreBoomerang');port.append(q.get('TnAmmo',variant))
        assert port==values
        original.append(dict(variant=variant,original_pickup_pc='6:96E3',original_return_pc='7:FDC8',pickup_cap=99,original_returns=values,port_returns=port))
    result=dict(passed=True,native_passed=False,goal_complete=False,ROM_sha256=TARGET,
                original_ROM_sha256=ORIGINAL,script_sha256=sha(Path(__file__)),
                direct_cpu_cases=len(rows)+len(original),checks=rows,original_comparisons=original,
                scope=__doc__,finding='Original ROM and current port both allow99 duplicate refill followed by100/101/102 refunds. Do not classify this as a port defect or invent a return cap. Actual acquired native three-return timing remains untested.')
    f=a.output/'proof.json';f.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['passed','native_passed','ROM_sha256','original_ROM_sha256','direct_cpu_cases','finding']}))


if __name__=='__main__':main()
