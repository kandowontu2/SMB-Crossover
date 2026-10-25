"""Bind an independently verified private candidate and reviewable source patch."""
from pathlib import Path
import difflib,hashlib,json,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/level-variants-candidate-agent';C=O/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    native=json.loads((O/'native-verification.json').read_text());cpu=json.loads((O/'component-verification.json').read_text());build=json.loads((O/'build.json').read_text());prep=json.loads((O/'preparation.json').read_text())
    assert native['passed']and cpu['passed']
    assert all(sha(R/n)==h for n,h in prep['source_before'].items()),'Main source changed; do not silently rebase'
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==h for m,h in prep['parent_ROMs'].items())
    assert cpu['ROMs']=={m:sha(C/f'build/smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
    assert all(z['ROM_sha256']==cpu['ROMs'][z['mapper']]and z['passed']for z in native['cases'])
    assert sha(R/'docs/qa/level-layout-audit-2026-10-22.md')=='1432919b6cebb61cbc190ebaf63f5ede4404bb5ac4678a1c31e6b5e82351b9ec'
    patch=[]
    for name,h in build['modified_files'].items():
        assert sha(C/name)==h
        old=(R/name).read_text().splitlines(keepends=True)if(R/name).exists()else[]
        new=(C/name).read_text().splitlines(keepends=True)
        patch+=difflib.unified_diff(old,new,fromfile='a/'+name if old else'/dev/null',tofile='b/'+name)
    (O/'implementation.patch').write_text(''.join(patch))
    reject=dict(fixture_rejections={'native-coin-mmc3':'Did not establish coherent active game mode/task; rejected arena setup, not an attributed game regression.','native-coin-mmc3-b':'Same incoherent mode/task, trace retained. Corrected fixture passes in final18.','native-lift-mmc3-a':'Did not initialize stage timer; rejected incomplete arena setup.'},candidate_failures_fixed={'initial-lift-failures':'Actual compiled counter alias and native passenger-wrap failures, with pre-fix ROMs.','native-lift-mmc3-b':'Valid native rising-wrap passenger teleport witness; fixed final fixture passes both mappers.'})
    (O/'rejected-and-fixed-witnesses.json').write_text(json.dumps(reject,indent=2)+'\n')
    files={}
    for name in ['build.json','preparation.json','implemented-cell-contract.json','component-verification.json','native-verification.json','full-parser-differences.json','spawn-differences.json','helper-swept-bound-proof.json','implementation.patch','rejected-and-fixed-witnesses.json']:
        p=O/name;files[p.relative_to(R).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
    for n in build['modified_files']:
        p=C/n;files[p.relative_to(R).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
    for m in('mmc3','mmc5'):
        for suffix in('','-baseline'):
            for ext in('nes','dbg','lbl','map'):
                p=C/f'build/smb-crossover-{m}{suffix}.{ext}';files[p.relative_to(R).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
    note=R/'docs/qa/level-layout-implementation-2026-10-22.md';files[note.relative_to(R).as_posix()]=dict(bytes=note.stat().st_size,sha256=sha(note))
    for n in('build_level_variants_agent.py','level_variants_source.s','verify_level_variants_agent.py','native_level_variants_agent.py','level_variant_coin_native_agent.lua','level_variant_lift_native_agent.lua','freeze_level_variants_agent.py'):
        p=R/'tools/audit'/n;files[p.relative_to(R).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
    manifest=dict(status='PRIVATE_AUTHORED_LEVEL_CANDIDATE_VERIFIED_NOT_ADOPTED',parent_checkpoint=prep['parent_checkpoint'],parent_manifest_sha256=prep['parent_manifest_sha256'],ROMs=cpu['ROMs'],source_overlay=build['modified_files'],source_patch='build/verification/level-variants-candidate-agent/implementation.patch',component_cases=cpu['cases'],native_cases=len(native['cases']),new_RAM_bytes=0,cold_span='physical1A A000..A587;1416B; assembler bound A800',reserved_parent_cold='A800..BBFF',native_bbox_gate_insertion='After level_lift_bridges.inc, before old130B DrawSmallPlatform padding; bank0 BE8E..BEBC,47B on both current mappers',original_audit_unchanged=True,main_source_and_ROMs_unchanged=True,files=files,limits=cpu['limits'],goal_complete=False)
    (O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(status=manifest['status'],cases=cpu['cases'],native_cases=len(native['cases']),manifest_sha256=sha(O/'manifest.json'))),flush=True)
if __name__=='__main__':main()
