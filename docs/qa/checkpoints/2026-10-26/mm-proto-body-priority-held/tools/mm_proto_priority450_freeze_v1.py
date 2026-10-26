"""Freeze the one native pilot and its held physical-cadence result."""
from pathlib import Path
import argparse,hashlib,json,shutil

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PACKET=D/'mm-proto-body-priority-450-ready-v1'
SOURCE=D/'mm-proto-body-priority-v3/ready-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p,z):Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    assert not a.output.resolve().is_relative_to(R);a.output.mkdir(parents=True,exist_ok=False)
    ready=json.loads((PACKET/'readiness.json').read_text());grant=json.loads((PACKET/'ROOT-grant.json').read_text());native=json.loads((PACKET/'native-receipt.json').read_text());pair=json.loads((PACKET/'paired-review-v1/proof.json').read_text());negative=json.loads((PACKET/'deficit-review-v1/proof.json').read_text())
    assert sha(PACKET/'ROOT-grant.json')=='7d909a72298b919820570af2ed0df38504e148791126117f7813be81b75a9a80'
    assert native['passed']and native['launches']==1 and native['retries']==0 and native['worker_released']
    assert pair['native_mechanical_guards_pass']and not pair['native_no_harm_cadence_pass']and pair['matched_completed_DMA_delta']==-1
    assert negative['candidate_held']and negative['physical_prefix_deficit_frames']==[385]+list(range(437,451))
    assert not list(PACKET.glob('retry*'))
    bindings=ready['bindings']|grant['qualification_bindings']
    for p,h in bindings.items():assert sha(p)==h,p
    deps={Path(p)for p in bindings}
    deps|={p for p in PACKET.rglob('*')if p.is_file()and not p.resolve().is_relative_to(a.output.resolve())}
    deps|={SOURCE/'receipt.json',SOURCE/'catalog.json',SOURCE/'qualification.json',SOURCE/'source.zip'}
    own=[R/'tools/audit'/name for name in['mm_proto_priority450_prepare_v1.py','mm_proto_priority450_review_v1.py','mm_proto_priority450_deficits_v1.py','mm_proto_priority450_freeze_v1.py','mm_proto_priority_capacity_closure_v1.py','mm_proto_priority_capacity_closure_v2.py','mm_proto_priority_capacity_closure_v3.py']]
    deps|=set(own)
    report=R/'docs/qa/mm-proto-body-priority-native-2026-10-26.txt';capacity_report=R/'docs/qa/mm-proto-body-priority-capacity-2026-10-26.txt'
    deps|={report,capacity_report}
    shutil.copyfile(report,a.output/'report.txt');shutil.copyfile(capacity_report,a.output/'capacity-addendum.txt')
    (a.output/'tools').mkdir()
    for q in own:shutil.copyfile(q,a.output/'tools'/q.name)
    put(a.output/'all-actual-artifact-bindings.json',{str(q.resolve()):dict(bytes=q.stat().st_size,sha256=sha(q))for q in sorted(deps)})
    (a.output/'proofs').mkdir()
    for label,root,name in [('native',PACKET,'native-receipt.json'),('independent-hardware',PACKET/'review-v1','proof.json'),('paired',PACKET/'paired-review-v1','proof.json'),('deficits',PACKET/'deficit-review-v1','proof.json')]:shutil.copyfile(root/name,a.output/'proofs'/(label+'.json'))
    catalog={str(q.relative_to(a.output)).replace('\\','/'):dict(bytes=q.stat().st_size,sha256=sha(q))for q in sorted(a.output.rglob('*'))if q.is_file()}
    put(a.output/'catalog.json',catalog)
    receipt=dict(passed=True,freeze_verified=True,native_run=True,candidate_held=True,adopted=False,native_no_harm_cadence_pass=False,native_mechanical_guards_pass=True,ROM_sha256=native['ROM_sha256'],exact_actual_baseline_ROM_sha256=pair['baseline_ROM_sha256'],launches=1,retries=0,worker_released=True,completed_hardware_DMA=[402,401],paired_actual_frames=275,exact_RGB_pairs=206,visible_capture_prefix_deficit_frames=15,maximum_prefix_deficit=2,final_DMA_delta=-1,first_deficit_visible_frame=385,source_owner_and_persistent_shot_visibility_unproved=True,owned_tools=len(own),actual_artifact_bindings=len(deps),actual_artifact_bindings_sha256=sha(a.output/'all-actual-artifact-bindings.json'),catalog_files=len(catalog),catalog_sha256=sha(a.output/'catalog.json'),source_receipt_sha256=sha(SOURCE/'receipt.json'),tool_sha256=sha(__file__),limits='Positive hardware guard result preserved separately from held physical cadence/visibility acceptance. No optimization, retry, production/default/settings/Git mutation. Source qualifiers are exact00fb only; native scope is this single finite450 case.')
    put(a.output/'receipt.json',receipt)
    print(json.dumps(dict(receipt_sha256=sha(a.output/'receipt.json'),**receipt),indent=2))


if __name__=='__main__':main()
