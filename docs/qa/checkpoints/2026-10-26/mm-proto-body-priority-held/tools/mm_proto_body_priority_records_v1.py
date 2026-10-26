"""Complete original Mega pose-index band and all six ordinary shot kinds."""
from pathlib import Path
import argparse,hashlib,itertools,json,traceback
import mm_proto_body_priority_partition_v6 as fixture
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['parent','candidate','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
    try:
        old,new=[scoped_load(q)for q in[a.parent,a.candidate]]
        poses=[];start=address(old,'METASPRITE_MM_HAIR_STAND')
        for index in range(48):
            names=[name for name in old['syms']if name.startswith('METASPRITE_MM_')and '::'not in name and address(old,name)==start+index]
            assert names,('No genuine pose name',index,start+index)
            poses.append(sorted(names)[0])
        for pose,face,outlines,first in itertools.product(poses,[1,2],[0,1],[0,112]):
            cfg=dict(entry='DrawAllMetasprites',pose=pose,variant=0,face=face,outlines=outlines,first=first,types=[1,2,5,6],flags=0x61)
            c,m,_,info=fixture.run(old,cfg,reference=True);d,n,_,extra=fixture.run(new,cfg)
            assert fixture.outcome(c,m)==fixture.outcome(d,n),('Pose reference mismatch',cfg)
            f,fm,_,plain=fixture.run(old,cfg)
            assert(f.a,f.x,f.y,f.p&207,f.sp)==(d.a,d.x,d.y,d.p&207,d.sp),('Pose original ABI mismatch',cfg,(f.a,f.x,f.y,f.p&207,f.sp),(d.a,d.x,d.y,d.p&207,d.sp))
            assert[v for at,v in fm.writes if 0x200<=at<0x300]==[v for at,v in n.writes if 0x200<=at<0x300],('Pose ordered original OAM values/count mismatch',cfg)
            rows.append(dict(tag='all48Mega_pose_band',cfg=cfg,body_record_stores=len(extra['body_writes']),delta=d.processorCycles-f.processorCycles))
        for variant,kind,face,age,first in itertools.product([0,1],range(1,7),[1,2],[0,1,15,255],[0,112]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,face=face,types=[kind]*4,age=age,first=first,flags=0xa3)
            c,m,_,info=fixture.run(old,cfg,reference=True);d,n,_,extra=fixture.run(new,cfg)
            assert fixture.outcome(c,m)==fixture.outcome(d,n),('Shot reference mismatch',cfg)
            f,fm,_,plain=fixture.run(old,cfg)
            assert(f.a,f.x,f.y,f.p&207,f.sp)==(d.a,d.x,d.y,d.p&207,d.sp),('Shot original ABI mismatch',cfg)
            assert[v for at,v in fm.writes if 0x200<=at<0x300]==[v for at,v in n.writes if 0x200<=at<0x300],('Shot ordered original OAM values/count mismatch',cfg)
            rows.append(dict(tag='all6shot_types_both_variants',cfg=cfg,delta=d.processorCycles-f.processorCycles))
        proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),cases=len(rows),Mega_original_pose_band=[start,start+47],all48Mega_pose_indices_both_faces_outlines=True,all6shot_types_both_variants_faces_ages=True,complete_independent_reference_state_and_unmodified_parent_registers_ordered_OAM_values_count_exact=True,maximum_own_cycle_delta=max(r['delta']for r in rows),checker_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');(a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');print(json.dumps(proof,indent=2))
    except BaseException as error:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(error),traceback=traceback.format_exc(),completed_cases=len(rows),checker_sha256=sha(__file__)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
