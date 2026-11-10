"""Dedicated Sonic native service/epoch/projection proposal; no public hook.

Only listed host globals are read/written. No host ZP is borrowed as scratch.
Unimplemented service rows reject; this envelope is not gameplay admission.
"""
from hashlib import sha256
import struct
import sonic_sms_native_eighth_payload_1110 as Payload
from sonic_sms_compact_cold_worker_1110 import assemble

CONTEXT=0xc119
FIELDS=('Ready','HaveEpoch','Epoch','CacheX','CachePage','CacheY','CacheYHigh','OldX','OldInput')
HOST=('GameEngineSubroutine','GamePauseStatus','TimerControl','FrameCounter','SavedJoypadBits','AreaType',
      'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
      'Player_X_Scroll','Player_X_Speed','Player_X_MoveForce','Player_Y_Speed','Player_Y_MoveForce',
      'Player_State','PlayerFacingDir','PlayerStatus','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','GuestPowerupUpdate')
ROWS=('Main','No','No','No','No','No','Status','No','No','Yes','No','No','No','No','No','Fresh','No','No','No',
      'Fresh','No','No','No','Yes','No','No','No','No','No','No','No','No','No','Powerup','Yes','No','Fresh','No')

SOURCE='''
.setcpu "6502"
.segment "SERVICES"
SonicHostFresh:
 lda #0
 sta Ready
 sta HaveEpoch
SonicHostYes:
 sec
 rts
SonicHostNo:
 clc
 rts
SonicHostStatus:
 lda PlayerStatus
 sec
 rts
SonicHostMain:
 lda GameEngineSubroutine
 cmp #8
 beq HostOrdinary
 lda #0
 sta HaveEpoch
 clc
 rts
HostOrdinary:
 lda GamePauseStatus
 and #1
 ora TimerControl
 beq HostUnpaused
 lda #0
 sta HaveEpoch
 sec
 rts
HostUnpaused:
 lda AreaType
 beq HostUnavailable
 lda Player_Y_HighPos
 cmp #1
 bne HostUnavailable
 lda Player_Y_Position
 cmp #240
 bcc HostInPlane
HostUnavailable:
 lda #9
 sta FrameStatus
 sec
 rts
HostInPlane:
 lda Ready
 bne HostReady
 jsr SonicHostConstruct
HostReady:
 lda HaveEpoch
 beq HostNewEpoch
 lda FrameCounter
 cmp Epoch
 bne HostNewEpoch
 sec
 rts
HostNewEpoch:
 lda FrameCounter
 sta Epoch
 lda #1
 sta HaveEpoch
 lda Player_X_Position
 cmp CacheX
 bne HostCorrectX
 lda Player_PageLoc
 cmp CachePage
 beq HostCheckY
HostCorrectX:
 jsr ImportX
HostCheckY:
 lda Player_Y_Position
 cmp CacheY
 bne HostCorrectY
 lda Player_Y_HighPos
 cmp CacheYHigh
 beq HostStep
HostCorrectY:
 lda Player_Y_Position
 jsr ImportY
HostStep:
 lda Player_X_Position
 sta OldX
 lda $c0a8
 sta OldInput
 lda SavedJoypadBits
 sta $c0a8
 inc $c092
 jsr NativeFrame
 bcs HostProject
 dec $c092
 lda OldInput
 sta $c0a8
 lda #0
 sta Player_X_Scroll
 sec
 rts
HostProject:
 lda $c071
 sec
 sbc OldX
 sta Player_X_Scroll
 lda $c071
 sta Player_X_Position
 sta CacheX
 lda $c072
 sta Player_PageLoc
 sta CachePage
 lda $c074
 sta Player_Y_Position
 sta CacheY
 lda $c075
 clc
 adc #1
 sta Player_Y_HighPos
 sta CacheYHigh
 lda $c070
 sta Player_X_MoveForce
 lda $c060
 sta Player_Y_MoveForce
 lda $c061
 sta Player_Y_Speed
 lda $c020
 lsr
 lsr
 lsr
 lsr
 sta OldInput
 lda $c021
 asl
 asl
 asl
 asl
 ora OldInput
 sta Player_X_Speed
 lda $c030
 and #2
 bne HostLeft
 lda #1
 bne HostFace
HostLeft:
 lda #2
HostFace:
 sta PlayerFacingDir
 lda $c030
 bmi HostGround
 ldy #2
 lda $c062
 bpl HostState
 dey
 bne HostState
HostGround:
 ldy #0
HostState:
 sty Player_State
 sec
 rts
SonicHostConstruct:
 lda #0
 sta CtorTileX
 sta CtorTileY
 jsr OriginalConstructor
 lda #0
 sta $c047
 sta $c048
 sta $c058
 sta $c0aa
 sta $c0ab
 jsr ImportX
 lda Player_Y_Position
 clc
 adc #8
 jsr ImportY
 ldy #5
HostRecord:
 lda $c070,y
 sta ObjectRecord+1,y
 dey
 bpl HostRecord
 lda Player_X_Position
 sta CacheX
 lda Player_PageLoc
 sta CachePage
 lda Player_Y_Position
 sta CacheY
 lda Player_Y_HighPos
 sta CacheYHigh
 lda #1
 sta Mode
 sta Ready
 rts
ImportX:
 lda Player_X_Position
 sta $c071
 lda Player_PageLoc
 sta $c072
 lda #0
 sta $c070
 rts
ImportY:
 sta $c074
 lda Player_Y_HighPos
 sec
 sbc #1
 sta $c075
 lda #0
 sta $c073
 rts
SonicHostPowerup:
 pha
 lda #0
 sta HaveEpoch
 pla
 sta SafecallA_SMC+1
 lda #<GuestPowerupUpdate
 sta FarcallJmpTarget_SMC+1
 lda #>GuestPowerupUpdate
 sta FarcallJmpTarget_SMC+2
 lda #GuestPowerupBank
 jmp FarCallCommon
'''


def build(bundle,*,packet=None):
    if packet is None:packet=Payload.build()
    frame=packet['frame'];fields={n:CONTEXT+i for i,n in enumerate(FIELDS)}
    address=lambda n:int(bundle['syms'][n]['val'],0)
    definitions={n:address(n)for n in HOST}
    definitions.update(fields,Mode=frame['selector']['shape']['context']['Mode'],
        FrameStatus=Payload.Frame.STATUS,CtorTileX=Payload.Frame.TILE_X,CtorTileY=Payload.Frame.TILE_Y,
        NativeFrame=frame['symbols']['SonicNativeOrdinaryFrame'],
        OriginalConstructor=frame['symbols']['SonicOriginalObjectConstructor'],ObjectRecord=Payload.Frame.RECORD)
    segment=bundle['segs'][bundle['syms']['GuestPowerupUpdate']['seg']]
    definitions['GuestPowerupBank']=((int(segment['ooffs'],0)-16)//8192)|128
    text='\n'.join(f'{n}=${v:04x}'for n,v in definitions.items())+'\n.setcpu "6502"\n.segment "SERVICES"\nSonicServices:\n'
    assert len(ROWS)==38
    text+='\n'.join(' jmp SonicHost'+name for name in ROWS)+'\n'+SOURCE
    start=packet['proposed_service_base'];program=assemble(text,{'SERVICES':(start,0xbfe0-start)})
    image=program['images']['SERVICES'];end=start+len(image)
    # Host ZP references are named native ABI globals, never temporary bytes.
    assert not any(i['mode']in('inx','iny','ind')for i in program['instructions'])
    assert not set(range(CONTEXT,CONTEXT+len(FIELDS)))&set(range(0xc000,0xc119))
    return dict(packet=packet,image=image,code_half_open=[start,end],symbols=program['symbols'],
        instructions=program['instructions'],fields=fields,context_half_open=[CONTEXT,CONTEXT+len(FIELDS)],
        remaining_before_header=0xbfe0-end,source=text,image_SHA256=sha256(image).hexdigest(),
        explicit_unimplemented_rows=[i for i,n in enumerate(ROWS)if n=='No'],
        native_lifetime_or_public_dispatch_granted=False)


def packet_with_services(program):
    """New typed payload; the separately frozen eighth packet stays exact."""
    old=program['packet'];kernel=bytearray(old['kernel']);metadata=bytearray(old['metadata'])
    lo,hi=program['code_half_open'];kernel[lo-0xa000:hi-0xa000]=program['image']
    metadata[:8]=b'SMSONIC3';metadata[8:10]=struct.pack('<H',hi-0xa000)
    metadata[46:62]=struct.pack('<8H',program['symbols']['SonicServices'],program['symbols']['SonicHostMain'],
        program['symbols']['SonicHostFresh'],program['symbols']['SonicHostPowerup'],
        *program['context_half_open'],program['symbols']['SonicHostConstruct'],38)
    cookie=bytes((0xa7,43,1))+sha256(kernel+metadata).digest()[:13]
    return dict(old,kernel=bytes(kernel),metadata=bytes(metadata),cookie=cookie,
        source_payload_bytes=hi-0xa000,remaining_before_header=0xbfe0-hi,host_services=program,
        scope='New native service/epoch/pixel projection source component; private in-memory cold proof only. No public gate, worldedge/effects/rendering/damage/death closure or RAM lease.')
