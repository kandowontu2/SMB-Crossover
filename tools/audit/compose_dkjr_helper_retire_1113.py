"""Source-bound DK retirement page; private CPU qualification only."""
from hashlib import sha256
from functools import lru_cache
import json
import re

import compose_dkjr_head_bridge_1113 as T

B=T.Base
LAYOUT=B.R/'tools/reference/dkjr_retire_layout_1113.s'
FUNDING=B.R/'tools/reference/dkjr_helper_retire_funding_1113.s'
GRANT=B.R/'docs/qa/allocations/dkjr-retire-page-1113.json'
KARNOV_CURRENT='526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2'
PRINCE_CURRENT='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
FIXTURE='2172ef3c3713c13bc8f5152771b88b105dfc3b0eadc3eda365e479b76c8b9e20'


@lru_cache(maxsize=3)
def proof_parent(raw):
    """Explicit frozen62 normalization; older/future inputs are not inferred."""
    digest=sha256(raw).hexdigest()
    if digest==PRINCE_CURRENT:
        import compose_prince_entrance_current_1113 as Prince
        assert Prince.PIN==PRINCE_CURRENT and Prince.PARENT==KARNOV_CURRENT
        karnov=Prince.reverse(raw)
        assert sha256(karnov).hexdigest()==KARNOV_CURRENT
        parent,_=proof_parent(karnov)
        return parent,dict(input_SHA256=digest,proof_parent_SHA256=B.STEVE_SUCCESSOR,
            inverse=['compose_prince_entrance_current_1113.reverse',
                'compose_karnov_ladder_native_1113.inverse_current'],
            intermediate_SHA256=KARNOV_CURRENT,ROM_written=False)
    if digest==KARNOV_CURRENT:
        from compose_karnov_ladder_native_1113 import inverse_current
        parent=inverse_current(raw)
        assert sha256(parent).hexdigest()==B.STEVE_SUCCESSOR
        return parent,dict(input_SHA256=digest,proof_parent_SHA256=B.STEVE_SUCCESSOR,
            inverse='compose_karnov_ladder_native_1113.inverse_current',ROM_written=False)
    assert digest==B.STEVE_SUCCESSOR,digest
    return raw,dict(input_SHA256=digest,proof_parent_SHA256=digest,inverse=None,ROM_written=False)


def frozen_labels():
    data=T.retained(B.R/'build/dkjr-native-source-1102-v2/native-entrance-v89.lbl',
        'dkjr-entrance-ready-v100','0d3926e7791164c76f3727a35b748ebddf5357d58b28891473fbd05dcb1998be')
    return {name:int(value,16)for value,name in re.findall(r'^al ([0-9a-fA-F]+) \.(\w+)$',data.decode().replace('\r\n','\n'),re.M)}


def expand_branches(source):
    opposite=dict(jeq='bne',jne='beq',jcs='bcc',jcc='bcs',jmi='bpl',jpl='bmi',jvs='bvc',jvc='bvs')
    lines=source.splitlines();anonymous=[i for i,line in enumerate(lines)if line.strip()==':'];out=[]
    for i,line in enumerate(lines):
        if line.strip()==':':out.append(f'DkAnon{i}:');continue
        for token in(':+',':-'):
            if token in line:
                point=next(j for j in(anonymous if token==':+'else reversed(anonymous))if(j>i if token==':+'else j<i))
                line=line.replace(token,f'DkAnon{point}')
        match=re.fullmatch(r'\s*(j\w+)\s+(\w+)\s*',line)
        if match and match[1]in opposite:
            out.extend((f'{opposite[match[1]]} DkLong{i}',f'jmp {match[2]}',f'DkLong{i}:'))
        else:out.append(line)
    return '\n'.join(out)+'\n'


def body_parts(parent,alias):
    import prepare_dkjr_oam_slot_1109_v1 as Oam
    text,*_=T.old_source();labels=frozen_labels()
    carrier=T.payload(parent);draw=labels['DkNativeDraw']-0xa000
    assert carrier[draw]==0x20
    start=int.from_bytes(carrier[draw+1:draw+3],'little');end=labels['DkConstruct']
    assert Oam.SOURCES.resolve()==T.FROZEN.resolve()
    assert sha256(Oam.SOURCES.read_bytes()).hexdigest()==T.FROZEN_SHA
    _,repaired,rotate=Oam.source()
    body=repaired[repaired.index('DkjrNativeDrawBody:'):repaired.index('DkjrNativeBodyEnd:')]
    numeric=re.findall(r'^(\w+)\s*=\s*(\$[0-9a-fA-F]+|[0-9]+)\s*$',text,re.M)
    definitions=''.join(f'{name}={value}\n'for name,value in numeric)
    rotate=rotate.replace('@ready','DkRotateReady').replace('@bad','DkRotateBad')
    rotation=T.assemble(definitions+'.segment "ROTATE"\n'+rotate,dict(ROTATE=(0xa000,64)))['images']['ROTATE']
    assert carrier[:8160].count(rotation)==1
    rotate_at=0xa000+carrier[:8160].index(rotation)
    definitions+=f'DkRotateOAMY=${rotate_at:x}\n'
    old=T.assemble(definitions+'.segment "BODY"\n'+expand_branches(body),dict(BODY=(start,end-start)))
    used=old['used']['BODY'];old_box=T.girder_images()[0]['images']['BOX']
    assert start+used==T.GIRDER_LAYOUT['BOX'][0] and len(old_box)==8
    expected=old['images']['BODY']+old_box+b'\xea'
    assert T.payload(parent)[start-0xa000:end-0xa000]==expected,(hex(start),hex(end),
        [(hex(start+i),a,z)for i,(a,z)in enumerate(zip(T.payload(parent)[start-0xa000:end-0xa000],expected))if a!=z][:20])
    changed=once(body,''' lda $c210,x
 sta Sprite_Data,y
 lda $c211,x
 ora #1
 sta Sprite_Data+1,y''',''' lda $c210,x
 sta Sprite_Data,y
 lda $c211,x
 jsr DkDuplicateTileAlias
 sta Sprite_Data+1,y''')
    new=T.assemble(definitions+f'DkDuplicateTileAlias=${alias:x}\n.segment "BODY"\n'+expand_branches(changed),
        dict(BODY=(start,end-start)))
    assert new['used']['BODY']==old['used']['BODY']+1<=end-start
    assert start+new['used']['BODY']+len(old_box)==end
    return dict(start=start,end=end,old=old,new=new,box_address=start+new['used']['BODY'],
        old_box=old_box,source_validation_odd_bit_preserved=True)


def once(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after)


def effect_parts(parent):
    """Reproduce every current private effect tile writer, including D180."""
    import prepare_dkjr_oam_slot_1109_v1 as Oam
    text,*_=T.old_source();labels=frozen_labels();_,repaired,rotate=Oam.source()
    start,end=labels['DkNativeDraw'],labels['DkNativeEffectsEnd']
    block=repaired[repaired.index('DkNativeDraw:'):repaired.index('DkNativeEffectsEnd:')]
    block=once(block,' tya\n adc #$58',' jsr $d180')
    definitions=''.join(f'{name}={value}\n'for name,value in re.findall(
        r'^(\w+)\s*=\s*(\$[0-9a-fA-F]+|[0-9]+)\s*$',text,re.M))
    definitions+=f'DkjrNativeDrawBody=${labels["DkjrNativeDrawBody"]:x}\n'
    rotate=rotate.replace('@ready','DkRotateReady').replace('@bad','DkRotateBad')
    linked=T.assemble(definitions+'.segment "EFFECTS"\n'+expand_branches(block)+rotate,
        dict(EFFECTS=(start,end-start)))
    assert linked['used']['EFFECTS']==end-start==411
    assert T.payload(parent)[start-0xa000:end-0xa000]==linked['images']['EFFECTS']
    selector_source=(B.R/'tools/reference/dkjr_hanging_fruit_alias_1110.s').read_text()
    selector_source='\n'.join(line for line in selector_source.splitlines()if not line.startswith('.assert'))
    selector=T.assemble(selector_source,
        dict(CODE=(0xd180,11)))
    assert T.payload(parent)[T.offset(0xd180):T.offset(0xd18b)]==selector['images']['CODE']
    # All private Sprite_Data+1,Y stores are in the current body and this
    # exact effect emitter. No third particle/pickup/death renderer exists.
    assert T.payload(parent)[:8160].count(bytes.fromhex('990102'))==2
    return dict(linked=linked,start=start,end=end,selector=selector,source=block)


def score_source():
    source=T.SOURCE.read_text()
    source=once(source,'''    ldx #7
AwardSaveScratch:
    lda R0,x
    sta $c460,x
    dex
    bpl AwardSaveScratch
    lda ObjectOffset
    sta $c489
    ldx #32
AwardSaveSMC:
    lda $015a,x
    sta $c468,x
    dex
    bpl AwardSaveSMC''','''    lda ObjectOffset
    pha
    ldx #40
AwardSaveCombined:
    cpx #8
    bcc AwardSaveLow
    lda $0152,x
    bcs AwardSaveByte
AwardSaveLow:
    lda R0,x
AwardSaveByte:
    sta $c460,x
    dex
    bpl AwardSaveCombined''')
    source=once(source,'''    lda ScoreAmount
    and #$0f
    sta DigitModifier+4
    lda ScoreAmount''','''    lda ScoreAmount
    pha
    and #$0f
    sta DigitModifier+4
    pla''')
    start=source.index('    ldx #0\nAwardRestoreSMC:')
    end=source.index('AwardReturn:',start)
    source=source[:start]+'''    ldx #40
AwardRestoreCombined:
    lda $c460,x
    cpx #8
    bcc AwardRestoreLow
    sta $0152,x
    bcs AwardRestoreNext
AwardRestoreLow:
    sta R0,x
AwardRestoreNext:
    dex
    bpl AwardRestoreCombined
    pla
    sta ObjectOffset
'''+source[end:]
    source=once(source,'''OriginalFall:
    lda #4
    sta $c06b
    rts
''','OriginalFall=$a31f\n')
    return source


def cold_parts(parent):
    source=(B.R/'tools/reference/dkjr_cold_compact_1110_v2.s').read_text()
    old=T.assemble(source,dict(DK_COLD=(0xd25e,119)))
    assert old['used']['DK_COLD']==102
    assert T.payload(parent)[T.offset(0xd25e):T.offset(0xd2c4)]==old['images']['DK_COLD']
    changed=once(source,'''    cmp #8
    bne DkCopyRow
    rts''','''    cmp #9
    beq DkColdDone
    cmp #8
    bne DkCopyRow
    lda #$c9
    sta R1
    bne DkCopyRow
DkColdDone:
    lda #8
    cmp #8
    rts''')
    changed=once(changed,'.byte $31,$41,$4f,$58,$63,$71,$72,$73',
        '.byte $31,$41,$4f,$58,$63,$71,$72,$73,$bf')
    new=T.assemble(changed,dict(DK_COLD=(0xd25e,119)))
    assert new['used']['DK_COLD']==117
    return dict(old=old,new=new,destination=[0xc900,0xcd00],lease_granted=False)


def parts(parent):
    # No candidate or storage lease is created by this function.
    _,_,head=T.linked(parent);constants=head['symbols']
    names=('R0','ObjectOffset','DigitModifier','ScoreAmount','NativeHeadBank','NativeHeadEffect',
        'NativeAddScore','ScreenLeftX','ScreenLeftPage','HeadX','HeadPage','HeadTop','R2','R6','R7',
        'SafecallA','FarTarget','FarCall','RectPredicate','MTileAttribute','BlockBounceTimer',
        'GuestHurtTicks','TimerControl')
    predicate=T.assemble(FUNDING.read_text(),dict(PREDICATE=(0xaeef,62)))
    definitions=''.join(f'{name}=${constants[name]:x}\n'for name in names)
    definitions+=f'HeadReturn=${predicate["symbols"]["PredicateFalseRTS"]:x}\n'
    compact=T.assemble(definitions+score_source(),T.LAYOUT)
    assert compact['used']['SCORE']==103
    row=predicate['symbols']['DkCompactPredicateEnd']
    alias=compact['symbols']['DkScoreBridgeEnd']
    layout=dict(ALIAS=(alias,22),
        SERVICE_HEAD=(0xcbe0,64),SERVICE_TAIL=(0xcc60,32))
    extras=T.assemble(LAYOUT.read_text(),layout)
    assert extras['used']==dict(ALIAS=22,SERVICE_HEAD=55,SERVICE_TAIL=26)
    assert row+14<=0xaeef+62 and alias+22<T.SCORE_END
    # Keep the original clock entry and all its callers byte-exact.
    body=T.payload(parent)
    assert body[0xf2d:0xf2f]==bytes.fromhex('a203')
    assert body[0x31f:0x325]==bytes.fromhex('a9048d6bc060')
    return dict(head=compact,predicate=predicate,extras=extras,body=body_parts(parent,alias),cold=cold_parts(parent),row_address=row,
        alias_address=alias,allocated=False,ROM_written=False)


def girder_parts(parts,*,retirement=False):
    source=T.GIRDER.read_text()
    for before,after in(('ActorCount = 13','ActorCount = 14'),
        ('WorldColumns: .byte 26,','WorldColumns: .byte 21,26,'),
        ('    cpy #8\n    beq Horizontal','    cpy #9\n    beq Horizontal'),
        ('OscillatorY: .byte 128,','OscillatorY: .byte 128,128,')):
        source=once(source,before,after)
    if retirement:
        source='DkPrivateRetireOrBBox=$cbe0\n'+once(source,'    jsr DkNativeBBox','    jsr DkPrivateRetireOrBBox')
    layout=dict(T.GIRDER_LAYOUT,BOX=(parts['body']['box_address'],8),ROWS=(parts['row_address'],14))
    linked=T.assemble(source,layout)
    assert linked['used']['BOX']==8 and linked['used']['ROWS']==14
    assert linked['symbols']['DkAfterNativeConstructor']==0xd1f0
    return linked,layout


def alias_probe(parent,*,poison=True):
    """Owned-art/pose probe only: no C900 copy, code placement or retirement."""
    baseline,_=T.transform(parent,helper=True);p=parts(parent);body=bytearray(T.payload(baseline))
    def put(pc,image):
        at=T.offset(pc);body[at:at+len(image)]=image
    for name,(pc,size)in T.LAYOUT.items():put(pc,p['head']['images'][name].ljust(size,b'\xea'))
    put(0xaeef,p['predicate']['images']['PREDICATE'].ljust(62,b'\xea'))
    put(p['alias_address'],p['extras']['images']['ALIAS'])
    put(p['body']['start'],p['body']['new']['images']['BODY'])
    girder,layout=girder_parts(p)
    for name in('BOX','ROWS','PIPE','REFRESH'):put(layout[name][0],girder['images'][name])
    original=T.payload(parent)
    for a,z in((47,9),(49,41),(55,9)):
        at=8*1024+(a-1)*16;other=8*1024+(z-1)*16
        assert original[at:at+32]==original[other:other+32]
        if poison:body[at:at+32]=bytes([255])*32
    cookie=B.COOKIE[:3]+sha256(body).digest()[:13];image=bytearray(parent)
    for i,page in enumerate(B.PAGES):
        at=B.CHR+page*1024;image[at:at+1024]=body[i*1024:(i+1)*1024]
    image[B.COOKIE_AT:B.COOKIE_AT+16]=cookie
    changed=[i for i,(a,z)in enumerate(zip(parent,image))if a!=z]
    allowed={B.COOKIE_AT+i for i in range(16)}
    for page in B.PAGES:allowed.update(range(B.CHR+page*1024,B.CHR+(page+1)*1024))
    assert set(changed)<=allowed and len(image)==len(parent)
    return bytes(image),dict(status='PRIVATE_ART_ALIAS_PROBE_NOT_RETIREMENT',
        parent_SHA256=sha256(parent).hexdigest(),candidate_SHA256=sha256(image).hexdigest(),
        cookie=cookie.hex(),changed_bytes=len(changed),poisoned_duplicate_bytes=96 if poison else 0,
        conditional_C900_touched=False,new_RAM_lease=False,ROM_written=False)


def retirement_fixture(parent):
    """Frozen pre-grant byte fixture; use proposal_current for granted use."""
    alias,alias_info=alias_probe(parent);p=parts(parent);body=bytearray(T.payload(alias))
    def put(pc,image):
        at=T.offset(pc);body[at:at+len(image)]=image
    girder,layout=girder_parts(p,retirement=True)
    put(layout['REFRESH'][0],girder['images']['REFRESH'])
    put(0xd25e,p['cold']['new']['images']['DK_COLD'].ljust(119,b'\xff'))
    for name,offset,size in(('SERVICE_HEAD',736,64),('SERVICE_TAIL',864,32)):
        at=8*1024+offset;body[at:at+size]=p['extras']['images'][name].ljust(size,b'\xff')
    cookie=B.COOKIE[:3]+sha256(body).digest()[:13];image=bytearray(parent)
    for i,page in enumerate(B.PAGES):
        at=B.CHR+page*1024;image[at:at+1024]=body[i*1024:(i+1)*1024]
    image[B.COOKIE_AT:B.COOKIE_AT+16]=cookie
    return bytes(image),dict(status='UNALLOCATED_C900_CPU_FIXTURE_NOT_NATIVE_READY',
        parent_SHA256=sha256(parent).hexdigest(),candidate_SHA256=sha256(image).hexdigest(),
        cookie=cookie.hex(),conditional_destination=[0xc900,0xcd00],destination_bytes=1024,
        lease_granted=False,ROM_written=False,alias_probe_SHA256=alias_info['candidate_SHA256'])


def controller(raw,*,full=False,ride_fourth=False,fourth_window=False,ledge_wait=False,stationary_wait=False,early_stairs=False,riser_retreat=False,landing_prep=False):
    """Same frozen controls; bind only the moved private BOX return label."""
    import replay_dkjr_first_pickup_1113 as Replay
    text=Replay.full_stage_controller(raw)if full else Replay.controller(raw)
    # Body gains one byte, shifting BOX's DkPipeCreated to BD42. Native
    # constructor D1F0 and all input policies remain unchanged.
    if full:
        for before,after in (("mapped(0xbd41,'nesWorkRam',3*8192+0x1d41)",
            "mapped(0xbd42,'nesWorkRam',3*8192+0x1d42)"),
            ('end),emu.callbackType.exec,0xbd41)','end),emu.callbackType.exec,0xbd42)')):
            text=once(text,before,after)
    else:
        assert '0xbd41'not in text and '0x1d41'not in text
    if ride_fourth:
        assert full
        text=once(text," if phase=='roof'and index==4 then",
            " if phase=='roof'and index==4 and carried(d,down)then setPhase('lower',down)end\n if phase=='roof'and index==4 then")
    if fourth_window:
        assert full and not ride_fourth
        text=once(text,'down>=101 and down<=114 and down>priorTop[d]',
            'down>=115 and down<=128 and down>priorTop[d]')
    if ledge_wait:
        assert full and fourth_window
        text=once(text,"  right=player<takeoffX\n  if right and grounded",'''  right=player<takeoffX
  if player>=1168 and player<1182 and not ledgeGoomba then
   for _,actor in ipairs(approachActors())do
    if actor[2]==6 and actor[3]>player+30 and actor[4]<176 then
     ledgeGoomba={slot=actor[1],started=updates}
     right=false;setPhase('wait-ledge-goomba');break
    end
   end
  end
  if right and grounded''')
    if stationary_wait:
        assert ledge_wait
        text=once(text," if phase=='wait-ledge-goomba'then\n  local slot=ledgeGoomba.slot",''' if phase=='wait-ledge-goomba'then
  if grounded and y==176 and updates>=rearm then
   for _,actor in ipairs(approachActors())do
    local dx=actor[3]-player
    if (actor[2]==2 or actor[2]==6)and actor[5]&32==0 and actor[4]>=172 and dx>=18 and dx<=24 then
     hold=updates+8;rearm=updates+47;remember('stationary-Goomba-hop');break
    end
   end
  end
  local slot=ledgeGoomba.slot''')
        text=once(text,'updates-ledgeGoomba.started<110','updates-ledgeGoomba.started<160')
    if early_stairs:
        assert full and stationary_wait
        text=once(text,'local lateSteps={{2127,176,true},{2142,160,true},',
            'local lateSteps={{2118,176,true},{2134,160,true},')
        text=once(text,'{2351,176,true},{2366,160,true},',
            '{2342,176,true},{2358,160,true},')
    if riser_retreat:
        assert early_stairs
        text=once(text,'local lateStep=1','local lateStep=1\nlocal dkRiserPrep')
        text=once(text," if phase=='late-walk'then\n  right=true",''' if phase=='late-walk'then
  if dkRiserPrep then
   local elapsed=updates-dkRiserPrep.start
   if riserTrace then
    riserTrace.min_y=math.min(riserTrace.min_y,y)
    riserTrace.max_x=math.max(riserTrace.max_x,player)
    riserTrace.airborne=riserTrace.airborne or not grounded
   end
   if elapsed<12 then bits=2
   elseif elapsed<16 then bits=0
   elseif elapsed<24 then bits=129
   elseif elapsed<56 then bits=1
   else dkRiserPrep=nil end
   if dkRiserPrep then return end
  end
  right=true''')
        text=once(text,'  if ready and step[3] then\n   assert(riserAttempts', '''  if ready and step[3] and player>takeoff+6 then
   dkRiserPrep={start=updates}
   riserStart,riserAttempts=updates+16,riserAttempts+1
   remember('late-retreat-jump-'..lateStep)
   riserTrace=events[#events];riserTrace.min_y=y;riserTrace.max_x=player
   bits=2;return
  end
  if ready and step[3] then
   assert(riserAttempts''')
    if landing_prep:
        assert riser_retreat
        text=once(text,'   if elapsed<12 then bits=2',
            '   if elapsed>=24 and grounded and y==dkRiserPrep.target then dkRiserPrep=nil\n   elseif elapsed<12 then bits=2')
        text=once(text,'   dkRiserPrep={start=updates}',
            "   assert(riserAttempts<4,'Repeated late riser preparation '..lateStep)\n   dkRiserPrep={start=updates,target=step[2]-16}")
    return text


def proposal_current(raw):
    """Granted page, exact known62/526/7ef byte-disjoint composition."""
    parent,input_info=proof_parent(raw);grant=json.loads(GRANT.read_text())
    assert grant['reviewed_parent_ROM_SHA256']==B.STEVE_SUCCESSOR
    assert grant['reviewed_in_memory_fixture_SHA256']==FIXTURE
    assert grant['conditional_RAM']['bank']==2 and grant['conditional_RAM']['bytes']==1024
    frozen,info=retirement_fixture(parent);assert sha256(frozen).hexdigest()==FIXTURE
    image=bytearray(raw)
    for page in B.PAGES:
        at=B.CHR+page*1024
        assert raw[at:at+1024]==parent[at:at+1024],('Current overlap',page)
        image[at:at+1024]=frozen[at:at+1024]
    assert raw[B.COOKIE_AT:B.COOKIE_AT+16]==B.COOKIE
    image[B.COOKIE_AT:B.COOKIE_AT+16]=frozen[B.COOKIE_AT:B.COOKIE_AT+16]
    delta=[(i,a,z)for i,(a,z)in enumerate(zip(parent,frozen))if a!=z]
    actual=[(i,a,z)for i,(a,z)in enumerate(zip(raw,image))if a!=z]
    assert actual==delta
    return bytes(image),dict(info,status='GRANTED_PRIVATE_CPU_QUALIFICATION_NATIVE_PENDING',
        parent_SHA256=sha256(raw).hexdigest(),candidate_SHA256=sha256(image).hexdigest(),
        frozen62_fixture_SHA256=FIXTURE,input=input_info,grant=GRANT.relative_to(B.R).as_posix(),
        grant_SHA256=sha256(GRANT.read_bytes()).hexdigest(),identical_owned_byte_edits=len(delta),
        lease_granted=True,all_unrelated_bytes_retained=True,ROM_written=False)


def inverse_current(image):
    """Restore exact owned originals, then require a known-parent roundtrip."""
    body=bytearray(T.payload(image))
    assert image[B.COOKIE_AT:B.COOKIE_AT+16]==B.COOKIE[:3]+sha256(body).digest()[:13]
    source,rect,score,definitions=T.old_source()
    def put(pc,data):
        at=T.offset(pc);body[at:at+len(data)]=data
    put(T.RECT_START,T.assemble(f'D_ebe3=${T.RECT_END:x}\n.segment "OLD"\n'+rect,
        dict(OLD=T.LAYOUT['RECT']))['images']['OLD'])
    put(T.SCORE_START,T.assemble(definitions+'DkjrNativeAddScore=$bb37\n.segment "OLD"\n'+score,
        dict(OLD=T.LAYOUT['SCORE']))['images']['OLD'])
    put(T.HOOK,bytes.fromhex('a9048d6bc060'))
    start=source.index('D_ebe3:');end=source.index('D_f1af:',start)
    put(0xaeef,T.assemble('.segment "OLD"\n'+source[start:end],dict(OLD=(0xaeef,62)))['images']['OLD'])
    # Reconstruct the delivered rotated body from its exact source, with the
    # unchanged rotation helper resolved from the byte-exact effect renderer.
    import prepare_dkjr_oam_slot_1109_v1 as Oam
    _,repaired,_=Oam.source();effect=effect_parts(image)
    old_body=repaired[repaired.index('DkjrNativeDrawBody:'):repaired.index('DkjrNativeBodyEnd:')]
    defs=''.join(f'{n}={v}\n'for n,v in re.findall(r'^(\w+)\s*=\s*(\$[0-9a-fA-F]+|[0-9]+)\s*$',source,re.M))
    defs+=f'DkRotateOAMY=${effect["linked"]["symbols"]["DkRotateOAMY"]:x}\n'
    old=T.assemble(defs+'.segment "BODY"\n'+expand_branches(old_body),dict(BODY=(0xbc74,209)))
    assert old['used']['BODY']==200
    girders,_=T.girder_images()
    put(0xbc74,old['images']['BODY']+girders['images']['BOX']+b'\xea')
    for name in('PIPE','REFRESH'):
        pc,size=T.GIRDER_LAYOUT[name];put(pc,girders['images'][name].ljust(size,b'\xff'))
    cold=T.assemble((B.R/'tools/reference/dkjr_cold_compact_1110_v2.s').read_text(),dict(DK_COLD=(0xd25e,119)))
    put(0xd25e,cold['images']['DK_COLD']+T.OLD_ROWS)
    for old_tile,kept_tile in((47,9),(49,41),(55,9)):
        at=8192+(old_tile-1)*16;other=8192+(kept_tile-1)*16;body[at:at+32]=body[other:other+32]
    assert sha256(body).hexdigest()=='30b1118ac41a70e81c2eda030f5d93a5f56b57feb8600415f860e6007dfffc83'
    parent=bytearray(image)
    for i,page in enumerate(B.PAGES):
        at=B.CHR+page*1024;parent[at:at+1024]=body[i*1024:(i+1)*1024]
    parent[B.COOKIE_AT:B.COOKIE_AT+16]=B.COOKIE;parent=bytes(parent)
    proof_parent(parent);assert proposal_current(parent)[0]==image
    return parent


def main():
    raw,input_info=proof_parent(B.C.ROM.read_bytes());p=parts(raw)
    print('DKJR_RETIRE_INPUT '+json.dumps(input_info,separators=(',',':')),flush=True)
    print('DKJR_RETIRE_DRAFT_FIT '+json.dumps(dict(parent_SHA256=sha256(raw).hexdigest(),
        head=p['head']['used'],predicate=p['predicate']['used'],extras=p['extras']['used'],
        body_live_before=p['body']['old']['used'],body_live_after=p['body']['new']['used'],
        moved_box=hex(p['body']['box_address']),cold=p['cold']['new']['used'],
        row_address=hex(p['row_address']),alias_address=hex(p['alias_address']),
        entire_conditional_destination=[0xc900,0xcd00],destination_lease_granted=False,
        composition_created=False,output_files=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
