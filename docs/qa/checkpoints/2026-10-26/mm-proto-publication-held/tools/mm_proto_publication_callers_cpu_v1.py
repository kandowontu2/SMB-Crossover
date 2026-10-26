"""Publication experiment through genuine post-draw Main/release/NMI/next frame."""
from pathlib import Path
import argparse,hashlib,itertools,json,traceback
import mm_proto_body_priority_callers_v3 as real
import mm_proto_publication_render_cpu_v2 as render
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['parent','candidate','output']:ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
    old,new=[scoped_load(p)for p in[a.parent,a.candidate]]
    real.partition=render
    try:
        for variant,display,mask,first,star,irqflag in itertools.product([0,1],[0,64],[0,15],[0,112],[0,9],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,display=display,types=[mask>>i&1 for i in range(4)],first=first,star=star,irqflag=irqflag,flags=0x20)
            c,m,left=real.continuation(old,cfg);d,n,right=real.continuation(new,cfg)
            assert left['draw_return']==right['draw_return'],('Original draw ABI',cfg,left['draw_return'],right['draw_return'])
            assert(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks))==(d.pc,d.a,d.x,d.y,d.p&207,d.sp,tuple(n.banks)),('Full caller live boundary',cfg)
            assert n[render.STATE]==(display^64),('Actual regular acknowledgement',cfg,n[render.STATE])
            allowed=set(range(0x100,0x300))|{render.STATE,address(old,'RgOamRotation'),address(old,'GuestOamRotationActive')}
            diff=[(at,list.__getitem__(m,at),list.__getitem__(n,at))for at in range(0x8000)if at not in allowed and list.__getitem__(m,at)!=list.__getitem__(n,at)]
            assert not diff,('Actual caller RAM/SMC/HW leaked',cfg,diff[:20])
            assert len(left['trace'])==len(right['trace'])
            for x,y in zip(left['trace'],right['trace']):
                assert(x['pc'],x['bank'],x['writes'])==(y['pc'],y['bank'],y['writes']),('Continuation route/application stores',cfg,x,y)
            rows.append(dict(cfg=cfg,original_draw_return=left['draw_return'],live_boundary=[c.pc,c.a,c.x,c.y,c.p&207,c.sp],actual_regular_NMI=right['actual_NMI'],state_before=display,state_after=n[render.STATE],caller_cycles_delta=right['cycles']-left['cycles'],allocation={name:[m[address(old,name)],n[address(new,name)]]for name in ['RgOamRotation','GuestOamRotationActive']}))
        (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
        proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),actual_postdraw_Main_release_NMI_next_GameLoop_cases=len(rows),original_draw_and_live_caller_full_AXYP_SP_banks_exact=True,all_other_application_RAM_SMC_Hardware_exact=True,postdraw_control_flow_and_ordered_writes_exact=True,
                   explicit_differences=['physical OAM image','GuestOamRotationActive','RgOamRotation','new MmPublicationState5FF8'],dead_stack_only_excluded=True,actual_regularNMI_consumes_one_completed_owned_tag=True,
                   cycle_delta=[min(r['caller_cycles_delta']for r in rows),max(r['caller_cycles_delta']for r in rows)],
                   limits='Synthetic true compiled Main/release/NMI/next frame with actual controller reads. Physical PPU/DMA/visibility/cadence not modeled.',tool_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
    except BaseException as e:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),completed=len(rows)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise

if __name__=='__main__':main()
