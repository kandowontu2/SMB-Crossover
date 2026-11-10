"""Proposed old-position witness/preflight for native16 sweep, not collision.

Capture belongs immediately before unchanged original PositionStep, after
motor/caps/pose/animation. The preflight checks actual24-bit integration and
returns the inclusive old-to-new leading-cell span (at most3 cells). No contact,
PointRead, host hook, lifetime, code/RAM allocation or gameplay is added here.
"""
from sonic_sms_compact_cold_worker_1110 import assemble
import sonic_sms_native_shape_contact_1110 as Shape

CODE, CONTEXT = 0xb940, 0xc0bc
FIELDS = ('OldXFraction OldXLo OldXHi OldYFraction OldYLo OldYHi Ready '
          'Axis PositionIndex VelocityIndex Status Negative Edge '
          'OldLeadingLo OldLeadingHi NewLeadingLo NewLeadingHi '
          'StartCellLo StartCellHi EndCellLo EndCellHi CellCount '
          'SumFraction SumLo SumHi').split()
STATUS = {'valid':0,'unsupported_mode':8,'noncanonical_velocity':9,
          'coordinate_overflow':10,'unsupported_body':11,'missing_witness':12,
          'inconsistent_integrated_position':13,'oversized_displacement':14}
SOURCE = '''
.setcpu "6502"
.segment "WITNESS"
SonicSweepCapture:
 ldx #5
CaptureByte:
 lda XPosition,x
 sta OldXFraction,x
 dex
 bpl CaptureByte
 lda #$a7
 sta Ready
 rts
SonicSweepPreflightHorizontal:
 lda #0
 sta Axis
 sta PositionIndex
 sta VelocityIndex
 beq Begin
SonicSweepPreflightVertical:
 lda #1
 sta Axis
 lda #3
 sta PositionIndex
 lda #$40
 sta VelocityIndex
Begin:
 lda #0
 sta Status
 sta Negative
 sta CellCount
 lda Mode
 cmp #1
 beq CheckWitness
 lda #8
 jmp Fail
CheckWitness:
 lda Ready
 cmp #$a7
 beq CheckBody
 lda #12
 jmp Fail
CheckBody:
 lda BodyWidth
 cmp #24
 bne BadBody
 lda BodyHeight
 cmp #24
 beq CheckVelocity
 cmp #32
 beq CheckVelocity
BadBody:
 lda #11
 jmp Fail
CheckVelocity:
 ldx VelocityIndex
 lda XVelocity+1,x
 bmi NegativeVelocity
 cmp #17
 bcc PositiveCapped
 jmp TooFar
PositiveCapped:
 lda XVelocity+2,x
 beq AddPosition
 jmp BadVelocity
NegativeVelocity:
 cmp #$f0
 bcs NegativeCapped
 jmp TooFar
NegativeCapped:
 lda XVelocity+2,x
 cmp #255
 beq NegativeCanonical
 jmp BadVelocity
NegativeCanonical:
 inc Negative
AddPosition:
 ldy PositionIndex
 clc
 lda OldXFraction,y
 adc XVelocity,x
 sta SumFraction
 lda OldXLo,y
 adc XVelocity+1,x
 sta SumLo
 lda OldXHi,y
 adc XVelocity+2,x
 sta SumHi
 lda SumFraction
 cmp XPosition,y
 beq FractionMatches
 jmp BadPosition
FractionMatches:
 lda SumLo
 cmp XPosition+1,y
 beq LowMatches
 jmp BadPosition
LowMatches:
 lda SumHi
 cmp XPosition+2,y
 beq PositionMatches
 jmp BadPosition
PositionMatches:
 lda #0
 ldx Negative
 bne SaveEdge
 lda BodyWidth
 ldx Axis
 beq SaveEdge
 lda BodyHeight
SaveEdge:
 sta Edge
 clc
 adc OldXLo,y
 sta OldLeadingLo
 lda OldXHi,y
 adc #0
 bcc OldLeadingValid
 jmp Overflow
OldLeadingValid:
 sta OldLeadingHi
 clc
 lda Edge
 adc XPosition+1,y
 sta NewLeadingLo
 lda XPosition+2,y
 adc #0
 bcc NewLeadingValid
 jmp Overflow
NewLeadingValid:
 sta NewLeadingHi
 lda OldLeadingLo
 and #$f0
 sta StartCellLo
 lda OldLeadingHi
 sta StartCellHi
 lda NewLeadingLo
 and #$f0
 sta EndCellLo
 lda NewLeadingHi
 sta EndCellHi
 lda Negative
 bne ReverseSpan
 sec
 lda EndCellLo
 sbc StartCellLo
 sta SumLo
 lda EndCellHi
 sbc StartCellHi
 jmp SpanHigh
ReverseSpan:
 sec
 lda StartCellLo
 sbc EndCellLo
 sta SumLo
 lda StartCellHi
 sbc EndCellHi
SpanHigh:
 bcc TooFar
 bne TooFar
 lda SumLo
 cmp #33
 bcs TooFar
 lsr
 lsr
 lsr
 lsr
 clc
 adc #1
 sta CellCount
 lda #0
 sec
 rts
BadVelocity:
 lda #9
 bne Fail
Overflow:
 lda #10
 bne Fail
BadPosition:
 lda #13
 bne Fail
TooFar:
 lda #14
Fail:
 sta Status
 lda #0
 sta CellCount
 lda Status
 clc
 rts
'''


def build(*, code=CODE, context=CONTEXT):
    shape = Shape.build()
    fields = {name: context+i for i, name in enumerate(FIELDS)}
    assert shape['code_half_open'][1] <= code
    assert context >= shape['context_half_open'][1] and context+len(FIELDS) <= 0xc100
    definitions = dict(fields, Mode=shape['context']['Mode'], BodyWidth=0xc041,
                       BodyHeight=0xc042, XVelocity=0xc020, XPosition=0xc070)
    text = '\n'.join(f'{n}=${a:04x}' for n, a in definitions.items())+'\n'+SOURCE
    result = assemble(text, {'WITNESS': (code, 0xbc00-code)})
    assert not any(x['mode'] in ('zpg','zpx','zpy','inx','iny','ind') for x in result['instructions'])
    return dict(shape=shape,image=result['images']['WITNESS'],fields=fields,
                symbols=result['symbols'],code_half_open=[code,code+result['used']['WITNESS']],
                context_half_open=[context,context+len(FIELDS)],instructions=result['instructions'],
                status=STATUS,source_census=shape['census'],no_RAM_or_code_grant=True,
                no_PointRead_or_contact_or_native_hook=True)
