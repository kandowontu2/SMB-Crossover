"""Native world/effect derivative in the explicit Sonic metadata grant.

Unpublished source proposal. Frozen motor, readers, contacts and prior files
stay intact. No cartridge/native admission/RAM lease is created by capacity.
"""
import struct
from hashlib import sha256
import sonic_sms_native_host_services_1110 as Host
from sonic_sms_compact_cold_worker_1110 import assemble

START,LIMIT=0xd040,0xd25e
CONTEXT=0xc122
FIELDS=('HeadPending','HeadTile','HeadRow','HeadPhase','HeadColumn','HeadPage','DrawIndex','DrawFlip','DrawAttr')

SOURCE='''
.setcpu "6502"
.segment "EFFECTS"
MetaHorizontal:
 lda #0
 sta SAxis
 lda $c075
 bne MetaEmpty
 lda $c042
 lsr
 clc
 adc $c074
 bcs MetaEmpty
 cmp #32
 bcc MetaEmpty
 cmp #240
 bcs MetaEmpty
 jmp SweptH
MetaEmpty:
 lda #0
 sta SKind
 sta SStatus
 sta SEdge
 lda #$80
 sta SDX
 jmp PublishShape
MetaVertical:
 lda #1
 sta SAxis
 lda $c074
 sta PScreenYLo
 lda $c075
 sta PScreenYHi
 lda $c061
 bmi MetaVerticalPoint
 clc
 lda PScreenYLo
 adc $c042
 sta PScreenYLo
 lda PScreenYHi
 adc #0
 sta PScreenYHi
MetaVerticalPoint:
 lda PScreenYHi
 bne MetaEmpty
 lda PScreenYLo
 cmp #32
 bcc MetaEmpty
 cmp #240
 bcs MetaEmpty
 jsr SweptV
 bcc MetaReturn
 lda SKind
 cmp #4
 bne MetaSuccess
 lda #1
 sta HeadPending
 lda PTile
 sta HeadTile
 lda PCellYLo
 sec
 sbc #32
 sta HeadRow
 lda WNewLeadingLo
 and #15
 cmp #4
 bcs MetaHeadPhase
 lda #4
MetaHeadPhase:
 sta HeadPhase
 lda PCellXLo
 lsr
 lsr
 lsr
 lsr
 sta HeadColumn
 lda PBufferPage
 sta HeadPage
MetaSuccess:
 lda #0
 sec
MetaReturn:
 rts
MetaClassify:
 lda PTile
 cmp #$24
 beq MetaFlag
 cmp #$25
 beq MetaFlag
 lda PAttributes
 and #2
 rts
MetaFlag:
 lda #0
 sta PAttributes
 rts
MetaBounds:
 lda Player_Rel_XPos
 sta BoundingBox_UL_Corner
 clc
 adc #23
 sta BoundingBox_UL_Corner+2
 lda $c074
 sta BoundingBox_UL_Corner+1
 clc
 adc $c042
 sec
 sbc #1
 sta BoundingBox_UL_Corner+3
 ldx #0
 ldy #0
 sec
 rts
MetaAdder:
 ldy #0
 sec
 rts
MetaBody:
 lda #0
 sta GuestBodyNoStomp
 clc
 rts
MetaHead:
 lda HeadPending
 beq MetaNativeHead
 lda #0
 sta HeadPending
 lda HeadRow
 sta R2
 lda HeadPhase
 sta R4
 lda HeadColumn
 sta R6
 lda HeadPage
 beq MetaHeadFirst
 lda R6
 clc
 adc #$d0
 sta R6
MetaHeadFirst:
 lda #3
 sta R7
 lda HeadTile
 sta R3
 ldx #0
 lda R3
 rts
MetaNativeHead:
 jsr BlockBufferColli_Head
 jmp MetaCoinsOnly
MetaSide:
 jsr BlockBufferColli_Side
 cmp #$24
 beq MetaEffectReturn
 cmp #$25
 beq MetaEffectReturn
 cmp #$6c
 beq MetaEffectReturn
 cmp #$1f
 beq MetaEffectReturn
MetaCoinsOnly:
 cmp #$23
 beq MetaEffectReturn
 cmp #$c2
 beq MetaEffectReturn
 cmp #$c3
 beq MetaEffectReturn
 lda #0
MetaEffectReturn:
 ora #0
 rts
MetaFeet:
 jsr BlockBufferColli_Feet
 bit $c030
 bmi MetaEffectReturn
 jmp MetaCoinsOnly
MetaGraphics:
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda #0
 sta ObjectMetasprite
 lda #$85
 sta X5ChrMode
 lda #16
 sta CurrentCHRBank
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
 sec
 rts
MetaDraw:
 lda Player_Y_HighPos
 cmp #1
 bne MetaDrawDone
 lda Player_Rel_YPos
 cmp #32
 bcc MetaDrawDone
 cmp #224
 bcs MetaDrawDone
 lda CurrentOAMOffset
 cmp #237
 bcs MetaDrawDone
 lda PlayerFacingDir
 lsr
 lsr
 lda #0
 rol
 sta DrawFlip
 lsr
 ror
 ror
 ora Player_SprAttrib
 sta DrawAttr
 lda #0
 sta DrawIndex
MetaDrawNext:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq MetaDrawAt
 txa
 clc
 adc RgOamRotation
 tax
MetaDrawAt:
 ldy DrawIndex
 lda DrawY,y
 clc
 adc Player_Rel_YPos
 sta Sprite_Y_Position,x
 tya
 eor DrawFlip
 tay
 lda DrawTiles,y
 sta Sprite_Tilenumber,x
 lda DrawAttr
 sta Sprite_Attributes,x
 ldy DrawIndex
 lda DrawX,y
 clc
 adc Player_Rel_XPos
 sta Sprite_X_Position,x
 lda CurrentOAMOffset
 clc
 adc #4
 sta CurrentOAMOffset
 inc DrawIndex
 lda DrawIndex
 cmp #4
 bne MetaDrawNext
MetaDrawDone:
 sec
 rts
DrawY: .byte 0,0,16,16
DrawX: .byte 4,12,4,12
DrawTiles: .byte 0,2,32,34
MetaDeath:
 sta SafecallA_SMC+1
 lda #<MegaManDeathUpdate
 sta FarcallJmpTarget_SMC+1
 lda #>MegaManDeathUpdate
 sta FarcallJmpTarget_SMC+2
 lda #DeathBank
 jmp FarCallCommon
'''


def once(source,old,new):
    assert source.count(old)==1,(old,source.count(old));return source.replace(old,new)


def build(bundle):
    prior=Host.build(bundle);packet=prior['packet'];frame=packet['frame'];selector=frame['selector'];shape=selector['shape']
    address=lambda n:int(bundle['syms'][n]['val'],0)
    definitions={n:address(n)for n in('Player_Y_HighPos','Player_Rel_XPos','BoundingBox_UL_Corner',
        'R2','R3','R4','R6','R7','BlockBufferColli_Head','BlockBufferColli_Side','BlockBufferColli_Feet',
        'ObjectMetasprite','X5ChrMode','CurrentCHRBank','X5WideChrActive','ReloadCHRBank',
        'Player_Rel_YPos','Player_Pos_ForScroll','CurrentOAMOffset','PlayerFacingDir','Player_SprAttrib','GuestOamRotationActive','RgOamRotation',
        'Sprite_Y_Position','Sprite_Tilenumber','Sprite_Attributes','Sprite_X_Position','GuestBodyNoStomp',
        'SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','MegaManDeathUpdate')}
    segment=bundle['segs'][bundle['syms']['MegaManDeathUpdate']['seg']]
    definitions['DeathBank']=((int(segment['ooffs'],0)-16)//8192)|128
    definitions.update({n:CONTEXT+i for i,n in enumerate(FIELDS)})
    definitions.update({'S'+n:a for n,a in shape['context'].items()})
    definitions.update({'P'+n:a for n,a in shape['point']['fields'].items()})
    definitions.update({'W'+n:a for n,a in selector['witness']['fields'].items()})
    definitions.update(SweptH=selector['symbols']['SonicSweptHorizontal'],SweptV=selector['symbols']['SonicSweptVertical'],
        PublishShape=shape['symbols']['PublishShape'])
    text='\n'.join(f'{n}=${v:04x}'for n,v in definitions.items())+'\n'+SOURCE
    meta=assemble(text,{'EFFECTS':(START,LIMIT-START)})
    # Derivative source leaves the551-byte predecessor frozen. Only native
    # admission-to-world and projection semantics change here, not the motor.
    src=prior['source']
    old=''' lda Player_Y_HighPos
 cmp #1
 bne HostUnavailable
 lda Player_Y_Position
 cmp #240
 bcc HostInPlane
HostUnavailable:'''
    src=once(src,old,' jmp HostInPlane\nHostUnavailable:')
    src=once(src,' bne HostReady\n jsr SonicHostConstruct',''' bne HostReady
 lda Player_Y_HighPos
 cmp #1
 bne HostUnavailable
 lda Player_Y_Position
 cmp #240
 bcs HostUnavailable
 jsr SonicHostConstruct''')
    src=once(src,' lda $c074\n sta Player_Y_Position\n sta CacheY\n lda $c075\n clc\n adc #1',''' clc
 lda $c074
 adc $c042
 sta OldInput
 lda $c075
 adc #0
 sta Player_Y_HighPos
 sec
 lda OldInput
 sbc #32
 sta Player_Y_Position
 sta CacheY
 lda Player_Y_HighPos
 sbc #0
 clc
 adc #1''')
    src=once(src,' lda $c061\n sta Player_Y_Speed',''' lda $c061
 sta Player_Y_Speed
 lda HeadPending
 beq HostHeadSpeedReady
 lda #$ff
 sta Player_Y_Speed
HostHeadSpeedReady:''')
    src=once(src,' adc #8\n jsr ImportY',''' adc #8
 sta $c074
 lda Player_Y_HighPos
 sec
 sbc #1
 sta $c075
 lda #0
 sta $c073''')
    src=once(src,'ImportY:\n sta $c074\n lda Player_Y_HighPos\n sec\n sbc #1\n sta $c075','''ImportY:
 clc
 adc #32
 sta $c074
 lda Player_Y_HighPos
 adc #0
 sta $c075
 sec
 lda $c074
 sbc $c042
 sta $c074
 lda $c075
 sbc #1
 sta $c075''')
    src=once(src,' sta Mode\n sta Ready',' sta Mode\n sta Ready\n lda #0\n sta PlayerSize')
    src=once(src,'HostStep:\n lda Player_X_Position','HostStep:\n lda #0\n sta HeadPending\n lda Player_X_Position')
    # Root must explicitly route the genuine native foot getter to reserved
    # row35 before this derivative can own native background effects.
    lines=src.splitlines();at=lines.index('SonicServices:')+1
    for row,target in{1:'MetaGraphics',2:'MetaDraw',3:'MetaGraphics',8:'MetaDeath',10:'MetaHead',11:'MetaBody',12:'MetaAdder',13:'MetaAdder',14:'MetaSide',16:'MetaBounds',35:'MetaFeet'}.items():
        assert lines[at+row].startswith(' jmp SonicHost');lines[at+row]=' jmp '+target
    src='\n'.join(f'{n}=${v:04x}'for n,v in{**meta['symbols'],**{n:definitions[n]for n in FIELDS},'PlayerSize':address('PlayerSize')}.items())+'\n'+'\n'.join(lines)+'\n'
    start=prior['code_half_open'][0];service=assemble(src,{'SERVICES':(start,0xbfe0-start)})
    image=service['images']['SERVICES'];end=start+len(image)
    newservice=dict(prior,image=image,source=src,symbols=service['symbols'],instructions=service['instructions'],
        code_half_open=[start,end],remaining_before_header=0xbfe0-end,image_SHA256=sha256(image).hexdigest())
    result=Host.packet_with_services(newservice);kernel=bytearray(result['kernel']);metadata=bytearray(result['metadata'])
    # No branch, source motor byte or original contact changes. The copied
    # ordinary frame calls only these two new world-policy terrain leaves.
    calls=[]
    for name in('SweptH','SweptV'):
        target=frame['symbols'][name];matches=[i for i in frame['instructions']if i['op']=='JSR'and i['operand']==target]
        assert len(matches)==1,(name,matches)
        pc=matches[0]['pc'];replacement=meta['symbols']['MetaHorizontal'if name=='SweptH'else'MetaVertical']
        assert kernel[pc-0xa000]==0x20;kernel[pc-0xa000+1:pc-0xa000+3]=struct.pack('<H',replacement);calls.append([pc,target,replacement])
    lo=selector['symbols']['Classify'];hi=selector['symbols']['ClassifyTile'];assert hi-lo==10
    old=kernel[lo-0xa000:hi-0xa000]
    assert old[:5]==b'\xad'+struct.pack('<H',shape['point']['fields']['Attributes'])+b'\x29\x02'
    kernel[lo-0xa000:hi-0xa000]=(b'\x20'+struct.pack('<H',meta['symbols']['MetaClassify'])+b'\xf0\x05\x4c'+struct.pack('<H',selector['symbols']['Unsupported'])+b'\xea\xea')
    assert metadata[:8]==b'SMSONIC3'and metadata[62:64]==b'\xff\xff'
    metadata[START-0xd000:START-0xd000+len(meta['images']['EFFECTS'])]=meta['images']['EFFECTS']
    assert metadata[0x25e:0x25e+139]==packet['metadata'][0x25e:0x25e+139]
    cookie=bytes((0xa7,43,1))+sha256(kernel+metadata).digest()[:13]
    result=dict(result,kernel=bytes(kernel),metadata=bytes(metadata),cookie=cookie)
    return dict(packet=result,service=newservice,metadata=meta,metadata_half_open=[START,START+len(meta['images']['EFFECTS'])],
        context={n:CONTEXT+i for i,n in enumerate(FIELDS)},frame_terrain_calls=calls,
        remaining_metadata_bytes=LIMIT-START-len(meta['images']['EFFECTS']),remaining_private_bytes=0xbfe0-end,
        scope='Unqualified native world/effect source derivative; requires actual head/feet/side/bounds/flag/pit/death/cold/ISR and root dispatch. No public/raw43 or runtime allocation.')
