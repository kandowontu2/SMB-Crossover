"""Mini-only native shuffle/direct-Goomba worker on the delivered fc7d build."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import re
import subprocess

import measure_mini_goomba_funded_1108_v2 as B

P,N,R=B.P,B.N,B.R
OUT=R/'build/mini-goomba-mini-only-1108-v4'
PIN='fc7d4554fed204e8efa4c4489ee70cd5c6529ce95e0d606ffee1cda525188ec5'
ENTRY=0xa038
NATIVE_LOOP=0xa155
AFTER_LOOP=0xa1c6
NATIVE_RENDER=0xa4ee
DRAW_FAST=(20,0xbdbf,0xbdf4)
SOURCE='''
.setcpu "6502"
.segment "CODE"
.export MiniLoop,MiniDrawActor,MiniGoomba,MiniEnd
; Entered solely by the already-qualified Mini-only DRAW_FAST sequence.
; Preserve the full 24-slot bidirectional shuffle and firebar turn.
MiniLoop:
 lda #23
 sta M0
 lda SpriteShuffleOffset
 clc
 adc #19
 cmp #24
 bcc :+
 sbc #24
:
 sta SpriteShuffleOffset
 lda FrameCounter
 lsr
 lda SpriteShuffleOffset
 bcc Negative
Positive:
 clc
 adc #13
 cmp #24
 bcc :+
 sbc #24
:
 beq PosFirebar
 tay
 ldx ObjectMetasprite,y
 beq PosNext
 jsr MiniDrawActor
PosNext:
 dec M0
 bpl Positive
 bmi Finish
PosFirebar:
 jsr WorldFirebarDrawAdmission
 lda #0
 beq PosNext
Negative:
 sec
 sbc #13
 bcs :+
 adc #24
:
 beq NegFirebar
 tay
 ldx ObjectMetasprite,y
 beq NegNext
 jsr MiniDrawActor
NegNext:
 dec M0
 bpl Negative
Finish:
 jmp NativeDrawTail
NegFirebar:
 jsr WorldFirebarDrawAdmission
 lda #0
 beq NegNext

MiniDrawActor:
 cpx #$fc
 bcs ReturnActor
 sta SpriteShuffleOffset
 jsr MiniGoomba
 lda SpriteShuffleOffset
ReturnActor:
 rts

MiniGoomba:
 cpx #$67
 beq GoombaPose
 cpx #$68
 bne Native
GoombaPose:
 cpy #7
 bcs Native
 lda HpNativeDrawHi,y
 ora ObjectVerticalFlip,y
 bne Native
 ; The no-override, zero-vertical-offset lane leaves M1 zero.
 sta M1
 lda SprObject_X_Position,y
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda SprObject_PageLoc,y
 sbc ScreenLeft_PageLoc
 sta R5
 lda SprObject_Y_HighPos,y
 sta R7
 lda SprObject_Y_Position,y
 sta R6
 lda SprObject_SprAttrib,y
 sta R3
 lda PlayerFacingDir,y
 lsr
 bne Left
 lda MetaspriteTableRightLo,x
 bne Pointer
Left:
 lda MetaspriteTableLeftLo,x
Pointer:
 sta R0
 lda #$af
 sta R1
 ; Preserve native rendering, clipping, capacity, rotation and epilogue.
 ; Only the generic actor setup before this existing call is bypassed.
 jmp NativeRenderCall
Native:
 jmp DrawMetasprite
MiniEnd:
'''


def assemble(b):
    OUT.mkdir(exist_ok=True)
    stem=OUT/'mini-goomba';src=stem.with_suffix('.s');cfg=stem.with_suffix('.cfg')
    names=[*P.NAMES,'M0','FrameCounter','SpriteShuffleOffset','ObjectMetasprite','WorldFirebarDrawAdmission']
    src.write_text(''.join(f'{n}=${P.address(b,n):04x}\n' for n in names)+
                   f'DrawMetasprite=${P.ORIGINAL:04x}\nNativeDrawTail=${AFTER_LOOP:04x}\n'
                   f'NativeRenderCall=${NATIVE_RENDER:04x}\n'+SOURCE)
    cfg.write_text(f'MEMORY{{P:start=${ENTRY:04x},size=$100,file=%O;}}SEGMENTS{{CODE:load=P,type=ro;}}\n')
    cc=R/'tools/Windows/cc65/bin';obj=stem.with_suffix('.o');blob=stem.with_suffix('.bin');lbl=stem.with_suffix('.lbl')
    subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',blob,'-Ln',lbl],check=True)
    obj.unlink()
    return blob.read_bytes(),src,{n:int(v,16) for v,n in re.findall(r'^al ([0-9A-F]+) \.(\w+)$',lbl.read_text(),re.M)}


def bind(raw,code):
    assert raw[B.off(B.CLEAR):B.off(B.CONTINUE)]==B.HIDE
    assert raw[B.off(B.SHARED_CLEAR):B.off(B.SHARED_CLEAR)+192]==B.HIDE
    # The only redirected caller is the Mini-only optimized draw sequence.
    def off20(pc):return 16+20*8192+pc-0xa000
    before=bytes.fromhex('a9558d6c01a9a18d6d01a9844c5a01')
    block=raw[off20(0xbd86):off20(0xbdf4)];assert block.count(before)==1
    at=off20(0xbd86)+block.index(before)
    gate=raw[off20(0xbd28):off20(0xbd4b)]
    assert gate.startswith(bytes.fromhex('0848ad0260c929d019a50fc908d013adf77f'))
    data=bytearray(before);data[1]=ENTRY&255;data[6]=ENTRY>>8
    skip=B.control(0x20,B.SHARED_CLEAR)+B.control(0x4c,B.CONTINUE)
    assert len(code)<=B.CONTINUE-ENTRY, (len(code),B.CONTINUE-ENTRY)
    clear=(skip+code).ljust(B.EXTENT,b'\xea')
    rows=[(4,B.off(B.CLEAR),B.HIDE,clear),(20,at,before,bytes(data))]
    new=bytearray(raw)
    for _,pos,old,after in rows:
        assert new[pos:pos+len(old)]==old
        new[pos:pos+len(after)]=after
    for pc in P.SITES:
        assert raw[B.off(pc):B.off(pc)+3]==new[B.off(pc):B.off(pc)+3]==B.control(0x20,P.ORIGINAL)
    return bytes(new),[dict(physical_PRG=b,file_offset=p,old_hex=a.hex(),new_hex=z.hex()) for b,p,a,z in rows]


def main():
    raw=P.ROM.read_bytes();assert P.sha(raw)==PIN
    b=P.bundle(raw);closure=B.ownership(b);code,source,l=assemble(b)
    print(dict(code_bytes=len(code),labels=l),flush=True)
    after,patches=bind(raw,code)
    result=dict(passed=True,ROM_written=False,source_only=True,base_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
                code_bytes=len(code),labels=l,source_SHA256=P.sha(source.read_bytes()),patches=patches,
                ownership=closure,descriptors=P.prove_art(b))
    (OUT/'proposal.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':main()
