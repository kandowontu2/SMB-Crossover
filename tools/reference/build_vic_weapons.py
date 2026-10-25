"""Retarget original Gradius firing/shot/missile instructions for integration.

The generated terrain shim is explicitly a CPU-test fixture. A game adapter
must replace it with SMB world queries before exposing this character.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

import build_vic_motion as movement
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

R=movement.ROOT;O=movement.OUT


def main():
    movement.main()
    raw=Path('C:/NES/Gradius (USA).nes').read_bytes()
    cpu=MPU();cpu.memory[0x8000:]=raw[16:32784];dis=Disassembler(cpu)
    ram=dict(movement.MAP)
    ram.update({0x05:('VvFresh',0xe4),0x19:('VvStage',0xf9),0x35:('VvAutoFire',0xe2),
        0x41:('VvMissile',0xd9),0x44:('VvGun',0xdb),0x9a:('VvWeaponFresh',0xfb),
        0x9c:('VvWeaponScratch',0xfa),0xa4:('VvProbeX',0xf7),0xa5:('VvProbeY',0xf6),
        0xa8:('VvWeaponLoop',0xf8),0x123:('VvObjAnim+3',0x83),0x126:('VvObjAnim+6',0x86),
        0x129:('VvObjAnim+9',0x89),0x163:('VvObjSub+3',0x9b),0x166:('VvObjSub+6',0x9e),
        0x169:('VvObjSub+9',0xa1),0x323:('VvObjY+3',0x03),0x326:('VvObjY+6',0x06),
        0x329:('VvObjY+9',0x09),0x363:('VvObjX+3',0x43),0x366:('VvObjX+6',0x46),
        0x369:('VvObjX+9',0x49),0x383:('VvObjXF+3',0x63),
        0x3a3:('VvFireTimer',0xec),0x3a6:('VvFireTimer+3',0xef)})
    lines=['; Generated original Gradius USA firing, missile and shot program.']
    for name,offset in ram.values():
        if '+' not in name and name not in movement.FIELDS and name not in [n for n,o in movement.MAP.values()]:
            lines += [f'{name}=${movement.STATE+offset:04x}',f'.export {name}']
    lines+=['VvTestTerrainUnder=$5dfe','VvTestTerrainSide=$5dff',
        '.export VvTestTerrainUnder,VvTestTerrainSide','.pushseg','.segment "VIC_CORE"',
        '.proc VvNativeWeapons']
    ranges=((0xa0e9,0xa1a4),(0xa1aa,0xa285))
    branch={'BCC':'jcc','BCS':'jcs','BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BVC':'jvc','BVS':'jvs'}
    externals={0xc3af:'VvTerrainUnder',0xc3d3:'VvTerrainSide',0xec1e:'VvSoundEvent'}
    tables={0xa0e0:3,0xa0e3:3,0xa0e6:3,0xa1a4:2,0xa1a6:2,0xa1a8:2}
    instructions=[]
    for lo,hi in ranges:
        pc=lo
        while pc<hi:
            length,asm=dis.instruction_at(pc);assert pc+length<=hi
            mnemonic,_,operand=asm.partition(' ')
            if mnemonic in branch or mnemonic in ('JMP','JSR'):
                target=int(operand[1:],16)
                if target in externals:target_name=externals[target]
                else:
                    assert any(a<=target<b for a,b in ranges),(hex(pc),asm)
                    target_name=f'Vw{target:04x}'
                asm=branch.get(mnemonic,mnemonic.lower())+' '+target_name
            elif operand and not operand.startswith('#') and '$' in operand:
                match=re.search(r'\$([0-9a-fA-F]+)',operand);address=int(match[1],16)
                if address in tables:target_name=f'Vw{address:04x}'
                else:
                    assert address in ram,(hex(pc),asm)
                    target_name=ram[address][0]
                asm=mnemonic.lower()+' '+operand[:match.start()]+target_name+operand[match.end():]
            else:asm=asm.lower()
            lines += [f'Vw{pc:04x}: {asm} ; original${pc:04x}']
            instructions.append(dict(address=pc,raw=bytes(cpu.memory[pc:pc+length]).hex(),asm=asm));pc+=length
    for address,size in tables.items():
        lines += [f'Vw{address:04x}: .byte '+','.join(f'${b:02x}' for b in cpu.memory[address:address+size])]
    lines += ['.endproc','VvNativeMissiles=VvNativeWeapons::Vwa16f','VvNativeShots=VvNativeWeapons::Vwa1e6',
              '.export VvNativeMissiles,VvNativeShots',
              '.proc VvSoundEvent','  sta VvSfxEvent','  rts','.endproc',
              '; CPU fixture ONLY. Never enable a menu entry with these constant queries.',
              '.proc VvTerrainUnder','  lda VvTestTerrainUnder','  rts','.endproc',
              '.proc VvTerrainSide','  lda VvTestTerrainSide','  rts','.endproc','.popseg']
    source=O/'source/src/vic_native_weapons.s';source.write_text('\n'.join(lines)+'\n')
    motion=O/'source/src/vic_native_motion.s'
    motion.write_text(motion.read_text()+'.include "vic_native_weapons.s"\n')
    report=dict(original_rom_sha256=hashlib.sha256(raw).hexdigest(),instructions=instructions,
        ram_map={str(k):dict(symbol=n,address=movement.STATE+o) for k,(n,o) in ram.items()},
        tables={str(k):list(cpu.memory[k:k+size]) for k,size in tables.items()},
        scope=__doc__,playable=False)
    (O/'weapon-retarget.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(instructions=len(instructions),source=str(source),playable=False)))


if __name__=='__main__':main()
