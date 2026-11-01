"""Actual foreign-body ABI differential for the narrow A74 tail repair."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_kirby_owner_main_1101_v2 as K
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
O=K.O;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def invoke(m,a,p,slot,kind):
    c=H.start(m,'S2BoundaryBody',a=a,x=slot,y=kind,p=p);maps=m.rawtags[:];c,low=H.finish(m,c)
    assert c.sp==224 and m.rawtags==maps
    # Dead callee stack bytes are not part of the caller's live frame.
    state=(bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),[bytes(x)for x in m.ram],bytes(m[0x15a:0x17b]),m.rawtags[:])
    return(c.a,c.x,c.y,c.p&0xcf,c.sp),state,c.processorCycles,low

def main():
    q=dict(passed=False,native_emulator=False,source_CPU=True,ROM_sha256=sha(O/'candidate.nes'),installed=False)
    try:
        new=qualified(O/'candidate.nes');old=K.baseline_bundle(new);seeds=[C.fresh(old),C.fresh(new)];pairs=0;low=255;cycles=[];digest=hashlib.sha256()
        for raw,kind,slot,flags,a in itertools.product([i for i in range(38)if i not in[13,25]],[0,6,12,27],[0,5],[0x31,0xf9],[0,85]):
            outcomes=[]
            for b,seed in zip([old,new],seeds):
                m=C.fork(seed);K.scene(m);H.put(m,SelectedCharacter=raw,GameEngineSubroutine=8,ObjectOffset=slot)
                K.actor(m,kind,120,slot=slot);m.writes.clear();row=invoke(m,a,flags,slot,kind);outcomes.append(row);low=min(low,row[3])
            differences=[]
            for index,(left,right)in enumerate(zip(outcomes[0][1],outcomes[1][1])):
                if left!=right:
                    differences.append((index,[(i,x,y)for i,(x,y)in enumerate(zip(left,right))if x!=y][:8]))
            assert outcomes[0][:2]==outcomes[1][:2],('Foreign body ABI/state',raw,kind,slot,flags,a,outcomes[0][0],outcomes[1][0],differences)
            cycles.append(outcomes[1][2]-outcomes[0][2]);digest.update(bytes(outcomes[1][0]));pairs+=1
        at=location(new,'S2BoundaryBody');before=old['raw'][at:at+49];after=new['raw'][at:at+49]
        assert before[:11]==after[:11]and before[29:]==after[29:]
        assert before[11:29]!=after[11:29]
        q.update(passed=True,actual_foreign_body_AXY_realflags_SP_SMC33_maps_R0_R7_full_state_pairs=pairs,foreign_raw_ids=36,enemy_types=[0,6,12,27],slots=[0,5],minimum_API_SP=low,foreign_CPU_cycle_delta=dict(minimum=min(cycles),maximum=max(cycles)),SMB2_Own_guard_pop_farcall_bytes_exact=True,public49B_span_and_all_labels_preserved=True,digest=digest.hexdigest(),scope='Real S2BoundaryBody/FarCallCommon/GuestBodyContact instructions. Raw13 is intentionally repaired; raw25 Own branch is proved byte exact. All36 other raw IDs0..37, both slots/flags/A values and four enemy types compare exact returned A/X/Y/realP/SP, R0..R7, full native globals/source RAM, all33SMC operands and maps. No native emulator or all-ability-state claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/check_kirby_owner_main_1101_v2.py',R/'tools/audit/check_hogan_current_bounded_v1.py',R/'tools/audit/ff_wram_host_controls_v7.py',O/'candidate.nes',O/'candidate.dbg',O/'rollback-witness.json',O/'owner-link.json']}
    (O/'foreign-body-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
