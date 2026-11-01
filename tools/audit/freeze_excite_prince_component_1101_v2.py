"""Freeze the compact Excitebike component; Prince remains an art-only audit."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'build/excite-prince-component-1101-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    report=json.loads((O/'review.json').read_text());assert report['passed']
    for p,h in report['bindings'].items():assert sha(R/p)==h,p
    controls=json.loads((O/'component-CPU-controls.json').read_text())
    sequence=json.loads((O/'source-sequencing-CPU-controls.json').read_text())
    art=json.loads((O/'source-art.json').read_text())
    assert controls['passed']and controls['actor_component_cases']==2304
    assert sequence['passed']and sequence['frames']==1020 and sum(sequence['replaced_calls'].values())==14281
    assert {q['source_pose']for q in art['poses']}==set(range(23))
    selected=[R/'tools/audit/excite_prince_component_1101_v2.py',Path(__file__).resolve(),R/'tools/reference/excitebike_original_cpu_1101_v2.py',R/'tools/reference/excitebike_component_1101_v2.md',R/'tools/audit/thomas_original_cpu_1031_v1.py',R/'tools/audit/verify_native_relocation.py']
    selected+=[O/n for n in ['review.json','component-CPU-controls.json','source-sequencing-CPU-controls.json','compile.json','excitebike-component.s','component.cfg','component.bin','component.lbl','source-art.json','excitebike-body-patterns.bin','source-poses.png','prince-source-audit.json','prince-fixed-entry-disassembly.txt','prince-body-patterns.bin','prince-source-body.png']]
    # Discovery PC histograms, regenerated RAM states and object files are disposable.
    # No donor ROM, full PRG, complete source trees or per-frame capture forests.
    hashes={p.relative_to(R).as_posix():sha(p)for p in selected}
    target=O/'source-and-proof.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in selected:z.write(p,p.relative_to(R).as_posix())
        z.writestr('component-file-hashes.json',json.dumps(hashes,indent=2)+'\n')
    handoff=dict(status='EXCITEBIKE_ORIGINAL_ASSEMBLY_REVIEW_COMPONENT_NO_HOST_UNLOCK',source_CPU_only=True,native=False,installed=False,archive=dict(path=target.relative_to(R).as_posix(),sha256=sha(target),bytes=target.stat().st_size,members=len(selected)+1),excitebike=dict(donor_sha256=controls['donor_sha256'],code_bytes=controls['component_code_bytes'],table_bytes=controls['table_bytes'],explicit_differential_cases=2304,actual_donor_sequencing_frames=1020,actual_component_replacement_calls=14281,all23_pose_indices=True,patterns=154,pattern_bytes=2464,host_zero_page_preserved=True,limitations=controls['limits']+sequence['limitations']),prince=dict(status='FIXED_ENTRY_AND_HISTORICAL_BODY_AUDIT_ONLY',source_actor_assembled=False,native_rerun=False,installed=False,opaque_body_pixels=262,original_packet_extent=[16,40],limits='Not part of Excitebike movement proof. No Prince actor/input/animation recovery or gameplay claim.'),integration_notes='tools/reference/excitebike_component_1101_v2.md',next='Root reviews this compact packet, allocates selected-owner code/state/CHR, defines explicit side-view terrain/input adapter, then qualifies actual native dispatch/menu/controller play before a nightly unlock.',bindings=hashes)
    (O/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n')
    print(json.dumps(dict(passed=True,archive=str(target),bytes=target.stat().st_size,members=len(selected)+1,sha256=sha(target))))

if __name__=='__main__':main()
