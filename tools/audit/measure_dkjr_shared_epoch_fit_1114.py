"""Source-fit DK reuse of existing Mini epoch transport; no ROM composition.

Only proposed fragment bytes/preimages are reported. This is not a granted
cache, completed legal-writer/ISR proof, candidate, or performance result.
"""
from hashlib import sha256
import json

import replay_dkjr_final_handoff_1114 as F

A=F.Gate.H.T.assemble
HELPER_LAYOUT=dict(GATE=(0xa8dc,36),UTIL=(0xb06b,33),HEADER=(0xb8f0,16))
DEFINITIONS='''CurrentBankC=$7da1
SelectedCharacter=$6002
FrameCounter=$0e
MiniEpoch=$c3f0
DkEpoch=$c8ff
'''
OLD_HELPER=DEFINITIONS+'''.segment "GATE"
CheckMini:
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 lda FrameCounter
 beq Miss
 cmp MiniEpoch
 bne Miss
 jsr LiveHeader
 bcc Miss
 jmp CheckCodeHeader
Miss:
 clc
 jmp RestoreC
.segment "UTIL"
LiveHeader:
 lda $dfe0
 cmp #$a7
 bne Invalid
 lda $dfe1
 cmp #41
 beq HeaderReturn
Invalid:
 clc
HeaderReturn:
 rts
RestoreC:
 pla
MapC:
 sta CurrentBankC
 sta $5116
 rts
.segment "HEADER"
CheckCodeHeader:
 lda #3
 sta CurrentBankC
 sta $5116
 jsr LiveHeader
 jmp RestoreC
'''
NEW_HELPER=DEFINITIONS+'''.segment "GATE"
CheckMini:
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 jsr ReadEpoch
 beq Miss
 cmp FrameCounter
 bne Miss
 jsr LiveHeader
 bcc Miss
 jmp CheckCodeHeader
Miss:
 clc
 jmp RestoreC
.segment "UTIL"
LiveHeader:
 lda $dfe0
 cmp #$a7
 bne Invalid
 cpx $dfe1
 beq HeaderReturn
Invalid:
 clc
HeaderReturn:
 rts
RestoreC:
 pla
MapC:
 sta CurrentBankC
 sta $5116
 rts
CheckCodeHeader:
 lda #3
 jsr MapC
 jsr LiveHeader
 jmp RestoreC
.segment "HEADER"
ReadEpoch:
 ldx SelectedCharacter
 lda DkEpoch
 cpx #40
 beq EpochReturn
 lda MiniEpoch
EpochReturn:
 rts
'''
OLD_SELECTOR='''FarLo=$016c
FarHi=$016d
Selected=$6002
MiniTry=$a738
CoCheckCode=$aee2
ShCheckCode=$a800
PrSharedCall=$ab12
ShDispatch=$aaf7
ShDispatchNo=$ab4f
.segment "SELECTOR"
ExDispatch:
 jmp ShDispatch
PrFamily:
 lda FarHi
 cmp #$aa
 beq PrSh
 lda Selected
 sec
 sbc #37
 cmp #7
 bcc PrOdd
 lda FarLo
 jmp $b031
PrOdd:
 cmp #4
 beq MiniTry
MiniFullCheck:
 jsr CoCheckCode
 bcc DkLocalNo
MiniAuthorized:
 lda FarHi
 cmp #$b0
 bne DkLocalNo
 lda FarLo
 sec
 sbc #$8c
 bcc DkLocalNo
 cmp #114
 bcs DkLocalNo
 sta FarLo
 lda Selected
 cmp #38
 beq PrPrince
 bcc Source37
 cmp #43
 beq Source43
 lda #$a0
 bne Shared
Source37:
 lda #$a5
 bne Shared
Source43:
 lda #$d1
Shared:
 jmp PrSharedCall
DkLocalNo:
 jmp ShDispatchNo
PrSh:
 lda FarLo
 sec
 sbc #$88
 bcc DkLocalNo
 cmp #111
 bcs DkLocalNo
 sta FarLo
 jsr ShCheckCode
 bcc DkLocalNo
 lda #$a0
 jmp PrSharedCall
PrPrince:
 lda FarLo
 sta $0179
 lda #$1e
 sta FarLo
 lda #$df
 jmp PrSharedCall
'''


def once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def parts(raw):
    assert sha256(raw).hexdigest()==F.T.PIN
    oldh=A(OLD_HELPER,HELPER_LAYOUT);newh=A(NEW_HELPER,HELPER_LAYOUT)
    olds=A(OLD_SELECTOR,dict(SELECTOR=(0xa740,127)))
    new_selector=once(OLD_SELECTOR,' cmp #4\n beq MiniTry',' adc #1\n lsr\n cmp #2\n beq MiniTry')
    for base in('8c','88'):
        new_selector=once(new_selector,f' sbc #${base}\n bcc DkLocalNo',f' sbc #${base}')
    news=A(new_selector,dict(SELECTOR=(0xa740,127)))
    assert olds['used']['SELECTOR']==127 and news['used']['SELECTOR']==126
    rows=[]
    def row(bank,pc,size,old,new,role,fill):
        at=16+bank*8192+(pc&8191);before=old.ljust(size,bytes([fill]));after=new.ljust(size,bytes([fill]))
        assert raw[at:at+size]==before,(role,hex(pc),raw[at:at+size].hex(),before.hex())
        rows.append(dict(role=role,physical_PRG=bank,CPU_start=pc,file_offset=at,bytes=size,
            preimage_hex=before.hex(),preimage_SHA256=sha256(before).hexdigest(),
            proposed_hex=after.hex(),proposed_SHA256=sha256(after).hexdigest()))
    row(65,0xa740,127,olds['images']['SELECTOR'],news['images']['SELECTOR'],'Current selector before unchanged6B tail and DKcookie',0xea)
    oldc=bytes((0x90,(olds['symbols']['MiniFullCheck']-0xa7d7)&255,0xb0,(olds['symbols']['MiniAuthorized']-0xa7d9)&255))
    newc=bytes((0x90,(news['symbols']['MiniFullCheck']-0xa7d7)&255,0xb0,(news['symbols']['MiniAuthorized']-0xa7d9)&255))
    row(65,0xa7d5,5,oldc,newc,'Existing Mini checked branch slot',0xea)
    for name,(pc,size)in HELPER_LAYOUT.items():
        row(85,pc,size,oldh['images'][name],newh['images'][name],f'Existing Mini {name} source-owned helper extent',0xff)
    # Reproduce the exact existing Main from retained source before factoring.
    frozen,_,_,_=F.Gate.H.T.old_source();labels=F.Gate.P.frozen_labels()
    source=frozen[frozen.index('.segment "DK_MAIN"'):frozen.index('DkNativeMainEnd:')]
    scroll=(F.T.P.B.R/'tools/reference/dkjr_scroll_publish_1110_v1.s').read_text()
    scroll=scroll[:scroll.index('DkScrollPublishEnd:')]
    linked_scroll=A(scroll,dict(CAMERA=(0xd240,30)))
    body=F.T.P.T.payload(raw)
    assert body[9*1024+0x240:9*1024+0x25e]==linked_scroll['images']['CAMERA']
    source=once(source,' jsr DkPauseMain',' jsr DkScrollPublish')
    definitions='FrameCounter=$0e\nPlayer_X_Position=$75\nPlayer_Y_Position=$bd\nDkScrollPublish=$d240\n'+''.join(f'{n}=${labels[n]:x}\n'for n in('DkNativeAnchorReady','DkScoreFlush'))
    oldm=A(definitions+source,dict(DK_MAIN=(0xd65e,73)))
    start=source.index(' lda $c06b\n');end=source.index('DkMainNo:\n',start)
    source=source[:start]+''' lda $c06b
 eor #1
 cmp #4
 bcc DkMainState
 lsr
DkMainState:
 sta Player_State
 sec
 rts
'''+source[end:]
    source=once(source,' jsr DkScoreFlush\n bcc DkMainNo',' jsr DkScoreFlush\n bcc DkMainNo\n lda FrameCounter\n sta $c8ff')
    newm=A(definitions+source,dict(DK_MAIN=(0xd65e,73)))
    at=9*1024+0x65e
    assert body[at:at+73]==oldm['images']['DK_MAIN']
    proposed_main=newm['images']['DK_MAIN'].ljust(73,b'\xea')
    main=dict(role='Owned DK nativeMain carrier fragment',payload_offset=at,CPU_start=0xd65e,bytes=73,
        preimage_hex=body[at:at+73].hex(),preimage_SHA256=sha256(body[at:at+73]).hexdigest(),
        proposed_hex=proposed_main.hex(),proposed_SHA256=sha256(proposed_main).hexdigest())
    return dict(rows=rows,main=main,used=dict(old_helper=oldh['used'],new_helper=newh['used'],
        old_selector=olds['used'],new_selector=news['used'],old_main=oldm['used'],new_main=newm['used']),
        proposed_private_state=dict(address=0xc8ff,bytes=1,currently_granted=False),
        helper_labels=newh['symbols'],selector_labels=news['symbols'])


def main():
    _,raw=F.load_inputs();result=parts(raw)
    cases=[]
    for base,width in((0x8c,114),(0x88,111)):
        for low in range(256):assert(base<=low and low-base<width)==(((low-base)&255)<width)
        cases.append(dict(low_byte_base=base,width=width,cases=256,underflow_minimum=256-base))
    for source in range(1,6):
        value=source^1;value=value if value<4 else value>>1
        assert value==({1:0,2:3}.get(source,2))
    print('DKJR_SHARED_EPOCH_FIT '+json.dumps(dict(candidate_parent_SHA256=F.T.PIN,
        source_fit_only=True,granted=False,ROM_composed=False,outputs_written=0,
        underflow_equivalence=cases,source_projection_cases=5,
        source_projection_invalid0_or6plus_requires_actual_rejection_proof=True,
        remaining=['Current C8FF read/write/SMC domain closure and genuine cleared cold epochs',
            'Full first-auth failures, legal header mutations/cold/foreign/retire invalidations',
            'Saved outer-frame X restoration after the helper uses X as selected owner',
            'Busy NMI/IRQ, wrap and complete Mini foreign parity',
            'Root exact resource review before any owning ROM composition'],**result),separators=(',',':')),flush=True)


if __name__=='__main__':main()
