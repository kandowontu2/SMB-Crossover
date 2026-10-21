"""Durable completed-root progress; no release or full-goal acceptance."""
from pathlib import Path
import csv,datetime,hashlib,json,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root-current49-progress-q.json'
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
            pin=row['target'][key];p=Path(pin['path'])
            assert sha(p)==pin['sha256']==sha(ROOT/'build'/p.name)
    refs={
      'previous_P':'build/verification/root-current49-progress-p.json',
      'current_shared_P':'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json',
      'user_lossless_50GB_policy':'build/verification/root-workspace-storage-policy-50gb-a.json',
      'three_currentP_MMC3_fixed_clears':'build/verification/root49p-three-fixed-a/report.json',
      'Pit_I_early_assert_partial_capture_negative':'build/verification/root49p-pit-final-lift-i/report.json',
      'Pit_I2_native_lift_pass_then_13_death':'build/verification/root49p-pit-final-lift-i2/report.json',
      'Pit_I2_actual_support_unsignedQ_qualification':'build/verification/root49p-pit-i2-lift-host-review-a.json',
      'Pit_J_full_nine_CSV_literal':'build/verification/pit49p-13-platforms-j-passive/actual-attempt-receipt.json',
      'Pit_K_ordinary_13_pass_castle_death':'build/verification/pit49p-13-platforms-k-controller/actual-attempt-receipt.json',
      'Scrooge_currentP_H_original_castle_negative':'build/verification/root49p-scrooge-live-h/report.json',
      'Scrooge_H_vs_N_G_all9_literal':'build/verification/root49p-scrooge-h-vs-n-g-literal-a.json',
      'Scrooge_I_firebar_pass_then_controller_assert':'build/verification/root49p-scrooge-phase-i/report.json',
      'Scrooge_I2_firebar_pass_later_castle_death':'build/verification/root49p-scrooge-phase-i2/report.json',
      'Ryu_L_scope_cap_negative':'build/verification/ryu49-head-early-passive-l/o2-mmc3-actual-attempt-receipt.json',
      'Ryu_L2_terminal_partial_negative':'build/verification/ryu49-head-early-passive-l2/o2-mmc3-actual-attempt-receipt.json',
      'Ryu_L3_O2_full_own9_literal':'build/verification/ryu49-head-early-passive-l3/o2-mmc3-actual-attempt-receipt.json',
      'Ryu_L3_E_full_own9_literal':'build/verification/ryu49-head-early-passive-l3/e-mmc3-actual-attempt-receipt.json',
      'Bill_A_baseline_compile_negative':'build/verification/root49o2-bill-shape-private-a-driver.log',
      'Bill_B_original_layout_guard_negative':'build/verification/root49o2-bill-shape-private-b-driver.log',
      'Bill_C_scoped_layout_revision_build_source410':'build/verification/root49o2-bill-shape-b-layout-c/report.json',
      'Sophia_H4_actual_normal_handlers':'build/verification/root49o2-sophia-interrupt-h4-replays-a/report.json',
      'Sophia_H5_actual_MMC5_mature_handlers':'build/verification/root49o2-sophia-interrupt-h5-replays-a/report.json',
      'Sophia_H5_MMC3_broader_domain_negatives':'build/verification/root49o2-sophia-interrupt-h5-replays-b/report.json',
      'Sophia_H5_MMC3_retained_executed_derivative':'build/verification/root49o2-sophia-interrupt-h5-mmc3-driver-b.py',
      'Sophia_H5_MMC3_root_wrapper':'tools/audit/run_sophia49_interrupt_h5_replays_b.py',
      'Sophia_N_constructed_entry_smoke':'build/verification/root49o2-sophia-interruption-n-smoke-a.json',
      'Sophia_N_constructed_168_boundaries':'build/verification/root49o2-sophia-interruption-n-boundaries-a.json',
      'Sophia_O_independent_host_effect_reconstruction':'build/verification/root49o2-sophia-interruption-o-host-review-a/report.json',
      'QA':'docs/qa/roster-provisional-v49.md',
    }
    for mapper in ('mmc3','mmc5'):
        for side in ('before','after'):
            n=f'build/verification/root49o2-sophia-interrupt-l-{mapper}-{side}-review-a.json'
            r=json.loads((ROOT/n).read_text());assert r['status']=='PASS_NATIVE_L_RAM_BUS_NEUTRALITY_LAG_MODE_NO_CLOSURE_PROMOTION'
            refs[f'Sophia_L_{mapper}_{side}']=n
    for side in ('before','after'):
        n=f'build/verification/root49o2-sophia-interrupt-h6-mmc3-{side}-replay-a.json'
        r=json.loads((ROOT/n).read_text());assert r['status']=='PASS_H6_ACTUAL_MMC3_LAG_NMI_IRQ_REPLAY_ONLY'
        assert r['native_NMI']==r['native_IRQ']==4 and not r['normal_NMI_and_DMA_domain_covered']
        refs[f'Sophia_H6_actual_MMC3_lag_only_{side}']=n
    foot={}
    for role,frames in [('o2',15052),('e',1851)]:
        rr=json.loads((ROOT/refs['Ryu_L3_'+role.upper()+'_full_own9_literal']).read_text())
        assert rr['result']['frames']==frames and not rr['postcheck_errors']
        assert all(r['literal']for r in rr['nine_CSV_comparison'].values())
        p=Path(rr['output'])/'ryu49-foot-head-counts-l.csv'
        with p.open(newline='')as f:counts=list(csv.DictReader(f))
        assert len(counts)==frames and all(int(r['footEntry'])==int(r['footBody'])==0 for r in counts)
        foot[role]=dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),frames=len(counts),total_relocated_foot_calls=0,
                        measured_relocated_foot_overhead_cycles_this_attempt=0)
    pins={k:dict(path=n,sha256=sha(ROOT/n),bytes=(ROOT/n).stat().st_size)for k,n in refs.items()}
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used<50_000_000_000
    report=dict(status='progress-full-goal-incomplete',goal_complete=False,accepted_release=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
        working_checkpoint=cp.name,shared409_source_exact=True,root_ROM_DBG_LBL_MAP_exact=True,
        current_P_MMC3_fixed_ordinary_end2_2=['Mario','Luigi','Samus'],current_P_MMC5_fixed_ordinary_end2_2=[],
        workspace_bytes=used,prospective_cap_bytes=50_000_000_000,retain_lossless_captures=True,
        root_active_native_CPU_compile_jobs=[],references=pins,Ryu_global_foot_counts=foot,
        provenance_qualification='H5 MMC3 B wrapper executed the retained derivative with the original A __file__ to preserve ROOT inference; aggregate script_sha256 therefore records original A. Both actual derivative and wrapper are pinned above. Those negative B results are never promoted to PASS.',
        unfinished=[
          'Full current roster through2-2, every alternate attack/upgrade, visual/SFX review and retained final recordings.',
          'Pit actual1-2 and1-3 platform crossings now pass adaptively; castle low-roof crossing remains negative, complete fixed clear still absent.',
          'Scrooge passes the previously fatal firebar with ordinary timing and reachesX1373; later castle death remains unresolved.',
          'Ryu E real early head/side-clamp regression needs source/caller/cache repair. L3 actual writers are captured; no source correction or promotion yet.',
          'Bill B compiled/source410 is admitted only under explicit C layout revision. Exact CPU ABI/native46-scenario validation pending; fractional/source cache/water/Firebar obligations retained.',
          'Sophia ratio/friction remain private. Actual H4 normal and H5/H6 lag handler coverage plus one-seed constructed N boundary proof are separate; material promotion gates under review. Stress gain remains small, not lag-free.',
          'Rygar1-2, remaining full roster/weapon/source/audio/hardware performance audits incomplete.',
          'No source-perfect/allweapon/hardware/finalrelease claim.'])
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(path=str(OUT),sha256=sha(OUT),workspace_bytes=used)))

if __name__=='__main__':main()
