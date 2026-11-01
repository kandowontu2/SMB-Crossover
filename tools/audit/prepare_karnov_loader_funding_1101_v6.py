"""Pure source funding for the complete Karnov loader; never edits the host.

The optional carrier remains an ownership proposal.  This transformer only
funds its genuine original copy/verify/publication path in the existing lease.
"""
import re

SAVE_SMC=''' .repeat 5,I
 .if I=0
 lda NextBank_SMC+1
 .elseif I=1
 lda SafecallA_SMC+1
 .elseif I=2
 lda FarcallJmpTarget_SMC+1
 .elseif I=3
 lda FarcallJmpTarget_SMC+2
 .else
 lda SafereturnA_SMC+1
 .endif
 pha
 .endrepeat
'''
RESTORE_SMC=''' .repeat 5,I
 pla
 .if I=0
 sta SafereturnA_SMC+1
 .elseif I=1
 sta FarcallJmpTarget_SMC+2
 .elseif I=2
 sta FarcallJmpTarget_SMC+1
 .elseif I=3
 sta SafecallA_SMC+1
 .else
 sta NextBank_SMC+1
 .endif
 .endrepeat
'''
OFFSETS='''; Same five operands, in the same push order as both original frames.
; All reside in page1. No scratch, extra stack byte, or new SMC is borrowed.
KrSavedSmcOffsets:
 .byte <(NextBank_SMC+1),<(SafecallA_SMC+1)
 .byte <(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2)
 .byte <(SafereturnA_SMC+1)
.assert >NextBank_SMC=1,error,"SMC offset page"
.assert >SafecallA_SMC=1,error,"SMC offset page"
.assert >FarcallJmpTarget_SMC=1,error,"SMC offset page"
.assert >SafereturnA_SMC=1,error,"SMC offset page"
'''


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform_sources(*,resident,helper_source,carrier=True):
    """Return source/fragments only; no filesystem access or host mutation."""
    text=resident;fragments={'kr-loader-offsets-v6.inc':OFFSETS}
    assert 'KrSavedSmcOffsets'not in text and text.count(SAVE_SMC)==2
    # Only cold loading pays for indexed save/restore.  The hot dispatcher
    # retains its original unrolled instruction stream and genuine live Y.
    for name in ['KrLoad']:
        pos=text.index(name+':\n');end=text.index(SAVE_SMC,pos)
        text=text[:end]+text[end:].replace(SAVE_SMC,f''' ldx #0
{name}SaveSmc:
 ldy KrSavedSmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne {name}SaveSmc
''',1)
    assert text.count(RESTORE_SMC)==2
    for name in ['KrLoad']:
        pos=text.index(name+'Set:\n')if name=='KrLoad'else text.index('KrDispatchRestore:\n')
        end=text.index(RESTORE_SMC,pos)
        text=text[:end]+text[end:].replace(RESTORE_SMC,f''' ldx #4
{name}RestoreSmc:
 ldy KrSavedSmcOffsets,x
 pla
 sta $0100,y
 dex
 bpl {name}RestoreSmc
''',1)
    text=once(text,''' .repeat 8,I
 lda R0+I
 pha
 .endrepeat
''',''' ldx #0
KrLoadSaveZp:
 lda R0,x
 pha
 inx
 cpx #8
 bne KrLoadSaveZp
''')
    text=once(text,''' .repeat 8,I
 pla
 sta R7-I
 .endrepeat
''',''' ldx #7
KrLoadRestoreZp:
 pla
 sta R0,x
 dex
 bpl KrLoadRestoreZp
''')
    # The public checker retains its complete two-bank cookie loop and the
    # same save frame; this is the compact iteration already used by v5 auth.
    text=once(text,''' lda CurrentBankC
 cmp #2
 beq KrCheckYes
 ldx #2
 bne KrCheckBank
''',''' ldx CurrentBankC
 dex
 cpx #1
 bne KrCheckBank
''')
    # Share the two identical cold invalidation bodies.  Their write order
    # is unchanged; only these cold sites gain one2-byte JSR return address.
    bodies=[]
    for label in ['KrInvalidate','KrFailInvalidate']:
        body=f''' ldx #3
{label}:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 dex
 cpx #1
 bne {label}
'''
        bodies.append(body);text=once(text,body,' jsr KrInvalidateBoth\n')
    invalidate=bodies[0].replace('KrInvalidate:','KrInvalidateBank:').replace(' bne KrInvalidate\n',' bne KrInvalidateBank\n')
    fragments['kr-loader-invalidate-v6.inc']='KrInvalidateBoth:\n'+invalidate+' rts\n'
    # R0 is zeroed before all32 state pages, and no reachable instruction or
    # call between that write and the end of the copy/verify loop writes R0.
    text=once(text,'''KrCopyRow:
 lda #0
 sta R0
''','''KrCopyRow:
''')
    anchor='.include "kr-pickup-rom-auth-v5.inc"'
    text=once(text,anchor,'.include "kr-loader-offsets-v6.inc"\n.include "kr-loader-invalidate-v6.inc"\n'+anchor)
    if carrier:
        text=once(text,''' lda R2
 asl
 asl
 ora #$c0
 sta R1
 jsr KrMapRow
''',''' jsr KrCarrierRowSetup
 jsr KrMapRow
''')
        assert text.count(' ldx #4\nKrCopyByte:')==1
        text=once(text,' ldx #4\nKrCopyByte:',' ldx R4\nKrCopyByte:')
        text=once(text,' sbc #4\n sta R1\n jsr KrMapRow\n ldx #4\nKrVerifyByte:',
                  ' sbc R4\n sta R1\n jsr KrMapRow\n ldx R4\nKrVerifyByte:')
        text=once(text,' cmp #8\n bne KrCopyRow',' cmp #10\n bne KrCopyRow')
        text=once(text,'''KrMapRow:
 lda #1
 sta $5130
 lda R2
 clc
 adc #<399
 sta $512b
''','''KrMapRow:
 jsr KrCarrierMap
''')
        helper='\n'.join(line for line in helper_source.splitlines()
            if not re.match(r'\s*\.(?:pushseg|popseg|segment|import|importzp)\b',line))+'\n'
        helper=helper.replace('; Place these helpers AFTER the real source-aligned water table in ROM29tail.',
                              '; Funded within existing pre-water alignment padding; water staysBB8E.')
        fragments['kr-loader-carrier-v6.inc']=helper
        text=once(text,anchor,'.include "kr-loader-carrier-v6.inc"\n'+anchor)
    def hot(t):return t[t.index('KrDispatch:\n'):t.index('KrDispatchReturn:\n')+len('KrDispatchReturn:\n rts')]
    assert hot(text)==hot(resident),'Cold funding must not change the hot dispatch source'
    return dict(resident=text,fragments=fragments,carrier_proposal=bool(carrier),
        new_scratch=[],added_stack_bytes=2,added_stack_scope='Only the two cold cookie-invalidation calls; hot dispatch frame unchanged',SMC_push_order=['NextBank+1','SafecallA+1','FarcallTarget+1','FarcallTarget+2','SafereturnA+1'],
        expected_water_address=0xbb8e,expected_lease_end=0xbfb0,
        expected_pre_align_savings=72 if carrier else 57,
        carrier_ownership_granted=False,
        limits=['Pure source transformer; full owning main-object relink/native qualification is separate.',
                'Carrier1019/1020 remains a proposal until all other consumers are closed.',
                'Hot KrDispatch remains byte-for-byte identical apart from relocated operand addresses; caller Y needs no new restore.'])
