"""Unplaced hidden-head fit measurement only; no composer or ROM mutation."""
from hashlib import sha256
import json

import replay_smb2_hidden_oneup_1113 as Route
from compose_metal_head_bridge_1112 import assemble_segments


def once(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after)


def measure(raw):
    assert sha256(raw).hexdigest()==Route.PIN
    _,b,_=Route.inputs(raw);W=Route.W;Owner=Route.Current.Flag
    _,current,info=Owner.source_recipe(raw)
    old=current['probe'];assert len(old)==174 and raw[Owner.PROBE_AT:Owner.PROBE_AT+174]==old
    source=Owner.Check.SOURCE.read_text().split('.segment "S2_FLAG_WORLD"')[0]
    names=('R0','R2','R4','R5','R6','R7','S2X','S2Y','S2Page','S2YPage','S2ProbeDirection',
        'S2HeadX','S2HeadPage','S2HeadY','S2Math0','S2DF011','S2DF055','GetBlockBufferAddr','MTileAttribute','S2VY')
    constants={n:W.address(b,n)for n in names}
    baseline,labels=assemble_segments(source,{'S2_FLAG_PROBE':0xb128},constants)
    assert baseline['S2_FLAG_PROBE']==old
    factored=once(source,' lda R6\n sta R2\n lda R6\n sec',' sta R2\n sec')
    index_old=''' lda R5
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda R4
 lsr
 lsr
 lsr
 lsr
 ora R0'''
    index_new=''' lda R5
 lsr
 lda R4
 ror
 lsr
 lsr
 lsr
 pha
 and #$10
 sta R0
 pla'''
    factored=once(factored,index_old,index_new)
    shared='S2FlagSharedReturn:\n rts'
    # Strict leaf-ABI inline design: source owner survives on the old stack;
    # temporaryX distinguishes empty hidden queries from ordinary solids.
    inline=once(factored,' cmp #$60\n beq ProbeEmpty\n tay',''' cmp #$60
 bne HiddenNormalTile
 txa
 bne ProbeEmpty
 lda S2VY
 bpl ProbeEmpty
 bmi HiddenCacheGate
HiddenNormalTile:
 tay''')
    inline=once(inline,' lda S2ProbeDirection\n cmp #2\n bcs ProbeSolid',''' ldx #$ff
HiddenCacheGate:
 lda S2ProbeDirection
 cmp #2
 bcs HiddenReturnMode''')
    inline=once(inline,'ProbeSolid:\n lda #$ff\n bne ProbeResult','''HiddenReturnMode:
 txa
 bne ProbeResult
 sec
 bcs ProbeResult''')
    inline_code,inline_labels=assemble_segments(inline,{'S2_FLAG_PROBE':0xb128},constants)
    # A cold helper is reached only for60; normal tiles gain no helper call.
    main=once(factored,' cmp #$60\n beq ProbeEmpty\n tay',''' cmp #$60
 bne HiddenNormalTile
HiddenHelperCall:
 jsr S2HiddenHeadHelper
 sec
 bcs ProbeEmpty
HiddenNormalTile:
 tay''')
    helper='''.segment "S2_HIDDEN_HELPER"
S2HiddenHeadHelper:
 txa
 bne HiddenDone
 lda S2VY
 bpl HiddenDone
 lda S2ProbeDirection
 cmp #2
 bcs HiddenDone
 lda R4
 sta S2HeadX
 lda R5
 sta S2HeadPage
 lda R2
 sta S2HeadY
HiddenDone:
 rts
'''
    origins={'S2_FLAG_PROBE':0xb128,'S2_HIDDEN_HELPER':0}
    preliminary,_=assemble_segments(main+helper,origins,constants)
    padding=174-len(preliminary['S2_FLAG_PROBE']);assert padding>=0
    main=once(main,shared,' nop\n'*padding+shared)
    code,newlabels=assemble_segments(main+helper,origins,constants)
    assert len(code['S2_FLAG_PROBE'])==174 and newlabels['S2FlagSharedReturn']==0xb1d5
    changes=[]
    for i,(a,c)in enumerate(zip(old,code['S2_FLAG_PROBE'],strict=True)):
        if a!=c:
            at=Owner.PROBE_AT+i
            if changes and changes[-1][0]+changes[-1][1]==at:changes[-1][1]+=1
            else:changes.append([at,1])
    return dict(passed=True,ROM_SHA256=Route.PIN,current_probe_file=Owner.PROBE_AT,
        current_probe_SHA256=sha256(old).hexdigest(),current_probe_hex=old.hex(),
        strict_inline=dict(bytes=len(inline_code['S2_FLAG_PROBE']),
            shortfall=len(inline_code['S2_FLAG_PROBE'])-174,
            shared_return=inline_labels['S2FlagSharedReturn'],placeable=False),
        unplaced_cold_helper_plan=dict(main_bytes=174,helper_bytes=len(code['S2_HIDDEN_HELPER']),
            main_hex_with_UNBOUND_zero_helper_operand=code['S2_FLAG_PROBE'].hex(),
            helper_hex=code['S2_HIDDEN_HELPER'].hex(),
            helper_must_be_same_PRG118=True,helper_address_UNGRANTED=True,
            helper_call_operand_file=Owner.PROBE_AT+newlabels['HiddenHelperCall']-0xb128+1,
            shared_return=newlabels['S2FlagSharedReturn'],padding=padding,
            main_changed_ranges=changes,
            relocated_internal_labels={n:[labels[n],newlabels[n]]for n in labels if n in newlabels and labels[n]!=newlabels[n]},
            generated_source_SHA256=sha256((main+helper).encode()).hexdigest()),
        safe_factoring='Remove two duplicate LDA R6; form the same index with ROR while preserving original R0 and flags',
        intended_60_cache_gate='Only original X0, negative sourceVY, direction0/1; return still empty/C1/Y unchanged',
        all_non60_oracle_and_interrupt_gates_PENDING=True,
        source_candidate_ROM=False,composer_created=False,ROM_mutations=0,new_RAM_bytes=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    print(json.dumps(measure(Route.Post.Owner.NIGHTLY.read_bytes()),separators=(',',':')),flush=True)
