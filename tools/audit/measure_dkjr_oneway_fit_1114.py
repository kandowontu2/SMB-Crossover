"""Measure source-owned one-way support guard fragments; no ROM composition.

The existing Selected40 retirement guard is retained. Omitting jump-age0
uses the separately checked legal query lifecycle, not standalone query ABI.
Fragment compilation is not a resource grant or gameplay test.
"""
from hashlib import sha256
import json
import re

import replay_dkjr_final_handoff_1114 as F
import prepare_dkjr_oam_slot_1109_v1 as Oam

G,T=F.Gate,F.T
A=G.H.T.assemble
P=G.P


def once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def fragments(raw,*,include_components=False):
    body=T.P.T.payload(raw);frozen,*_=G.H.T.old_source();labels=P.frozen_labels()
    at=labels['EmptyWindow']-0xa000
    assert body[at]==0x20
    labels['NativeObjects']=int.from_bytes(body[at+1:at+3],'little')
    native_prefix=body[labels['NativeObjects']-0xa000:labels['PlatformLoop']-0xa000]
    compares=[i for i in range(len(native_prefix)-2)if native_prefix[i]==0xd9]
    assert len(compares)==1,compares
    labels['VineMaximum']=int.from_bytes(native_prefix[compares[0]+1:compares[0]+3],'little')+1
    at=labels['ObjectsDone']-0xa000-3
    assert body[at]==0x4c
    labels['IntersectAppend']=int.from_bytes(body[at+1:at+3],'little')
    defs=''.join(f'{n}={v}\n'for n,v in re.findall(r'^(\w+)\s*=\s*(\$[0-9a-fA-F]+|[0-9]+)\s*$',frozen,re.M))
    defs+=''.join(f'{n}=${v:x}\n'for n,v in labels.items())
    result=[]
    def emit(role,offset,size,old,new):
        assert len(old)==size and body[offset:offset+size]==old,(role,hex(offset))
        assert len(new)==size
        result.append(dict(role=role,payload_offset=offset,bytes=size,
            preimage_hex=old.hex(),preimage_SHA256=sha256(old).hexdigest(),
            proposed_hex=new.hex(),proposed_SHA256=sha256(new).hexdigest()))
    # Existing constructor-retirement code, using only the two owned spans.
    retire=(T.P.B.R/'tools/reference/dkjr_retire_layout_1113.s').read_text()
    retire=retire[retire.index('.segment "SERVICE_HEAD"'):]
    oldr=A(retire,dict(SERVICE_HEAD=(0xcbe0,64),SERVICE_TAIL=(0xcc60,32)))
    newr=once(retire,'OriginalBBox:\n    jmp $b7ca\n','')
    newr=once(newr,'.segment "SERVICE_TAIL"\n','.segment "SERVICE_TAIL"\nOriginalBBox:\n    jmp $b7ca\n')
    newr=once(newr,'DkPrivateRetireHeadEnd:\n','''DkPrivateRetireHeadEnd:
DkOneWaySupport:
    lda $c06b
    cmp #3
    beq DkOneWayJump
    lsr
    rts
DkOneWayJump:
    jmp DkOneWayVelocityLow
''')
    newr='DkOneWayVelocityLow=$d69e\n'+newr
    nr=A(newr,dict(SERVICE_HEAD=(0xcbe0,64),SERVICE_TAIL=(0xcc60,32)))
    assert oldr['used']==dict(SERVICE_HEAD=55,SERVICE_TAIL=26)
    assert nr['used']==dict(SERVICE_HEAD=64,SERVICE_TAIL=29)
    guard=nr['symbols']['DkOneWaySupport']
    assert guard==0xcc14
    for name,offset,size in(('SERVICE_HEAD',8*1024+736,64),('SERVICE_TAIL',8*1024+864,32)):
        emit(name,offset,size,oldr['images'][name].ljust(size,b'\xff'),nr['images'][name].ljust(size,b'\xff'))
    # Reproduce current body including its source-qualified tile alias.
    _,repaired,rotate=Oam.source()
    bsrc=repaired[repaired.index('DkjrNativeDrawBody:'):repaired.index('DkjrNativeBodyEnd:')]
    bsrc=re.sub(r'^DkShortCandidate\d+:\n','',bsrc,flags=re.M)
    bsrc=once(bsrc,' ora #1\n sta Sprite_Data+1,y',' jsr DkDuplicateTileAlias\n sta Sprite_Data+1,y')
    start=labels['DkjrNativeDrawBody'];end=0xbd3d;current=body[start-0xa000:end-0xa000]
    needle=bytes.fromhex('bd11c220');hits=[i for i in range(len(current)-6)if current[i:i+4]==needle]
    assert len(hits)==1,hits
    alias=int.from_bytes(current[hits[0]+4:hits[0]+6],'little')
    rotate=rotate.replace('@ready','DkRotateReady').replace('@bad','DkRotateBad')
    rb=A(defs+'.segment "ROTATE"\n'+rotate,dict(ROTATE=(0xa000,64)))['images']['ROTATE']
    matches=[i for i in range(8161-len(rb))if body[i:i+len(rb)]==rb]
    assert len(matches)==1,matches
    bdefs=defs+f'DkRotateOAMY=${0xa000+matches[0]:x}\nDkDuplicateTileAlias=${alias:x}\n'
    oldb=A(bdefs+'.segment "BODY"\n'+P.expand_branches(bsrc),dict(BODY=(start,end-start)))
    assert oldb['images']['BODY']==current
    newb=once(bsrc,''' tay
 and #1
 bne BodyDrawDone
 iny
 tya
''',''' lsr
 bcs BodyDrawDone
 rol
 adc #1
''')
    newb=once(newb,''' lda $c212,x
 cmp $c216,x
 bne BodyDrawDone
 and #$80
 bne BodyDrawDone
''',''' lda $c212,x
 bmi BodyDrawDone
 cmp $c216,x
 bne BodyDrawDone
''')
    newb=once(newb,' jsr DkRotateOAMY\n bcs BodyDrawDone\n ldx #0\n',
        ' jsr DkRotateOAMY\n bcs BodyDrawDone\n tax\n')
    stop=newb.index('BodyDrawDone:\n')
    assert newb[stop:].count(' pla\n tay\n pla\n tax\n pla\n plp\n')==2
    newb=newb[:stop]+'''BodyDrawDone:
 tsx
 lsr $0104,x
 lda DrawBodyResult
 lsr
 rol $0104,x
 pla
 tay
 pla
 tax
 pla
 plp
 rts
'''
    nb=A(bdefs+'.segment "BODY"\n'+P.expand_branches(newb),dict(BODY=(start,end-start)))
    assert oldb['used']['BODY']-nb['used']['BODY']==7
    velocity_high=start+nb['used']['BODY']
    high=A('.segment "HIGH"\nDkOneWayVelocityHigh:\n lda $c083\n sbc $c087\n rts\n',dict(HIGH=(velocity_high,8)))
    new_body=nb['images']['BODY']+high['images']['HIGH']
    emit('Source-equivalent body funding and velocity high',start-0xa000,end-start,current,new_body.ljust(end-start,b'\xea'))
    # Existing Main gains only its equivalent guarded state projection.
    msrc=frozen[frozen.index('.segment "DK_MAIN"'):frozen.index('DkNativeMainEnd:')]
    msrc=once(msrc,' jsr DkPauseMain',' jsr DkScrollPublish')
    mdefs=defs+'DkScrollPublish=$d240\n'
    oldm=A(mdefs+msrc,dict(DK_MAIN=(0xd65e,73)))
    at=msrc.index(' lda $c06b\n');stop=msrc.index('DkMainNo:\n',at)
    newm=msrc[:at]+''' lda $c06b
 eor #1
 cmp #4
 bcc DkMainState
 lsr
DkMainState:
 ora #0
 sta Player_State
 sec
 rts
'''+msrc[stop:]
    nm=A(mdefs+newm,dict(DK_MAIN=(0xd65e,73)))
    assert nm['used']['DK_MAIN']==64
    low=A(f'DkOneWayVelocityHigh=${velocity_high:x}\n.segment "LOW"\nDkOneWayVelocityLow:\n lda $c082\n cmp $c086\n jmp DkOneWayVelocityHigh\n',dict(LOW=(0xd69e,9)))
    main=nm['images']['DK_MAIN']+low['images']['LOW']
    emit('Source-equivalent Main funding and velocity low',9*1024+0x65e,73,
        oldm['images']['DK_MAIN'],main.ljust(73,b'\xea'))
    # Keep every PC from PlatformLoop onward, including all SMC targets.
    first=frozen.index('NativeObjects:\n');last=frozen.index('PlatformLoop:\n',first)+len('PlatformLoop:\n')
    wsrc=re.sub(r'^DkShortCandidate\d+:\n','',frozen[first:last],flags=re.M)
    oldw=A(defs+'.segment "WORLD"\n'+P.expand_branches(wsrc),
        dict(WORLD=(labels['NativeObjects'],labels['PlatformLoop']-labels['NativeObjects'])))
    neww=once(wsrc,' sta WScreenHi\n',' tax\n')
    neww=once(neww,' lda WScreenHi\n',' txa\n')
    neww=once(neww,' lda Vine_FlagOffset\n jeq ObjectsDone\n cmp #3\n jcs ObjectsDone\n tay\n',
        ' ldy Vine_FlagOffset\n jeq ObjectsDone\n cpy #3\n jcs ObjectsDone\n')
    neww=once(neww,' jcs Platforms\n',' jcs PlatformIngress\n')
    neww=re.sub(r'ObjectsDone:\n rts\n(?:(?:;[^\n]*|)\n)*Platforms:\n ldx #5\n',
        f'PlatformIngress:\n jsr ${guard:x}\n bpl Platforms\nObjectsDone:\n rts\nPlatforms:\n ldx #5\n',neww)
    assert neww!=wsrc and neww.count('ObjectsDone:\n')==1 and neww.count(' jsr $cc14\n')==1
    nw=A(defs+'.segment "WORLD"\n'+P.expand_branches(neww),
        dict(WORLD=(labels['NativeObjects'],labels['PlatformLoop']-labels['NativeObjects'])))
    assert oldw['used']==nw['used']
    assert nw['symbols']['ObjectsDone']==labels['ObjectsDone']
    assert nw['symbols']['Platforms']==labels['Platforms']
    emit('Vine scratch factoring and one-way platform ingress',labels['NativeObjects']-0xa000,
        len(oldw['images']['WORLD']),oldw['images']['WORLD'],nw['images']['WORLD'])
    calls=[0xa000+i-1 for i in range(1,8191)if body[i:i+2]==bytes.fromhex('e0cb')]
    assert calls==[0xb651],calls
    report=dict(fragments=result,guard_entry=guard,platform_ingress=nw['symbols']['PlatformIngress'],
        velocity_low=0xd69e,velocity_high=velocity_high,sole_current_retire_helper_JSR=calls,
        original_BBOX_relocated_to=nr['symbols']['OriginalBBox'],
        one_way_predicate='source3 and signed(C83:C82-C87:C86)<0',
        jump_age0_omission_requires_legal_query_lifecycle=True,
        private_retire_Selected40_guard_preserved=True,
        new_RAM_bytes=0,new_physical_CHR_pages=0,new_native_PRG_bytes=0,
        full_CPU_or_ISR_qualification=False)
    if include_components:report['_components']=dict(body_start=start,body_end=end,
        old_body=oldb['images']['BODY'],new_body=new_body.ljust(end-start,b'\xea'),
        alias_address=alias,alias=body[alias-0xa000:alias-0xa000+22],
        rotation_address=0xa000+matches[0],rotation=rb)
    return report


def main():
    _,raw=F.load_inputs();report=fragments(raw)
    print('DKJR_ONEWAY_SOURCE_FIT '+json.dumps(dict(parent_SHA256=T.PIN,source_fit_only=True,
        ROM_composed=False,root_grant=False,outputs_written=0,**report),separators=(',',':')),flush=True)


if __name__=='__main__':main()
