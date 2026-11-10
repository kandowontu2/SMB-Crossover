"""Proposed native16px flat geometry around unchanged SMS contact routines.

Mode0 is the original32px terrain leaf. Mode1 performs a real PointRead and
adapts a16px boundary into the donor's32px-aligned clipping expression. This
does not patch OrdinaryFrame, allocate RAM, admit raw43 or add native effects.
"""
from hashlib import sha256
from py65.devices.mpu6502 import MPU
import sonic_sms_relocated_core_1110 as Core
import sonic_sms_native_point_read_1110 as Point
from sonic_sms_compact_cold_worker_1110 import assemble

CODE=0xb780
CONTEXT=0xc0b4
CONTEXT_FIELDS=('Mode Status Kind Axis Negative Edge DX DY').split()
STATUS={**Point.STATUS,'unsupported_metatile':7,'unsupported_mode':8,
        'noncanonical_velocity':9,'coordinate_overflow':10,'unsupported_body':11}
KIND={'none':0,'right_wall':1,'left_wall':2,'floor':3,'ceiling':4}
SOURCE='''
.setcpu "6502"
.segment "ADAPTER"
SonicShapeHorizontal:
 lda Mode
 beq LegacyHorizontal
 cmp #1
 beq NativeHorizontal
 lda #8
 jmp Fail
LegacyHorizontal:
 jmp OriginalHorizontalTerrain
SonicShapeVertical:
 lda Mode
 beq LegacyVertical
 cmp #1
 beq NativeVertical
 lda #8
 jmp Fail
LegacyVertical:
 jmp OriginalVerticalTerrain
NativeHorizontal:
 lda #0
 sta Axis
 beq NativeBegin
NativeVertical:
 lda #1
 sta Axis
NativeBegin:
 lda #0
 sta Status
 sta Kind
 sta Negative
 lda BodyWidth
 cmp #24
 beq CheckHeight
 lda #11
 jmp Fail
CheckHeight:
 lda BodyHeight
 cmp #24
 beq SelectAxis
 cmp #32
 beq SelectAxis
 lda #11
 jmp Fail
SelectAxis:
 lda Axis
 bne VerticalProbe
 lda VXMid
 bmi HorizontalNegative
 lda VXHi
 beq HorizontalPositive
 jmp BadVelocity
HorizontalNegative:
 lda VXHi
 cmp #255
 beq HorizontalNegativeReady
 jmp BadVelocity
HorizontalNegativeReady:
 inc Negative
 lda #0
 beq HorizontalEdge
HorizontalPositive:
 lda BodyWidth
HorizontalEdge:
 sta Edge
 sta DX
 lda BodyHeight
 lsr
 sta DY
 jmp FormPoint
VerticalProbe:
 lda VYMid
 bmi VerticalNegative
 lda VYHi
 beq VerticalPositive
 jmp BadVelocity
VerticalNegative:
 lda VYHi
 cmp #255
 beq VerticalNegativeReady
 jmp BadVelocity
VerticalNegativeReady:
 inc Negative
 lda #0
 beq VerticalEdge
VerticalPositive:
 lda BodyHeight
VerticalEdge:
 sta Edge
 sta DY
 lda BodyWidth
 lsr
 sta DX
FormPoint:
 clc
 lda XLo
 adc DX
 sta PWorldXLo
 lda XHi
 adc #0
 sta PWorldXHi
 bcc FormY
 jmp CoordinateOverflow
FormY:
 clc
 lda YLo
 adc DY
 sta PScreenYLo
 lda YHi
 adc #0
 sta PScreenYHi
 bcc QueryNative
 jmp CoordinateOverflow
QueryNative:
 jsr NativePointRead
 bcs NativeAvailable
 lda PStatus
 jmp Fail
NativeAvailable:
 lda PAttributes
 and #2
 beq CheckSolid
 lda #7
 jmp Fail
CheckSolid:
 ; Native coin dispatch precedes clipping. Tile23 is the blank BG cell
 ; left while a struck block is represented by its separate native actor.
 lda PTile
 cmp #$23
 beq EmptyShape
 cmp #$c2
 beq EmptyShape
 cmp #$c3
 beq EmptyShape
 lda PAttributes
 and #1
 bne CheckSpecialSolid
EmptyShape:
 lda #$80
 sta DX
 jmp PublishShape
CheckSpecialSolid:
 lda Axis
 bne CheckOrdinarySpecial
 lda PTile
 cmp #$1c
 beq UnsupportedTile
 cmp #$6b
 beq UnsupportedTile
CheckOrdinarySpecial:
 lda PTile
 cmp #$5f
 beq UnsupportedTile
 cmp #$60
 beq UnsupportedTile
 cmp #$67
 beq UnsupportedTile
 cmp #$68
 bne FormShape
UnsupportedTile:
 lda #7
 jmp Fail
FormShape:
 ; ContactClip uses (leading-point &FFE0)+signed offset-edge.
 ; Positive travel uses the cell's near boundary (phase0/16).
 ; Negative travel uses its far boundary (phase16/32).
 lda Axis
 beq HorizontalOrigin
 lda PCellYLo
 jmp CellPhase
HorizontalOrigin:
 lda PCellXLo
CellPhase:
 and #16
 sta DX
 lda Negative
 beq FormKind
 clc
 lda DX
 adc #16
 sta DX
FormKind:
 lda Axis
 asl
 clc
 adc Negative
 adc #1
 sta Kind
PublishShape:
 lda DX
 sta ShapeOffset
 lda Edge
 sta EdgeOffset
 ; Original table index0 has neutral magnet/Xslide/Yslide factors.
 ; This is the explicit flat-host shape input, not a donor tileflag.
 lda #0
 sta ShapeClass
 lda Axis
 bne VerticalContact
 lda ActorFlags
 and #$bf
 sta ActorFlags
 jsr OriginalHorizontalContact
 lda #0
 sec
 rts
VerticalContact:
 lda ActorFlags
 and #$7f
 sta ActorFlags
 jsr OriginalVerticalContact
 lda #0
 sec
 rts
BadVelocity:
 lda #9
 bne Fail
CoordinateOverflow:
 lda #10
Fail:
 sta Status
 lda #0
 sta Kind
 lda Status
 clc
 rts
'''


def census(program,context=CONTEXT):
    direct=set();indexed=[];rows=[]
    for pc in program['boundaries'].values():
        offset=pc-Core.CODE_START
        op,mode=MPU.disassemble[program['image'][offset]]
        if Core.SIZES[mode]!=3:continue
        operand=int.from_bytes(program['image'][offset+1:offset+3],'little')
        if not 0xc000<=operand<0xc100:continue
        if mode=='abs':targets=[operand]
        elif mode=='aby':
            assert operand in(0xc071,0xc072),(hex(pc),op,mode,hex(operand))
            targets=[operand,operand+3]
            indexed.append(dict(pc=pc,op=op,mode=mode,base=operand,indices=[0,3]))
        elif mode=='abx':
            assert operand in(0xc020,0xc021,0xc022),(hex(pc),op,mode,hex(operand))
            targets=[operand,operand+0x40]
            indexed.append(dict(pc=pc,op=op,mode=mode,base=operand,indices=[0,0x40]))
        else:raise AssertionError(('State addressing',hex(pc),op,mode))
        direct.update(targets);rows.append((pc,op,mode,operand))
    assert len(indexed)==10 and max(direct)==0xc0b3
    # Inspect the literal original control around those indexed accesses.
    # Y is set to0 by HorizontalContact and3 by VerticalContact, and never
    # changes through the common contact code. ContactSlide X is only0/40.
    items=program['items'];names=program['symbols']
    between=lambda lo,hi:[i for n,i in enumerate(items)if i['kind']=='instruction'and
                          lo<=program['boundaries'].get(n,-1)<hi]
    slide=between(names['ContactSlide'],names['ContactYSlide'])
    assert not any(i['op']in('LDX','TAX','INX','DEX','PLX')for i in slide)
    contacts=between(names['ContactBegin'],names['ContactYSlide'])
    assert not any(i['op']in('LDY','TAY','INY','DEY','PLY')for i in contacts)
    assert names['ContactSlide']>names['ContactYVelocity']>names['VerticalContact']
    assert not set(range(context,context+len(CONTEXT_FIELDS)))&direct
    # Valid private read-pointer producers address carrier tables or the
    # retired source fixture map, never this proposed tail context.
    return dict(all_state_operand_sites=len(rows),distinct_state_bytes=len(direct),
                last_state_byte=max(direct),indexed_sites=indexed,
                proposed_unused_context_half_open=[context,context+len(CONTEXT_FIELDS)],
                valid_source_pointer_domains='carrier shape/animation tables and source fixtureC800..D7FF only',
                no_host_ZP=True,no_lifetime_grant=True)


def build(*,code=CODE,context=CONTEXT):
    core=Core.build();point=Point.build()
    assert sha256(core['image']).hexdigest()=='e3606c66ae062243e669809a54edce4019586f2097858480a60da834b3c2657d'
    assert sha256(point['image']).hexdigest()=='82ee77ec5d6923e2e28e7bec31c9fb8a9b55922ec72dd525b1be74e61749771d'
    private={name:context+i for i,name in enumerate(CONTEXT_FIELDS)}
    defs={**private,**{'P'+name:at for name,at in point['fields'].items()},
          'NativePointRead':point['entry'],
          'OriginalHorizontalTerrain':core['symbols']['HorizontalTerrain'],
          'OriginalVerticalTerrain':core['symbols']['VerticalTerrain'],
          'OriginalHorizontalContact':core['symbols']['HorizontalContact'],
          'OriginalVerticalContact':core['symbols']['VerticalContact'],
          'VXMid':0xc021,'VXHi':0xc022,'VYMid':0xc061,'VYHi':0xc062,
          'XLo':0xc071,'XHi':0xc072,'YLo':0xc074,'YHi':0xc075,
          'BodyWidth':0xc041,'BodyHeight':0xc042,'ActorFlags':0xc030,
          'ShapeOffset':0xc080,'EdgeOffset':0xc081,'ShapeClass':0xc082}
    text='\n'.join(f'{name}=${at:04x}'for name,at in defs.items())+'\n'+SOURCE
    result=assemble(text,{'ADAPTER':(code,1024)})
    image=result['images']['ADAPTER'];end=code+len(image)
    assert point['code_half_open'][1]<=code and end<=0xbc00
    assert not any(i['mode']in('zpg','zpx','zpy','inx','iny','ind')for i in result['instructions'])
    return dict(core=core,point=point,image=image,code_half_open=[code,end],context=private,
                context_half_open=[context,context+len(CONTEXT_FIELDS)],symbols=result['symbols'],
                entrypoints={name:result['symbols'][name]for name in('SonicShapeHorizontal','SonicShapeVertical')},
                census=census(core,context),instructions=result['instructions'],status=STATUS,kind=KIND,
                frozen_core_unchanged=True,no_native_admission=True,no_RAM_or_code_grant=True)
