"""Save actual D route progress, failed-controller evidence and full open goal."""
from pathlib import Path
import csv,datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def footprint(paths):
    files=set()
    for p in paths:
        if p.is_dir():files.update(x for x in p.rglob('*')if x.is_file())
        elif p.is_file():files.add(p)
    return dict(files=len(files),bytes=sum(p.stat().st_size for p in files))
def main():
    out=V/'root-current49-progress-ax.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json';c=json.loads(cp.read_text())
    assert sha(cp)=='1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88'
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in c['builds']:
        for a in b['artifacts'].values():assert sha(R/a['path'])==sha(R/a['frozen_path'])==a['sha256']
    tails=[]
    for suffix,tag in [('h','reference-h'),('i','gap-i'),('j','obstacles-j'),('k','castle-k'),('l','koopa-l'),('m','gap-m'),('n','landing-n'),('o','paratroopa-o'),('p','stair-p'),('q','cap-q')]:
        p=R/f'build/roster-through-2-2/root49-d-samus-m5-{tag}-2-v0-mmc5'
        log=H/f'native-mmc5-{suffix}.log';assert 'Mesen exit:'in log.read_text()
        m=json.loads((p/'manifest.json').read_text());t=rows(p/'trace.csv')
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['verified_through_2_2']
        assert m['rom_sha256']=='1d84dbb52d73a6748c8663c2bc44b09ac303b7a3e31b78119dfe3e57811f468a'
        owners=[x for x in rows(p/'actual-injury-b.csv')if x['event']=='InjurePlayer'and x['slot']==x['owner']]
        entries={}
        for x in t:
            if x['engine']=='8'and x['mode']=='1'and x['task']=='3':entries.setdefault(x['world']+'-'+x['level'],int(x['frame']))
        tails.append(dict(tag=tag,result=m.get('result'),last_trace=t[-1],stage_entries=entries,
          recent_native_owners=owners[-3:],files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x))for x in p.iterdir()if x.is_file()},
          emulated_writes=False,full_clear=False,source_collision_bug_proven=False))
    q=tails[-1];assert q['result']['frames']==23936 and q['result']['all_six_stages']and not q['result']['cleared']
    assert q['recent_native_owners'][-1]['id']=='10'and q['recent_native_owners'][-1]['slot']=='2'
    (H/'tail-review-ax.json').write_text(json.dumps(dict(status='RETAINED_ORDINARY_MMC5_DISCOVERIES_REACH_2_2_NOT_CLEAR',
      script_sha256=sha(__file__),runs=tails,limits=['Physical native enemy proxies and inclusive edge contacts are not exact original enemy-Q16 proof.',
        'Raw injury snapshots were capped128; later owner CSV does not imply all later whole-RAM snapshots.',
        'O/P rejected wrong host support-plane/tile assumptions. Q binds actual supported C0 cap before jumping.',
        'No final fixed replay, movie or all-arsenal claim.'],goal_complete=False),indent=2)+'\n')
    refs=['root-current49-progress-aw.json','root49-current-d-transfers-a/samus-review-a.json',
      'root49-current-d-transfers-a/controller-review-ax.json','root49-current-d-transfers-a/bill-lance-review-ax.json',
      'root49-current-d-transfers-a/tail-review-ax.json','root49-d-remaining-routes-ax/review.json','root49-goal-coverage-ax.json',
      'specialist-bill-combined-route-a/lance-proof-freeze-aw.json','specialist-bill-combined-route-a/phase-freeze-ay.json',
      'specialist-bill-lance-current-d-a/m3-transfers-freeze-b.json']
    references={n:dict(sha256=sha(V/n),bytes=(V/n).stat().st_size)for n in refs}
    base=list((R/'build/roster-through-2-2').glob('root49-current-d-samus-*'))+list((R/'build/roster-through-2-2').glob('root49-d-samus-m5-*'))
    own=footprint([H]+base+[V/f"smb-crossover-{'mmc3'if p.name.endswith('mmc3')else'mmc5'}-run-{p.name}.log"for p in base])
    bpaths=list((R/'build/roster-through-2-2').glob('root49-d-roster-ax-*'))
    batch=footprint([V/'root49-d-remaining-routes-ax']+bpaths+[V/f'smb-crossover-mmc3-run-{p.name}.log'for p in bpaths])
    assert own['bytes']<1000000000 and batch['bytes']<900000000
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size<70000000000
    ci=V/'agent49-samus-bill-arsenal-a/source-ci'
    differences=[n for n,h in c['source_hashes'].items()if(ci/n).exists()and sha(ci/n)!=h]
    result=dict(status='PROGRESS_FIVE_ACTUAL_D_IDENTITIES_CLEAR_SAMUS_MMC5_REACHES_2_2_FULL_GOAL_ACTIVE',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
      previous_acknowledgement_turn_classification='no progress; the wrong-chat withdrawal/thanks did not cancel the goal',
      current_goal_turn_classification='progress',checkpoint_sha256=sha(cp),shared_main_source455_generated11_artifact8_rehashed=True,
      main_D_unchanged_this_turn=True,ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in c['builds']},references=references,
      completed_evidence=['LanceC independent full31258/zero-death proof rehashed and movement/native rows independently compared.',
       'ActualD Bill31773 andLance31258 full fixed clears; nine whole hardware/audio/controller CSVs literal toC.',
       'ActualD Mario16991 andLuigi17412 full fixed clears; nine whole CSVs literal toC; actual next-level movement40to56/51.',
       'Seven older-tape negative transfers retained with first19field difference/NMI counts, not labeled runtime defects.',
       'SamusMMC5 neutral nine-stream injury owner probe and controller discoveries now visit allsix stages; latestQ fatal23936 in2-2.',
       'Root identifies privateCI composition must preserve both D optimizedfeet/head files and corrects incomplete EffectsAny caller/cost comment.'],
      Samus_MMC5=dict(latest='root49-d-samus-m5-cap-q-2-v0-mmc5',full_clear=False,water_entry=22697,
        nonfatal_Blooper=dict(frame=23394,slot=1,x=796,y=160,playerX=784,playerY=152,power=1),
        fatal_CheepCheep=dict(frame=23936,slot=2,id=10,x=1190,y=53,playerX=1201.5,playerY=35),
        next_action='Investigate earlier actual Blooper contact and later CheepCheep phase, adapt ordinary water controls from real pose/support; independently replay any clear.'),
      private_Ice=dict(installed=False,CI_different_existing_paths=differences,
        preserve_D_files=['src/characters.s','src/sophia_source_terrain.s'],
        known_scope='Freeze/thaw/360-updateSTOP; cannon bypass; beam pool cleanup; sourceNSF24; local blue palette NMI lease; defeated actor AvFrozen cleanup pending final proof.',
        scope_limits='CI protocol/native proofs are specialist-owned candidates until frozen and independently reviewed; initial NSF $EC alias and missed death cleanup remain retained evidence.'),
      root_live_native_handles=[],root_batch_status='41515 terminal0, two clears/seven negatives, independently reviewed',
      specialists=dict(link_simon_ryu='ActiveD Sophia ordinary route: Vclearscastle,2-1entry14726; actual Goomba cluster death16012, preparing next supported control. Phase538.7MB/1GB,100MBreserve.',
        mario_luigi_scrooge_s2='BothD/MMC3 Bill/Lance proofs frozen. D/MMC5 G91368 reportedlive; actual castle boss/flame controller adaptation; phase~200MB/1GB,100MBreserve.',
        samus_contra_s2='PrivateCI fullISR/palette/reset/audio protocols; final defeated-actor AvFrozen/Hi cleanup being proved. Cap950MB/50MBreserve; main unchanged.'),
      budget=dict(workspace_bytes=size,global_cap_bytes=70000000000,root_D_phase=own,root_batch_phase=batch,
        root_phase_cap_bytes=1000000000,root_final_reserve_bytes=100000000,arsenal_phase_cap_bytes=950000000,arsenal_final_reserve_bytes=50000000,
        retains_all_lossless_and_negatives=True,source_of_cap='Explicit user instruction to retain lossless captures and raise the original30GB cap.'),
      regressions=dict(legacy_native_passed=688,legacy_native_failed=73,separate_stock_Mario_comparison_failed=True,full_suite_passed=False,
        scope='Original broad suite wasB; retained failures are not waived or represented as currentD full-suite passes.'),
      next_actions=['Finish SamusMMC5 water route then full independent fixed replay.',
       'Finish SophiaD fullroute/fixedproof and BillMMC5 controller investigation.',
       'Freeze/review complete Ice lifecycle/protocol/cost packet; composeoverD preserving feet/head; build/regress/adopt only after review.',
       'Bind parent behavior and first differing completed update for seven older-tape negatives; recover Scroge1-2 moving-platform route.',
       'Complete every character attack/alternate/upgrade/lag check and final retained lossless recordings; preserve earlier shortcut/nonshortcut scope.'],
      QA=dict(path='docs/qa/easy-hard-legacy-v49.md',sha256=sha(R/'docs/qa/easy-hard-legacy-v49.md')),
      all_roster_complete=False,all_arsenal_complete=False,final_recordings_complete=False,goal_status='active',goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=sha(out),workspace_bytes=size,root_D_phase=own,root_batch_phase=batch)))
if __name__=='__main__':main()
