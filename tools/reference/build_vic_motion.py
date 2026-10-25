"""Retarget the original NES Gradius motion instructions into private ExRAM.

Source addresses remain beside every emitted instruction. This is a component
port, not the SMB world/camera adapter or a playable character by itself.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile

sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/vic-viper-lq'
STATE=0x5d00
MAP={
    0x07:('VvHeld',0xe3),0x18:('VvPlayer',0xde),0x40:('VvSpeed',0xd8),
    0x45:('VvOptions',0xdc),0x98:('VvStepLo',0xe0),0x99:('VvStepHi',0xe1),
    0x9b:('VvTilt',0xdf),0x120:('VvObjAnim',0x80),0x121:('VvObjAnim+1',0x81),
    0x140:('VvObjTimer',0x8c),0x141:('VvObjTimer+1',0x8d),0x160:('VvRingCursor',0xa4),
    0x320:('VvObjY',0x00),0x340:('VvObjYF',0x20),0x360:('VvObjX',0x40),
    0x380:('VvObjXF',0x60),0x7a0:('VvRingX',0xa8),0x7c0:('VvRingY',0xc0),
}
FIELDS={'VvMissile':0xd9,'VvMeter':0xda,'VvGun':0xdb,'VvShield':0xdd,
        'VvAutoFire':0xe2,'VvFresh':0xe4,'VvPrevious':0xe5,'VvFlags':0xe6,
        'VvInitialized':0xe7,'VvObjSub':0x98,'VvFireTimer':0xec,
        'VvAlive':0xe8,'VvScoreDigit':0xe9,'VvSfxEvent':0xea,
        'VvScoreBonus':0xeb,'VvHudDirty':0xf5}


def main():
    raw=Path('C:/NES/Gradius (USA).nes').read_bytes()
    assert hashlib.sha1(raw).hexdigest()=='92645fe142861c3d3fda209bb906ad2b0e353988'
    source=OUT/'source';source.mkdir(parents=True,exist_ok=True)
    marker=source/'src/entrypoint.s'
    if not marker.exists():
        with zipfile.ZipFile(ROOT/'build/checkpoints/expanded-profiles-lr/source.zip') as z:z.extractall(source)
        text=marker.read_text();assert text.count('.include "x5_profiles.s"')==1
        marker.write_text(text.replace('.include "x5_profiles.s"','.include "x5_profiles.s"\n.include "vic_native_motion.s"'))
        cfg=source/'smb1base-mmc5-expanded.cfg';text=cfg.read_text()
        cfg.write_text(text.replace('SEGMENTS {','SEGMENTS {\n    VIC_CORE:load=X5_NEW_4B,type=ro;\n',1))
    cpu=MPU();cpu.memory[0x8000:]=raw[16:32784];dis=Disassembler(cpu)
    ranges=((0xa006,0xa0e0),(0xa285,0xa2c0))
    lines=['; Generated from the authenticated Gradius USA ROM. Do not hand-edit.',
           '; Original local screen coordinates/clamps; world/camera adaptation is separate.']
    aliases={name:STATE+offset for name,offset in MAP.values() if '+' not in name}
    aliases.update({name:STATE+offset for name,offset in FIELDS.items()})
    for name,addr in sorted(aliases.items()):lines.append(f'{name}=${addr:04x}')
    lines+=['.export '+','.join(sorted(aliases)),'.pushseg','.segment "VIC_CORE"','.proc VvNativeMotion']
    emitted=[]
    branch={'BCC':'jcc','BCS':'jcs','BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BVC':'jvc','BVS':'jvs'}
    for lo,hi in ranges:
        pc=lo
        while pc<hi:
            length,asm=dis.instruction_at(pc)
            assert pc+length<=hi,(hex(pc),asm)
            mnemonic,_,operand=asm.partition(' ')
            if mnemonic in branch or mnemonic in ('JMP','JSR'):
                target=int(operand[1:],16)
                assert target==0xa0e9 or any(a<=target<b for a,b in ranges),(hex(pc),asm)
                asm=(branch.get(mnemonic,mnemonic.lower())+' '+('VvMotionEnd' if target==0xa0e9 else f'Vn{target:04x}'))
            elif operand and not operand.startswith('#') and '$' in operand:
                match=re.search(r'\$([0-9a-fA-F]+)',operand);address=int(match[1],16)
                assert address in MAP,(hex(pc),asm)
                asm=mnemonic.lower()+' '+operand[:match.start()]+MAP[address][0]+operand[match.end():]
            else:asm=asm.lower()
            lines += [f'Vn{pc:04x}: {asm} ; original${pc:04x}']
            emitted.append(dict(address=pc,raw=bytes(cpu.memory[pc:pc+length]).hex(),asm=asm))
            pc+=length
        if lo==0xa006:lines+=['VvMotionEnd: rts']
    lines+=['.endproc','.popseg']
    lines += ['.include "vic_gear.s"']
    (source/'src/vic_native_motion.s').write_text('\n'.join(lines)+'\n')
    (source/'src/vic_gear.s').write_bytes((ROOT/'tools/reference/vic_gear.s').read_bytes())
    manifest=dict(original_rom_sha256=hashlib.sha256(raw).hexdigest(),
        ranges=[dict(start=a,end_exclusive=b,sha256=hashlib.sha256(raw[16+a-0x8000:16+b-0x8000]).hexdigest()) for a,b in ranges],
        memory_mapping={str(a):dict(symbol=n,address=STATE+o) for a,(n,o) in MAP.items()},
        aliases=aliases,instructions=emitted,
        scope='Retargeted native movement/tilt/twoOption position-ring component. No full gameplay/camera/weapon claim.')
    (OUT/'motion-retarget.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(instructions=len(emitted),state_start=STATE,output=str(source/'src/vic_native_motion.s'))))


if __name__=='__main__':main()
