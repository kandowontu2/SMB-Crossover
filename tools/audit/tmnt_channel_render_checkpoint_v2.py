"""Prepare a bounded text-only70ba rollback checkpoint; no Git/native mutation."""
from pathlib import Path
import argparse
import ast
import difflib
import hashlib
import json
import shutil
import subprocess
from tmnt_native_storage_driver import ROOT,CURRENT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
FINAL='70ba4f682723e62b00ef4278c19e3b898383d2903ce6ad6b35199816748217de'
NATIVE='27c28c6936396fdb226d09d611ed02198b1d0cf73034bf1938972c13942eba35'
SOURCE='a2b3cdf6f24801bb5541770d59fc8fd1b12f729df6b399b3606b8c0f8ca65f1c'
CHECKPOINT=ROOT/'docs/qa/checkpoints/2026-10-26/tmnt-channel-render-held'


def js(path):return json.loads(path.read_text())


def hashes(folder):
    return {p.relative_to(folder).as_posix():sha(p)for p in folder.rglob('*')if p.is_file()and'__pycache__'not in p.parts}


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=CHECKPOINT);a=p.parse_args()
    out=a.output.resolve();assert out==CHECKPOINT.resolve()and not out.exists()
    final=D/'tmnt-equipment-channel-ready-v1';native=D/'tmnt-equipment-channel-native-result-v1'
    assert sha(final/'receipt.json')==SOURCE and sha(native/'receipt.json')==NATIVE
    assert js(final/'receipt.json')['ROM_sha256']==FINAL and js(native/'receipt.json')['candidate_ROM_sha256']==FINAL
    assert sha(ROOT/'build/smb-crossover-mmc5-expanded.nes')==CURRENT
    checkpoint_root=ROOT/'docs/qa/checkpoints/2026-10-26'
    parser=checkpoint_root/'tmnt-parser-source-held';renderer=checkpoint_root/'render-lifecycle-holds/tmnt'
    remote=git('rev-parse','@{upstream}').decode().strip();remote_ref=git('rev-parse','--abbrev-ref','--symbolic-full-name','@{upstream}').decode().strip()
    assert git('merge-base','--is-ancestor','1f35997',remote)==b''
    dependencies={}
    def published(path,expected=None):
        name=path.relative_to(ROOT).as_posix();blob=git('show',f'{remote}:{name}')
        actual=hashlib.sha256(blob).hexdigest();assert actual==sha(path),(name,'Working dependency differs from pushed blob')
        if expected:assert actual==expected,(name,'Dependency hash differs from frozen source')
        dependencies[name]=dict(sha256=actual,bytes=len(blob),git_commit=remote)
        return actual
    # Complete pinned baseline650 plus published31-file parser and5-file
    # renderer overlays reconstruct the exact668-member8d602 source tree.
    base_folder=D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/source'
    base=hashes(base_folder);assert len(base)==650
    prior_parser=parser/'packets/tmnt-parser-tail-writers-ready-v1'
    parser_bind=js(prior_parser/'source-bindings.json');parser_changes=js(prior_parser/'changed-source-versus-50b5.json')
    for path in [parser/'root-review.json',prior_parser/'source-bindings.json',prior_parser/'changed-source-versus-50b5.json']:
        published(path)
    virtual=dict(base)
    for name,change in parser_changes.items():
        assert virtual.get(name)==change['before_sha256'];published(parser/'changed-source'/name,change['after_sha256']);virtual[name]=change['after_sha256']
    assert virtual==parser_bind and len(virtual)==666
    published(renderer/'receipt.json','ce0ff605c45df40cfb58d2763706b2ea7cddd3b955e62a49c9659bb4f2785614')
    for path in [renderer/'source-bindings.json',renderer/'changed-source-versus-1d741.json']:published(path)
    render_changes=js(renderer/'changed-source-versus-1d741.json')
    for name,change in render_changes.items():
        assert virtual.get(name)==change['before_sha256'];published(renderer/'source'/name,change['after_sha256']);virtual[name]=change['after_sha256']
    renderer_bind=js(renderer/'source-bindings.json');assert virtual==renderer_bind and len(virtual)==668
    target_bind=js(final/'source-bindings.json');assert hashes(final/'source')==target_bind and len(target_bind)==670
    changes={n:dict(before_sha256=virtual.get(n),after_sha256=h)for n,h in target_bind.items()if virtual.get(n)!=h}
    assert not(set(virtual)-set(target_bind))
    expected={'src/tmnt.s','src/tmnt_equipment_draw.s','src/tmnt_equipment_shot_scope.s',
              'src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_source_channel_owner.s'}
    assert set(changes)==expected
    out.mkdir(parents=True);origins={}
    def put(name,path,kind):
        assert path.is_file();data=path.read_bytes();data.decode('utf-8');assert b'\x00'not in data
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        origins[name]=dict(classification=kind,origin=str(path),origin_sha256=sha(path))
    def generated(name,value,kind):
        path=out/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');origins[name]=dict(classification=kind,generated=True)
    patch=''
    old_source=D/'tmnt-equipment-emitter-ready-v1/source'
    for name,change in sorted(changes.items()):
        put('source/'+name,final/'source'/name,'exact_incremental_source')
        original=old_source/name
        assert (sha(original)if original.exists()else None)==change['before_sha256']
        patch+=''.join(difflib.unified_diff(original.read_text().splitlines(True)if original.exists()else[],(final/'source'/name).read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
        virtual[name]=sha(out/'source'/name)
    assert virtual==target_bind,'Full670-member restoration must be byte-exact'
    (out/'review-versus-8d602.patch').write_text(patch,encoding='utf-8');origins['review-versus-8d602.patch']=dict(classification='generated_source_review',generated=True)
    generated('incremental-source.json',changes,'source_restore_manifest')
    generated('pushed-parent-dependencies.json',dict(upstream_ref=remote_ref,upstream_commit=remote,dependencies=dependencies),'published_parent_bindings')
    generated('baseline50b-source-bindings.json',base,'pinned_baseline_source_manifest')
    put('source-bindings-70ba.json',final/'source-bindings.json','complete_target_source_manifest')
    for name in ['receipt.json','qualification.json','reporting-errata.json','retained-negatives.json']:
        put('source-qualification/'+name,final/name,'source_CPU_qualification')
    for name,row in js(final/'qualification.json')['proofs'].items():
        path=Path(row['path']);assert sha(path)==row['sha256']and js(path)['passed'];put('source-proofs/'+name+'/proof.json',path,'source_CPU_proof')
    for name in ['receipt.json','easy-strict-proof.json']:
        put('native-result/'+name,native/name,'actual_native_result_STRICT_FAIL')
    put('reports/source-70ba.txt',final/'report.txt','source_report')
    put('reports/native-70ba.txt',native/'report.txt','native_report_STRICT_FAIL')
    # Exact reporter2 is executable source. Invalid1 is retained as TEXT so it
    # cannot be mistaken for a runnable audit tool or break Python discovery.
    reporter=native/'tools/tmnt_equipment_channel_native_report_v2.py';ast.parse(reporter.read_text())
    put('frozen-tools/tmnt_equipment_channel_native_report_v2.py',reporter,'working_reporter_exact')
    bad=native/'tools/tmnt_equipment_channel_native_report_v1.py'
    try:ast.parse(bad.read_text())
    except SyntaxError as e:error=dict(type='SyntaxError',line=e.lineno,message=e.msg)
    else:raise AssertionError('Retained invalid first reporter unexpectedly parses')
    put('retained-invalid/tmnt_equipment_channel_native_report_v1.py.failed.txt',bad,'invalid_reporter_NOT_RUNNABLE')
    generated('retained-invalid/classification.json',dict(artifact='tmnt_equipment_channel_native_report_v1.py.failed.txt',sha256=sha(bad),
        error=error,stage='Reporter parse before any output; no emulation or game mutation',
        replacement='../../frozen-tools/tmnt_equipment_channel_native_report_v2.py',
        performance_verdict_unchanged=True,do_not_execute_or_count_as_native_ROM_failure=True),'tooling_negative_classification')
    # Summary contains captured timing/source metadata and hashes; no raw OAM
    # pages, screenshots, ROM/NSF/sample bytes, replay streams or video captures.
    cases=js(native/'deficit-cases.json');summary=[]
    for case in cases:
        rows={}
        for key,q in case['maps'].items():
            dma=q['real_associated_DMA'];d=dma['data']
            rows[key]=dict(index_one_based=q['index_one_based'],gameplay_row_zero_based=q['gameplay_row_zero_based'],
                actual_pre_TnMovement_geometry=q['actual_before_movement_geometry'],draw_construction=q['captured_draw_construction'],
                completed_GameLoop_return=q['captured_completed_return'],main_span=q['main_span'],
                derived_Main_CPUstart=q['CPUstart_derived_return_minus_inclusive_cycles'],
                DMA_ordinal=dma['ordinal'],DMA_start=d['start'],DMA_finish=d['finish'],DMA_exact=d['exact'],DMA_safe=d['safe'],
                hardware256_sha256=q['hardware256_sha256'],source256_sha256=hashlib.sha256(bytes(d['source'])).hexdigest(),
                actual_surrounding_audio_and_original_source_tick=q['surrounding_completed_audio_intervals'])
        summary.append(dict(strict_deficit=case['strict_deficit'],classification=case['classification'],
            associated_DMA_epoch_delta=case['associated_DMA_epoch_delta'],cases=rows,OAM_comparison=case['OAM_page_comparison'],
            actual_NMIentry_stackedPC_and_NmiDisable_store_not_logged=True))
    generated('native-result/deficit-summary.json',dict(original_full_case_map_sha256=sha(native/'deficit-cases.json'),cases=summary),'derived_actual_deficit_summary')
    epochs=js(native/'physical-DMA-epochs.json');assert len(epochs)==600
    windows=[q for q in epochs if q['physical_epoch']in {330,929}or any(abs(q['physical_epoch']-v)<=2 for v in [862,890,918])]
    generated('native-result/physical-epoch-summary.json',dict(original_full_epoch_map_sha256=sha(native/'physical-DMA-epochs.json'),
        first_epoch=330,last_epoch=929,observed_epochs=len(epochs),total_baseline_DMA=572,total_candidate_DMA=575,
        net_extra_candidate_DMA=3,minimum_cumulative_DMA_count_difference=min(q['candidate_minus_baseline_DMA_count']for q in epochs),
        actual_one_epoch_construction_deferral=[560],completion_label_only_updates=[532,588],selected_epoch_windows=windows,
        global_DMA_count_does_not_establish_each_construction_freshness=True,
        source600_next_DMA_outside_capture=True,initial_DMA_source_precedes_active_ledger=True),'derived_actual_epoch_summary')
    diagnosis=js(native/'diagnosis.json')
    generated('native-result/phase-cost-summary.json',dict(phase_costs=diagnosis['phase_costs'],native_inputs=diagnosis['native_inputs'],
        same_BEFORE_phase_setup_commands=True,source_original_executable_calls=602,original_ordered_APU_requests=2125,
        original188byte_state_exact=True,strict_performance_gate_passed=False),'derived_native_phase_summary')
    generated('external-artifact-bindings.json',dict(source_packet=dict(path=str(final/'receipt.json'),sha256=SOURCE),
        native_packet=dict(path=str(native/'receipt.json'),sha256=NATIVE),
        native_diagnosis=dict(path=str(native/'diagnosis.json'),sha256=sha(native/'diagnosis.json')),
        full_deficit_map=dict(path=str(native/'deficit-cases.json'),sha256=sha(native/'deficit-cases.json')),
        full_physical_epoch_map=dict(path=str(native/'physical-DMA-epochs.json'),sha256=sha(native/'physical-DMA-epochs.json')),
        production_ROM_sha256=CURRENT,held_candidate_ROM_sha256=FINAL,
        source670_files_sha256=sha(final/'source-bindings.json')),'external_exact_artifact_bindings')
    readme=f'''TMNT CHANNEL/RENDER ROLLBACK CHECKPOINT â€” HELD
2026-10-26. Exact private70ba {FINAL}
Accepted production remains {CURRENT}

Source/CPU correctness passed, including original16-song execution and compiled
IRQ/NMI/caller proofs. Native source/hardware/CHR/SMC/stack guards passed one
staged Easy600 matched pair. Native PERFORMANCE DID NOT PASS and is not adopted.
The unchanged strict comparator still fails3absolute/3phase prefixes532/560/588.
532 and588 reached the same DMA epochs862/918 as baseline despite endFrame
completion labels crossing. Construction560 genuinely transfers in891 versus
baseline890. At epoch890 candidate retains559. This remains a real one-epoch
construction deferral despite NO cumulative physical DMA-count deficit and
net+3candidate DMAs (575versus572). Longer source-safe code verification is not
native-qualified performance, universal60Hz, natural acquisition or campaign QA.
Cold renderer+2/+7 remain recorded. Source740..749/735model is not recovery.

Exact native result receipt {NATIVE}
Native result/strictFAIL are copied byte-for-byte; summaries retain exact case
ordinals, pre-TnMovement geometry, DMA source/time hashes and audio/core ticks.
Full paired256B pages differ; no RGB or unlogged actor ownership assertion.
Actual NMIentry/stackedPC/NmiDisable publication-store time was not captured.
Initial DMA predates active construction ledger; last construction600 has no
next DMA within the bounded capture. Full external raw evidence remains bound.

RESTORE SOURCE INTO A SEPARATE PRIVATE CHECKOUT, NEVER AUTOMATICALLY ADOPT:
1. Start with exact650-member50b5 source snapshot identified by
   baseline50b-source-bindings.json (original inputs/assets remain required).
2. Overlay the31full changed inputs in sibling
   ../tmnt-parser-source-held/changed-source using its packet
   packets/tmnt-parser-tail-writers-ready-v1/changed-source-versus-50b5.json.
   Verify its complete666-member source-bindings manifest. The already-pushed
   native-drum.dmc dependency is referenced, not copied by this text checkpoint.
3. Overlay the5full source changes in sibling
   ../render-lifecycle-holds/tmnt/source using its changed-source-versus-1d741.
   Verify that sibling's complete668-member8d602 manifest.
4. Overlay ALL SIX full files under this checkpoint's source/ using
   incremental-source.json, verifying each before/after hash. Two files are new.
5. The resulting670-member manifest MUST equal source-bindings-70ba.json exactly.
   The checkpoint producer has verified this full map, including every input
   unchanged by the increment. Source is not an installed or accepted build.

Published parents are bound to {remote_ref} at {remote}; each referenced
file's bytes were verified against that actual Git object. No commit, push or
production restoration was performed here. Existing canonical70ba and ordinary
flagoff proofs are retained; this checkpoint preparation does not claim a new
build, native run, source optimization, adoption or performance waiver.

frozen-tools/ contains the EXACT working reporter v2. retained-invalid/ stores
the exact invalid v1 as .py.failed.txt, explicitly NOT runnable: it failed at
Python parse before any output, with no game/native failure implication.
The source reports' two invalid CPU fixture attempts and audio inheritance
wording erratum remain separately classified in their retained catalogs.

No ROM, NSF, DMC/sample, archive, screenshots, captures or replay media copied.
The verified catalog binds all checkpoint payloads; checkpoint-proof.json binds
the catalog and records the full source reconstruction and strict held scope.
'''
    (out/'README.txt').write_text(readme,encoding='utf-8');origins['README.txt']=dict(classification='checkpoint_scope_and_restore_instructions',generated=True)
    put('frozen-tools/tmnt_channel_render_checkpoint_v2.py',Path(__file__),'checkpoint_producer')
    failed=D/'tmnt-channel-checkpoint-preparation-v1-negative'
    assert failed.exists()
    generated('retained-invalid/checkpoint-preparation-v1.json',dict(
        stage='Checkpoint catalog verification only; no game/native mutation',
        reason='Default Windows cp1252 text write encoded generated README em dash as0x97; UTF8-only catalog correctly rejected it. v2 explicitly writes generated UTF8.',
        external_retained_preparation=str(failed),README_sha256=sha(failed/'README.txt'),
        original_producer_sha256=sha(failed/'frozen-tools/tmnt_channel_render_checkpoint_v1.py'),
        source_reconstruction_and_native_verdict_unchanged=True),'checkpoint_preparation_tooling_negative')

    entries={}
    forbidden={'.nes','.nsf','.dmc','.zip','.gz','.png','.jpg','.mp4','.avi','.wav','.bin','.bmp','.state','.mmo'}
    for path in sorted(out.rglob('*')):
        if not path.is_file():continue
        assert path.suffix.lower()not in forbidden;content=path.read_bytes();content.decode('utf-8');assert b'\x00'not in content
        name=path.relative_to(out).as_posix();assert name in origins
        entries[name]=dict(bytes=len(content),sha256=sha(path),**origins[name])
    generated_catalog=dict(format='text-only-checkpoint-v1',payloads=entries)
    (out/'catalog.json').write_text(json.dumps(generated_catalog,indent=2)+'\n',encoding='utf-8')
    for name,row in js(out/'catalog.json')['payloads'].items():
        assert sha(out/name)==row['sha256']and(out/name).stat().st_size==row['bytes']
        if 'origin'in row:assert sha(Path(row['origin']))==row['origin_sha256']==row['sha256']
    proof=dict(passed=True,prepared=True,checkpoint_only=True,production_adopted=False,performance_gate_passed=False,
        no_native_run_commit_stage_push_or_optimization=True,source_CPU_qualified=True,native_source_hardware_guards_passed=True,
        candidate_ROM_sha256=FINAL,production_ROM_sha256=CURRENT,
        exact_incremental_source_files=len(changes),complete_restored_source_files=len(virtual),full670_restoration_hash_map_exact=True,
        published_parent_input_files_verified=len(dependencies),upstream_ref=remote_ref,upstream_commit=remote,
        source_receipt_sha256=SOURCE,native_result_receipt_sha256=NATIVE,
        strict_prefix_failures=[532,560,588],actual_one_epoch_construction_deferral=[560],completion_label_only=[532,588],
        cumulative_physical_DMA_count_deficit=False,total_DMAs=dict(baseline=572,candidate=575,net_candidate=3),
        working_reporter_v2_exact=True,invalid_v1_exact_retained_as_nonrunnable_text=True,
        all_payloads_UTF8_text_no_NUL=True,no_ROM_NSF_samples_captures_or_media_included=True,
        payload_files=len(entries),payload_bytes=sum(r['bytes']for r in entries.values()),
        catalog_sha256=sha(out/'catalog.json'),producer_sha256=sha(Path(__file__)),
        limits='Source restoration/byte/catalog proof and summaries of the one existing paired native result. Does not rerun a build/native case, certify performance, ship base assets or authorize adoption.')
    (out/'checkpoint-proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,checkpoint=str(out),incremental_source_files=len(changes),source_members=len(virtual),
        payloads=len(entries),payload_bytes=proof['payload_bytes'],catalog_sha256=sha(out/'catalog.json'),checkpoint_proof_sha256=sha(out/'checkpoint-proof.json'))))


if __name__=='__main__':main()
