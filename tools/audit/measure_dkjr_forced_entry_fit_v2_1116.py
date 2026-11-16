"""Detached entry-fit v2: explicit native rising rejection, no overlay/CPU."""
from hashlib import sha256
import json
from pathlib import Path

import measure_dkjr_forced_entry_fit_1116 as Prior
import check_dkjr_entry_fit_consumers_1116 as Consumers

C,Plan,W=Prior.C,Prior.Plan,Prior.W
H=lambda value:sha256(value).hexdigest()
PRIOR_SHA='002b7265c649a794ecc676a7592758bee868673dadc52e1746b802e365f150f6'
CONSUMERS_SHA='1b223c603a31eed47150c4c80f30bd97c4f6c4967ed557777a6f0733b9dce99b'


def measure(parent):
    assert H(Path(Prior.__file__).read_bytes())==PRIOR_SHA
    assert H(Path(Consumers.__file__).read_bytes())==CONSUMERS_SHA
    base=Prior.measure(parent);raw,_=C.proposal(parent)
    rows={row['role']:dict(row,members=[dict(member)for member in row['members']])for row in base['fragments']}
    def member(role,name):return next(item for item in rows[role]['members']if item['name']==name)
    entry=member('fruit','ENTRY')['PC'];context=member('draw','CONTEXT')['PC']
    visible=member('draw','VISIBLE')['PC'];forced=visible+17
    _,labels=Plan.Plan.source_inputs()
    bundle=dict(W.Symbols.bundle());bundle['raw']=raw
    definitions=f'MeasuredAnchorReady=${entry:x}\nMeasuredEntryContext=${context:x}\n'+\
        f'DkjrNativeImportAnchor=${labels["DkjrNativeImportAnchor"]:x}\n'+\
        f'Player_State=${W.address(bundle,"Player_State"):x}\nPlayer_Y_Speed=${W.address(bundle,"Player_Y_Speed"):x}\n'
    source='''.segment "ANCHOR"
 jmp MeasuredAnchorReady
MeasuredVisiblePending:
 jsr MeasuredEntryContext
 bcc VisibleNo
 lda Player_State
 and #$fd
 bne VisibleNo
 jmp DkjrNativeImportAnchor
VisibleNo:
 clc
 rts
 .byte $ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea
 ; Explicit unreachable spare inside the31B owned envelope.
.segment "FORCED"
MeasuredForcedFall:
 jsr MeasuredEntryContext
 bcc ForcedNo
 lda Player_State
 cmp #2
 bne ForcedNo
 lda Player_Y_Speed
 bmi ForcedNo
 ; CMP#2 establishedC1; LDA/BMI preserve it, including genuine initialVY0.
 rts
ForcedNo:
 clc
 rts
'''
    code=Prior.T.assemble(definitions+source,dict(ANCHOR=(0xbfc1,31),FORCED=(forced,18)))
    assert code['used']==dict(ANCHOR=31,FORCED=18)
    assert code['symbols']['MeasuredVisiblePending']==0xbfc4
    fruit=bytearray.fromhex(rows['fruit']['new_hex']);at=entry-rows['fruit']['PC']
    body=bytes(fruit[at:at+61]);old_call=bytes.fromhex('20c4bf')
    assert body.count(old_call)==1
    body=body.replace(old_call,bytes((0x20,forced&255,forced>>8)),1)
    fruit[at:at+61]=body
    draw=bytearray.fromhex(rows['draw']['new_hex']);at=visible-rows['draw']['PC']
    assert draw[at+11:at+14]==bytes.fromhex('4cd2bf')
    draw[at+11:at+14]=bytes.fromhex('4cc4bf')
    at=forced-rows['draw']['PC'];assert draw[at:]==b'\xea'*19
    draw[at:at+18]=code['images']['FORCED']
    rows['draw']['members'].append(dict(name='FORCED_VY_QUALIFIED',PC=forced,bytes=18))
    for role,data in(('fruit',bytes(fruit)),('draw',bytes(draw)),('anchor',code['images']['ANCHOR'])):
        rows[role]['new_hex']=data.hex();rows[role]['new_SHA256']=H(data)
    result=dict(base,fragments=list(rows.values()),revision=2,
        revision1_fit_receipt_SHA256=H(json.dumps(base,sort_keys=True,separators=(',',':')).encode()),
        frozen_revision1_source_SHA256=PRIOR_SHA,spare=dict(fruit=1,draw=1,anchor=12),
        native_VY_negative_explicitly_rejected=True,initial_VY_zero_preserved=True,
        visible_native_states_exactly_zero_or_two=True,source_physics_or_fall_limits_changed=False,
        fragment_delta_scope='Only pending EntryJSR target, visible-tail JMP target, new18B leaf in owned draw spare, and31B anchor; original semantic relocation/SMC funding is unchanged.')
    assert result['logical_bytes']==1070
    assert result['moved_labels']==base['moved_labels']
    return result


def consumers(parent):
    old=Consumers.check(parent);new=measure(parent)
    assert {row['label']:dict(old=row['old_PC'],new=row['new_PC'])for row in new['moved_labels']}==old['moved_label_map']
    proof=dict(old,revision=2,measured_fit_receipt_SHA256=H(json.dumps(new,sort_keys=True,separators=(',',':')).encode()),
        frozen_revision1_consumer_source_SHA256=CONSUMERS_SHA,
        semantic_relocation_and_old_SMC_writers_rechecked_unchanged=True,
        new_18B_leaf_uses_only_private_context_and_native_state_VY_reads=True,
        new_internal_references=[dict(role='pending_entry_JSR',target=next(x['PC']for r in new['fragments']for x in r['members']if x['name']=='FORCED_VY_QUALIFIED')),
            dict(role='visible_tail_JMP',target=0xbfc4)],
        new_leaf_or_source_CPU_not_executed=True)
    return proof


def physical(parent):
    report=measure(parent);raw,_=C.proposal(parent);body=C.Camera.payload(raw)
    owner=C.Camera.Plan.Current.F.Prior.Early.Old
    digest=sha256();cursor=0;chunks=[]
    for row in sorted(report['fragments'],key=lambda item:item['payload_offset']):
        at=row['payload_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex'])
        assert at>=cursor and body[at:at+len(before)]==before
        digest.update(body[cursor:at]);digest.update(after);cursor=at+len(before)
        done=0
        while done<len(before):
            page,within=divmod(at+done,1024);size=min(1024-within,len(before)-done)
            file=owner.CHR+owner.PAGES[page]*1024+within
            a,b=before[done:done+size],after[done:done+size]
            assert raw[file:file+size]==a
            chunks.append(dict(role=row['role'],file_half_open=[file,file+size],CHR_page=owner.PAGES[page],
                bytes=size,old_hex=a.hex(),new_hex=b.hex(),old_SHA256=H(a),new_SHA256=H(b)))
            done+=size
    digest.update(body[cursor:]);cookie=raw[534485:534488]+digest.digest()[:13]
    chunks.append(dict(role='necessary-cookie',file_half_open=[534485,534501],bytes=16,
        old_hex=raw[534485:534501].hex(),new_hex=cookie.hex()))
    rom=sha256();cursor=0
    for row in sorted(chunks,key=lambda item:item['file_half_open'][0]):
        lo,hi=row['file_half_open'];assert lo>=cursor
        rom.update(raw[cursor:lo]);rom.update(bytes.fromhex(row['new_hex']));cursor=hi
    rom.update(raw[cursor:])
    return dict(detached=True,revision=2,source_parent_a3fb=H(raw),
        fit_receipt_SHA256=H(json.dumps(report,sort_keys=True,separators=(',',':')).encode()),
        predicted_ROM_SHA256=rom.hexdigest(),predicted_packet_SHA256=digest.hexdigest(),predicted_cookie=cookie.hex(),
        physical=chunks,owned_code=1070,owned_with_cookie=1086,
        ROM_composed=False,CPU_executed=False,outputs=0)


if __name__=='__main__':
    parent=C.BT.ROM.read_bytes()
    for tag,report in(('FIT',measure(parent)),('CONSUMERS',consumers(parent)),('PHYSICAL',physical(parent))):
        text=json.dumps(report,sort_keys=True,separators=(',',':'))
        print('DKJR_ENTRY_V2_'+tag+' '+text,flush=True)
        print('DKJR_ENTRY_V2_'+tag+'_SHA256 '+H(text.encode()),flush=True)
