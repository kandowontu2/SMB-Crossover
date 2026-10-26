"""Freeze the finite eight-route result without rewriting original receipts."""
from pathlib import Path
import argparse,csv,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SHA='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def rows(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 batch=D/'current3cee-eight-routes-v1';bill=D/'current3cee-bill-gap-v1';review=D/'current3cee-eight-routes-review-v3';rootrev=D/'root-current3cee-eight-review-v1';candidate=D/'root-chip-hud-composed-v1'
 assert sha(candidate/'candidate.nes')==SHA
 dependencies={Path(__file__)}
 for ready in[batch/'readiness.json',bill/'readiness.json']:
  z=get(ready);assert all(sha(f)==h for f,h in z['bindings'].items());dependencies|={Path(f)for f in z['bindings']}|{ready}
 original=get(batch/'native/proof.json');assert original['complete']and not original['passed']
 assert get(bill/'execution.json')['passed']and get(bill/'execution.json')['one_worker_released']
 rr=get(rootrev/'root-review-summary.json');assert rr['total_independently_verified_saved_frames']==48450 and rr['total_manually_viewed_sampled_whole_frames']==264
 assert all(sha(z['path'])==z['sha256']for z in rr['routes'])
 dependencies|={batch/'native/proof.json',batch/'execution.json',batch/'launch.json',bill/'execution.json',rootrev/'root-review-summary.json'}
 cases=['megaman-easy','proto-easy','samus-easy','bill-easy','lance-easy','bass-hard','roll-easy','ryu-easy'];result=[];selected=[]
 for case in cases:
  discovery=bill/'discovery'if case=='bill-easy'else batch/'native'/case
  direct=bill/'direct'if case=='bill-easy'else batch/'native'/(case+'-direct')
  m=get(discovery/'manifest.json');d=get(direct/'proof.json');v=get(review/case/'proof.json')
  assert d['passed']and d['ROM_sha256']==SHA and m['result']['cleared']and m['result']['deaths']==0
  assert d['raw_gzip_roundtrip_exact']and d['every_saved_PNG_RGB_exact']and d['actual_PPU_frame_ids_complete']
  assert sha(direct/'direct-frame-index.csv')==d['frame_index_sha256']
  archive=d['raw_lossless_archive'];assert sha(archive['path'])==archive['sha256']
  assert v['passed']and v['numeric_modes_observed']==([1]if case=='bass-hard'else[0])
  assert all(c['exact']for n,c in v['comparisons'].items()if n!='events.csv')and v['comparisons']['events.csv']['gameplay_suffix_exact']
  # Bind full index/archive plus every small receipt/CSV; indexes bind all PNGs.
  dependencies|={Path(archive['path'])}
  for directory in[discovery,direct,review/case,rootrev/case]:
   dependencies|={f for f in directory.iterdir()if f.is_file()and(f.suffix.lower()in['.json','.csv','.lua','.log']or f.name.endswith('PPU.png')or f.name=='whole-PPU-samples.png')}
  s=get(review/case/'selected-frames.json')
  chosen=[z for z in s if z['sheet']=='status-window'or case=='bill-easy']
  assert all(sha(z['path'])==z['sha256']for z in chosen);dependencies|={Path(z['path'])for z in chosen};selected+=chosen
  result.append(dict(case=case,identity=v['identity'],mode=v['mode'],actual_numeric_mode=v['actual_numeric_mode'],discovery=str(discovery),direct=str(direct),result=m['result'],direct_frames=d['direct_frames'],direct_proof_sha256=sha(direct/'proof.json'),archive=archive,review=str(review/case/'proof.json'),review_sha256=sha(review/case/'proof.json'),power_status_transitions=v['power_status_transitions'],source_CHR_commit=v['source_CHR_commit'],completed_loop=v['completed_loop'],request_store_events=v['request_store_events'],hardware_APU_write_count=v['hardware_APU_write_count'],event_file_comparison=v['comparisons']['events.csv']))
 assert sum(z['direct_frames']for z in result)==48450 and len(selected)==78
 oldbill=batch/'native/bill-easy';dependencies|={f for f in oldbill.iterdir()if f.is_file()and f.suffix in['.json','.csv','.lua','.log']}
 source=candidate/'source/src';mm=batch/'native/megaman-easy-direct';tr=rows(mm/'trace.csv');rd=rows(mm/'render.csv');ip=rows(mm/'inputs.csv');low=[]
 for frame in[1286,2475,2871]:
  t=next(z for z in tr if int(z['frame'])==frame);r=next(z for z in rd if int(z['frame'])==frame);window=[z for z in ip if frame-90<=int(z['frame'])<=frame]
  assert window and not any(int(z['mask'])&4 for z in window)
  low.append(dict(frame=frame,trace=t,render=r,preceding_90_frame_input_rows=len(window),Down_observed=False,raw_PPU_path=str(mm/'frames'/f'{frame:06d}.png'),raw_PPU_sha256=sha(mm/'frames'/f'{frame:06d}.png')))
  dependencies.add(mm/'frames'/f'{frame:06d}.png')
 for name in['characters.s','megaman_physics.s','megaman_injury.s']:dependencies.add(source/name)
 put(out/'low-body-open.json',dict(ROM_sha256=SHA,actual_samples=low,source_owner='MegaManGraphics chooses GuestPowerupPose, GuestHurtTicks recoil, MmSliding pose12, then native MmRenderPose/skin/wind/step aliases. Generic render.pose/crouch does not identify these native owners.',finding='Selected actual PPU low-body visibility remains open. No Down in preceding90frame rows; current telemetry omits MmSliding/MmRenderPose/GuestHurtTicks and cannot prove intentional slide/invulnerability. maxSprites13 is source pressure evidence, not an epoch-bound hardware occlusion diagnosis.',limits='No new defect/fix or full sprite fidelity claim; no inferred DMA-row-to-PPU mapping.'))
 put(out/'agent-visual-review.json',dict(agent_visual_review=True,offline_only=True,own_selected_samples=selected,own_sample_count=78,root_summary=str(rootrev/'root-review-summary.json'),root_summary_sha256=sha(rootrev/'root-review-summary.json'),root_verified_all_saved_frames=48450,root_selected_sample_count=264,observations=['Selected physical mushroom/contact/growth and source firing windows are present; exact status transitions are in the route records.','Bill retry gap/flag/movable1-2 wholeframes were viewed. ROOT independently viewed264 samples over all8routes.','No obvious displaced or green background block corruption in this selected sample. Mega low-body visibility remains open.','Bass forward buster/arm is visible in selected firing frames; RollHP28/EN28 is readable.'],limits='Selected-frame agent inspection, not human review or every-frame/source-fidelity/all-pixel improvement verdict. Tiny Parodius font, mixed body overload and original areaFALSE/natural Buffer2 limitation remain independent open/history findings.'))
 report=ROOT/'docs/qa/current3cee-eight-routes-native-2026-10-26.txt'
 lines=['Current3cee eight ordinary1-1 routes: bounded native/replay packet','',f'ROM SHA256 {SHA}',f'External final packet: {out}',f'Original main aggregate remains FALSE: {batch}/native/proof.json','Seven original passing Easy/Hard routes plus a separately passing controller-only Bill retry are selected below. No original result was rewritten. Native worker is released.','', 'case | numeric mode | discovery endpoint | direct saved frames | deaths']
 lines += [f"{z['case']} | {z['actual_numeric_mode']} | {z['result']['frames']} | {z['direct_frames']} | {z['result']['deaths']}"for z in result]
 lines += ['', 'Total: 48,450 actual endFrame PNG/RGB frames and lossless records; complete200..endpoint-1 capture, index/archive roundtrip, matching independent inputs/trace and movable1-2 outcome. ROOT independently verified all48,450 and inspected264 selected wholePPU frames. This agent inspected66 selected contact/status frames plus12Bill overview samples (78sample placements, not claimed unique).', '', 'Observed item/use scope: all8 PlayerStatus0->1 readbacks; Mega/Bill/Lance later1->0. Native question-block/mature mushroom acquisition windows are visible for Mega/Proto/Samus/Bill/Lance/Roll/Ryu. Bass late power readback occurs7166; the selected window does not identify the physical item owner. Engine9contact->commit starts: Mega824->885 and1178->1239; Proto835->896; Samus995->1055; Bill975->1035 and2290->2350; Lance1019->1079 and2338->2398; Bass7106->7166; Roll824->824; Ryu976->1037. These are finite readbacks/window interpretations, not every-item/tier/weapon lifecycle certification.', 'Actual request-store lists and perframe APU activity are bound perroute. They do not prove audible waveform/duration/priority/original audio fidelity, nor one distinct SFX/use perstore. No audio source was modified.', '', 'Replay equality: inputs/trace/render/audio-events/OAM/CHR/CHR-commit/scroll/stomp/completed-loop CSVs exact for all8. events.csv alone has three discovery pregame menu request rows204/205 absent in the fixed replay logger; native inputs/trace are exact and every event from actual first1-1 entry is literally exact. This retained selectionDone observation-gate difference is disclosed, not relabeled wholefile equality.', '', 'Bill original death failure: firstpit worldX1419/y245, lastgrounded takeoff near1323 spent jump arc beforepit1376..1439. Approved retry changes controller returns only world0/level0 X1304..1490: releaseA/walk to grounded1356 then holdRight/A until landing. Original policy body runs everywhere; no outcome/position/resource/physics/ROM writes. Original FALSE remains.', '', 'Graphics boundary: source/DMA bodyCHR checks pass, completed-loop movement limits pass, actual hardware8sprite settings remain enabled. Existing harness validates committed body mapping, resident stomp opcode/hook and scroll observations. It does not include a complete fiveSMC/SP/NMI ownership oracle for these routes; those claims are not made. No constant60Hz/lag improvement/all-pose fidelity claim.', 'Mega low-body samples1286/2475/2871 remain open. No preceding90frame Down input, but native MmSliding/MmRenderPose/GuestHurtTicks were not logged. Source alone cannot classify these actual images as intentional slide/injury or establish a first wrong OAM owner. No code repair is justified from this packet.', '', 'Stable executed commands:', f'python -B tools/audit/current3cee_eight_routes_run_v1.py --packet "{batch}" --native-grant', f'python -B tools/audit/current3cee_bill_gap_v1.py run --batch "{batch}" --output "{bill}" --native-grant', 'These one-shot native runs are finished; the commands document the frozen execution, not authorization to repeat.', '', 'ROOT review summary: '+str(rootrev/'root-review-summary.json'), 'ROOT summary SHA256: '+sha(rootrev/'root-review-summary.json'), 'Limits: sevenEasy + BassHard only; ordinary starting form plus observed physical progression, not allpowerups/allfamilies/allSFX/allmodes/fullroster completion. Earlier mixed Parodius/Sophia bodyvisibility and original areaFALSE/conditional natural Buffer2 overlap limitations are unchanged. No production, Downloads, settings or Git changes by this agent.']
 report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 dependencies|={report,out/'low-body-open.json',out/'agent-visual-review.json'}|set((ROOT/'tools/audit').glob('current3cee*.py'))
 bindings={str(f.resolve()):sha(f)for f in sorted(dependencies,key=str)};put(out/'manifest.json',bindings)
 final=dict(passed=True,selected_eight_routes_passed=True,original_batch_passed=False,original_batch_FALSE_preserved=True,ROM_sha256=SHA,native_worker_released=True,native_new_run=False,profiles=result,total_direct_saved_frames=48450,ROOT_review_summary_sha256=sha(rootrev/'root-review-summary.json'),report_path=str(report),report_sha256=sha(report),manifest_sha256=sha(out/'manifest.json'),bindings_count=len(bindings),scope='Finite selected8 current-ROM1-1replays with retained Bill failure/controller retry. Open visibility and allitem/audio/fullroster limits retained.')
 put(out/'proof.json',final)
 checkpoint=ROOT/'docs/qa/checkpoints/2026-10-26/current3cee-eight-routes-v1';checkpoint.mkdir(parents=True,exist_ok=False)
 for n in['proof.json','manifest.json','agent-visual-review.json','low-body-open.json']:(checkpoint/n).write_bytes((out/n).read_bytes())
 (checkpoint/'README.txt').write_text('Additive selected8route checkpoint; original batchFALSE remains. No binary/capture/settings copied. Large exact proofs/images remain at '+str(out)+'\nReport: '+str(report)+'\n',encoding='utf-8')
 put(checkpoint/'checkpoint-manifest.json',{str(f.relative_to(checkpoint)):sha(f)for f in sorted(checkpoint.iterdir())if f.is_file()})
 print(json.dumps(dict(passed=True,proof=str(out/'proof.json'),proof_sha256=sha(out/'proof.json'),manifest_sha256=sha(out/'manifest.json'),report_sha256=sha(report),bindings=len(bindings),checkpoint_manifest_sha256=sha(checkpoint/'checkpoint-manifest.json')),indent=2))
if __name__=='__main__':main()
