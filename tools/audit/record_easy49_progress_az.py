"""Save exact F performance progress, new D full proofs and the remaining full goal."""
from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def footprint(paths):
    files=set()
    for p in paths:
        if p.is_dir():files.update(q for q in p.rglob('*')if q.is_file())
        elif p.is_file():files.add(p)
    return dict(files=len(files),bytes=sum(q.stat().st_size for q in files))
def main():
    out=V/'root-current49-progress-az.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json'
    assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2';c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in c['builds']:
        for q in b['artifacts'].values():assert sha(R/q['path'])==sha(R/q['frozen_path'])==q['sha256']
    refs=['root-current49-progress-ay.json','root49-goal-coverage-az.json',
      'root49-freeze-render-fast-f/preparation-b.json','root49-freeze-render-fast-f/build-review.json',
      'root49-freeze-render-fast-f/leaf-review-c.json','root49-freeze-render-fast-f/native-review-e/review.json',
      'root49-freeze-render-fast-f/matched-native-cost-f.json','root49-freeze-render-fast-f/freeze-g.json',
      'root49-freeze-fast-adoption-f/preparation.json','root49-freeze-fast-adoption-f/main-smoke/review.json',
      'root49-sophia-d-full-review-az.json','agent-lsr-sophia-current-d-route-a/freeze.json',
      'root49-lance-d-mmc5-review-az.json','specialist-bill-lance-current-d-a/phase-handoff-ab.json',
      'specialist-bill-lance-current-d-a/phase-freeze-aa.json','specialist-bill-lance-current-d-a/injury-qualification-ab.json',
      'root49-current-f-samus-a/review-az.json']
    references={n:dict(sha256=sha(V/n),bytes=(V/n).stat().st_size)for n in refs}
    own=footprint([V/'root49-freeze-render-fast-f']);runs=list((R/'build/roster-through-2-2').glob('root49-f-samus-*'))
    route=footprint([V/'root49-current-f-samus-a']+runs+list(V.glob('smb-crossover-*-run-root49-f-samus-*.log')))
    assert own['bytes']+50000000<300000000 and route['bytes']+100000000<500000000
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size<70000000000
    result=dict(status='PROGRESS_ACTIVE_ICE_RENDER_F_OPTIMIZED_D_SOPHIA_LANCE_FULL_CLEARS_CURRENT_F_ROUTES_OPEN',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
      previous_goal_turn_classification='progress: E integration installed/reviewed, actual D SamusMMC5 andBillMMC5 clears independently verified; two E transfer negatives retained.',
      current_goal_turn_classification='progress',checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),
      shared_main=dict(sources_rehashed=457,generated_rehashed=11,primary_artifacts_rehashed=8,
        changed_source_from_E=['src/samus_freeze_render.s'],changed_ROM_bytes_each=486,
        only_active_palette_leaf_and_trailing_local_tables_changed=True,other_ROM_bytes_and_RAM_addresses_literal_E=True,
        smokes_passed=2,backup=c['backup']),ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in c['builds']},references=references,
      completed_evidence=[
        'Four private F builds pass; both disabled baselines remain literal.',
        '6328 strict E/F leaf components retain all10240RAM/registers/flags/stack/mapper/orderedwrites, saving1009to1072 cycles in that broad set.',
        'Four new actual F native groups and original independent reviewers pass:1118completecallers,471wholeISR bodies,87/127OAM leases,360updateSTOP/pause/resume/NSF24/pending/DMA/AllOnes protocols.',
        '214freshF start states independently executeE/F: activepassM3 median4134to3062, M5 4072to3062. No whole-gameFPS/visibility claim.',
        'ReviewedF installed with476actualmainEfiles backedup; actualinstalled bothmapper startup/load/control/floor checks pass.',
        'Sophia D/MMC3 independent full25661/zero-death proof: all9wholeCSVs literal; root248receipts/455source/artifacts rehashed; single10k endpoint identity/control verified.',
        'Lance D/MMC5 independent full33044/zero-death proof:33044movement+32545native rows exact toX; root1686Dfiles/allpreservedfreezes/455source+8artifacts rehashed. Bill/Lance bothDmaps now separateproofs.',
        'ActualF/Easy Samus C controller usesintrinsicMorph/Bombs, defeatsbothfirstundergroundGoombas, boosts, expiresallbombs andunmorphsgrounded8388. Laterdeath9659retained.'
      ],
      retained_negatives=dict(Samus_F_MMC3=dict(A_death=8310,B_death=8328,C_death=9659,D_death=9486,
        latest_owner='D actual Koopa0 at853/Y184 versusballSamus840/Y176; controller watchedonlyfartherGoombas/neverstartedbombs.',
        next_action='Use actual actor roles and range/fuse timing; preserve primary/air/ball distinctions. No source runtime defect inferred.'),
        prior_E_transfers='M3death8174 andM5death3920 remain actualE negatives; F inactivepath bytes/costs unchanged but no automaticfullF transfer.',
        host_preflight='Initial F shortbranch -131 compilernegative retained; semantically equivalent longbranch repaired. Native runner budget-occurrence1vs2 preflight retained and corrected before any native launch.'),
      performance=c['cost'],source_fidelity_limits=c['limits'],
      root_live_native_handles=[],root_native_handles_closed=dict(buildRepair25992=0,leaf95061=0,native93265=0,
        Samus_A19754=1,Samus_B26791=1,Samus_C13569=1,Samus_D2372=1),
      specialists=dict(
        link_simon_ryu='ImmutableD Sophia phasefrozen1.182GB/1.4GB. NewF500MB/100MBreserve: firstfulloldDtransferfails1901; actualposepaced controls clear1-1/1-2/1-3, castlebossHP/flamephase recovery G lastreported38673. No F fullclear/media claim.',
        mario_luigi_scrooge_s2='Final D phaseAB frozenall4Bill/Lance proofs/1686files/24nativepackets,~680MB/1GB. NewF500MB/100MBreserve authorized: BillM3 fixedcandidate then ordinary recovery/map/varianttransfers; originalMario/Luigi/Scrooge/arsenal scope retained.',
        samus_contra_s2='ExplicitD MM primary route reached2-1entry17321. PassiveZ proves17941stompGoomba3 followed17942naturalupwardbounce andsidecontactwithGoomba4; no runtimebug. AA ordinaryairbrake lastreported28003. Bassstillpending; phase~465MB/1GB/100MBreserve.'),
      budget=dict(workspace_bytes=size,global_cap_bytes=70000000000,root_performance_phase=own,root_route_phase=route,
        performance_cap=300000000,performance_reserve=50000000,route_cap=500000000,route_reserve=100000000,
        Sophia_D_cap_extension=dict(old=1250000000,new=1400000000,reserve=100000000,
          basis='Actual1074993209 +60MBnext +60MBfixed +100MBreserve exceeded1.25GB; authorized before AN launch.'),
        new_F_specialist_allocations=dict(Sophia=dict(cap=500000000,reserve=100000000),Bill_Lance=dict(cap=500000000,reserve=100000000)),
        retains_all_lossless_and_negatives=True,cap_source='User explicitly requested retaining lossless captures and raising original30GB cap.'),
      regressions=dict(legacy_native_passed=688,legacy_native_failed=73,separate_stockMario_comparison_failed=True,full_suite_passed=False,
        scope='Original B suite only. No automatic F green claim and no waiver of retained failures.'),
      next_actions=[
        'Finish F Sophia actual boss/water route and independentfixed proofs; actualF Bill/Lance transfers/recovery.',
        'Recover full F Samus route with actor-aware controls, including range/fuse timing; then independentfixed and mapper proofs.',
        'Finish D MM/Bass realordinaryroutes and retained first-input-producer timing work, then explicit currentF transfers; recover remaining identities includingScrooge movinglifts/Linkpre-options distinction.',
        'Complete every oneof66weapon/item entries, natural acquisition/selection/tier interactions, remaining poses/water/enemy/block/SFX/graphics/palette properties, and measured lag/foreign regressions.',
        'Only afterfinal integration, produceandinspect retainedlossless finalplaythroughs for all14identities, preservingearlier shortcut/nonshortcut/everyenemy/item requirements.'
      ],QA=dict(path='docs/qa/easy-hard-legacy-v49.md',sha256=sha(R/'docs/qa/easy-hard-legacy-v49.md')),
      all_roster_complete=False,all_arsenal_complete=False,final_recordings_complete=False,goal_status='active',accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out),workspace_bytes=size,performance_phase=own,route_phase=route)))
if __name__=='__main__':main()
