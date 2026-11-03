"""Freeze compact private score/packet/FF-and-nested-IRQ qualification."""
import json, zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R,O=A.R,A.O


def main():
    names=['check_dkjr_native_service_ff_1102_v51.py',
        'check_dkjr_native_service_fullcuts_1102_v52.py',
        'check_dkjr_native_service_nested_1102_v53.py',
        'prepare_dkjr_native_score_tail_1102_v54.py',
        'check_dkjr_native_score_tail_1102_v55.py',
        'check_dkjr_native_score_tail_irq_1102_v56.py',
        'check_dkjr_native_score_audio_1102_v57.py',
        'check_dkjr_native_packet_domains_1102_v58.py',
        'freeze_dkjr_native_score_tail_1102_v59.py']
    sources=[R/'tools/audit'/n for n in names]
    receipts=['native-service-v51-FF-negative.json','native-service-v52-FF.json',
        'native-service-v53-nested-negative.json','native-scoretail-v54-layout.json',
        'native-scoretail-v55-CPU.json','native-scoretail-v56-deep.json',
        'native-scoretail-v56-direct.json','native-scoretail-v57-nested.json',
        'native-packet-domains-v58.json']
    for n in receipts:
        j=json.loads((O/n).read_text())
        assert bool(j['passed'])==('negative'not in n),n
        for path,digest in j.get('bindings',{}).items():
            assert A.sha((R/path).read_bytes())==digest,('stale frozen input',n,path)
    generated=[O/n for n in receipts]
    for stem,version in [('native-scoretail',54),('native-domains',58)]:
        generated += [O/f'{stem}-v{version}.{ext}'for ext in ['s','cfg','bin','lbl']]
        generated += [O/f'{stem}-{kind}-v{version}.bin'for kind in ['pause','main','ports']]
    archive=O/'native-score-tail-v59-inputs.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(set(sources+generated)):
            rel=p.relative_to(R).as_posix();data=p.read_bytes();z.writestr(rel,data)
            members.append(dict(path=rel,bytes=len(data),SHA256=A.sha(data)))
    q=json.loads((O/'native-scoretail-v54-layout.json').read_text());L=q['labels']
    direct=json.loads((O/'native-scoretail-v56-direct.json').read_text())
    nested=json.loads((O/'native-scoretail-v57-nested.json').read_text())
    domain=json.loads((O/'native-packet-domains-v58.json').read_text())
    assert direct['actual_interrupts']==dict(IRQ=725,lagNMI=725)
    assert nested['actual_interrupts']==dict(nestedIRQ=4044) and nested['minimum_ISR_SP']==128
    out=dict(passed=True,status='FROZEN_PRIVATE_LOCAL_SCORE_TAIL_AND_PACKET_QUALIFICATION',
        qualified=False,ROM_written=False,installed=False,native_owner_admitted=False,shared_mutation=False,
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,
        archive_SHA256=A.sha(archive.read_bytes()),members=members,
        source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=A.sha(p.read_bytes()))for p in sources],
        assembly=dict(body_bytes=q['body_bytes'],body_end=L['DkjrComponentEnd'],header_spare=0xbfe0-L['DkjrComponentEnd'],
            metadata_end=L['DkNativePortsEnd'],metadata_spare=0xd800-L['DkNativePortsEnd'],pause_thaw=L['DkPauseThaw'],
            actual_vector_entries=38,implemented_rows=q['implemented_vector_rows'],unfinished_rows=q['unimplemented_rows'],
            conditional_private_service_packet=[0xc460,0xc4bb],existing_pending_amount=0xc8f9,new_unconditional_RAM=0),
        descriptive_correction=dict(path='native-scoretail-v54-layout.json',field='metadata_spare',
            inherited_historical_value=136,current_label_derived_value=133,
            explanation='Frozen54 copied an old descriptive spare count while relinking Main+3B; exact code, metadata_endD77B, labels and all proofs use the current layout. This manifest derives the actual133B spare and leaves earlier proof inputs immutable.'),
        proven=['Source point-kind and popup publication remains at originalEC3F; genuine native AddToScore/HUD executes after donor phase returns, before same owning Main returns/nativeAI. No shared posthook or source mechanic change.',
            '144direct native/source point cases and248paired completeGameCore epochs preserve original/private actor state, native application boundary/AXYP/maps, exactHUD/score bytes, both native score owners,400+800score,60D1AEupdates and nextnormal thaw.',
            'Conservative compiledCFG over3625instructions/42declared native+typedfruit roots proves maximumone original point publication perMain.26packet sites/32nearby indexed sites and23translatedindirect sites have bounded source-backed domains; fresh clears pending and all actualMain returns consume it.',
            '725independent actualIRQ and725genuineFFlagNMI service PC/A/C/I shapes preserve source/private/R0..7/SMC/native state. Collector includesI1 forNMI; reached service fixture has0I1shapes. Every lag incrementsNmiSkipped once and excludes regularNMI.',
            '4044independent actualnativeIRQs inside genuineFFlag/audio across capture1/firsthit2/terminalhit61/normal-thaw62 preserve all continuation state. Minimum nestedSP128; only three source-bound outer sound clocks mayadvance.'],
        retained_negatives=[dict(path='native-service-v51-FF-negative.json',kind='oracle incomplete',detail='Genuine PlaySmackEnemy+6 STA07D8 was not in initial finite writer list; corrected by52 source binding.'),
            dict(path='native-service-v53-nested-negative.json',kind='real runtime SMC overwrite',minimum_actual_SP=118,
                detail='Old immediate score stack at foregroundA645/SP144 permits lag-audio IRQ to overwrite0176..017A. Negative outer summary minimum_SP255 is uninitialized because failure precedes return; exact actual118 is preserved inside its error witness. Local54tail removes this depth.')],
        immutable_prior_inputs=[dict(manifest='docs/qa/checkpoints/2026-11-03/dkjr-native-services-v50/manifest.json',
            archive_SHA256='9d5a804e3f038ccb86a92f92635e1dab8e9531a74923274ae0f2d03e6f2d8f1d',
            purpose='Frozen36..50 source/compiled dependencies and prior41/43/47negatives; do not rehydrate whole predecessor tree.')],
        remaining=['17typed APIs remain unfinished; no functional/public admission for CLR fallback rows. Actual raw40 fullbox/contact/item/bounce/nativeHUD/menu/portrait caller gates still need source-funded current routing proof.',
            'Latest Prince/Bub/Sunny fingerprints, real payload-derived cookie/twoheader coldcopy/retire/scene/current-owner ISR rebind are mandatory. Existing shared fixtures remain historicalv65 matchingheader models, not the latest proposedPrince115.',
            'Full actor Main/draw/ceiling/powerup/life ISR regressions on final linked payload and actual native menu/gameplay/idlecadence remain pending root queue.',
            'No native SMB fruit/vine/helper placements yet.15px donor jump retained; native helper-assisted1-1 still needs resource proposal/location inventory and root verification. SharedDKportrait/focused-onlySelect are deliberate initial limitations.'],
        scope='Private existing resource lease only; no physicalROM/shared/menu mutation/install/native-emulator qualification. Exact legal typed-input domains and declared synchronous API ownership; arbitrary internal-label calls or poisoned private pointers are not admitted.')
    (O/'native-score-tail-v59.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in['passed','status','archive_bytes','archive_SHA256','assembly','descriptive_correction']}))


if __name__=='__main__':main()
