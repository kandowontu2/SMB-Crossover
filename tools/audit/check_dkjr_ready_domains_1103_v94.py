"""Close compiled Ready aliases against source-bound finite index domains.

This is a private instruction-domain proof, not a global host-writer census.
The separately tested native interrupts/imports remain external obligations.
"""
import collections
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A

R,O=A.R,A.O


def main():
    prior=json.loads((O/'native-ready-domains-v93-census.json').read_text())
    source=(O/'native-entrance-v89.s').read_text()
    for rel,digest in prior['bindings'].items():assert A.sha((R/rel).read_bytes())==digest,rel
    def exact(text):
        assert source.count(text)==1,text
    # Stage/profile is fixed by both constructors before any phase/query. The
    # original initializer starts clearing at53 and cannot clear profile4A.
    exact('D_ca84: ; original $CA84: ldx #$53\n ldx #$53\nD_ca86: ; original $CA86: sta $00,x\n sta $c000,x')
    assert source.count(' sta $c04a\n')==2
    exact('DkConstruct:\n lda #1\n sta $c04a')
    exact(' lda #1\n sta $c04a\n sta $c0a0\n sta $c0b0')
    exact(' lda $c04a\n cmp #1\n bne DkjrNativePhaseReject')
    for pc in ['e8db','e927','e979']:
        at=source.index('D_'+pc+':');part=source[at:at+700]
        assert ' lda $c04a' in part and ' sec\n' in part and ' sbc #$01' in part and ' asl a' in part and ' tax' in part
    exact(' ldx #6\nPublish:\n lda #0\n sta $c8c0,x\n lda #$40\n sta $c8c8,x\n lda #$80\n sta $c8d0,x\n lda #$c8\n sta $c8c1,x\n sta $c8c9,x\n sta $c8d1,x\n dex\n dex\n bpl Publish')
    exact('DkjrUseNativeGeometry:\n ; Three typed source-format lists, each at most15inclusive rectangles and\n ; FF sentinel, occupy C800/40/80. Validate every record before publishing.\n ldy #0')
    exact(' iny\n iny\n iny\n iny\n tya\n and #$3f\n cmp #60\n bcc Validate\n lda $c800,y\n cmp #$ff\n bne Reject')
    exact('ValidList:\n tya\n and #$c0\n clc\n adc #$40\n tay\n cpy #$c0\n bne Validate')
    exact('DkjrNativeWorldBuild:\n lda #0\n sta WCount\n sta WError\n ldx WKind\n lda ListOffsets,x\n sta StoreRect+1\n sta StoreEnd+1')
    exact('ListOffsets:.byte $40,$40,$80,0,0')
    exact('PublishEnd:\n ldy WCount\n lda #$ff\nStoreEnd:\n sta $c800,y\n rts')
    exact('AppendRect:\n ldy WCount\n cpy #60\n bcc :+\n lda #1\n sta WError\n rts\n:\n ldx #0\nCopyRect:\n lda WL,x\nStoreRect:\n sta $c800,y\n iny\n inx\n cpx #4\n bne CopyRect\n sty WCount\n rts')
    exact('DkFullBoxCopy:\n txa\n and #1\n asl\n tay\n lda $c5fc,x\n clc\n adc WLeft,y\n sta BoundingBox_UL_Corner,x\n dex\n bpl DkFullBoxCopy\n ldx #0\n sec\n rts')
    # Exact finite branch machines underlying the loops above. No per-case
    # fixture files and no arbitrary-call permission for internal source PCs.
    validation=[]
    for page in [0,64,128]:
        for count in range(16):
            record=[page+4*i+j for i in range(count)for j in range(4)]
            sentinel=page+count*4
            assert max(record+[sentinel])<=188
            validation.extend(record+[sentinel])
    writes=[]
    for offset in [0,64,128]:
        for count in range(0,60,4):writes.extend(0xc800+offset+count+i for i in range(4))
        writes.extend(0xc800+offset+count for count in range(0,61,4))
    assert max(writes)==0xc8bc and 0xc8fe not in writes
    domains=[]
    for row in prior['possible_indexed_ready_aliases']:
        z=dict(row);base=z['base'];op=z['operation']
        if base in [0xc8c0,0xc8c1,0xc8c8,0xc8c9,0xc8d0,0xc8d1]:
            assert z['mode']=='abx' and op in ['LDA','STA']
            indexes=[0] if op=='LDA' else [0,2,4,6]
            reason='Profile1 fixes getterX=(1-1)*2=0; publisherX6/4/2/0.'
        elif base in [0xc800,0xc801,0xc802,0xc803] and op!='STA':
            assert z['mode']=='aby';indexes=list(range(0,189,4))
            # Last sentinel reads onlyC800; conservative other fields remain
            # belowC8C0 even with index188, so the same bound suffices.
            reason='Three64B lists,15records+sentinel; Y<=188.'
        elif base==0xc800 and op=='STA':
            assert z['mode']=='aby';indexes=list(range(61))
            reason='Low-byte SMC baseC800/C840/C880; count0..60, recordcopy0..59.'
        elif base==0xc8e4:
            assert op=='LDA'and z['mode']=='abx';indexes=list(range(4));reason='CopyRectX0..3.'
        elif base==0xc8e8:
            assert op=='ADC'and z['mode']=='aby';indexes=[0,2];reason='FullBoxX3..0 mapsY=(X&1)*2.'
        else:raise AssertionError(('unclassified Ready alias',z))
        maximum=base+max(indexes)+(128 if base==0xc800 and op=='STA' else 0)
        assert maximum<0xc8fe
        z.update(index_domain=indexes,last_possible_address=maximum,excludes_Ready=True,source_bound=reason)
        domains.append(z)
    assert len(domains)==21
    # Direct writers and readers are already decoded from all42 compiled
    # roots. Bind their semantic guards to the same source, not old labels.
    assert collections.Counter(z['operation']for z in prior['ready_writers'])=={'STA':2,'INC':1}
    exact(' lda #1\n sta $c8fe\n sec\n rts')
    exact('DkNativeReset:\n jsr DkPauseThaw\n lda #0\n sta $c8fe\n sec\n rts')
    exact(' jsr DkjrNativeImportAnchor\n bcc DkAnchorNo\n jsr DkjrNativeCameraSync\n inc $c8fe')
    for name in ['DkNativeDeathStart','DkNativeDeath','DkFullBox','DkNativeMature']:
        exact(name+':\n lda $c8fe\n cmp #2')
    assert ' lda $c8fe\n cmp #2\n bne DkBounceNo' in source
    assert ' lda $c8fe\n cmp #2\n jne BodyDrawDone' in source
    exact('DkNativePickup:\n lda $c8fe\n cmp #2\n beq DkPickupReady')
    exact('DkNativeAnchorReady:\n lda $c8fe\n cmp #2\n beq DkAnchorYes\n cmp #1\n bne DkAnchorNo\n lda GameEngineSubroutine\n cmp #8\n bne DkAnchorNo')
    assert len(prior['inherited_original_SMC_indirect_sites'])==23
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        compiled_instruction_count=prior['compiled_reachable_instructions'],compiled_roots=42,
        exact_direct_Ready_readers=8,exact_direct_Ready_writers=3,
        indexed_aliases_closed=domains,validated_list_index_cases=len(validation),maximum_geometry_write=max(writes),
        original_translated_indirect_sites=23,indirect_domain_excludes_Ready=prior['inherited_indirect_domains'],
        remaining_external_obligations=['NewReady2 real native IRQ/FF/nested continuations','Fresh/scene/reset/retirement populated pause lifecycle','Final stable Prince manager rebind'],
        scope='All42 compiled public/world roots: eight direct readers use exact0/1/2 semantics; onlyConstruct1/Reset0/first-validAnchorINC publishReady. Every21 possible absolute-indexed alias is source-bounded belowC8FE, including mutable low-byte geometry stores; unchanged23 original indirect sites retain frozen58 finite fruit/render/descriptor domains. Cold worker clearsReady only while overlay invalid/forcedblank/interruptsdisabled. This is private-state source closure, not a global host-writer census, shared grant or native admission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),O/'native-ready-domains-v93-census.json',O/'native-entrance-v89.s',O/'native-entrance-v89.bin',O/'native-entrance-v92-CPU.json']})
    (O/'native-ready-domains-v94-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','compiled_instruction_count','compiled_roots','exact_direct_Ready_readers','exact_direct_Ready_writers','maximum_geometry_write','remaining_external_obligations']}))


if __name__=='__main__':main()
