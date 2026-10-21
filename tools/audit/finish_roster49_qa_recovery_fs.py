"""Restore byte-exact QA history and finish the already-passed Pit admission."""
from pathlib import Path
import datetime, hashlib, json, os, sys
from recover_roster49_qa_fr import literal_append

R = Path(__file__).resolve().parents[2]
V = R/'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
write = lambda p, j: Path(p).write_text(json.dumps(j, indent=2)+'\n', encoding='utf-8')

def main():
    backup = V/'root49-QA-recovery-fr-exact-fj.md'
    expected = 'f6915d6f93be658d55e0a5673fc6b302e84a6cdbdb9ef3b02735c5327e10009a'
    assert sha(backup) == expected
    qa = R/'docs/qa/easy-hard-legacy-v49.md'
    assert qa.stat().st_size == 0
    zero = V/'root49-QA-recovery-fs-truncated-original.md'
    assert not zero.exists()
    zero.write_bytes(qa.read_bytes())
    temp = qa.with_name(qa.name+'.recovery-fs.tmp')
    assert not temp.exists()
    temp.write_bytes(backup.read_bytes())
    assert sha(temp) == expected
    os.replace(temp, qa)
    assert sha(qa) == expected
    receipt = V/'root49-QA-recovery-fs.json'
    assert not receipt.exists()
    write(receipt, dict(status='EXACT_BYTE_RECOVERY_VERIFIED_AND_ATOMICALLY_RESTORED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        target=str(qa.relative_to(R)), restored_bytes=qa.stat().st_size,
        restored_sha256=sha(qa), expected_saved_FJ_sha256=expected,
        backup=str(backup.relative_to(R)), backup_sha256=sha(backup),
        failed_original_sha256=sha(zero),
        recovery_script_sha256=sha(R/'tools/audit/recover_roster49_qa_fr.py'),
        successful_patch_receipts=60, replayed_update_patches=59,
        literal_append_stages=['cg','cv','eb','fj'],
        all_five_intermediate_saved_checksums_matched=True,
        original_error='Default cp1252 write_text opened/truncated QA before U+2192 encoding failure in FP. No ROM/source/replay evidence changed.',
        prevention='Retained exact full backup; future QA writes use explicit encoding and atomic temporary files.',
        original_failed_script_retained=True, runtime_changed=False))
    append = literal_append(R/'tools/audit/review_roster49_pit_h_fp.py')
    updated = qa.read_bytes()+append.replace('→','->').replace('\n','\r\n').encode('utf-8')
    temp.write_bytes(updated)
    assert temp.read_bytes().startswith(backup.read_bytes())
    os.replace(temp, qa)
    cp = R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json'
    assert sha(cp) == '8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
    for n,h in read(cp)['source_hashes'].items():
        assert sha(R/n) == h
    for n,h in read(cp)['generated11'].items():
        assert sha(R/'build/generated'/n) == h
    for b in read(cp)['builds']:
        for a in b['artifacts'].values():
            assert sha(R/a['path']) == a['sha256']
    index = V/'root49-goal-coverage-fp.json'
    review = V/'root49-pit-h-root-review-fp.json'
    assert sum(bool(q['current_H_independently_admitted_base_routes'])for q in read(index)['roster']) == 10
    assert read(review)['hardware']['actual_DMA'] == 22440
    # Persist the already-authorized additive specialist allowance.
    cap = V/'root49-lsr-g-allocation-fq.json'
    assert not cap.exists()
    prior = V/'root49-lsr-g-allocation-ez.json'
    assert sha(prior) == '908348ee9a7dbfd6b42d9e149c4b858ff09ff55deda7c8d345ecbc654280114d'
    write(cap, dict(status='ADDITIVE_LSR_FROZEN_G_ROUTE_PROOF_ALLOCATION',
        prior_path=str(prior.relative_to(R)), prior_sha256=sha(prior),
        prior_cap=1800000000, new_cap=1950000000,
        owner_reported_inclusive_phase=1674150586,
        planned_discovery=80000000, planned_two_fixed=60000000,
        reserve=100000000, planned_total=1914150586,
        workspace_observed=77787566448, global_cap=80000000000,
        requirements=read(prior)['requirements'],
        authorization='Root collaboration message approved before owner local preflight. This receipt records that existing approval.',
        goal_complete=False))
    sys.path.insert(0,str(R/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 80000000000
    out = V/'root-current49-progress-fs.json'
    assert not out.exists()
    write(out, dict(status='PROGRESS_TEN_H_BASE_IDENTITIES_QA_EXACTLY_RECOVERED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        previous_handoff='build/verification/root-current49-progress-fj.json',
        previous_handoff_sha256=sha(V/'root-current49-progress-fj.json'),
        partial_FP_completed_additively=True,
        Pit_review=dict(path=str(review.relative_to(R)),sha256=sha(review)),
        coverage_index=dict(path=str(index.relative_to(R)),sha256=sha(index)),
        QA=dict(path=str(qa.relative_to(R)), recovered_prior_sha256=expected,sha256=sha(qa),
            recovery_receipt_sha256=sha(receipt)),
        allocation_FQ_sha256=sha(cap), working_checkpoint_sha256=sha(cp),
        installed_revision='H', private_I_installed=False,
        actual_H_admitted_identities=10, actual_H_DMA_total=200388,
        retained_H_base_recordings=4,
        private_Arm='All32 candidate native source-correct cases passed; all4 original H free-lift assertions fail as source-negative controls. Final ABI/foreign/cost controls and root review still pending. Not installed.',
        remaining_base_identities=['Samus','Rygar','Simon','Ryu'],
        specialist_owned_native_handles={'Rygar':60423,'Simon':11600},
        root_owned_native_handles=[],
        full_goal_scope_unchanged=True, all_arsenal_complete=False,
        thorough_lag_optimization_complete=False, final_all_roster_media_complete=False,
        workspace_bytes=used, workspace_cap=80000000000,
        lossless_negatives_and_recovery_evidence_retained=True,
        current_goal_turn='progress', goal_status='active', blocked=False,
        accepted_release=False,goal_complete=False))
    print(json.dumps(dict(recovery_sha256=sha(receipt), QA_sha256=sha(qa),
        progress_sha256=sha(out), FQ_sha256=sha(cap), workspace_bytes=used)))

if __name__ == '__main__':
    main()
