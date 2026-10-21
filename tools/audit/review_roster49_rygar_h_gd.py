"""Independent root admission of Rygar's actual H clear, retaining late-split finding."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';A=V/'specialist-pit-rygar-current-h-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 out=V/'root49-rygar-h-root-review-gd.json';index=V/'root49-goal-coverage-gd.json';assert not out.exists()and not index.exists()
 cat=A/'freeze-phase-n.json';assert sha(cat)=='1af035b219367321a10e1a002efad5c4f82f96aff3857dd291c7a158bcadbcbf'
 q=subprocess.run([sys.executable,str(A/'review-phase.py'),'--catalogue',str(cat),'--sha256',sha(cat)],cwd=R,capture_output=True,text=True)
 log=V/'root49-rygar-h-root-review-gd.log';log.write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0,q.stderr
 hand=A/'handoff-rygar-n.json';assert sha(hand)=='70e53d5efbec528837065b63a9abf08d24047ab4b08866b3452be30e93960123';z=read(hand)
 window=A/'rygar-window-p.json';assert sha(window)=='5865922048c89d06538a954927a21dad3dc03f13a17cf0555e1d3678e8f8aa16'
 d=R/z['proof'];m=read(d/'manifest.json');assert m['verified_through_2_2']and m['rom_sha256']=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
 assert m['result']['frames']==21537 and m['result']['deaths']==0 and z['support']['kinds']=={'actual_native_terrain_top':107,'actual_native_platform_owner':3,'actual_native_compressed_spring':1}and not z['support']['unknown']
 sys.path.insert(0,str(R/'tools/audit'));from review_roster49_h_transfers_dl import hardware
 hw=hardware(d,21537);assert hw['actual_DMA']==18621
 receipt=dict(status='PASS_ROOT_ACTUAL_H_RYGAR_CONTROLLER_CLEAR_WITH_OPEN_LATE_HUD_SPLIT',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),catalogue_sha256=sha(cat),catalogued_files=len(read(cat)['files']),handoff_sha256=sha(hand),read_only_review_log_sha256=sha(log),manifest=str((d/'manifest.json').relative_to(R)),manifest_sha256=sha(d/'manifest.json'),identity=7,variant=0,mapper='mmc3',execution_revision='H',result=m['result'],hardware=hw,support=z['support']['kinds'],late_HUD_split=dict(raw_callback_frame=4943,completed_frame=4944,scanline=34,dots=[277,289],aligned_DMA=1,aligned_lag_flag=0,previous_DMA=0,previous_lag_flag=1,window_sha256=sha(window),cause='Unresolved; not intentionally deferred by NMI source. Focused diagnosis separately authorized.',resolved=False),motion_flags='5136 actual native StopPlayerMove;15428/15490 are signed16 high-byte wrap, actualdy-4/+4.',limits=z['limits'],source_perfect=False,clean_physical_video=False,goal_complete=False)
 out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 prior=V/'root49-goal-coverage-fp.json';j=read(prior);row=next(v for v in j['roster']if(v['character'],v['variant'])==(7,0));assert not row['current_H_independently_admitted_base_routes']
 row['current_H_independently_admitted_base_routes']=[dict(identity=7,variant=0,manifest=receipt['manifest'],manifest_sha256=receipt['manifest_sha256'],result=receipt['result'],hardware=hw,root_review_sha256=sha(out),open_physical_findings=[receipt['late_HUD_split']])]
 row['pinned_full_clear_candidates'].append(dict(revision='H',mapper='mmc3',manifest=receipt['manifest'],sha256=receipt['manifest_sha256'],frames=21537,recorded=False))
 assert sum(bool(v['current_H_independently_admitted_base_routes'])for v in j['roster'])==11
 j.update(prior_index_sha256=sha(prior),current_H_actual_MMC3_admitted_identity_count=11,current_H_actual_native_mapper_pairs=11,latest_Rygar_root_review_sha256=sha(out),goal_complete=False)
 j['completion_scope']='Eleven actual H/Easy/MMC3 base identities independently admitted, with retained source/physical/equipment limitations and Rygar completed4944 HUD split unresolved. Four retained H base movies. All14/full equipment/intrinsic/source/mode/lag/final all-roster media requirements remain active. Private I and Arm correction not installed.'
 index.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
 qa=R/'docs/qa/easy-hard-legacy-v49.md';before=sha(qa);assert before=='32f3a716bf3cdf2ed7ffa7312c439b16c155df48d499bb6c442d6b6e8fd53e19'
 backup=V/'root49-QA-before-gd.md';assert not backup.exists();backup.write_bytes(qa.read_bytes())
 addition='\r\n\r\nRoot GD independently reexecutes the435-file Pit/Rygar packet and separately\r\ndecodes Rygar H21537/21536, zero deaths, all six stages and25 responsive2-3\r\ncontrols. All111 actual launches classify as107 terrain,three live platform\r\nowners and one compressed spring;18,621 DMA snapshots decode independently.\r\nThis is the eleventh H base identity and219,009 total independently decoded\r\nDMA snapshots. Rygar tier0 alone and equipment/source/movie limits remain.\r\nThe real late HUD split remains unresolved: raw PPU4943 maps completed4944,\r\nscan34/dots277,289, aligned DMA1/lagFlag0 after prior DMA0/lagFlag1. Both NMI\r\npaths programIRQ31; no intentional34 deferral is claimed. The source owner\r\nand cause need new passive chronology; no clean physical-video claim.\r\nSamus, Simon and Ryu current-build proofs and all broader requirements remain.\r\n'
 temp=qa.with_name(qa.name+'.gd.tmp');assert not temp.exists();temp.write_bytes(qa.read_bytes()+addition.encode('utf-8'));os.replace(temp,qa)
 progress=V/'root-current49-progress-gd.json';assert not progress.exists()
 progress.write_text(json.dumps(dict(status='PROGRESS_ELEVEN_H_BASE_IDENTITIES_OPEN_RYGAR_HUD_FINDING',prior_handoff_sha256=sha(V/'root-current49-progress-fs.json'),root_review_sha256=sha(out),index_sha256=sha(index),QA_before_sha256=before,QA_sha256=sha(qa),current_H_actual_base_identities=11,actual_H_DMA_total=219009,working_revision='H',private_I_installed=False,private_Arm_installed=False,remaining_base=['Samus','Simon','Ryu'],full_scope_unchanged=True,goal_complete=False),indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(review_sha256=sha(out),index_sha256=sha(index),progress_sha256=sha(progress),QA_sha256=sha(qa))))
if __name__=='__main__':main()
