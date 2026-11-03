"""Compact private terrain/art/earned-Main/native-stack milestone, no admission."""
import json,zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    names=['prepare_dkjr_native_terrain_ports_1102_v36.py','check_dkjr_native_terrain_ports_1102_v37.py','prepare_dkjr_native_atlas_1102_v38.py','prepare_dkjr_native_effects_1102_v39.py','check_dkjr_native_effects_1102_v40.py','check_dkjr_native_earned_main_1102_v41.py','prepare_dkjr_native_service_packets_1102_v42.py','check_dkjr_native_service_packets_1102_v43.py','check_dkjr_native_drop_boundary_1102_v44.py','prepare_dkjr_native_defeat_leaf_1102_v45.py','check_dkjr_native_defeat_leaf_1102_v46.py','check_dkjr_native_service_irq_1102_v47.py','prepare_dkjr_native_register_packets_1102_v48.py','check_dkjr_native_register_packets_1102_v49.py','freeze_dkjr_native_services_1102_v50.py']
    sources=[R/'tools/audit'/n for n in names]
    receipts=['native-terrain-v36-layout.json','native-terrain-v37-Main.json','native-terrain-v37-CPU.json','native-atlas-v38.json','native-effects-v39-layout.json','native-effects-v40-CPU.json','native-earned-Main-v41-negative.json','native-packets-v42-layout.json','native-packets-v43-Main-negative.json','native-drop-boundary-v44.json','native-defeat-v45-layout.json','native-service-v47-IRQ-negative.json','native-registers-v48-layout.json','native-registers-v49-CPU.json','native-registers-v49-qualified.json','native-registers-v49-IRQ.json','native-registers-v49-Main-CPU.json']
    for name in ['native-terrain-v37-CPU.json','native-effects-v40-CPU.json','native-drop-boundary-v44.json','native-registers-v49-CPU.json']:assert json.loads((O/name).read_text())['passed']
    for name in ['native-earned-Main-v41-negative.json','native-packets-v43-Main-negative.json','native-service-v47-IRQ-negative.json']:assert not json.loads((O/name).read_text())['passed']
    generated=receipts+[f'native-art-{p}-v38.chr'for p in [959,960,961]]
    for stem,version in [('native-terrain',36),('native-effects',39),('native-packets',42),('native-defeat',45),('native-registers',48)]:
        generated += [f'{stem}-v{version}.{ext}'for ext in ['s','cfg','bin','lbl']]
        generated += [f'{stem}-{part}-v{version}.bin'for part in ['pause','main','ports']]
    paths=sources+[O/n for n in generated]
    archive=O/'native-services-v50-inputs.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(set(paths)):
            rel=p.relative_to(R).as_posix();data=p.read_bytes();z.writestr(rel,data);members.append(dict(path=rel,bytes=len(data),SHA256=A.sha(data)))
    q=json.loads((O/'native-registers-v48-layout.json').read_text());proof=json.loads((O/'native-registers-v49-CPU.json').read_text())
    out=dict(passed=True,status='FROZEN_PRIVATE_NATIVE_SERVICES_EARNED_MAIN_AND_RETAINED_NEGATIVES',ROM_written=False,native_owner_admitted=False,shared_mutation=False,
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=A.sha(archive.read_bytes()),members=members,
        source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=A.sha(p.read_bytes()))for p in sources],
        immutable_prior_inputs=[dict(manifest='build/dkjr-native-source-1102-v2/native-lifecycle-v35.json',manifest_SHA256=A.sha((O/'native-lifecycle-v35.json').read_bytes()),archive_SHA256=json.loads((O/'native-lifecycle-v35.json').read_text())['archive_SHA256']),dict(manifest='docs/qa/checkpoints/2026-11-02/dkjr-source-core-v1/manifest.json',purpose='Read only1728B original atlas and pose metadata from the existing compact checkpoint; never restore its whole build tree.')],
        assembly=dict(body_bytes=q['body_bytes'],body_end=q['body_end'],header_spare=q['header_spare'],metadata_end=q['metadata_end'],metadata_spare=q['metadata_spare'],actual_vector_entries=38,implemented_rows=q['implemented_vector_rows'],unfinished_rows=q['unimplemented_rows'],conditional_private_service_packet=[0xc460,0xc4bb],new_unconditional_RAM=0),
        proven=['Real nativeGameCore86idle/walk/jump updates match original private phase after genuine fixed native head/side query ports;900architecturalAXYP/scratch/private controls.','Original2176B body/hangingBG/falling/hit/point art packed in granted3pages. All legal8x16read ranges avoid cold/helper code;6144pixel/30capacity controls and nativeHuDraw/stablezeroheader pass.','Actual wholeGameCore62epochs earns fruit drop/native victim defeat,400+800points,60originalD1AEupdates and nextnormal thaw. Earned sourcehit/timers are not seeded.','Native raw40drop boundary144cases has onlyInvDropEnemy side effect; dedicatedprivateleaf preserves it before genuine unchanged lower-fixedShellOrBlockDefeat+3.192fullserviceAXYP/nativeRAM/private/maps cases pass.','Dedicated91B conditional source-dead save packets repair actual foreground and lag-NMI stack negatives. Actual deepestIRQ/lagNMI returns and fullMain/servicecontinuations pass.'],
        retained_negative_paths=['native-earned-Main-v41-negative.json','native-packets-v43-Main-negative.json','native-service-v47-IRQ-negative.json'],
        stack_scope=dict(minimum_foreground_SP=proof['deepest_actual_IRQ']['minimum_foreground_SP'],minimum_ISR_SP=proof['deepest_actual_IRQ']['minimum_ISR_SP'],warning='Only deepest fixture IRQ/lagNMI controls, not complete changed-instruction/audio/lifetime certification.'),
        remaining=['17private vector APIs remain unfinished; source-safe CLR rows must not be called functional before actual-caller proof. Raw40 fullbox/contact/rare-pickup/bounce shared ingress still needs exact source-funded proposal and root grant.','Dedicated C460..C4BB packet writer/reader/reentrancy/lifetime and full changed-instruction ISR/audio-state closure remain pending final qualification.','Status/menu/portrait/cold/life/stage/select integration must preserve source identity and documented sharedDKportrait/focused-only policy. Nativeworldfruit/vine/helper placement and assisted1-1 remain unqualified.','Final current Prince/Bub/Sunny fingerprints and full payload-derived cookies/twoheader coldcopy must rebind; all current shared CPU fixtures are historicalv65 matching-cookie models.','No shared/public/menu/ROM/install grant or native-emulator/playable claim. Root owns the sole Mesen queue.'],
        scope='Stable compact source/private CPU milestone. Exact existing private resource lease only, no physical cartridge bytes or other agent outputs changed.')
    (O/'native-services-v50.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','status','archive_bytes','archive_SHA256','assembly','stack_scope']}))


if __name__=='__main__':main()
