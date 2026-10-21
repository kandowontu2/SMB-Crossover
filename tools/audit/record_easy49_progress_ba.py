"""Save current-F route/attack evidence without reducing the remaining goal."""
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
    out=V/'root-current49-progress-ba.json';assert not out.exists()
    prior=V/'root-current49-progress-az.json';assert sha(prior)=='325215a3b33966d5ac5f2eb2f2e8eaaa52ea5c934c7c9ace278273ca9ca9ad72'
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2';c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in c['builds']:
        for z in b['artifacts'].values():assert sha(R/z['path'])==sha(R/z['frozen_path'])==z['sha256']
    refs=['root49-goal-coverage-bb.json','root49-sophia-f-full-review-ba.json','agent-lsr-sophia-current-f-route-a/freeze.json',
      'root49-current-f-samus-a/review-ba.json','root49-current-f-samus-a/review-bb.json',
      'root49-current-f-samus-inventory-ba/review.json','root49-current-f-samus-inventory-ba/scope-b.json']
    route=footprint([V/'root49-current-f-samus-a']+list((R/'build/roster-through-2-2').glob('root49-f-samus-*'))+list(V.glob('smb-crossover-*-run-root49-f-samus-*.log')))
    inventory=footprint([V/'root49-current-f-samus-inventory-ba'])
    assert route['bytes']+100000000<500000000 and inventory['bytes']+20000000<120000000
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size<70000000000
    result=dict(status='PROGRESS_FIRST_CURRENT_F_FULL_FIXED_CLEAR_AND_ADDITIONAL_SAMUS_ATTACK_COMPONENTS',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),prior_handoff_sha256=sha(prior),
      previous_goal_turn_classification='progress: AZ installed/reviewed the F Ice active-pass optimization, independently verified D Sophia/Lance full clears and real F intrinsic bomb use.',
      current_goal_turn_classification='progress',checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),
      shared_main=dict(sources_rehashed=457,generated_rehashed=11,primary_artifacts_rehashed=8,production_revision='F',runtime_edits_this_turn=False),
      ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in c['builds']},references={n:dict(sha256=sha(V/n),bytes=(V/n).stat().st_size)for n in refs},
      completed_evidence=[
        'First current F complete ordinary proof: Sophia/Easy/MMC3 K and independentfixed L25404frames/25403polls,all6stages,zero deaths,real2-3 entry25380 and25 controlled rowsX40to67.',
        'Root independently rehashes101 frozen receipts/457sources/11generated/8artifacts, compares all9whole canonical CSVs byte-for-byte and checks fixedsingle10k endpoint identity/control. No two-run RAM or MMC5/media/arsenal claim.',
        'Samus F/G add3 real bomb defeats; J adds3 Goomba defeats via grounded planted-bomb retreat, then genuine Up unmorph. Original C2-bomb-kill witness remains separately verified.',
        'Actual supported16px brick-step fresh-A witness and11600 I/J wholemovement/input prefix equality; current F Samus L clears1-1/1-2/1-3 and reachescastle.',
        'Unchanged explicit Hard inventory fixture passes6 private pickups/map on both F mappers; actual missile spawn/spending and Ice/Wave creation assertions. Morph/Varia/Screw effects and Long are carefully qualified, no natural-block acquisition claim.'],
      retained_negatives=dict(Samus=dict(E='9457 rearKoopa2 contact; front-only bomb controller ignored it.',
        F='Controllerguard10090 after held-Up atboost apex.',G='Controllerguard after completed Up action remained nearest reference.',
        H='Controllerguard11999 at16px brickstep1361/Y96.',I='Actualdeath11819 toGoomba3 after boost delayed subsequent volley.',
        J='Controllerguard12823 while generic stationary bomb policy waited acrosspipewall; actual retreatvolley has3Goombas, not initial2.',
        K='FreshUp works12615, then immediate remorph/wait for a distantGoomba yieldsguard13165; initial diagnosis superseded.',
        L='Actualdeath21109 toBowser0 ID45/X2179/Y113 HP80 againstSamus2164/Y128. Earlier flame assumption corrected; rawowner retained.'),
        root_reviewer='review-bb-host-negative preserves initial bad flame-ID assertion and exact failed reviewer before actor-corrected successor.'),
      root_native_handles_closed=dict(E23574=1,F81645=1,G78124=1,H1444=1,I21075=1,J22068=1,K63218=1,L87576=1,inventory29145=0),root_live_native_handles=[],
      specialists=dict(link_simon_ryu='F Sophia frozen336.25MB/500MB, no child. New Link F500MB/100MBreserve: lastreported E80933, actual1-2 entry6359, laterpit control recovery. OriginalSimon/Ryu/arsenal remain open.',
        mario_luigi_scrooge_s2='F Bill actualcastleclear/2-1entry19296, with realnonfatalBowserinjury andtierloss. Lastreported L83155 actualstairfresh-A correction; ~245MB/500MB,100MBreserve. RemainingBill/Lance/Mario/Luigi/Scroge obligations retained.',
        samus_contra_s2='ImmutableD MegaMan actual2-2 X2481; species7/10/11 corrections additive. AJ interrupted by host clock/timeout, host23809terminal1 and zero actual Mesen processes independently checked before exact-policy/prefix AM retry. Lastreported1GB/100MBreserve; Bass/arsenal pending.'),
      performance=dict(current_F_active_leaf='Prior matched native-start E/F work25percent lower active Ice palette pass; exact output/callers/ISR checks remain pinned in AZ. No new whole-game FPS or lag-solved claim.',broader_lag_optimization_complete=False),
      budget=dict(workspace_bytes=size,global_cap_bytes=70000000000,root_route_phase=route,root_route_cap=500000000,root_route_final_reserve=100000000,
        root_inventory_phase=inventory,root_inventory_cap=120000000,root_inventory_reserve=20000000,retains_all_lossless_and_negatives=True,
        cap_source='User explicitly requested retaining lossless captures and raising the original30GB cap;70GB is the current internal working ceiling.'),
      remaining_requirements=['All14 identities and every66 inventory entry still require full final-build acquisition/selection/tier/contact/pose/water/terrain/graphics/palette/SFX/lifecycle coverage.',
        'Complete current-F remaining routes, preserving actual source/mapper/mode scopes; Sophia MMC5 remains unexecuted.',
        'Finish source-bound runtime/fixture review of73 original suite failures and separate stockMario comparison; no full-suite green claim.',
        'Profile and optimize remaining laggy abilities/powerups, then retain, decode and inspect final all-character lossless recordings, including original1-1 shortcut/nonshortcut/everyenemy/item scope.'],
      next_root_action='Use actual L castle actor/HP/position receipts for a real boss-aware control recovery. Bowser is alive at80HP; do not reuse the incorrect flame diagnosis. Preserve fullprefix then independently replay any complete clear.',
      QA=dict(path='docs/qa/easy-hard-legacy-v49.md',sha256=sha(R/'docs/qa/easy-hard-legacy-v49.md')),
      all_roster_complete=False,all_arsenal_complete=False,final_recordings_complete=False,goal_status='active',accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=sha(out),workspace_bytes=size,root_route=route,goal_complete=False)),flush=True)
if __name__=='__main__':main()
