"""Durable current-P/source identity and completed root evidence, with all gaps."""
from pathlib import Path
import datetime,hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root-current49-progress-p.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    cp=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
    assert sha(cp/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    m=json.loads((cp/'manifest.json').read_text());cat=m['source_hashes']
    assert len(cat)==409 and all(sha(ROOT/n)==h for n,h in cat.items())
    archive=cp/'source-v49-pit-wings-p.zip';assert sha(archive)==m['source_archive_sha256']
    with zipfile.ZipFile(archive)as z:assert json.loads(z.read('archived-file-hashes.json'))==cat
    for row in m['compiled']:
        for key in ('rom','debug','labels','map'):
            r=row['target'][key];p=Path(r['path']);assert sha(p)==r['sha256']==sha(ROOT/'build'/p.name)
    refs={
      'previous_O':'build/verification/root-current49-progress-o.json',
      'current_P':'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json',
      'user50GB_lossless_policy':'build/verification/root-workspace-storage-policy-50gb-a.json',
      'three_current_P_fixed_clears':'build/verification/root49p-three-fixed-a/report.json',
      'Sophia_C2b_5352608_CPU_cases':'build/verification/root49o2-sophia-friction-c2b-cpu-full-f/report.json',
      'Sophia_C2b_actual_small_performance_gain':'build/verification/root49o2-sophia-friction-c2b-profile-g/report.json',
      'Sophia_C2b_38_native_host_regressions':'build/verification/root49o2-sophia-friction-c2b-native-h/report.json',
      'Sophia_G_zero_overlap_negative':'build/verification/root49o2-sophia-interrupt-g-mmc5-before-review-a.json',
      'Sophia_I_page1_bus_classification_negative':'build/verification/root49o2-sophia-interrupt-i-mmc5-before-review-a.json',
      'Sophia_H2_model_CE_timing_negative':'build/verification/root49o2-sophia-interrupt-h2-mmc5-before-replay-a.json',
      'Sophia_H3_exact_model_DMA_role_negatives':'build/verification/root49o2-sophia-interrupt-h3-replays-a/report.json',
      'Ryu_I_fresh_setup_native_components':'build/verification/root49o2-head-i-native-a/report.json',
      'Ryu_J_strict_queries_independent_full_end':'build/verification/root49o2-head-j-strict-a/report.json',
      'Ryu_K_actual_independent_components_review':'build/verification/ryu49o2-head-ij-actual-review-k/report.json',
      'Ryu_K_O2_ordinary_full_fixed_control':'build/verification/ryu49o2-head-ordinary-comparison-k/o2-mmc3-actual-attempt-receipt.json',
      'Ryu_K_E_early_ordinary_regression_negative':'build/verification/ryu49o2-head-ordinary-comparison-k/e-mmc3-actual-attempt-receipt.json',
      'Bill_S_full_Q_prefix_support_lifecycle':'build/verification/root49n-bill-foot-contract-wait-s-review-a.json',
      'Bill_T_native_fixed_same_death':'build/verification/root49n-bill-castle-t-native-a/report.json',
      'Bill_T2_actual_owner_probe_and_writer_review':'build/verification/root49n-bill-castle-t2-review-a.json',
      'Bill_T2_source_jump_head_gap':'build/verification/agent49n-bill-castle-contact-review-t2/actual-source-review-b.json',
      'Pit_Rygar_currentP_old_fixed_negatives':'build/verification/root49p-pit-rygar-fixed-b/report.json',
      'Pit_Rygar_ordinary_C_negatives':'build/verification/root49p-pit-rygar-live-c/report.json',
      'Pit_Rygar_ordinary_D_retained_lossless_negatives':'build/verification/root49p-pit-rygar-live-d/report.json',
      'Pit_Rygar_D_all_DMA_rows_review':'build/verification/root49p-recorded-d-frame-review-a.json',
      'Pit_Rygar_ordinary_E_negatives':'build/verification/root49p-pit-rygar-live-e/report.json',
      'Pit_Rygar_ordinary_F_negatives':'build/verification/root49p-pit-rygar-live-f/report.json',
      'Pit_Rygar_ordinary_G_negatives':'build/verification/root49p-pit-rygar-live-g/report.json',
      'Pit_H_fixed_all9_literal_lift_supplement':'build/verification/pit49p-final-lifts-h-passive/actual-attempt-receipt.json',
      'QA_as_of_this_snapshot':'docs/qa/roster-provisional-v49.md',
    }
    for mapper in ('mmc3','mmc5'):
        for side in ('before','after'):
            n=f'build/verification/root49o2-sophia-interrupt-j-{mapper}-{side}-review-a.json'
            r=json.loads((ROOT/n).read_text());assert r['status']=='PASS_NATIVE_I_RAM_BUS_NEUTRALITY_NO_CLOSURE_PROMOTION'
            assert r['actual_NMI']==r['actual_IRQ']==4
            refs[f'Sophia_actual_bus_profile_neutrality_{mapper}_{side}']=n
    cpu=json.loads((ROOT/refs['Sophia_C2b_5352608_CPU_cases']).read_text())
    assert cpu['status']=='PASS_ALL12_FROZEN_FRICTION_CPU_MATRICES'
    assert sum(c['result']['cases']for c in cpu['cases'])==5_352_608
    native=json.loads((ROOT/refs['Sophia_C2b_38_native_host_regressions']).read_text())
    assert native['status']=='PASS_38_UNCHANGED_SOPHIA_NATIVE_AND_HOST_REGRESSIONS' and len(native['cases'])==38
    assert all(c['native_and_host_exit']==0 and c['has_PASS']for c in native['cases'])
    pins={k:dict(path=n,sha256=sha(ROOT/n),bytes=(ROOT/n).stat().st_size)for k,n in refs.items()}
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used<50_000_000_000
    report=dict(status='progress-full-goal-incomplete',goal_complete=False,accepted_release=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
        working_checkpoint=cp.name,shared409_source_exact=True,root_ROM_DBG_LBL_MAP_exact=True,
        current_P_MMC3_fixed_ordinary_end2_2=['Mario','Luigi','Samus'],current_P_MMC5_fixed_ordinary_end2_2=[],
        workspace_bytes=used,prospective_cap_bytes=50_000_000_000,retain_lossless_captures=True,
        root_active_native_CPU_compile_jobs=[],references=pins,
        unfinished=[
          'Full current roster through2-2, every alternate attack/upgrade and final retained recordings.',
          'Sophia ratio/friction stay private: stress remains114/180 M3 and105/180 M5; H3 handler DMA-role negatives and all-boundary coherence remain open.',
          'Ryu E component checks pass except explicit CPU-only80 gap, but ordinary fixed run diesearly and shows repeated+16 worldX steps. Actual writer/caller and global foot-call performance gates remain open.',
          'Bill actual short-jump head/terrain/body mismatch needs source-backed correction; fireball source phase/pivot/water cache obligations remain qualified.',
          'Pit actual final1-2 moving-lift/support supplement needs review and a successful ordinary controller; Rygar1-2 remains negative.',
          'Scrooge actual castle firebar contact is identified; successful ordinary tactic remains unprepared.',
          'Source48 isolated audio-owner full reset lineage and current49 transplant remain unaccepted.',
          'No source-perfect/allweapon/hardware/finalrelease claim.'])
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(path=str(OUT),sha256=sha(OUT),workspace_bytes=used)))

if __name__=='__main__':main()
