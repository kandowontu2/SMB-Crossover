"""Native bounded hanging/falling fruit, donor hit and source point sprites."""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    prior=json.loads((O/'native-terrain-v36-layout.json').read_text());assert json.loads((O/'native-terrain-v37-CPU.json').read_text())['passed']
    assert json.loads((O/'native-atlas-v38.json').read_text())['passed']
    source=(O/'native-terrain-v36.s').read_text();assert source.count(' jmp DkjrNativeDrawBody\n')==1
    source=source.replace(' jmp DkjrNativeDrawBody\n',' jmp DkNativeDraw\n',1)
    leaves='''
.export DkNativeDraw,DkNativeEffects,DkEmitEffectPair,DkNativeEffectsEnd
; Body emits its four original vertical pairs and stable unbanked zeroheader.
; Capacity rejection still means handled: never fall through to raw40's old
; native art tables. All effects preserve the same public AXYP/Cset contract.
DkNativeDraw:
 jsr DkjrNativeDrawBody
DkNativeEffects:
 php
 pha
 txa
 pha
 tya
 pha
 lda GuestOamRotationActive
 beq DkEffectsAligned
 lda RgOamRotation
 and #3
 bne DkEffectsDone
DkEffectsAligned:
 ; Typed world records project only currently available hanging fruits.
 lda FruitCount
 cmp #5
 bcs DkFallingStart
 ldx #0
DkHangingLoop:
 lda $c09a,x
 beq DkHangingNext
 lda $c42c,x
 sec
 sbc #$a4
 cmp #9
 bcs DkHangingNext
 and #3
 bne DkHangingNext
 lda $c42c,x
 sec
 sbc #$4c
 sta WTile
 lda $c420,x
 sec
 sbc ScreenLeft_X_Pos
 sta WLeft
 lda $c428,x
 sec
 sbc #1
 sta WTop
 lda $c08d,x
 and #3
 tay
 lda DkEffectPalette,y
 sta WKind
 jsr DkEmitEffectPair
 lda WLeft
 clc
 adc #8
 sta WLeft
 inc WTile
 inc WTile
 jsr DkEmitEffectPair
DkHangingNext:
 inx
 cpx #4
 bcc DkHangingLoop
DkFallingStart:
 ldx #$30
DkFallingLoop:
 lda $c200,x
 clc
 adc #8
 cmp $c204,x
 bne DkFallingNext
 lda $c201,x
 cmp #$a4
 bcc DkFallingNext
 cmp #$b0
 bcs DkFallingNext
 and #1
 bne DkFallingNext
 lda $c201,x
 clc
 adc #1
 cmp $c205,x
 bne DkFallingNext
 lda $c202,x
 cmp $c206,x
 bne DkFallingNext
 and #$80
 bne DkFallingNext
 lda $c203,x
 cmp $c207,x
 bne DkFallingNext
 sta WLeft
 lda $c200,x
 sta WTop
 lda $c201,x
 sec
 sbc #$24
 sta WTile
 lda $c202,x
 and #3
 tay
 lda DkEffectPalette,y
 sta WKind
 lda $c202,x
 and #$60
 ora WKind
 sta WKind
 jsr DkEmitEffectPair
DkFallingNext:
 txa
 clc
 adc #8
 tax
 cpx #$40
 bcc DkFallingLoop
 lda #0
 sta WCount
DkSingleLoop:
 ldy WCount
 ldx DkSingleOffsets,y
 lda $c202,x
 and #$80
 bne DkSingleNext
 lda $c201,x
 sta WTile
 cmp #$90
 bcc DkFindPoint
 cmp #$94
 bcs DkFindPoint
 sec
 sbc #$90
 asl
 clc
 adc #$8c
 bne DkSingleTile
DkFindPoint:
 ldy #7
DkFindPointLoop:
 lda DkPointTiles,y
 cmp WTile
 beq DkPointFound
 dey
 bpl DkFindPointLoop
 bmi DkSingleNext
DkPointFound:
 tya
 asl
 ora #$70
DkSingleTile:
 sta WTile
 lda $c200,x
 sta WTop
 lda $c203,x
 sta WLeft
 lda $c202,x
 and #$60
 ora #3
 sta WKind
 jsr DkEmitEffectPair
DkSingleNext:
 inc WCount
 lda WCount
 cmp #5
 bcc DkSingleLoop
DkEffectsDone:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
; One complete native8x16 entry, bounded before all writes. X is the source
; index and survives. Y and A are private scratch; public wrapper saves both.
DkEmitEffectPair:
 ldy CurrentOAMOffset
 beq DkEmitNo
 tya
 and #3
 bne DkEmitNo
 lda WTop
 cmp #239
 bcs DkEmitNo
 lda WLeft
 cmp #249
 bcs DkEmitNo
 lda WTop
 sta Sprite_Data,y
 lda WTile
 ora #1
 sta Sprite_Data+1,y
 lda WKind
 sta Sprite_Data+2,y
 lda WLeft
 sta Sprite_Data+3,y
 tya
 clc
 adc #4
 sta CurrentOAMOffset
DkEmitNo:
 rts
DkEffectPalette:.byte 2,3,1,1
DkSingleOffsets:.byte $00,$04,$30,$34,$c0
DkPointTiles:.byte $f1,$f2,$5e,$f3,$f4,$f5,$f6,$f7
DkNativeEffectsEnd:
'''
    # These newly written branches are deliberately explicit short encodings;
    # ca65 verifies every range. Long cross-section edges use pseudo macros.
    leaves=leaves.replace(' bne DkEffectsDone',' jne DkEffectsDone')
    marker='DkjrComponentEnd:\n.export DkjrComponentEnd\n';assert source.count(marker)==1
    source=source.replace(marker,leaves+marker)
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-effects-pause-v39.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-effects-main-v39.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-effects-ports-v39.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    blob,L=A.assemble('native-effects-v39',source,cfg)
    old=(O/'native-terrain-v36.bin').read_bytes();assert blob[114:len(old)]==old[114:]
    assert L['DkPauseThaw']==0xd60c
    q=dict(prior);q.update(labels=L,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),draw_added_bytes=len(blob)-len(old),implemented_vector_rows={**prior['implemented_vector_rows'],'2':'DkNativeDraw'},
        scope='Private native art/effect output only. Original body/phase/fruit/points instructions remain unchanged. Actual source/tile/palette/clip/capacity and native Draw ingress CPU tests remain required.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-terrain-v36.s',O/'native-terrain-v37-CPU.json',O/'native-atlas-v38.json',O/'native-effects-v39.s',O/'native-effects-v39.bin']})
    (O/'native-effects-v39-layout.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','body_bytes','header_spare','draw_added_bytes','metadata_spare']}))


if __name__=='__main__':main()
