"""Run Mini's existing projectile renderer from its authenticated C2 overlay."""
import argparse
import hashlib
import json
from pathlib import Path

from prepare_mini_fireball_art_1108 import REFERENCE, assemble, patch, verify_cold
from prepare_mini_no_wall_1108 import CODE, COOKIE
from prepare_mini_side_alias_1108 import BASE, PIN, compare_memory
from prepare_mini_mario_native_power_1103_v56 import N, bundle
from prepare_selected_native_packet_v1 import R, sha
from profile_mini_busy_1108_v1 import fixture

META=CODE+5120
STAGE=BASE.with_name('art-stage.bin')
DRAW_SOURCE=0xbdc1
DRAW_RUN=0xd460
GATE_RUN=0xd445
DRAW_RETURN=0xbdb0
FIRE_BANK=89


def profile(before,after,draw_size):
    """Real linked GameCore, rendering enabled, powered and unpowered."""
    images=[bundle(raw) for raw in (before,after)]
    rows=[]
    for powered in (False,True):
        for actors in (0,3):
            pair=[fixture(image,actors,False,False) for image in images]
            savings=[]
            for frame in range(2,22):
                result=[]
                for m in pair:
                    key=64 if powered and frame in (10,13) else 0
                    N.put(m,PlayerStatus=2 if powered else 0,FrameCounter=frame,
                          SavedJoypadBits=key,SavedJoypad1Bits=key,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                    result.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
                assert all(result[0][f]==result[1][f] for f in ('A','X','Y','P')),(frame,result)
                # Staged executable bytes and payload-derived cookies differ.
                compare_memory(*pair,ram_exclusions={2:[(0x1239,0x124f),(0x1445,0x145c),
                                                        (0x1460,0x1460+draw_size),(0x1fe3,0x1ff0)],
                                                     3:[(0x1fe3,0x1ff0)]})
                assert pair[0][0x15a:0x17b]==pair[1][0x15a:0x17b],(powered,actors,frame,'Live SMC')
                savings.append(result[0]['CPU']-result[1]['CPU'])
            rows.append(dict(powered=powered,actors=actors,minimum=min(savings),maximum=max(savings),average=sum(savings)/len(savings)))
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(BASE)==PIN
    original=BASE.read_bytes()
    old_stage=STAGE.read_bytes()
    wrapper=original[META+0x239:META+0x24f]
    assert wrapper.hex()=='088d6a01a9b08d6c01a9bd8d6d01a9d9205a01283860'
    fire=BASE.with_name('MINI_FB_HELPERS.bin').read_bytes()
    draw=fire[DRAW_SOURCE-0xbd72:]
    return_bytes=fire[DRAW_RETURN-0xbd72:DRAW_SOURCE-0xbd72]
    assert len(return_bytes)==17 and 0<len(draw)<128 and draw[-1]==0x60
    args.output.mkdir(exist_ok=True)
    assert not (args.output/'proof.json').exists()
    asm=args.output/'art-fast.s'
    cold_source=REFERENCE.read_text()
    assert cold_source.count(' jmp __RESTORE_RUN__')==1
    cold_source=cold_source.replace(' jmp __RESTORE_RUN__',' jsr $d23c\n jmp __RESTORE_RUN__')
    asm.write_text(cold_source+'''
.export MiniFireballDrawGate
MiniFireballDrawGate:
 php
 pha
 lda $25
 ora $26
 beq Empty
 txa
 pha
 tya
 pha
 jsr $d460
 pla
 tay
 pla
 tax
Empty:
 pla
 plp
 sec
 rts
''',encoding='utf-8')
    staged=args.output/'art-fast.bin'
    labels=assemble(asm,STAGE.with_suffix('.cfg').read_text(),staged)
    new_stage=staged.read_bytes()
    assert len(new_stage)==len(old_stage)+26<=0xa0
    # The phase writer stays at the same CPU address with byte-exact code.
    assert labels['MiniFireballPose']==0xd400 and labels['MiniFireballDrawGate']==GATE_RUN
    phase_start=labels['__PHASE_LOAD__']-0xd300
    assert new_stage[phase_start:phase_start+0x45]==old_stage[0x3e:]
    gate=args.output/'empty-draw.s'
    gate.write_text('''.setcpu "6502"
.segment "GATE"
 jmp $d445                 ; Runtime caller at D239.
 lda #$b0                  ; Cold-only caller at D23C.
 sta $016c
 lda #$bd
 sta $016d
 lda #$d9
 jmp $015a
''',encoding='utf-8')
    gate_bin=gate.with_suffix('.bin')
    assemble(gate,'MEMORY{M:start=$d239,size=22,file=%O;}SEGMENTS{GATE:load=M,type=ro;}',gate_bin)
    raw=bytearray(original)
    previous=R/'build/mini-native-lifts-v2-1108/candidate.nes'
    attributes=previous.read_bytes()[META+0x300:META+0x400]
    patch(raw,META+0x300,old_stage+attributes[len(old_stage):len(new_stage)],new_stage)
    patch(raw,META+0x239,wrapper,gate_bin.read_bytes().ljust(len(wrapper),b'\xff'))
    constructor=args.output/'copy-draw.s'
    constructor.write_text(f'''.setcpu "6502"
.segment "COPY"
 ldx #{len(draw)-1}
Copy:
 lda $bdc1,x
 sta $d460,x
 dex
 bpl Copy
 sec
 rts
''',encoding='utf-8')
    code=constructor.with_suffix('.bin')
    assemble(constructor,'MEMORY{M:start=$bdb0,size=17,file=%O;}SEGMENTS{COPY:load=M,type=ro;}',code)
    prg=16+FIRE_BANK*8192+(DRAW_RETURN&8191)
    patch(raw,prg,return_bytes,code.read_bytes().ljust(len(return_bytes),b'\xea'))
    raw[COOKIE+3:COOKIE+16]=hashlib.sha256(raw[CODE:CODE+7168]).digest()[:13]
    verify_cold(raw,attributes,new_stage[phase_start:])
    m=fixture(bundle(raw),0,False,False)
    assert m.ram[2][0x1460:0x1460+len(draw)]==draw
    rows=profile(original,raw,len(draw))
    assert all(row['minimum']>0 for row in rows)
    ranges=[(COOKIE+3,COOKIE+16),(META+0x239,META+0x24f),
            (META+0x300,META+0x300+len(new_stage)),(prg,prg+len(return_bytes))]
    report=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=hashlib.sha256(raw).hexdigest(),
        full_cpu=rows,native_draw_address=DRAW_RUN,native_draw_bytes=draw.hex(),
        ram_exclusions={2:[(0x1239,0x124f),(0x1445,0x145c),(0x1460,0x1460+len(draw)),(0x1fe3,0x1ff0)],
                        3:[(0x1fe3,0x1ff0)]},
        patches=[dict(file_offset=a,old_hex=original[a:b].hex(),new_hex=raw[a:b].hex()) for a,b in ranges],
        scope='Direct Mini-owned renderer, exact CHR art and whole GameCore state. Native render and cold lifetime tested separately.')
    (args.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,full_cpu=rows)))


if __name__=='__main__':
    main()
