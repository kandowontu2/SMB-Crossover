"""Move native-service save frames off the live native trampoline stack.

Two independent42B frames occupy source-dead C460..C4B4 inside the already
conditional private mutable lease. No shared byte or unconditional RAM added.
"""
import json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    prior=json.loads((O/'native-effects-v39-layout.json').read_text());negative=json.loads((O/'native-earned-Main-v41-negative.json').read_text())
    assert not negative['passed']and negative['first_SMC_stack_overlap_PC_SP_A_maps'][1]==0x7b
    source=(O/'native-effects-v39.s').read_text();before=source
    assert not any(0xc460<=int(v,16)<0xc4b4 for v in re.findall(r'\$([cC]4[0-9a-fA-F]{2})',source))
    for prefix,base in [('Award',0xc460),('Victim',0xc48a)]:
        scratch=base;smc=base+8;obj=base+41
        old=f''' ldx #7
{prefix}SaveScratch:
 lda R0,x
 pha
 dex
 bpl {prefix}SaveScratch
 lda ObjectOffset
 pha
 ldx #32
{prefix}SaveSMC:
 lda $015a,x
 pha
 dex
 bpl {prefix}SaveSMC'''
        assert source.count(old)==1,prefix
        new=old.replace(' lda R0,x\n pha',' lda R0,x\n sta $%04x,x'%scratch).replace(' lda ObjectOffset\n pha',' lda ObjectOffset\n sta $%04x'%obj).replace(' lda $015a,x\n pha',' lda $015a,x\n sta $%04x,x'%smc)
        source=source.replace(old,new,1)
        old=f''' ldx #0
{prefix}RestoreSMC:
 pla
 sta $015a,x
 inx
 cpx #33
 bne {prefix}RestoreSMC
 pla
 sta ObjectOffset
 ldx #0
{prefix}RestoreScratch:
 pla
 sta R0,x
 inx
 cpx #8
 bne {prefix}RestoreScratch'''
        assert source.count(old)==1,prefix
        new=old.replace(' pla\n sta $015a,x',' lda $%04x,x\n sta $015a,x'%smc).replace(' pla\n sta ObjectOffset',' lda $%04x\n sta ObjectOffset'%obj).replace(' pla\n sta R0,x',' lda $%04x,x\n sta R0,x'%scratch)
        source=source.replace(old,new,1)
    # Re-link all live absolute source operands; fixed helper entry addresses
    # retain the same lifetime contract while their source callees move.
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-packets-pause-v42.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-packets-main-v42.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-packets-ports-v42.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    blob,L=A.assemble('native-packets-v42',source,cfg)
    assert len(blob)==prior['body_bytes']+24 and L['DkPauseThaw']==0xd60c
    # Exact direct/indexed source fields before this successor end below460.
    # The only retained private source indirect domains are pose/OAM200..2FF,
    # native geometry800..8D8, immutable relocated descriptors and typed fruit
    # pointer400 plus length<=28. None can reach either new save packet.
    literals=sorted({int(v,16)for v in re.findall(r'\$([cC]4[0-9a-fA-F]{2})',before)})
    q=dict(prior);q.update(labels=L,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),
        private_service_frames=[dict(owner='native-source-score',half_open=[0xc460,0xc48a],R0_R7=[0xc460,0xc468],SMC33=[0xc468,0xc489],ObjectOffset=0xc489),dict(owner='native-fruit-victim',half_open=[0xc48a,0xc4b4],R0_R7=[0xc48a,0xc492],SMC33=[0xc492,0xc4b3],ObjectOffset=0xc4b3)],
        source_dead_frame_funding=dict(existing_conditional_mutable_grant=[0xc000,0xc900],new_unconditional_RAM=0,all_previous_direct_C4xx_literals=literals,typed_indexed_extent_before_packets=[0xc400,0xc457],source_indirect_domains=['OAM200..2FF; source pose destination and original renderer.','Geometry800..8D8; validated native source-format lists and pointer tables.','Typed world-fruit pointer400, recordCount<=4, length<=28.','Relocated immutable original descriptor tables.']),
        scope='Private save mechanism repair only. NativeR0..7/Object/SMC values and every source ability remain preserved;42stack bytes per service become dedicated private RAM. Full actual earned Main/IRQ/reentrancy and source state parity still require successor tests.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-effects-v39.s',O/'native-effects-v39-layout.json',O/'native-earned-Main-v41-negative.json',R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json',O/'native-packets-v42.s',O/'native-packets-v42.bin']})
    (O/'native-packets-v42-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','body_bytes','header_spare','private_service_frames']}))


if __name__=='__main__':main()
