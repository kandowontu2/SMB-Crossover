"""Detached visible native-entry fit in existing DK spans; no CPU/ROM overlay."""
from hashlib import sha256
import json
import re

import plan_dkjr_forced_entry_admission_1116 as Plan

C,T,W=Plan.C,Plan.Plan.Source.T,Plan.W
H=lambda value:sha256(value).hexdigest()


def measure(parent):
    census=Plan.descriptor(parent)
    raw,_=C.proposal(parent);body=C.Camera.payload(raw)
    source,known=Plan.Plan.source_inputs()
    original=T.assemble(''.join(f'{n}=${v:x}\n'for n,v in known.items())+
        Plan.Plan.Source.expand_branches(source),dict(DKJR=(0xa000,8160),DK_MAIN=(0xd65e,73),
        DK_PAUSE=(0xd540,286),DK_PORTS=(0xd6a7,345)))
    labels=original['symbols']
    fragments={};funded=[]
    for role,first,last,pointer,wanted in(('FRUIT','D_d955','D_da14','91',dict(lda=4,sta=0)),
                                        ('DRAW','D_ea08','D_eb69','04',dict(lda=3,sta=3))):
        text=source[source.index(first+':'):source.index(last+':')]
        begin,end=labels[first],labels[last];counts=dict(lda=0,sta=0)
        for match in list(re.finditer(r'^DIndirect_([0-9a-f]+): (lda|sta) \$ffff,y$',text,re.M)):
            suffix,operation=match.groups()
            if counts[operation]>=wanted[operation]:continue
            name='D_'+suffix;start=text.index(name+':')
            piece=text[start:match.end()]
            assert re.findall(r' lda \$(c[0-9a-f]{3})\n',piece)==['c0'+pointer,'c0'+f'{int(pointer,16)+1:02x}']
            funded.append(dict(role=role,label=name,operation=operation,old_PC=labels[name],old_template_bytes=25,
                old_cell_PC=labels['DIndirect_'+suffix]))
            counts[operation]+=1
        assert counts==wanted,(role,counts,wanted)
        # Work backwards because each removed prefix shifts later text offsets.
        for row in reversed([row for row in funded if row['role']==role]):
            match=re.search(r'^DIndirect_'+row['label'][2:]+r': '+row['operation']+r' \$ffff,y$',text,re.M)
            start=text.index(row['label']+':')
            helper='ReadPointer'+pointer if row['operation']=='lda'else'StorePointer04'
            text=text[:start]+row['label']+':\n jsr '+helper+'\n'+text[match.end():]
        fragments[role]=text
        assert text.rstrip().endswith('rts')
    entry='''MeasuredAnchorReady:
 lda $c8fe
 cmp #2
 beq EntryYes
 cmp #1
 bne EntryNo
 lda GameEngineSubroutine
 cmp #8
 bne EntryNo
 jsr MeasuredForcedFall
 bcc EntryImport
 ; Pending pause may project the body, but never advances native gravity.
 lda TimerControl
 bne EntryProject
 lda #<NativeVertical
 sta FarcallJmpTarget_SMC+1
 lda #>NativeVertical
 sta FarcallJmpTarget_SMC+2
 lda #NativeVerticalBank
 jsr FarCallCommon
EntryProject:
 jsr DkjrNativeImportAnchor
 clc
 rts
EntryImport:
 jsr DkjrNativeImportAnchor
 bcc EntryNo
 jsr DkjrNativeCameraSync
 inc $c8fe
EntryYes:
 rts
EntryNo:
 clc
 rts
'''
    context='''MeasuredEntryContext:
 lda OperMode
 cmp #1
 bne ContextNo
 lda OperMode_Task
 cmp #3
 bne ContextNo
 lda $c04a
 cmp #1
 bne ContextNo
 lda GameEngineSubroutine
 eor #8
 ora DisableCollisionDet
 ora JumpspringAnimCtrl
 ora SwimmingFlag
 ora $c068
 bne ContextNo
 lda Player_Y_HighPos
 cmp #1
 bne ContextNo
 lda PlayerEntranceCtrl
 cmp #1
 bne ContextNo
 sec
 rts
ContextNo:
 clc
 rts
'''
    predicates=''' jmp MeasuredAnchorReady
MeasuredForcedFall:
 jsr MeasuredEntryContext
 bcc EntryPredicateNo
 lda Player_State
 cmp #2
 beq EntryPredicateYes
EntryPredicateNo:
 clc
 rts
EntryPredicateYes:
 ; CMP#2's equal path already supplies carry.
 rts
MeasuredVisiblePending:
 jsr MeasuredEntryContext
 bcc EntryPredicateNo
 lda Player_State
 and #$fd
 bne EntryPredicateNo
 ; Exact states0/2 only. Project AFTER native BG as well, for visible landing.
 jmp DkjrNativeImportAnchor
'''
    visible='''MeasuredDrawAdmission:
 lda $c8fe
 cmp #2
 beq DrawYes
 cmp #1
 bne DrawNo
 jmp MeasuredVisiblePending
DrawYes:
 rts
DrawNo:
 clc
 rts
'''
    reader04='''ReadPointer04:
 php
 pha
 lda $c004
 sta EntryReadCell+1
 lda $c005
EntryReadTranslate:
 cmp #8
 bcs EntryReadROM
 ora #$c0
EntryReadROM:
 sta EntryReadCell+2
 pla
 plp
EntryReadCell:
 lda $ffff,y
 rts
'''
    reader91='''ReadPointer91:
 php
 pha
 lda $c091
 sta EntryReadCell+1
 lda $c092
 jmp EntryReadTranslate
'''
    store04='''StorePointer04:
 php
 pha
 lda $c004
 sta EntryStoreCell+1
 lda $c005
 cmp #8
 bcs EntryStoreROM
 ora #$c0
EntryStoreROM:
 sta EntryStoreCell+2
 pla
 plp
EntryStoreCell:
 sta $ffff,y
 rts
'''
    fruit,draw=labels['D_d955'],labels['D_ea08']
    assert census['source_declared_capacity']['fruit_original']['bytes']==315
    draw_size=census['source_declared_capacity']['draw_original']['bytes']
    assert draw_size==labels['D_eb69']-draw==714
    draw_compact=draw_size-6*22
    layout=dict(FRUIT=(fruit,227),READ04=(fruit+227,26),ENTRY=(fruit+253,61),
        DRAW=(draw,draw_compact),READ91=(draw+draw_compact,14),STORE04=(draw+draw_compact+14,26),
        CONTEXT=(draw+draw_compact+40,56),VISIBLE=(draw+draw_compact+96,17),
        ANCHOR=(0xbfc1,31),BODY_GUARD=(0xbc8c,10))
    pieces=dict(FRUIT=fragments['FRUIT'],READ91=reader91,ENTRY=entry,
        DRAW=fragments['DRAW'],READ04=reader04,STORE04=store04,CONTEXT=context,VISIBLE=visible,
        ANCHOR=predicates,BODY_GUARD=' jsr MeasuredDrawAdmission\n bcs BodyAdmissionYes\n jmp $bd27\nBodyAdmissionYes:\n nop\n nop\n')
    all_text=''.join('.segment "'+name+'"\n'+pieces[name]for name in layout)
    local=set(re.findall(r'^(\w+):',all_text,re.M))
    bundle=dict(W.Symbols.bundle());bundle['raw']=raw
    native_names=('OperMode','OperMode_Task','GameEngineSubroutine','PlayerEntranceCtrl','Player_State',
        'Player_Y_HighPos','TimerControl','DisableCollisionDet','JumpspringAnimCtrl','SwimmingFlag',
        'FarcallJmpTarget_SMC','FarCallCommon')
    removed_cells={'DIndirect_'+row['label'][2:]for row in funded}
    defs=Plan.Plan.numeric(source)+''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in local|removed_cells)
    defs+=''.join(f'{n}=${W.address(bundle,n):x}\n'for n in native_names)
    native_pc,native_file=W.address(bundle,'MovePlayerVertically'),W.location(bundle,'MovePlayerVertically')
    defs+=f'NativeVertical=${native_pc:x}\nNativeVerticalBank=${((native_file-16)//8192)|128:x}\n'
    linked=T.assemble(defs+all_text,layout)
    assert all(linked['used'][name]==size for name,(_,size)in layout.items()),linked['used']
    rows=[]
    for role,begin,end in(('fruit',fruit,fruit+315),('draw',draw,draw+draw_size),
                          ('anchor',0xbfc1,0xbfe0),('body_guard',0xbc8c,0xbc96)):
        old=body[begin-0xa000:end-0xa000];new=bytearray(b'\xea'*(end-begin));members=[]
        for name,(pc,size)in layout.items():
            if begin<=pc<end:
                assert pc+size<=end
                new[pc-begin:pc-begin+size]=linked['images'][name]
                members.append(dict(name=name,PC=pc,bytes=size))
        rows.append(dict(role=role,PC=begin,end_exclusive=end,payload_offset=begin-0xa000,bytes=end-begin,
            old_hex=old.hex(),new_hex=bytes(new).hex(),old_SHA256=H(old),new_SHA256=H(new),members=members))
    moved=[dict(label=name,old_PC=pc,new_PC=linked['symbols'][name])for name,pc in labels.items()
        if name.startswith(('D_','DkShortCandidate'))and name in linked['symbols']and ((fruit<=pc<fruit+315)or(draw<=pc<draw+draw_size))
        and linked['symbols'][name]!=pc]
    return dict(detached_measurement=True,owning_current91dc=H(parent),source_parent_a3fb=H(raw),
        fragments=rows,logical_bytes=sum(row['bytes']for row in rows),future_cookie_bytes=16,
        exact_funding_templates=funded,moved_labels=moved,
        old_original_SMCell_templates_removed=[row['old_cell_PC']for row in funded],
        self_contained_readers=dict(cell_PC=linked['symbols']['EntryReadCell'],translate_PC=linked['symbols']['EntryReadTranslate'],
            store_cell_PC=linked['symbols']['EntryStoreCell'],
            full_reader_bytes=26,prefix_reader_bytes=14,full_store_bytes=26,protected_head_bytes_or_runtime_cells_used=0),
        spare=dict(fruit=1,draw=19,anchor=0),native_gravity_PC=native_pc,native_gravity_bank=((native_file-16)//8192)|128,
        original_fall_and_world_bytes_untouched=True,no_after_floor_hook=True,new_service_rows=0,
        no_new_RAM_or_carriers=True,visible_pending_draw_reprojects_on_native0_or2=True,
        pending_Timer_nonzero_does_not_advance_native_gravity=True,
        implementation_or_mount_authorized=False,ROM_composed=False,CPU_executed=False,outputs=0,
        required_before_lease=['All fruit/draw moved exports, literal/table/indirect/SMC consumers',
            'Complete read-prefix flags, shared-cell consumers, stack/IRQ/reentry contract',
            'Ready1 native gravity/BG caller order and first genuine ground proof in all legal entries',
            'Complete cold/respawn/pipe/vine/water/fault/foreign/pause ABI and visible pending-body contract'])


if __name__=='__main__':
    report=measure(C.BT.ROM.read_bytes())
    text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_ENTRY_ONLY_FIT '+text,flush=True)
    print('DKJR_ENTRY_ONLY_FIT_SHA256 '+H(text.encode()),flush=True)
