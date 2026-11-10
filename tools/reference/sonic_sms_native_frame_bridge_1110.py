"""Source-order ordinary frame with native sweep and explicit rollback.

No public/native hook or RAM lease. The source constructor is the literal
type0/tile-coordinate object contract; host pixel projection and lifecycle
admission remain separate. Original prefix/caps/motor/animation are unchanged.
"""
from hashlib import sha256
import re
import sonic_sms_native_swept_selector_1110 as Selector
from sonic_sms_compact_cold_worker_1110 import assemble

STATUS=0xc116
TILE_X,TILE_Y=0xc117,0xc118
SNAPSHOT,RECORD=0xc200,0xc300
MAPPED_ZERO=(0xc020,0xc021,0xc022,0xc060,0xc061,0xc062,
             0xc030,0xc031,0xc041,0xc042,0xc090,0xc0a1)


def prefix(core):
    text=Selector.Witness.Shape.Core.SOURCE.read_text()
    block=text.split('OrdinaryFrame:\n',1)[1].split('ComposedMotionStep:\n',1)[0]
    items=Selector.Witness.Shape.Core.parse('OrdinaryFrame:\n'+block)
    stop=next(i for i,x in enumerate(items)if x.get('op')=='JSR'and x.get('operand')=='PositionStep')
    items=items[:stop+1]
    labels={i:'Frame_'+(x['name']or f'Anonymous{i}')for i,x in enumerate(items)if x['kind']=='label'}
    named={x['name']:labels[i]for i,x in enumerate(items)if x['kind']=='label'and x['name']}
    anonymous=[i for i,x in enumerate(items)if x['kind']=='label'and not x['name']]
    output=[];normalized=[]
    for i,item in enumerate(items):
        if item['kind']=='label':output.append(labels[i]+':');continue
        assert item['kind']=='instruction',item
        op,operand=item['op'],item['operand']
        normalized.append((op,operand))
        if operand in(':+',':-'):
            choices=[j for j in anonymous if(j>i if operand==':+'else j<i)]
            operand=labels[choices[0]if operand==':+'else choices[-1]]
        elif operand in named:operand=named[operand]
        elif operand in core['symbols']:operand=f'${core["symbols"][operand]:04x}'
        elif re.fullmatch(r'\$[0-9a-fA-F]{1,2}',operand):operand=f'${0xc000+int(operand[1:],16):04x}'
        if op=='JSR'and item['operand']=='PositionStep':
            # Capture writes no donor state; retain the original X ABI too.
            output.extend((' txa',' pha',' jsr Capture',' pla',' tax'))
        output.append(' '+op.lower()+(' '+operand if operand else''))
    output.append('NativeFrameAfterPosition:')
    return '\n'.join(output),normalized


def build(*,code=None):
    selector=Selector.build();core=selector['shape']['core']
    if code is None:code=selector['code_half_open'][1]
    body,original_prefix=prefix(core)
    definitions=dict(Mode=selector['shape']['context']['Mode'],FrameStatus=STATUS,
        Snapshot=SNAPSHOT,ObjectRecord=RECORD,CtorTileX=TILE_X,CtorTileY=TILE_Y,
        OriginalFrame=core['symbols']['OrdinaryFrame'],Capture=selector['witness']['symbols']['SonicSweepCapture'],
        SweptH=selector['symbols']['SonicSweptHorizontal'],SweptV=selector['symbols']['SonicSweptVertical'],
        SMC1=core['SMC_operands'][0],SMC2=core['SMC_operands'][2])
    header='''
.setcpu "6502"
.segment "FRAME"
SonicNativeOrdinaryFrame:
 lda Mode
 bne NativeMode
 jmp OriginalFrame
NativeMode:
 cmp #1
 beq NativeBegin
 lda #8
 sta FrameStatus
 clc
 rts
NativeBegin:
 php
 pha
 txa
 pha
 tya
 pha
 jsr SaveFrame
 pla
 tay
 pla
 tax
 pla
 plp
'''
    footer='''
 lda $c030
 and #32
 bne Committed
 jsr SweptH
 bcc Aborted
 jsr SweptV
 bcc Aborted
Committed:
 lda #0
 sta FrameStatus
 sec
 rts
Aborted:
 sta FrameStatus
 jsr RestoreFrame
 lda FrameStatus
 clc
 rts
SaveFrame:
 ldx #0
SaveByte:
 lda $c000,x
 sta Snapshot,x
 inx
 cpx #$b4
 bne SaveByte
 ldx #1
SaveSMC:
 lda SMC1,x
 sta Snapshot+$b4,x
 lda SMC2,x
 sta Snapshot+$b6,x
 dex
 bpl SaveSMC
 rts
RestoreFrame:
 ldx #0
RestoreByte:
 lda Snapshot,x
 sta $c000,x
 inx
 cpx #$b4
 bne RestoreByte
 ldx #1
RestoreSMC:
 lda Snapshot+$b4,x
 sta SMC1,x
 lda Snapshot+$b6,x
 sta SMC2,x
 dex
 bpl RestoreSMC
 rts
; Original bank0:235E..239B, first actor type0 from232B list loader.
; All26 original bytes are retained, including unmodelled object fields.
SonicOriginalObjectConstructor:
 lda #0
 ldx #25
ClearObject:
 sta ObjectRecord,x
 dex
 bpl ClearObject
 lda CtorTileX
 lsr
 lsr
 lsr
 sta ObjectRecord+3
 lda CtorTileX
 asl
 asl
 asl
 asl
 asl
 sta ObjectRecord+2
 lda CtorTileY
 lsr
 lsr
 lsr
 sta ObjectRecord+6
 lda CtorTileY
 asl
 asl
 asl
 asl
 asl
 sta ObjectRecord+5
 ldx #5
PublishObjectPosition:
 lda ObjectRecord+1,x
 sta $c070,x
 dex
 bpl PublishObjectPosition
 lda #0
'''
    footer+='\n'.join(f' sta ${at:04x}'for at in MAPPED_ZERO)+'\n sta FrameStatus\n rts\n'
    text='\n'.join(f'{n}=${a:04x}'for n,a in definitions.items())+'\n'+header+body+'\n'+footer
    result=assemble(text,{'FRAME':(code,0xbfe0-code)})
    assert not any(x['mode']in('zpg','zpx','zpy','inx','iny','ind')for x in result['instructions'])
    image=result['images']['FRAME']
    return dict(selector=selector,image=image,code_half_open=[code,code+len(image)],
        symbols=result['symbols'],instructions=result['instructions'],source=text,
        snapshot_half_open=[SNAPSHOT,SNAPSHOT+0xb8],record_half_open=[RECORD,RECORD+26],
        private_inputs=dict(FrameStatus=STATUS,CtorTileX=TILE_X,CtorTileY=TILE_Y),
        original_prefix=original_prefix,image_SHA256=sha256(image).hexdigest(),
        remaining_before_header=0xbfe0-code-len(image),no_native_RAM_or_hook_or_lifecycle_grant=True)
