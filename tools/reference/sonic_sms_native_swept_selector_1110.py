"""Earliest native16-cell selector around frozen original Sonic contacts.

No ROM/native admission or RAM grant. Terrain selection is read-only until
the first supported solid cell is known. A selected probe is staged only for
the unchanged contact API, preserving fractions and ContactGround's real path.
"""
from hashlib import sha256
from sonic_sms_compact_cold_worker_1110 import assemble
import sonic_sms_native_sweep_witness_1110 as Witness

CODE, CONTEXT = 0xbaca, 0xc0d5
FIELDS = ('CursorLo CursorHi Remaining Probes').split()
SOURCE = '''
.setcpu "6502"
.segment "SELECTOR"
SonicSweptHorizontal:
 lda Mode
 bne PreflightHorizontal
 jmp FrozenShapeHorizontal
PreflightHorizontal:
 jsr PreflightH
 bcs Begin
 jmp Fail
SonicSweptVertical:
 lda Mode
 bne PreflightVertical
 jmp FrozenShapeVertical
PreflightVertical:
 jsr PreflightV
 bcs Begin
 jmp Fail
Begin:
 lda #0
 sta SStatus
 sta SKind
 sta Probes
 lda WAxis
 sta SAxis
 lda WNegative
 sta SNegative
 lda WEdge
 sta SEdge
 lda WStartCellLo
 sta CursorLo
 lda WStartCellHi
 sta CursorHi
 lda WCellCount
 sta Remaining
 lda WAxis
 bne VerticalOrthogonal
 lda BodyHeight
 lsr
 clc
 adc YLo
 sta PScreenYLo
 lda YHi
 adc #0
 sta PScreenYHi
 bcc StartQueries
 jmp Overflow
VerticalOrthogonal:
 clc
 lda XLo
 adc #12
 sta PWorldXLo
 lda XHi
 adc #0
 sta PWorldXHi
 bcc StartQueries
 jmp Overflow
StartQueries:
 lda WAxis
 bne SetQueryY
 lda CursorLo
 sta PWorldXLo
 lda CursorHi
 sta PWorldXHi
 jmp ReadCell
SetQueryY:
 lda CursorLo
 sta PScreenYLo
 lda CursorHi
 sta PScreenYHi
ReadCell:
 inc Probes
 jsr NativePointRead
 bcs Classify
 lda PStatus
 jmp Fail
Classify:
 lda PAttributes
 and #2
 beq ClassifyTile
 jmp Unsupported
ClassifyTile:
 lda PTile
 cmp #$23
 beq EmptyCell
 cmp #$c2
 beq EmptyCell
 cmp #$c3
 beq EmptyCell
 lda PAttributes
 and #1
 beq EmptyCell
 lda WAxis
 bne CheckSpecial
 lda PTile
 cmp #$1c
 beq Unsupported
 cmp #$6b
 beq Unsupported
CheckSpecial:
 lda PTile
 cmp #$5f
 beq Unsupported
 cmp #$60
 beq Unsupported
 cmp #$67
 beq Unsupported
 cmp #$68
 beq Unsupported
 ; Stage the chosen cell origin as the original integer leading probe.
 ; Normal nonnegative shape offsets then enter genuine ContactGround.
 sec
 lda CursorLo
 sbc WEdge
 sta WSumLo
 lda CursorHi
 sbc #0
 bcc Overflow
 sta WSumHi
 ldy WPositionIndex
 lda WSumLo
 sta XLo,y
 lda WSumHi
 sta XHi,y
 jmp FrozenFormShape
EmptyCell:
 dec Remaining
 bne AdvanceCell
 lda #$80
 sta SDX
 jmp FrozenPublishShape
AdvanceCell:
 lda WNegative
 bne PreviousCell
 clc
 lda CursorLo
 adc #16
 sta CursorLo
 lda CursorHi
 adc #0
 bcs Overflow
 sta CursorHi
 jmp StartQueries
PreviousCell:
 sec
 lda CursorLo
 sbc #16
 sta CursorLo
 lda CursorHi
 sbc #0
 bcc Overflow
 sta CursorHi
 jmp StartQueries
Unsupported:
 lda #7
 bne Fail
Overflow:
 lda #10
Fail:
 sta SStatus
 lda #0
 sta SKind
 lda SStatus
 clc
 rts
'''


def build(*, code=CODE, context=CONTEXT, code_limit=0xbfe0):
    witness=Witness.build();shape=witness['shape'];point=shape['point']
    assert code>=witness['code_half_open'][1]
    assert context>=witness['context_half_open'][1] and context+len(FIELDS)<=0xc100
    fields={n:context+i for i,n in enumerate(FIELDS)}
    definitions=dict(fields,
        **{'W'+n:a for n,a in witness['fields'].items()},
        **{'S'+n:a for n,a in shape['context'].items()},
        **{'P'+n:a for n,a in point['fields'].items()},
        Mode=shape['context']['Mode'],BodyHeight=0xc042,XLo=0xc071,XHi=0xc072,YLo=0xc074,YHi=0xc075,
        NativePointRead=point['entry'],PreflightH=witness['symbols']['SonicSweepPreflightHorizontal'],
        PreflightV=witness['symbols']['SonicSweepPreflightVertical'],
        FrozenShapeHorizontal=shape['entrypoints']['SonicShapeHorizontal'],
        FrozenShapeVertical=shape['entrypoints']['SonicShapeVertical'],
        FrozenFormShape=shape['symbols']['FormShape'],FrozenPublishShape=shape['symbols']['PublishShape'])
    text='\n'.join(f'{n}=${a:04x}'for n,a in definitions.items())+'\n'+SOURCE
    result=assemble(text,{'SELECTOR':(code,code_limit-code)})
    assert not any(x['mode']in('zpg','zpx','zpy','inx','iny','ind')for x in result['instructions'])
    image=result['images']['SELECTOR'];end=code+len(image)
    return dict(witness=witness,shape=shape,point=point,image=image,fields=fields,
        symbols=result['symbols'],code_half_open=[code,end],context_half_open=[context,context+len(FIELDS)],
        instructions=result['instructions'],image_SHA256=sha256(image).hexdigest(),
        requires_eighth_carrier=end>0xbc00,over_seven_rows=max(0,end-0xbc00),
        no_native_hook_or_RAM_grant=True,proposed_eighth_page=330 if end>0xbc00 else None)
