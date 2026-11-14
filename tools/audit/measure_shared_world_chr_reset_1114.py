"""Unplaced29B native area-CHR restore fit; isolated CPU fixtures, no ROM output.

This measures an explicit policy proposal, not an allocation or composed image.
Modes are cleared only for the logical windows the existing macro resets.
Private window0 and all wide/special/HUD ownership state are preserved.
"""
from hashlib import sha256
import json

import replay_shared_world_sprite_images_1114 as C
from py65.devices.mpu6502 import MPU

START,END=0x8a63,0x8a80


def measure(raw):
    assert sha256(raw).hexdigest()==C.PIN
    b=dict(C.W.Symbols.bundle(),raw=raw)
    assert C.W.address(b,'LoadAreaPointer')==0x8a30
    at=16+126*8192+(START&8191);old=raw[at:at+END-START]
    banks=C.W.address(b,'CurrentCHRBank');modes=C.W.address(b,'X5ChrMode')
    table=C.W.address(b,'CHRBankInitValues');reload=C.W.address(b,'ReloadCHRBank');area=C.W.address(b,'AreaType')
    expected=bytearray((0xa2,20))
    for i in range(1,8):
        expected+=bytes((0x8e,(banks+i)&255,(banks+i)>>8))
        if i<7:expected+=b'\xe8'
    assert old==expected and len(old)==29
    suffix=raw[at+29:at+36]
    assert suffix==bytes((0xee,reload&255,reload>>8,0xad,area&255,area>>8,0x60))
    # Clear11..1 without disturbing private0. Restore7..1 from the existing
    # immutable native table; finalLDX reproduces original live outputX26.
    new=bytes((0xa2,11,0xa9,0,0x9d,modes&255,modes>>8,0xca,0xd0,0xfa,
        0xa2,6,0xbd,(table+1)&255,(table+1)>>8,0x9d,(banks+1)&255,(banks+1)>>8,
        0xca,0x10,0xf7,0xa2,26))+b'\xea'*6
    assert len(new)==len(old)
    reference=bytearray(65536)
    reference[0x8000:0xa000]=raw[16+126*8192:16+127*8192]
    reference[0xe000:]=raw[16+127*8192:16+128*8192]
    assert bytes(reference[table+1:table+8])==bytes(range(20,27))
    assert reference[END:END+7]==suffix
    cases=0;cycles=[set(),set()];minimum=255
    for flags in range(256):
        for area_type in range(4):
            for pattern in range(4):
                seed=bytearray(reference)
                for i in range(12):seed[banks+i]=(flags*13+pattern*47+i*7)&255;seed[modes+i]=(flags*37+pattern+i*11)&255
                seed[reload]=(flags+pattern*63)&255;seed[area]=area_type
                for i in range(3):seed[modes+12+i]=(flags+pattern+i*59)&255
                results=[]
                for which,code in enumerate((old,new)):
                    mem=bytearray(seed);mem[START:END]=code
                    cpu=MPU(memory=mem,pc=START);cpu.a=(area_type*4+pattern)&255
                    cpu.x=(flags*17+pattern)&255;cpu.y=area_type;cpu.p=flags;cpu.sp=208
                    cpu.stPushWord(0x5aff)
                    for _ in range(256):
                        if cpu.pc==0x5b00:break
                        minimum=min(minimum,cpu.sp);cpu.step()
                    else:raise AssertionError('Isolated native macro return bound')
                    regs=tuple(getattr(cpu,n)for n in('a','x','y','p','sp'))
                    results.append((mem,regs));cycles[which].add(cpu.processorCycles)
                before,after=results
                assert before[1]==after[1],(flags,area_type,pattern,before[1],after[1])
                for i in range(1,12):
                    assert after[0][modes+i]==0
                    after[0][modes+i]=before[0][modes+i]
                # Code bytes differ intentionally; all remaining RAM, including
                # private0, wide flag and special/HUD uppers, must be identical.
                assert before[0][:0x8000]==after[0][:0x8000]
                assert after[0][modes]==seed[modes] and after[0][modes+12:modes+15]==seed[modes+12:modes+15]
                assert after[0][banks+1:banks+8]==bytes(range(20,27))
                cases+=1
    return dict(ROM_SHA256=C.PIN,proposal_only=True,allocation_granted=False,ROM_composed=False,
        span=dict(PRG=126,CPU_half_open=[START,END],file_offset=at,bytes=len(old),old_hex=old.hex(),
            old_SHA256=sha256(old).hexdigest(),proposed_hex=new.hex(),proposed_SHA256=sha256(new).hexdigest()),
        retained_suffix=dict(CPU=END,hex=suffix.hex(),SHA256=sha256(suffix).hexdigest()),
        fields=dict(CurrentCHRBank=banks,X5ChrMode=modes,CHRBankInitValues=table,ReloadCHRBank=reload,AreaType=area),
        CPU_cases=cases,all256_input_flags=True,all4_legal_area_types=True,register_A_X_Y_P_SP_exact=True,
        original_cycles=sorted(cycles[0]),proposed_cycles=sorted(cycles[1]),minimum_SP=minimum,
        window0_and_wide_special_HUD_state_exact=True,logical_windows1_to7_exact=True,modes1_to11_zero=True,
        additional_stack_bytes=0,new_RAM_CHR_storage=0,existing_span_bytes=29,used_bytes=23,NOP_bytes=6,
        cold_Start_pipe_nextlevel_samepose_NMI_publication_gates='PENDING; isolated macro parity is insufficient',
        Mesen_run=False,outputs=0)


if __name__=='__main__':print(json.dumps(measure(C.ROM.read_bytes()),separators=(',',':')),flush=True)
