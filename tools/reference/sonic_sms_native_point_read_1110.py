"""Proposed no-ZP, read-only native PointRead leaf, assembled in memory.

Neither the code PC nor the explicit22-byte private scratch signature is a
host allocation. This leaf grants no raw identity, constructor or gameplay.
It accepts only the currently queryable column interval, not all32 retained
ring slots: [floor(actual screen-left/16), committed native parser end).
OOB is an explicit failure, never an empty traversable floor result.
"""
from sonic_sms_compact_cold_worker_1110 import assemble

CODE=0xb600
SCRATCH=0xc100
HOST={
    'ColumnSets':0x0721,'AreaParserTaskNum':0x0722,
    'CurrentPageLoc':0x0728,'CurrentColumnPos':0x0729,
    'BlockBufferColumnPos':0x04a0,
    'ScreenLeftPage':0x071d,'ScreenLeftX':0x071f,
    'BlockBuffer1':0x0300,'BlockBuffer2':0x03d0,'MTileAttribute':0xef36,
}
FIELDS=('WorldXLo WorldXHi ScreenYLo ScreenYHi Tile Attributes CellXLo CellXHi '
        'CellYLo CellYHi Status BufferIndex BufferPage '
        'StartColumnLo StartColumnHi EndColumnLo EndColumnHi '
        'QueryColumnLo QueryColumnHi ColumnCount ColumnOffset Phase').split()
STATUS={'valid':0,'vertical_outside':1,'initial_columns_incomplete':2,
        'unstable_parser_phase':3,'inconsistent_ring_cursor':4,
        'invalid_queryable_capacity':5,'outside_queryable_interval':6}
PHASE_ADD=(0,1,1,1,0,1,1,1)
SOURCE='''
.setcpu "6502"
.segment "POINT"
SonicNativePointRead:
 ; Inputs: WorldX16, screenY16. Caller owns the proposed private block.
 ; Successful C1/A=actual tile/X=exact attributes/Y=buffer index0..207.
 ; Failure C0/A=X=Y=0 with nonzero Status; it means outside/unavailable.
 ; All other flag results are unspecified. Inputs and maps are preserved.
 lda #0
 ldx #17
ClearOutputs:
 sta Tile,x
 dex
 bpl ClearOutputs
 lda ScreenYHi
 beq CheckVerticalLow
 ldx #1
 jmp Reject
CheckVerticalLow:
 lda ScreenYLo
 cmp #32
 bcs CheckVerticalBottom
 ldx #1
 jmp Reject
CheckVerticalBottom:
 cmp #240
 bcc CheckInitialColumns
 ldx #1
 jmp Reject
CheckInitialColumns:
 lda ColumnSets
 cmp #255
 beq CheckPhase
 ldx #2
 jmp Reject
CheckPhase:
 lda AreaParserTaskNum
 cmp #8
 bcc CheckColumn
 ldx #3
 jmp Reject
CheckColumn:
 sta Phase
 lda CurrentColumnPos
 cmp #16
 bcc CheckRing
 ldx #4
 jmp Reject
CheckRing:
 lda CurrentPageLoc
 and #1
 asl
 asl
 asl
 asl
 ora CurrentColumnPos
 cmp BlockBufferColumnPos
 beq FormStart
 ldx #4
 jmp Reject
FormStart:
 lda ScreenLeftPage
 lsr
 lsr
 lsr
 lsr
 sta StartColumnHi
 lda ScreenLeftPage
 asl
 asl
 asl
 asl
 sta StartColumnLo
 lda ScreenLeftX
 lsr
 lsr
 lsr
 lsr
 ora StartColumnLo
 sta StartColumnLo
 lda CurrentPageLoc
 lsr
 lsr
 lsr
 lsr
 sta EndColumnHi
 lda CurrentPageLoc
 asl
 asl
 asl
 asl
 ora CurrentColumnPos
 ldx Phase
 clc
 adc CommittedCurrentColumn,x
 sta EndColumnLo
 lda EndColumnHi
 adc #0
 sta EndColumnHi
 sec
 lda EndColumnLo
 sbc StartColumnLo
 sta ColumnCount
 lda EndColumnHi
 sbc StartColumnHi
 beq CheckCapacity
 ldx #5
 jmp Reject
CheckCapacity:
 lda ColumnCount
 beq InvalidCapacity
 cmp #33
 bcc FormQuery
InvalidCapacity:
 ldx #5
 jmp Reject
FormQuery:
 lda WorldXHi
 lsr
 lsr
 lsr
 lsr
 sta QueryColumnHi
 lda WorldXHi
 asl
 asl
 asl
 asl
 sta QueryColumnLo
 lda WorldXLo
 lsr
 lsr
 lsr
 lsr
 ora QueryColumnLo
 sta QueryColumnLo
 sec
 sbc StartColumnLo
 sta ColumnOffset
 lda QueryColumnHi
 sbc StartColumnHi
 beq CheckOffset
 ldx #6
 jmp Reject
CheckOffset:
 lda ColumnOffset
 cmp ColumnCount
 bcc ReadNativeCell
 ldx #6
 jmp Reject
ReadNativeCell:
 lda WorldXLo
 and #$f0
 sta CellXLo
 lsr
 lsr
 lsr
 lsr
 sta BufferIndex
 lda ScreenYLo
 and #$f0
 sta CellYLo
 sec
 sbc #32
 clc
 adc BufferIndex
 tay
 sty BufferIndex
 lda WorldXHi
 sta CellXHi
 and #1
 sta BufferPage
 beq ReadFirstBuffer
 lda BlockBuffer2,y
 jmp ReadAttributes
ReadFirstBuffer:
 lda BlockBuffer1,y
ReadAttributes:
 sta Tile
 tax
 lda MTileAttribute,x
 sta Attributes
 tax
 lda Tile
 sec
 rts
Reject:
 stx Status
 lda #0
 tax
 tay
 clc
 rts
CommittedCurrentColumn:
 .byte 0,1,1,1,0,1,1,1
'''


def build(*,code=CODE,scratch=SCRATCH):
    """Explicit proposed addresses only; caller must acquire their lifetime."""
    fields={name:scratch+i for i,name in enumerate(FIELDS)}
    assert scratch>=256 and scratch+len(FIELDS)<=65536
    definitions={**HOST,**fields}
    text='\n'.join(f'{name}=${value:04x}'for name,value in definitions.items())+'\n'+SOURCE
    result=assemble(text,{'POINT':(code,1024)})
    image=result['images']['POINT']
    assert code+len(image)<=0xbc00,'The current seven-row load ends atBC00; this is not a code grant'
    assert not any(i['mode']in('zpg','zpx','zpy','inx','iny','ind')for i in result['instructions'])
    assert not any(i['op']in('JSR','PHA','PHP','PLA','PLP')for i in result['instructions'])
    return dict(image=image,entry=code,fields=fields,scratch_half_open=[scratch,scratch+len(FIELDS)],
                code_half_open=[code,code+len(image)],instructions=result['instructions'],
                symbols=result['symbols'],status=STATUS,host=HOST,phase_add=PHASE_ADD,
                proposed_only=True,no_native_admission=True)
