"""Freeze compact DK lifecycle/encoding proofs and the actual Main negative."""
import json,zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    receipts=['native-powerup-v29-IRQ.json','native-lifecycle-v30-layout.json','native-lifecycle-v31-CPU.json','native-branches-v32-layout.json','native-branches-v33-CPU.json','native-branches-v33-vector.json','native-branches-v33-display.json','native-branches-v33-powerup.json','native-branches-v33-lifecycle.json']
    proofs={n:json.loads((O/n).read_text())for n in receipts};assert all(q['passed']for q in proofs.values())
    negative=json.loads((O/'native-main-boundary-v34.json').read_text());assert not negative['passed']and negative['negative']['epoch']==0
    names=['check_dkjr_powerup_interrupts_1102_v29.py','prepare_dkjr_native_lifecycle_1102_v30.py','check_dkjr_native_lifecycle_1102_v31.py','prepare_dkjr_native_branches_1102_v32.py','check_dkjr_native_branches_1102_v33.py','check_dkjr_native_main_boundary_1102_v34.py','freeze_dkjr_native_lifecycle_1102_v35.py']
    sources=[R/'tools/audit'/n for n in names]
    generated=receipts+['native-main-boundary-v34.json']
    for stem,version in [('native-lifecycle',30),('native-branches',32)]:
        generated += [f'{stem}-v{version}.{ext}'for ext in ['s','cfg','bin','lbl']]
        generated += [f'{stem}-{part}-v{version}.bin'for part in ['pause','main','ports']]
    paths=sources+[O/n for n in generated]
    archive=O/'native-lifecycle-v35-inputs.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(set(paths)):
            rel=p.relative_to(R).as_posix();data=p.read_bytes();z.writestr(rel,data)
            members.append(dict(path=rel,bytes=len(data),SHA256=A.sha(data)))
    q=proofs['native-branches-v32-layout.json'];irq=proofs['native-powerup-v29-IRQ.json'];lifecycle=proofs['native-lifecycle-v31-CPU.json']
    prior=O/'native-ingress-v28.json';frozen=json.loads(prior.read_text())
    out=dict(passed=True,status='FROZEN_PRIVATE_LIFECYCLE_AND_BRANCH_ENCODING_PROOFS_WITH_MAIN_NEGATIVE',ROM_written=False,native_owner_admitted=False,shared_mutation=False,
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=A.sha(archive.read_bytes()),members=members,
        source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=A.sha(p.read_bytes()))for p in sources],
        immutable_prior_inputs=dict(checkpoint_manifest=prior.relative_to(R).as_posix(),manifest_SHA256=A.sha(prior.read_bytes()),archive=frozen['archive'],archive_SHA256=frozen['archive_SHA256'],note='Use exact existing compactv28/v20/v10 inputs only; no recursive archive extraction.'),
        assembly=dict(body_bytes=q['body_bytes'],body_end=q['body_end'],header_spare=q['header_spare'],metadata_end=q['metadata_end'],metadata_spare=q['metadata_spare'],actual_vector_entries=38,implemented_rows=q['implemented_vector_rows'],unfinished_rows=q['unimplemented_rows']),
        proven=dict(actual_nested_powerup_IRQ_lagNMI_returns=irq['actual_IRQ_and_lagNMI_returns'],independent_deepest_stack_controls=irq['independent_deepest_stack_controls'],minimum_ISR_SP=irq['minimum_ISR_SP'],lifecycle=lifecycle['checks'],conditional_instructions_shortened=q['shortened_branches'],private_bytes_recovered=q['bytes_recovered'],all_flag_encoding_cases=proofs['native-branches-v33-CPU.json']['full_flag_condition_encoding_cases'],semantic_source_normalization_exact=True,all_existing_source_native_controls_unchanged=True),
        actual_Main_negative=negative['negative'],
        scope='Only source/CPU private overlays. Historicalv65 owner matching-cookie fixture, never final payload authentication or current-Prince rebind. Actual Main negative is retained: unfinished head/side callbacks return incomingA and native terrain interprets it as a metatile, shifting idleX40to47. This does not weaken or waive admission checks.',
        remaining=['Wire/qualify remaining21 typed APIs and actual native head/side/fullbox/contact/pickup ingress.','Complete source fruit/hit/point/hanging art readers and bounded native OAM, authored worldfruits/vines/helper traversal.','Final latest-Prince/current-Bub/Sunny owner fingerprints, actual complete cold/lifecycle/IRQ and payload-derived full cookie/header proof.','No shared/public/menu/ROM/install grant; root retains all native emulator qualification.'])
    (O/'native-lifecycle-v35.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','status','archive_bytes','archive_SHA256','assembly','actual_Main_negative']}))


if __name__=='__main__':main()
