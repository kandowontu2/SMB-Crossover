"""Measure unallocated DK endpoint bodies and current exact preimages.

The link origins below are measurement addresses only. No candidate, source
overlay, RAM lease, native routing change, or new executable span is created.
"""
from hashlib import sha256
import argparse
import json
import re

import compose_dkjr_oneway_support_1114 as S
import check_dkjr_platform_query_lifecycle_1114 as Life
import compose_dkjr_oneway_current_1114 as Current
import current_dkjr_review_input_1114 as Input

F=S.Replay;G=F.Gate
P,H,N,W=G.P,G.H,G.N,G.W


def measure(*,current_kind='hidden-421'):
    _,old=F.load_inputs();raw,_=S.proposal(old);body=P.T.payload(raw)
    _,labels=Life.closure(old);b=W.Symbols.bundle();b['raw']=raw
    names=('OperMode','OperMode_Task','GameEngineSubroutine','PlayerEntranceCtrl',
        'Player_State','Player_Y_HighPos','Player_Y_Position','TimerControl',
        'Player_X_Position','Player_PageLoc','ScreenLeft_X_Pos','ScreenLeft_PageLoc',
        'DisableCollisionDet','JumpspringAnimCtrl','SwimmingFlag',
        'FarcallJmpTarget_SMC','FarCallCommon')
    defs=''.join(f'{name}=${W.address(b,name):x}\n'for name in names)
    for name in ('DkjrNativeImportAnchor','DkjrNativeCameraSync','DkjrNativeShiftCamera'):
        defs+=f'{name}=${labels[name]:x}\n'
    carry=labels['CarryAccepted'];at=carry-0xa000
    assert body[at:at+6]==bytes.fromhex('adf7c8c901f0')
    defs+=f'DkExistingAirLanding=${carry+7:x}\nCarryTop=$c8f5\n'
    defs+=f'DkjrNativeWorldBuild=${labels["DkjrNativeWorldBuild"]:x}\n'
    adder=H.T.offset(labels['DkNativeAdder'])
    assert body[adder:adder+4]==bytes.fromhex('a0023860')
    at_adder=W.location(b,'BlockBufferAdderData');base=raw[at_adder+2]
    xadder=W.location(b,'BlockBuffer_X_Adder');yadder=W.location(b,'BlockBuffer_Y_Adder')
    assert base==14 and tuple(raw[xadder+base+1:xadder+base+3])==(3,12)
    assert tuple(raw[yadder+base+1:yadder+base+3])==(32,32)
    pc=W.address(b,'MovePlayerVertically');offset=W.location(b,'MovePlayerVertically')
    bank=((offset-16)//8192)|128
    defs+=f'NativeVertical=${pc:x}\nNativeVerticalBank=${bank:x}\n'
    entry='''
.segment "ENTRY"
MeasuredAnchorReady:
 lda $c8fe
 cmp #2
 beq EntryYes
 cmp #1
 bne EntryNo
 lda GameEngineSubroutine
 cmp #8
 bne EntryNo
 ; Only the native header's Y32 falling entrance keeps native gravity.
 ; A pipe/vine/ordinary grounded first anchor retains the old import.
 jsr MeasuredForcedDrop
 bcc EntryImport
 lda #<NativeVertical
 sta FarcallJmpTarget_SMC+1
 lda #>NativeVertical
 sta FarcallJmpTarget_SMC+2
 lda #NativeVerticalBank
 jsr FarCallCommon
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
MeasuredAnchorEnd:
.segment "PREDICATE"
MeasuredForcedDrop:
 lda OperMode
 cmp #1
 bne DropNo
 lda OperMode_Task
 cmp #3
 bne DropNo
 lda $c04a
 cmp #1
 bne DropNo
 lda GameEngineSubroutine
 eor #8
 ora TimerControl
 ora DisableCollisionDet
 ora JumpspringAnimCtrl
 ora SwimmingFlag
 ora $c068
 bne DropNo
 lda PlayerEntranceCtrl
 cmp #1
 bne DropNo
 lda Player_State
 cmp #2
 bne DropNo
 lda Player_Y_HighPos
 cmp #1
 bne DropNo
 sec
 rts
DropNo:
 clc
 rts
.segment "VISIBLE"
MeasuredDrawAdmission:
 lda $c8fe
 cmp #2
 beq DrawYes
 cmp #1
 bne DrawNo
 jmp MeasuredForcedDrop
DrawYes:
 rts
DrawNo:
 clc
 rts
'''
    floor='''
.segment "FLOOR"
MeasuredAfterEffects:
 php
 pha
 txa
 pha
 tya
 pha
 lda OperMode
 cmp #1
 bne FloorDone
 lda OperMode_Task
 cmp #3
 bne FloorDone
 lda $c8fe
 cmp #2
 bne FloorDone
 lda $c04a
 cmp #1
 bne FloorDone
 lda GameEngineSubroutine
 eor #8
 ora TimerControl
 ora DisableCollisionDet
 ora JumpspringAnimCtrl
 ora SwimmingFlag
 ora $c068
 bne FloorDone
 lda Player_Y_HighPos
 cmp #1
 bne FloorDone
 lda $c06b
 cmp #4
 bne FloorDone
 lda Player_State
 bne FloorDone
 jsr DkjrNativeShiftCamera
 bcc FloorDone
 lda Player_Y_Position
 clc
 adc #32
 bcs FloorDone
 sta CarryTop
 jsr MeasuredStaticFloor
 bcc FloorDone
 ; This bypasses only CarryAccepted's phase1 test, not its screen-X
 ; validation, pre-snap fall comparison, pending transition or original Land.
 jsr DkExistingAirLanding
FloorDone:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
MeasuredAfterEffectsEnd:
.segment "STATIC"
MeasuredStaticFloor:
 ; Save the original actor's query and selector. Kind2 builds static-only
 ; terrain; its NativeObjects path cannot contribute a platform plane.
 lda $c8db
 pha
 ldx #0
StaticSave:
 lda $c03e,x
 pha
 inx
 cpx #4
 bne StaticSave
 lda Player_Y_Position
 and #15
 bne StaticNo
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta $c03e
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 bne StaticNo
 lda $c03e
 cmp #8
 bcc StaticNo
 cmp #232
 bcs StaticNo
 clc
 adc #3
 sta $c03e
 clc
 adc #9
 sta $c040
 lda CarryTop
 sta $c03f
 sta $c041
 lda #2
 sta $c8db
 jsr DkjrNativeWorldBuild
 lda $c8dd
 cmp #1
 jmp StaticRestore
StaticNo:
 clc
StaticRestore:
 ldx #3
StaticPop:
 pla
 sta $c03e,x
 dex
 bpl StaticPop
 pla
 sta $c8db
 rts
'''
    layout=dict(ENTRY=(0x9000,256),FLOOR=(0x9200,256),PREDICATE=(0x9400,256),VISIBLE=(0x9600,256),STATIC=(0x9800,256))
    linked=H.T.assemble(defs+entry+floor,layout)
    frozen,*_=H.T.old_source();start=frozen.index('DkNativeAnchorReady:')
    stop=frozen.index('DkjrComponentEnd:',start)
    old_source=frozen[start:stop]
    defined=set(re.findall(r'^(\w+):',old_source,re.M))
    old_defs=''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined)
    original=H.T.assemble(old_defs+'.segment "OLD"\n'+P.expand_branches(old_source),
        dict(OLD=(labels['DkNativeAnchorReady'],0xbfe0-labels['DkNativeAnchorReady'])))['images']['OLD']
    assert original==body[labels['DkNativeAnchorReady']-0xa000:0x1fe0]
    table=labels['DkServices'];row34=table+34*3
    assert body[row34-0xa000]==0x4c
    def record(name):
        data=linked['images'][name]
        return dict(bytes=len(data),measurement_origin=layout[name][0],
            generated_hex=data.hex(),SHA256=sha256(data).hexdigest())
    cold_path=P.B.R/'tools/reference/dkjr_cold_compact_1110_v2.s'
    cold=cold_path.read_text()
    cold=P.once(cold,'    cmp #8\n    bne DkCopyRow\n    rts','''    cmp #9
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
    cold=P.once(cold,'.byte $31,$41,$4f,$58,$63,$71,$72,$73',
        '.byte $31,$41,$4f,$58,$63,$71,$72,$73,$bf')
    before=H.T.assemble(cold,dict(DK_COLD=(0xd25e,119)))
    current_cold=before['images']['DK_COLD'].ljust(119,b'\xff')
    assert before['used']['DK_COLD']==117
    assert current_cold==body[H.T.offset(0xd25e):H.T.offset(0xd25e)+119]
    cold=P.once(cold,'    cmp #9\n','    cmp #10\n')
    cold=P.once(cold,',$73,$bf',',$73,$bf,$a3')
    after=H.T.assemble(cold,dict(DK_COLD=(0xd25e,119)))
    assert after['used']['DK_COLD']==118
    # Root named931 solely as a REVIEW TARGET. Assembling its prospective
    # low byte is a measurement, not an allocation or cartridge placement.
    current,input_info=Input.read(kind=current_kind)
    assert sha256(current).hexdigest()==Current.PARENT
    review_page=931;review_at=1048592+review_page*1024
    review_preimage=current[review_at:review_at+1024]
    assert review_preimage==b'\xff'*1024
    body_guard=bytes.fromhex('adfec8c902f0034c24bd')
    assert body[:0x1fe0].count(body_guard)==1
    guard_at=body.index(body_guard)
    return dict(measurement_only=True,allocation_granted=False,ROM_composed=False,
        existing_private_SHA256=S.PIN,entry=record('ENTRY'),after_effects=record('FLOOR'),
        current_review_input=input_info,
        shared_forced_drop_predicate=record('PREDICATE'),pending_draw_admission=record('VISIBLE'),
        static_floor_validator=record('STATIC'),
        exact_native_feet=dict(private_adder_return=2,native_adder_base=14,
            X_offsets=[3,12],Y_offsets=[32,32],original_query_and_kind_saved_restored=True,
            actor_planes_excluded_by_world_kind2=True),
        current_anchor=dict(PC=labels['DkNativeAnchorReady'],bytes=len(original),
            preimage_hex=original.hex(),SHA256=sha256(original).hexdigest()),
        current_row34=dict(PC=row34,preimage_hex=body[row34-0xa000:row34-0xa000+3].hex()),
        current_body_readiness_guard=dict(PC=0xa000+guard_at,bytes=10,
            preimage_hex=body_guard.hex(),
            measured_replacement_hex_at_VIRTUAL_address='200096b0034c24bdeaea',
            size_unchanged=True),
        existing_landing_continuation=dict(PC=carry+7,phase_test_bytes=body[at:at+7].hex(),
            remaining_screen_and_pre_snap_injury_validation_preserved=True),
        native_vertical=dict(PC=pc,raw_bank=bank,first32_SHA256=sha256(raw[offset:offset+32]).hexdigest()),
        conditional_code_request=dict(RAM_bank=2,CPU_half_open=[0xcd00,0xd000],bytes=768,
            lease_currently_granted=False,requested_native_PRG_bytes=0,
            physical_CHR_pages_requested=1,physical_page_chosen=False,
            root_review_target=review_page,review_target_only_not_granted=True,
            current421_page_file_offset=review_at,
            current421_page_preimage_SHA256=sha256(review_preimage).hexdigest(),
            required_page_domain=[768,1023],cold_copy_half_open=[0xcd00,0xd100],
            source_page_layout='first768B new private handlers; last256B exact current D000..D0FF',
            metadata_overlap_SHA256=sha256(body[9216:9472]).hexdigest(),
            ownership_writer_reader_and_native_grant_pending=True),
        cold_extension=dict(PC=0xd25e,owned_capacity=119,current_used=117,proposed_used=118,
            current_preimage_hex=current_cold.hex(),
            proposed_hex_with_REVIEW_ONLY_page931=after['images']['DK_COLD'].hex(),
            source_file_SHA256=sha256(cold_path.read_bytes()).hexdigest()),
        net_handler_growth_bytes=sum(linked['used'].values())-len(original),
        existing_source_declared_spare=dict(ports_D7FC_D800=4,
            one_way_tail_CC7D_CC80=3,body_to_BFE0=0,Main_to_D6A7=0,
            original_geometry_tables_present=False),
        complete_layout_fit=False,new_RAM_or_CHR_allocation=0,outputs_written=0,
        open_gates=['All current legal row34 caller/context/area/spring/IRQ and saved-P ABI closure',
            'Pending-entry real native gravity at the exact owner call and complete entrance lifecycle',
            'Source-backed disjoint physical storage/executable spans and root allocation',
            'Finite gameplay/constructor/ISR/current421 preservation, full route and native replay'],
        scope='Conservative source bodies only, linked at virtual measurement addresses. Current preimages and native binding are exact. These bytes are not placed in a ROM or admitted as candidate code.')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--current-kind',choices=Input.KINDS,default='hidden-421')
    args=ap.parse_args()
    print('DKJR_FLOOR_ENTRY_HANDLER_MEASURE '+json.dumps(measure(current_kind=args.current_kind),separators=(',',':')),flush=True)
