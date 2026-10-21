"""Durable current-state handoff after the requested menu update."""
from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2]
OUT=R/'build/verification/root-current49-progress-r.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not OUT.exists()
    cp=R/'build/checkpoints/roster-audit-v49-menu-options-s2'
    m=json.loads((cp/'manifest.json').read_text());assert m['status']=='PASS_WORKING_MENU_OPTIONS_BOTH_MAPPERS'
    assert len(m['source_hashes'])==410 and all(sha(R/n)==h for n,h in m['source_hashes'].items())
    for row in m['builds']:
        for ext,p in row['outputs'].items():
            assert sha(R/p['path'])==p['sha256']and sha(cp/Path(p['path']).name)==p['sha256']
    migration=cp/'test-migration/report.json';migrated=json.loads(migration.read_text())
    assert migrated['status']=='PASS_APPLIED_VERIFIED_MODE_EXPLICIT_TEST_MIGRATION'
    assert all(sha(R/n)==p['after_sha256']for n,p in migrated['files'].items())
    refs={
        'prior_Q_snapshot':'build/verification/root-current49-progress-q.json',
        'working_checkpoint':str((cp/'manifest.json').relative_to(R)),
        'test_migration':str(migration.relative_to(R)),
        'requested_menu_validation':'build/verification/root49-menu-validation-s2.json',
        'optimized_R_full_original_761':'build/verification/root49p-sophia-integrated-private-r/qa-suite-a/report.json',
        'R_performance_MMC3':'build/verification/root49p-sophia-integrated-performance-s-mmc3-review-a.json',
        'R_performance_MMC5':'build/verification/root49p-sophia-integrated-performance-s-mmc5-review-a.json',
        'Scrooge_J2_passive_actual_castle_hit':'build/verification/root49p-scrooge-castle-observer-j2/report.json',
        'Scrooge_J_broad_cap_negative':'build/verification/root49p-scrooge-castle-observer-j/report.json',
        'QA':'docs/qa/roster-provisional-v49.md','menu_QA':'docs/qa/menu-options-v49.md',
    }
    pins={k:dict(path=n,sha256=sha(R/n),bytes=(R/n).stat().st_size)for k,n in refs.items()}
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(R);assert used<50_000_000_000
    report=dict(status='progress-full-goal-incomplete',goal_complete=False,accepted_release=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
        working_checkpoint=cp.name,main_source410_exact=True,root_ROM_DBG_LBL_MAP_LST_exact=True,
        menu_request_complete=True,default_behavior='1.0',default_shadows='OFF',
        character_select_contains_options=False,read_only_route_audit_records_actual_behavior=True,
        current_S2_fixed_ordinary_end2_2=[],prior_P_MMC3_fixed_ordinary_end2_2=['Mario','Luigi','Samus'],
        workspace_bytes=used,prospective_cap_bytes=50_000_000_000,retain_lossless_captures=True,
        root_active_native_CPU_compile_jobs=[],references=pins,
        unfinished=[
            'Fresh S2 full-roster ordinary power-on routes through2-2, every alternate/special/upgrade, frame/SFX review and retained final recordings.',
            'Prior P proofs are historical and cannot be relabeled as S2. S2 now defaults1.0; source2.02 routes must select2.02 through actual menu input.',
            'Pit1-2/1-3 adaptive crossings pass; castle low-roof crossing remains negative. Castle L passive packet is unexecuted.',
            'Scrooge I2/J2 reaches later castle firebar at frame11484; actual native firebar injury is recorded, not a proven hitbox defect. Complete route remains open.',
            'Ryu previous25 head N2 remains frozen/unbuilt; early E regression is diagnosed. Bill shape E remains compiled/private and unexecuted; combined bank budgets require care.',
            'Rygar1-2 and remaining character/source/audio/hardware performance audits incomplete.',
            'Sophia software ratio/friction is integrated and validated; measured crowded scenes still lag. Separate MMC5 hardware-product proposal is not applied.',
            'No source-perfect, all-weapons, hardware timing, PCM-audio or final-release claim.'])
    OUT.write_text(json.dumps(report,indent=2)+'\n');print(str(OUT),sha(OUT),used)
if __name__=='__main__':main()
