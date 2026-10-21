"""Independently admit frozen current-H Pit, retaining every source qualification."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';A=V/'specialist-pit-rygar-current-h-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def main():
 out=V/'root49-pit-h-root-review-fp.json';index=V/'root49-goal-coverage-fp.json';handoff=V/'root-current49-progress-fp.json';assert not any(p.exists()for p in[out,index,handoff])
 cat=A/'freeze-pit-f.json';hand=A/'handoff-pit-e.json';assert sha(cat)=='84febf0beeffeaa2e6270b239042ad5d9fd0505bed002ec60b2388591703e19c'and sha(hand)=='0ddec5d431d6c82e3f4b3292004b991439dfc6cc60c2821badf1283a4441a257'
 args=[sys.executable,str(A/'review-pit-f.py'),'--catalogue',str(cat),'--sha256',sha(cat)]
 q=subprocess.run(args,cwd=R,capture_output=True,text=True);log=V/'root49-pit-h-root-review-fp.log';log.write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 z=read(hand);assert z['result']['cleared']and z['result']['frames']==25750 and z['support']['accepted_launches']==153 and not z['support']['unclassified']
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';c=read(cp)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==a['sha256']
 d=R/z['proof'];m=read(d/'manifest.json');assert m['verified_through_2_2']and m['rom_sha256']=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
 sys.path.insert(0,str(R/'tools/audit'));from review_roster49_h_transfers_dl import hardware
 hw=hardware(d,25750);assert hw['actual_DMA']==22440
 receipt=dict(status='PASS_ROOT_ACTUAL_H_PIT_FULL_FIXED_BASE_WITH_QUALIFIED_NATIVE_SUPPORT',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),catalogue_sha256=sha(cat),handoff_sha256=sha(hand),catalogued_files=len(read(cat)['files']),independent_review_log_sha256=sha(log),manifest=str((d/'manifest.json').relative_to(R)),manifest_sha256=sha(d/'manifest.json'),identity=6,variant=0,mapper='mmc3',execution_revision='H',result=m['result'],hardware=hw,support=z['support']['kinds'],qualified_corner_frame=5872,spring_physical_contact=18699,spring_armed_nested_callbacks=18707,source_motion_candidate=z['hardware']['motion_flag_qualification'],limits=z['limits']+['All original native source/art/audio/power qualifiers retained. No Pit tier2 flight/acquisition, Hard/MMC5, exact source-alpha or final movie claim.'],goal_complete=False)
 out.write_text(json.dumps(receipt,indent=2)+'\n')
 prior=V/'root49-goal-coverage-fj.json';assert sha(prior)=='0995c6c662106a1ea8e402d477b045dc6bba4cb48a63efff64047c7f3f456da8';j=read(prior)
 row=next(v for v in j['roster']if(v['character'],v['variant'])==(6,0));assert not row['current_H_independently_admitted_base_routes']
 row['current_H_independently_admitted_base_routes']=[dict(identity=6,variant=0,manifest=receipt['manifest'],manifest_sha256=receipt['manifest_sha256'],result=receipt['result'],hardware=hw,root_review_sha256=sha(out))]
 row['pinned_full_clear_candidates'].append(dict(revision='H',mapper='mmc3',manifest=receipt['manifest'],sha256=receipt['manifest_sha256'],frames=25750,recorded=False));row['current_H_discovery_candidate'].update(full_hardware_proof_pending=False,root_admitted=True)
 assert sum(bool(v['current_H_independently_admitted_base_routes'])for v in j['roster'])==10
 for v in j['roster']:assert not any(v[n]for n in ['base_moves_and_power_tiers_complete','all_specials_upgrades_complete','final_recording_complete','overall_complete'])
 j.update(prior_index_sha256=sha(prior),current_H_actual_MMC3_admitted_identity_count=10,current_H_actual_native_mapper_pairs=10,latest_root_Pit_review_sha256=sha(out),goal_complete=False)
 j['completion_scope']=j['completion_scope'].replace('nine independently admitted','ten independently admitted').replace('New Pit H discovery clear is not admitted until full independent hardware/support review.','Pit actual H full replay is independently admitted with its native corner/spring/motion qualifications retained.')
 index.write_text(json.dumps(j,indent=2)+'\n')
 qa=R/'docs/qa/easy-hard-legacy-v49.md';before=sha(qa);assert before=='f6915d6f93be658d55e0a5673fc6b302e84a6cdbdb9ef3b02735c5327e10009a'
 qa.write_text(qa.read_text()+'''

Additive root FP review now admits actual H Pit's independent full replay,
25,750 frames with zero deaths,25 native2-3 control rows and22,440 actual
DMA snapshots independently decoded again. The133-file frozen packet and
source458/generated11/frozen16 proofs recheck. All153 actual accepted launches
are classified:148 solid tops,three live platform owners,one specifically
qualified landing/side-resolution corner at5872,one compressed spring18699.
Nested spring callbacks18707 are the same armed continuation. The one13940
motion candidate retains actual native side/stop chronology, with no universal
writer/source-equivalence claim. Power0→1→0 is observed; exact item/injury
lifecycle and tier2 flight remain separate. The installed H total is now ten
identities and200,388 independently decoded actual DMA snapshots. Samus,
Rygar, Simon and Ryu still need complete current-build proofs. Overall
equipment/source/mode/lag and all-character final media remain incomplete.
''')
 previous=V/'root-current49-progress-fj.json';assert sha(previous)=='f64243a4cea354087f4abed6625c3ab94524b8cd2332c594dc627b93ed891fb8'
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used<80000000000
 handoff.write_text(json.dumps(dict(status='PROGRESS_H_TEN_BASE_ROUTES_WITH_PIT_ROOT_ADMITTED_PRIVATE_I_NOT_INSTALLED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_handoff=dict(path=str(previous.relative_to(R)),sha256=sha(previous)),working_checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),latest_root_review=dict(path=str(out.relative_to(R)),sha256=sha(out)),index=dict(path=str(index.relative_to(R)),sha256=sha(index)),QA=dict(path=str(qa.relative_to(R)),prior_sha256=before,sha256=sha(qa)),workspace_bytes=used,workspace_cap=80000000000,actual_H_admitted_identities=10,actual_H_DMA_total=200388,retained_base_H_recordings=4,private_I_installed=False,main_unchanged_H=True,root_live_native_handles=[],specialists_at_update=dict(mario_luigi_scrooge_s2='Pit frozen/root-admitted. Rygar actualH native correction latestowned99936 live at last owner report,500MB phase/100MB reserve.',samus_contra_s2='Private H Arm B2 layout passes all four builds, original A+4 negative retained; next native publicB source witnesses. Main untouched;1.35GB inclusive plus200MB dedicated/50MB reserve.',link_simon_ryu='FrozenG SimonAS reached2554/2-2;RyuAA reached1922;bothterminal at latestreport.1.8GB phase/100MB reserve; no complete root-admitted candidates.'),completion_scope='All prior FJ requirements remain unchanged. Every14/full equipment/source/mode/lag/finalmedia requirement remains active; ten base clears are partial evidence only.',previous_goal_turn='progress',current_goal_turn='progress',goal_status='active',blocked=False,accepted_release=False,goal_complete=False),indent=2)+'\n')
 print(json.dumps(dict(status=receipt['status'],review_sha256=sha(out),handoff_sha256=sha(handoff),index_sha256=sha(index),QA_sha256=sha(qa),workspace_bytes=used)))
if __name__=='__main__':main()
