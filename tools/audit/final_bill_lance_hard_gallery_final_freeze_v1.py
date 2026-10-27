"""Freeze the finite two-identity gallery, preserving both historical FALSEs."""
from pathlib import Path
import argparse,json,shutil
from final_bill_lance_hard_gallery_source_v1 import D,ROOT,SHA,sha,put
from final_item_abilities_remaining731_run_v1 import verify_manifest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--public',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);a.public=a.public.resolve();a.public.mkdir(parents=True,exist_ok=False)
    ready=D/'final-bill-hard-v5-qualified-lance-ready-v2';post=D/'final-lance-hard-v5-postrun-v1';body=D/'final-bill-hard-v5-body-review-correction-v1'
    native=D/'final-bill-lance-hard-gallery-ready-v5/profiles/lance-hard/native'
    assert sha(native/'proof.json')=='afc53f44b536ec8d9521f698237be5c22c9dd5e8f8352926cd32dd318f2df60b'
    actual=json.loads((native/'proof.json').read_text());reparse=json.loads((post/'proof.json').read_text())
    assert actual['passed']and actual['worker_released']and actual['launches']==1 and actual['retries']==0 and actual['dependencies_unchanged']
    assert reparse['offline_schema_local_comparison_passed']and reparse['original_host_aggregate_passed']and len(reparse['native_cases'])==7
    assert reparse['hardware']==dict(complete256DMAs=3540,startFrame_epochs=4366,scoped_enables=3205,late_scoped_enables=0)
    assert reparse['PPU']['frames']==4367 and reparse['cadence']['entries']==3860 and reparse['cadence']['finishes']==3859
    assert json.loads((body/'proof.json').read_text())['passed']
    report=ROOT/'docs/qa/final-bill-lance-gallery-status-2026-10-26.txt'
    files={Path(__file__),report,ready/'proof.json',ready/'ROOT-grant-lance-hard.json',ready/'ROOT-review.json',native/'proof.json',post/'proof.json',post/'manifest.json',body/'proof.json',body/'manifest.json',ROOT/'tools/audit/final_bill_lance_hard_gallery_postrun_v3.py',ROOT/'tools/audit/final_bill_gallery_body_review_correction_v1.py'}
    # Root review filename is optional metadata; do not invent its availability.
    files={f for f in files if f.exists()}
    bindings={Path(z['path']):z['sha256']for z in json.loads((post/'manifest.json').read_text())['bindings']}
    assert verify_manifest(post/'manifest.json')==1361
    for f in files:bindings[f]=sha(f)
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=h,bytes=f.stat().st_size)for f,h in sorted(bindings.items())]))
    put(a.output/'proof.json',dict(freeze_complete=True,ROM_sha256=SHA,additional_native_launches=0,total_v5_native_launches=2,
        launches_per_identity=1,retries=0,all_workers_released=True,seven_legal_cases_per_identity=True,total_actual_completed_stages=56,
        Bill_original_host_aggregate_FALSE_retained=True,Bill_additive_typed_empty_plan_full_collector_passed=True,
        Lance_original_host_aggregate_PASS=True,Lance_proof_sha256=sha(native/'proof.json'),Lance_additive_full_collector_sha256=sha(post/'proof.json'),
        actual_Lance_outcomes=reparse['native_cases'],Lance_hardware=reparse['hardware'],Lance_PPU=reparse['PPU'],Lance_cadence=reparse['cadence'],
        native_variant_and_mode='Actual cold-menu Lance1/Hardnumeric1 readback; Bill0/Hard1 separately retained.',
        agent_visual_review=dict(whole_frame_placements=35,sheets=[str(post/'whole-frame-review-1.png'),str(post/'whole-frame-review-2.png')],
            finding='Lance red variant/firing poses, sampled gun effects/contact/terrain coherent. Selected capsule overwrites WORLD/TIME exactly as Bill. No all-frame cleanliness claim. Earlier Bill-body misread explicitly corrected by standalone/crop/CPU-DMA proof.'),
        remaining_product_issue='Confirmed Bill/Lance selected capsule/header overlap; private exact3b HUD candidate9d296d is source-only and excluded from these native tests.',
        scope='Controlled staged-mature physical-item grants/autoequip/passiveRapid, actual input/fire/contact/source requests/terrain/natural expiry. No block rise/random campaign acquisition, waveform fidelity, paired baseline lag or full-route claim.',
        manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings)))
    payload={'Lance-original-native-PASS.json':native/'proof.json','Lance-outcomes-and-reparse.json':post/'proof.json','final-component-proof.json':a.output/'proof.json',
        'external-evidence-bindings.json':a.output/'manifest.json','Lance-exact-plan-types.json':post/'plan-type-differences.json',
        'Lance-actual-birth-speed-cadence.json':post/'actual-speed-cadence-vs-compiled-source.json','Lance-negative-controls.json':post/'offline-negative-controls.json',
        'Lance-whole-frame-review-1.png':post/'whole-frame-review-1.png','Lance-whole-frame-review-2.png':post/'whole-frame-review-2.png',
        'Lance-image-provenance.json':post/'review-files.json','current-consolidated-report.txt':report,'Bill-additive-body-correction.json':body/'proof.json'}
    rows=[]
    for name,f in payload.items():
        target=a.public/name;shutil.copyfile(f,target);assert sha(f)==sha(target);rows.append(dict(path=name,source=str(f),sha256=sha(f),bytes=f.stat().st_size))
    owned=[Path(__file__),ROOT/'tools/audit/final_bill_lance_hard_gallery_postrun_v3.py',report]
    (a.public/'OWNED-FILES.txt').write_text('\n'.join(str(f.relative_to(ROOT)).replace('\\','/')for f in owned)+'\n'+str(a.public.relative_to(ROOT)).replace('\\','/')+'/\n',encoding='utf-8')
    (a.public/'README.txt').write_text('Exact3b finite Hard Bill/Lance controlled-use qualification; no ROM/source install. Lance fresh single native launch PASS/all7cases/28stages; worker released. Bill prior host FALSE remains raw, exact two-empty-plan-type offline correction passes. Historical cold-settle FALSE also retained. Native control includes already-mature staged physical items, source gun exclusivity/autoequip/passiveRapid, render/sourceSFX requests/contact/ground/natural cleanup and full256DMA timing.35 Lance whole-frame samples reviewed; capsule/header overlap remains real. Bill body claim corrected additively: actual crop identical, no defect demonstrated. No waveform, native rise/random acquisition campaign or global no-lag claim. Raw lossless/ROM/emulator/settings/large native JSON are excluded; exact external bindings state local reproduction limits.\n',encoding='utf-8')
    put(a.public/'REVIEW-FILES.json',dict(native_receipt='Lance-original-native-PASS.json',actual_outcomes='Lance-outcomes-and-reparse.json',visual=['Lance-whole-frame-review-1.png','Lance-whole-frame-review-2.png'],scope_and_correction='current-consolidated-report.txt'))
    put(a.public/'manifest.json',dict(ROM_sha256=SHA,payloads=rows,stable_owned_files=[dict(path=str(f.relative_to(ROOT)).replace('\\','/'),sha256=sha(f),bytes=f.stat().st_size)for f in owned],freeze_sha256=sha(a.output/'proof.json')))
    print(json.dumps(dict(freeze_complete=True,proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),public_manifest_sha256=sha(a.public/'manifest.json'),public_bytes=sum(f.stat().st_size for f in a.public.rglob('*')if f.is_file()))))


if __name__=='__main__':main()
