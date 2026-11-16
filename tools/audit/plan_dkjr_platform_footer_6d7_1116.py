"""Detached platform-only footer fit over source6d7; no proposed code executes."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_carry_camera_components_1116 as K
import check_dkjr_platform_contact_funding_1113 as Funding

C,N,Route=K.C,K.N,K.Route
H=lambda value:sha256(value).hexdigest()
LAYOUT=dict(RYU=(0xb963,27),NATIVE=(0xb97e,60),POLICY=(0xb707,11),GENERIC_A=(0xbd5b,26),GENERIC_B=(0xbdd5,26))

# This is assembled only into independent small fragments. It is never
# overlaid on a ROM or CPU bus by this module.
SOURCE='''Selected=$6002
PlayerVY=$8e
PlayerState=$1e
Passenger=$0566
Footer=$065b
EnemyY=$be
SavedA=$016a
TargetLo=$016c
TargetHi=$016d
Far=$015a
LPC=$b453
Timer=$074a
.segment "RYU"
RyuBridge:
 lda Selected
 cmp #10
 bne RyuNative
 lda #$54
 sta TargetLo
 lda #$b8
 sta TargetHi
 lda #$96
 jsr Far
 bcc Done
RyuNative:
 jmp $9a2c
.segment "NATIVE"
Dispatch:
 lda Selected
 cmp #40
 bne Generic
 jsr Descending
 bcs Generic
 txa
 cmp Passenger,x
 bne Generic
 lda Footer
 ; A normal DK footer is nativeY+30. Exclude nativeY0/1 and wrapped
 ; off-bottom envelopes. This admitted CMP suppliesC1 for ADC#1 below.
 cmp #32
 bcc Generic
 pha
 ; NES ADC#1 with admittedC1 adds exactly2; PHA does not alterC.
 adc #1
 bcs Native
 cmp EnemyY,x
 bne Native
 sta Footer
Native:
 jsr LPC
 pla
 sta Footer
Done:
 rts
Generic:
 lda #<GenericWorker
 sta TargetLo
 lda #>GenericWorker
 sta TargetHi
 lda #$ba
 jmp Far
.segment "POLICY"
Descending:
 lda PlayerVY
 bmi No
 ; Native0/2 can both represent a normal donor passenger; vine3 cannot.
 lda PlayerState
 lsr
 rts
No:
 sec
 rts
.segment "GENERIC_A"
GenericWorker:
 lda Selected
 cmp #11
 bcc Slow
 lda Timer
 bne Slow
 jmp LPCFar
Slow:
 jsr $bf5c
 jsr LPCFar
 jmp FinishWorker
.segment "GENERIC_B"
FinishWorker:
 sta SavedA
 jmp $bf83
LPCFar:
 lda #$53
 sta TargetLo
 lda #$b4
 sta TargetHi
 lda #$80
 jmp Far
'''


def at(bank,pc):return 16+bank*8192+(pc&8191)


def detached(candidate):
    assert H(candidate)==C.CANDIDATE
    import recover_dkjr_current_identity_67_1115 as Identity
    for offset,old in Identity.PUBLIC_NATIVE:
        assert candidate[offset:offset+len(old)]==old
    # Actual current source-owned live prefixes and all52 reclaimable EA
    # tails, including same-bank and standard encoded far/vector consumers.
    # This routine assembles original source/preimages only; no overlay.
    leaves=Funding.sources(candidate)
    linked=Funding.H.T.assemble(SOURCE,LAYOUT)
    assert linked['used']==dict(RYU=27,NATIVE=60,POLICY=10,GENERIC_A=24,GENERIC_B=21)
    rows=[]
    packed=linked['images']['RYU']+linked['images']['NATIVE']
    for bank,pc,size,new,role in((0,0xb963,87,packed,'resident selector and Ryu compaction'),
            (0,0xb43f,3,bytes.fromhex('207eb9'),'sole RunLargePlatform JSR operand'),
            (0,0xb707,11,linked['images']['POLICY'].ljust(11,b'\xea'),'resident current sole-policy-call span'),
            (58,0xbd5b,26,linked['images']['GENERIC_A'].ljust(26,b'\xea'),'retired prepare tail'),
            (58,0xbdd5,26,linked['images']['GENERIC_B'].ljust(26,b'\xea'),'retired finish tail')):
        offset=at(bank,pc);old=candidate[offset:offset+size]
        assert len(old)==len(new)==size
        rows.append(dict(role=role,physical_PRG=bank,CPU_half_open=[pc,pc+size],
            file_half_open=[offset,offset+size],old_hex=old.hex(),old_SHA256=H(old),
            proposed_hex=new.hex(),proposed_SHA256=H(new),
            changed_bytes=sum(a!=b for a,b in zip(old,new))))
    bank=candidate[16:8208];refs=[]
    for i in range(len(bank)-2):
        target=bank[i+1]+256*bank[i+2]
        if bank[i]in(0x20,0x4c) and 0xb963<=target<0xb9ba and not 0xb963<=0xa000+i<0xb9ba:
            refs.append([0xa000+i,bank[i],target])
    assert refs==[[0xb43f,0x20,0xb98e],[0xb483,0x20,0xb963]],refs
    tuples=[];far=[];prg=candidate[16:1048592]
    for target in range(0xb963,0xb9ba):
        needle=bytes((target&255,target>>8,0x80))
        begin=0
        while True:
            pos=prg.find(needle,begin)
            if pos<0:break
            tuples.append([target,pos+16]);begin=pos+1
        standard=bytes((0xa9,target&255))+bytes.fromhex('8d6c01')+bytes((0xa9,target>>8))+bytes.fromhex('8d6d01a980')
        if standard in prg:far.append(target)
    assert tuples==[[0xb97c,484603],[0xb9a8,3998],[0xb9a8,621502],[0xb9b9,910064]] and not far,(tuples,far)
    assert candidate[484595:484614]==bytes.fromhex('b97a7d1d427c9d427cb9807d9d667cb9867d9d')
    # A8(TAY)/B9(LDA abs,Y)/80(low address), not a native target tuple.
    assert candidate[3994:4005]==bytes.fromhex('c903b00da8b980af9de806')
    assert candidate[621496:621511]==bytes.fromhex('2a2a29030503a8b980bd05049d2a5c')
    music=(C.R/'audio/full-roster/full-0b.bin').read_bytes()
    assert len(music)==8192 and candidate[16+111*8192:16+112*8192]==music
    literal_notes=[dict(file=484603,classification='PRG59 STA operand crosses LDA abs,Y opcode/operand'),
        dict(file=3998,classification='TAY then LDA AF80,Y opcode and low operand'),
        dict(file=621502,classification='TAY then LDA BD80,Y opcode and low operand'),
        dict(file=910064,classification='unchanged complete audio/full-roster/full-0b.bin bank, frame data not a native function descriptor',
            full_bank_SHA256=H(music))]
    assert bank[0x1483:0x1489]==bytes.fromhex('2063b9a60d60')
    assert bank[0x143f:0x144a]==bytes.fromhex('208eb9ad4a07d0032089b4')
    assert candidate[at(0,0xb707):at(0,0xb712)]==bytes.fromhex('ad0260c90bad4a0760eaea')
    policy_refs=[];policy_tuples=[];policy_far=[]
    for target in range(0xb707,0xb712):
        for i in range(len(bank)-2):
            if bank[i]in(0x20,0x4c) and bank[i+1]+256*bank[i+2]==target:
                policy_refs.append([0xa000+i,bank[i],target])
        if bytes((target&255,target>>8,0x80))in prg:policy_tuples.append(target)
        needle=bytes((0xa9,target&255))+bytes.fromhex('8d6c01')+bytes((0xa9,target>>8))+bytes.fromhex('8d6d01a980')
        if needle in prg:policy_far.append(target)
    assert policy_refs==[[0xb992,0x20,0xb707]] and not policy_tuples and not policy_far,(policy_refs,policy_tuples,policy_far)
    gap_cases=0
    for footer in range(256):
        for plane in range(256):
            total=footer+1+1 # successful same-slot CMP suppliesC1.
            admitted=footer>=32 and total<256 and (total&255)==plane
            assert admitted==(footer>=32 and plane-footer==2)
            gap_cases+=1
    return dict(parent_source_candidate_SHA256=C.CANDIDATE,
        source_SHA256=H(SOURCE.encode()),used=linked['used'],labels=linked['symbols'],
        spans=rows,owned_bytes=sum(r['file_half_open'][1]-r['file_half_open'][0] for r in rows),
        leaf_tail_preimage_and_ingress=leaves,same_bank_native_consumers=refs,
        standard_farcall_consumers=far,raw_tuple_occurrences=tuples,literal_classification=literal_notes,
        old_policy_consumers=policy_refs,policy_native_tuples=policy_tuples,policy_standard_farcall=policy_far,
        exact_nonwrapping_gap_formula_cases=gap_cases,
        old_policy_only_consumer_B992_replaced=True,new_RAM=0,new_carrier=0,new_cookie=0,
        proposed_code_executed=False,ROM_composed=False,output_files=0,
        unresolved='Ryu27 shares an existing resident RTS with the footer branch; Ryu28 reference A/NZCV and intermediate SMC actual-caller/ISR liveness must be requalified on owning image after a separate source lease. Previous-passenger rising-zero and stale-flag lifecycle proof remains required before leasing this descending-only selector; nativeVY alone is not the predicate.')


def formulas(candidate):
    _,seed=Route.cold(candidate)
    whole,labels=C.Plan.source_inputs()
    assert ' adc #15\n sta WAnchorY\n'in whole
    native_source=(C.R/'src/zelda2_link_platform.s').read_text()
    assert 'Native:pla\n sec\n sbc #32\nStore:sta Player_Y_Position\n'in native_source
    bbox_at=N.location(seed.bundle,'BoundBoxCtrlData')
    table=candidate[bbox_at:bbox_at+12]
    assert table==bytes((2,8,14,32,3,20,13,32,2,20,14,32))
    body=C.payload(candidate)
    a=whole.index('DkFullBox:');z=whole.index('DkGraphics:',a)
    fragment=whole[a:z]
    local=set(__import__('re').findall(r'^(\w+):',fragment,__import__('re').M))
    defs=C.Plan.numeric(whole)+''.join(f'{name}=${pc:x}\n'for name,pc in labels.items()if name not in local)
    linked=Funding.H.T.assemble(defs+'.segment "BOX"\n'+fragment,dict(BOX=(labels['DkFullBox'],200)))
    code=linked['images']['BOX'];pc=labels['DkFullBox']
    assert bytes(seed.ram[2][pc&8191:(pc&8191)+len(code)])==code
    rows=[]
    for native_y in (32,107,109,176):
        m=K.prepare(seed,delta=0)
        N.put(m,Player_Y_Position=native_y,Player_Y_HighPos=1)
        m.ram[2][0x8fe]=2;m.ram[2][0x6b]=m.ram[2][0x6c]=1
        assert K.private(m,0xb24c).p&1
        assert m.ram[2][0x210]==native_y+15
        K.private(m,pc)
        dk=list(m[0x658:0x65c]);assert dk[3]==native_y+30,(native_y,dk)
        for control in (0,1,2):
            N.put(m,SprObject_Rel_XPos=80,SprObject_Rel_YPos=native_y,SprObj_BoundBoxCtrl=control)
            N.invoke(m,'BoundingBoxCore',x=0,y=0)
            mario=list(m[0x658:0x65c]);assert mario[3]==native_y+32
        rows.append(dict(native_Y=native_y,imported_source_Y=m.ram[2][0x210],
            DK_body=dk,Mario_footer=native_y+32,platform_snap_plane=native_y+32,gap=2))
    return dict(actual_unchanged_candidate_CPU=True,source_only=True,
        native_table_file=bbox_at,native_table_hex=table.hex(),
        FullBox_PC=pc,FullBox_bytes=len(code),FullBox_SHA256=H(code),rows=rows,
        proposed_footer_code_executed=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent',type=Path,required=True)
    ap.add_argument('--formulas',action='store_true')
    ap.add_argument('--compact',action='store_true')
    args=ap.parse_args()
    parent=args.parent.read_bytes();candidate,_=C.proposal(parent)
    assert C.inverse(candidate)==parent
    report=detached(candidate)
    if args.formulas:report['actual_formula_check']=formulas(candidate)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    display=encoded
    if args.compact:
        display=json.dumps(dict(full_receipt_SHA256=H(encoded.encode()),
            source_SHA256=report['source_SHA256'],used=report['used'],owned_bytes=report['owned_bytes'],
            spans=[{k:v for k,v in row.items()if k not in('old_hex','proposed_hex')}for row in report['spans']],
            proposed_code_executed=False,ROM_composed=False,output_files=0),sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_DETACHED '+display,flush=True)
    print('DKJR_FOOTER_DETACHED_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
