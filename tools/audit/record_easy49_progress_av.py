"""Freeze the adopted working checkpoint and remaining active audit work."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=V/'root-current49-progress-av.json';assert not out.exists()
    checkpoint=R/'build/checkpoints/roster-audit-v49-combined-ground-audio-samus-c/manifest.json'
    assert sha(checkpoint)=='7bde77980e47d11ed78b9348384016b1a805ff40a02ff180b33f0e8e727b5305'
    c=json.loads(checkpoint.read_text())
    assert len(c['source_hashes'])==455
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in c['builds']:
        for h in b['artifacts'].values():assert sha(R/h['path'])==sha(R/h['frozen_path'])==h['sha256']
    files=[
        'root49-combined-working-b/preparation.json','root49-combined-working-b/composition-review.json',
        'root49-combined-working-c/preparation.json','root49-combined-working-c/composition-review.json',
        'root49-combined-working-c/targeted-native/summary.json','root49-combined-full-suite-c/summary.json',
        'root49-full-suite-admission-a.json','root49-full-failure-parent-e-a/freeze.json',
        'root49-landing-audio-admission-a.json','root49-samus-action-review-a/independent-review.json',
        'root49-samus-armor-filter-review-a/review.json','root49-legacy-fixture-triage-a/freeze.json',
        'agent-lsr-sophia-feet-perf-a/implementation-freeze.json',
        'agent49-samus-bill-arsenal-a/action-freeze-k/freeze.json',
        'agent49-samus-bill-arsenal-a/missile-freeze-y/freeze.json',
        'root49-samus-reference-pacing-a/contact-review-c.json',
        'root49-samus-reference-pacing-a/contact-review-j.json',
        'root49-samus-reference-pacing-a/revision-k.json',
        'root49-main-combined-c-smoke/smb-crossover-mmc3-baseline.log',
        'root49-main-combined-c-smoke/smb-crossover-mmc5-baseline.log',
        'root-current49-progress-au.json',
    ]
    refs={n:dict(sha256=sha(V/n),bytes=(V/n).stat().st_size) for n in files}
    spec=importlib.util.spec_from_file_location('route_census',R/'tools/playthroughs/roster_run.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    size=module.workspace_bytes(R);assert size+100000000<70000000000
    phase=V/'root49-samus-reference-pacing-a'
    routes=sorted((R/'build/roster-through-2-2').glob('root49-samus-pacing-*-2-v0-mmc3'))
    routes.append(R/'build/roster-through-2-2/root49-samus-phase-reference-f-2-v0-mmc3')
    phase_bytes=module.workspace_bytes(phase)+sum(module.workspace_bytes(p) for p in routes)
    assert phase_bytes+50000000<500000000
    result=dict(status='PROGRESS_WORKING_C_ADOPTED_COMPLETE_REGRESSION_CLASSIFICATION_GOAL_ACTIVE',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
        checkpoint=dict(path=str(checkpoint.relative_to(R)),sha256=sha(checkpoint)),
        shared_main_verified=dict(source_files=455,generated_files=11,primary_artifacts=8,changed_sources_since_GQ=35),
        ROMs={b['mapper']:b['artifacts']['nes']['sha256'] for b in c['builds']},
        references=refs,QA=dict(path='docs/qa/easy-hard-legacy-v49.md',sha256=sha(R/'docs/qa/easy-hard-legacy-v49.md')),
        full_suite=dict(passed_native_slots=688,failed_native_slots=73,separate_stockMario_comparison_failed=True,
            all73_actual_first_failures_reproduce_on_immutable_E=True,fixture_entries_unchanged=566,
            full_suite_passed=False,no_failures_converted_to_passes=True),
        final_working_C=dict(targeted_native_fixtures_passed=12,main_boot_smokes_passed=2,
            exact_tested_parent_union=True,missile_region_bytes=19,missile_changed_ROM_bytes=9),
        root_owned_live_handles=[],
        root_route_status=dict(source='immutable audio E, not newly installed C',latest='K terminal death16556/X1373/Y75',
            advances='First three stages clear. Supported48-poll wait passes firstcastle firebar. Primary phase match passes lowerbar, upperbar remains a real contact.',
            exact_GQ_phase_reference='F reproduces full28285-frame prior clear with byte-identical trace/inputs.',
            contact_C='Fixed replay exact, conservative container overlaps, no source-disjoint defect established.',
            contact_J='Fixed I replay exact, upper slot3 point119/77 lies in native bodybox113/56..127/81.',
            no_E_or_C_full_route_clear=True,no_new_final_movie=True,
            pending_leads=['Further ordinary route timing/stance adaptation.',
                'If investigating initial firebar phase, bind actual InitShortFirebar pre/post first. Its high byte aliases Enemy_Y_Speed and only low is written there; source FireBar is freshly constructed. This static lead alone establishes no new runtime bug and was not changed.']),
        specialists=dict(
            link_simon_ryu='All optimization, action review, armor predicate, representative and all73 parent comparison packets frozen; idle, no native children.',
            samus_contra_s2='Private Ice AC source-order repair;149 new INVENTORY bytes, old PCs/RAM preserved;34 full native caller reexecutions/map exact. Additional source-order/foreign/cost and inherited palette/timer/SFX gaps remain. No AC main adoption.',
            mario_luigi_scrooge_s2='Bill ordinary route Z in2-2 on frozen E, phase below600MB/1GB,100MB final reserve. No fullclear/Lance/current-main proof yet. Latest reported native80241; agent owns current-state and successors.'),
        budget=dict(workspace_bytes=size,global_cap_bytes=70000000000,retains_all_lossless_captures_and_negatives=True,
            root_Samus_pacing_combined_bytes=phase_bytes,root_Samus_phase_cap_bytes=500000000,root_Samus_final_reserve_bytes=50000000,
            phase_budget_correction='Inclusive final census includes311MB of sibling route outputs and exceeds the earlier250MB planning amount; negative retained, phase allowance explicitly raised to500MB under unchanged70GB global cap. No captures deleted.',
            reason='User explicitly requested retaining lossless captures and raising the earlier30GB cap.'),
        next_actions=['Finish source-correct Ice order, then actual palette/timer/BulletProof gaps; compose only after independent reviewed private packet.',
            'Finish ordinary Bill/Lance and Samus on immutable candidate, independently replay final streams, then transfer to final working image explicitly.',
            'Continue remaining roster/arsenal and source fidelity audit, profile remaining lag and retain lossless final recordings.',
            'Migrate legacy fixture oracles only with independent source/actual-entry evidence; all present failures remain open.'],
        goal_status='active',goal_complete=False,accepted_release=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out),workspace_bytes=size,root_pacing_bytes=phase_bytes,root_live_handles=[])))


if __name__=='__main__':main()
