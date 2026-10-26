"""Freeze five actual acquired-ability components and selected-frame review."""
from pathlib import Path
import argparse,collections,csv,hashlib,json,shutil
from final_item_abilities_remaining731_run_v1 import verify_manifest,PROFILES
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['ready','reviews','pending','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==CURRENT
 bound=verify_manifest(a.ready/'manifest.json');pending=json.loads((a.pending/'proof.json').read_text());assert pending['passed']and pending['pending_epochs']==3 and pending['wholeframes']==9
 rows=[];totals=collections.Counter();files=set();sheets=[];components=[]
 for profile in ready['profiles']:
  name=profile['profile'];native=Path(profile['output']);proof=json.loads((native/'proof.json').read_text());n=json.loads((native/'native-abilities.json').read_text());review=a.reviews/name;r=json.loads((review/'proof.json').read_text());count=verify_manifest(review/'manifest.json')
  family,hard,mode,cases=PROFILES[name];assert proof['passed']and r['passed']and n['hard']is hard and n['actual_mode_readback']==mode and len(n['abilities'])==cases
  for fn,record in proof['output_bindings'].items():f=native/fn;assert sha(f)==record['sha256']and f.stat().st_size==record['bytes'];files.add(f)
  audio=list(csv.DictReader((native/'apu.csv').open()));audio_real=sum(0x4000<=int(q['register'])<=0x4013 or int(q['register'])in[0x4015,0x4017]for q in audio)
  assert len(audio)==n['apuWrites']
  growth=sum(q['transformCalls']for q in n['physical_collections']);assert growth==120 and len(n['physical_collections'])==2
  metrics=dict(ability_cases=cases,physical_collections=2,committed_transform_updates=growth,updates=n['updates'],nmis=n['nmis'],irq31_stores=n['irq_scroll_stores'],CHR_bank_latch_checks=n['hardware_chr_checks'],original_publication_endFrame_checks=n['complete_dma_checks'],actual_full_PPU_frames=r['actual_full_PPU_frames'],completed256_DMA=r['completed_full256_DMAS'],DMA_data_write_checks=r['data_write_checks'],startFrame_snapshots=r['startFrame_snapshots'],scoped_safe_enables=r['scoped_safe_render_enables'],pending_cold_starts=r['pending_startFrame_count'],case_screenshots=len(r['all_case_captures_exact']),selected_gameplay_frames=r['selected_unique_whole_PPU_frames'],selected_gameplay_placements=r['selected_placements'],old_4000_4017_counter=n['apuWrites'],actual_audio_register_stores=audio_real)
  totals.update(metrics)
  row=dict(profile=name,ROM_sha256=CURRENT,actual_mode=mode,passed=True,native_proof=str(native/'proof.json'),native_proof_sha256=sha(native/'proof.json'),review=str(review/'proof.json'),review_sha256=sha(review/'proof.json'),review_bindings_verified=count,min_sampled_SP=n['minSP'],metrics=metrics,abilities=n['abilities'],physical_collections=n['physical_collections'],sheets=r['sheets'])
  rows.append(row);sheets +=[dict(profile=name,**s)for s in r['sheets']]
  obs={'pit':['six hammer contact/defeat/cleanup cases, bothfacings at alltiers','tier0/1 flight refusal','tier2 sixtyfuel/exhaust/landing60recharge/nextjump and nineteenfuel release/recharge'],
   'rygar':['standing disk free/hit at alltiers,bothfacings','40/64/88 exact extension/retraction/mirrored hand anchor','twelve actual catches/native cleanup and six actual Goomba defeats'],
   'scrooge':['three tier-groundpogo cases each three real rebounds/release','six actual airborne descending Goomba hits/defeats and safe nativeFA2500 rebound','native protection/release/cleanup; cane ability does not gain a new tier-specific effect']}[family]
  components.append(dict(identity={'pit':'Pit','rygar':'Rygar','scrooge':'Scrooge'}[family],actual_mode='hard'if hard else'easy',actual_numeric_mode=mode,ROM_sha256=CURRENT,track='A+B',native_receipt=row['native_proof'],native_receipt_sha256=row['native_proof_sha256'],A_observed=['actual head/block/reveal/fullrise/no-premature-grant','two physical0→1→2 collections/two60committed transforms'],A_setup='Staged visible/logical arena; explicit post-rise item contact alignment. Not an unassisted route.',B_observed=obs,B_setup='Actual controller/native use after physical acquisition; source-valid staged world/player/motion/oldempty-pools/protection/Goomba scaffolding, no tier/fuel/reach/pogo outcome writes.',complete_powerup_cell=False,remaining=['capped pickup','ordinary arrow/cane/air/crouch/edge/pool uses outside these plans','star/1up','damage/downgrade/reacquisition','all original sourcepixel/audio/no-flicker fidelity']))
  files.update([native/'proof.json',review/'proof.json',review/'manifest.json']);files.update(f for f in review.rglob('*')if f.is_file())
 assert totals['ability_cases']==52 and totals['physical_collections']==10 and totals['committed_transform_updates']==600
 assert totals['completed256_DMA']==11650 and totals['actual_full_PPU_frames']==12221 and totals['selected_gameplay_frames']==627
 assert len(sheets)==62
 visual=dict(passed=True,ROM_sha256=CURRENT,agent_visual_review=True,selected_gameplay_wholeframes=627,selected_gameplay_placements=663,additional_cold_transition_wholeframes=9,total_selected_wholeframe_placements=672,sheets=sheets,cold_context_sheet=pending['sheet'],cold_context_sheet_sha256=sha(pending['sheet']),findings=[
  dict(status='no_obvious_new_graphics_or_ability_defect_in_main_selected_windows',scope='All62case/pickup sheets inspected: item emergence/contact/transform,hammer,flight/refusal/exhaust/recharge,disk extension/retraction/catch/hit,pogo ground/descending contact/rebound/release/cleanup. Not every12221frame/sourcepixel.'),
  dict(status='source_policy_readability_limit_preserved',scope='Rygar powered reach shows a gap between arm and disk. Frozen expanded_weapons.s Chain explicitly emits one chain sprite twelve pixels behind disk center. No new CHR-loss/fix claim; original pixel-fidelity comparison is outside this component.'),
  dict(status='cold_blanked_transition_preserved',scope='EachHard run PPU111 has a thin backdrop strip during the render-disabled Options rebuild;112/113 show stable Options(before mode toggle). Mask6 through pending start112, actual DMA completes112:-1:105, enable112:-1:116. No completed-image waiver or universal late-NMI/transition-pixel fidelity claim.')],limits=['Selected636unique wholeframes (627main+9cold),not all12221frames or allposes.','Actual foreground state can precede displayed OAM publication; all case images are bound to actual indexed frames and observed startFrame/DMA.','No full powerupcell,cappedpickup,star/1up,injury/reacquisition,campaign,sourceaudio/waveform or global no-flicker pass.'])
 put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n')
 put(a.output/'visual-review.json',visual);put(a.output/'ledger-components.json',components)
 report=ROOT/'docs/qa/final-item-abilities-remaining731-native-2026-10-26.txt';assert not report.exists()
 lines=['Remaining five current731 acquired-ability native components,2026-10-26','',
 'PASS:exact52plannedcases,5one-shot launches in grantedorder;no retries/firstFALSEs.',
 'Worker explicitlyRELEASED. No production/default/settings/Git changes.',
 'ROM '+CURRENT,'Ready '+str(a.ready/'proof.json'),'Ready SHA256 '+sha(a.ready/'proof.json'),'',
 'Profile | actualmode | cases | updates | fullPPU | full256DMA | starts | safeenables | minSP | nativeSHA']
 for r in rows:
  m=r['metrics'];lines.append(f"{r['profile']} | {r['actual_mode']} | {m['ability_cases']} | {m['updates']} | {m['actual_full_PPU_frames']} | {m['completed256_DMA']} | {m['startFrame_snapshots']} | {m['scoped_safe_enables']} | {r['min_sampled_SP']} | {r['native_proof_sha256']}")
 lines +=['','Combined actual counts:52abilities,10physicalcollections,600committedtransformupdates;',
  '10462updates/10457NMI/10462IRQ31stores/minSP193;125484CHRbank-latchchecks;',
  '9986original publication/endFramechecks.12221fullPPUframes and301originalcase',
  'screenshots all hash/dimension/index checked;everycasecapture equals its exact rawslice.',
  '11650actualcompleted256DMAs/2982400datawrites,12216startFrames and9585scoped',
  'safe enables independently reparsed. All256source/hardware bytes,destinations,',
  'perwrite mask andE008completion guards pass.3coldpendingstarts are explicitly',
  'pending,never relabeled completed. Theirfull256transfers complete while mask6',
  'at112:-1:105;nextenable112:-1:116. Actualneighborframes111..113 are retained.',
  '',
  'Observed family scope:',
  'PitHard:6actualhammer hits/defeats,bothfacings/alltiers;2lowtierflightrefusals;',
  'tier2full60fuel burn/exactFE8000lift/exhaust/ground60recharge/nextjump and19fuel',
  'partialrelease/recharge. The earlierPitEasy10case packet remains separate.',
  'RygarEasy+Hard:12diskuses eachprofile,free/hit xbothfacings x3tiers;actual40/64/88',
  'extension/retraction,mirrored nativehandanchor,twelvecatches and6Goombadefeats each.',
  'ScroogeEasy+Hard:9cases each;each3groundpogo cases chains3realrebounds;6actual',
  'descending enemyhits/defeats withFA2500sourcebounce,noinjury,release/cleanup.',
  'Tier is hostprogression,not an invented stronger cane.',
  '',
  'A/B setup:two actual head/block/reveal/fullrise/no-premature-grant physical',
  'collections0→1→2 perprofile,two60updatetransforms. Explicitpostrise itemcontact',
  'alignment remains. B world/player/motion/facing/fractions/oldempty pools/protection',
  'and legal nativeGoomba targets are controlled at GameLoopboundary. Scrooge targets',
  'enter onlyafter actualairborne separation. No tier/fuel/flight/reach/pogo result',
  'writes. This is physical delivery withdisclosedsetup plus real acquired use,not',
  'an unassisted route or natural earned-depletion claim.',
  '',
  'Agent imageinspection:all62mainwholePPUcontact sheets/627uniquegameplayframes',
  '(663placements) plus9coldneighborframes on1sheet. No obviousnew graphic/ability',
  'defect in the selected mainpickup/transform/disk/pogo/flight/cleanupwindows.',
  'Not all12221frames/sourcepixels/allposes or sourceart/originalgame fidelity.',
  'Rygarlongreach chain gaps follow explicitone-chain-sprite/12pxsourcepolicy;',
  'not newly proved CHR corruption andnot a readability/fidelity closure.',
  'HardPPU111thinstrip is retained during rendering-off Options rebuild;112/113',
  'are stable OptionsbeforeactualHard toggle. No global transitionpixel/lateNMI',
  'claim andno completed-source-versus-partial-hardware comparison waiver.',
  '',
  'Counterprecision:unchangedoldapuWrites62218 counts4000..4017 includingDMA and',
  'controllerstores;actualaudio-register subset32245. No waveform/audibility/SFX',
  'priority/originalaudiofidelity verdict from those counts.',
  '',
  'All source/NMI/IRQ/fiveSMC/actualbank/stack/CHR/mode assertions remain unchanged.',
  'Actual0/1 mode readbacks are required. Historical84/220withdrawals and529mode',
  'receipts retain exactoldhashes;current52plansare genuinelydifferent actualmode',
  'runs. Additive ledger-components.json doesnotmarkcompletepowerupcells.',
  '',
  'Open:cappedpickup,ordinaryPitB-arrow/Scroogecane/air/crouch/edge/pool cases',
  'outside theseplans,star/1up,damage/downgrade/reacquisition,allsourcepixels/audio,',
  'globalno-flicker/campaign. No new native scope orgrant follows thisfreeze.','',
  'Exactsheet paths and allactualframeplacements/epoch/rawbindings:']
 for r in rows:lines.append(r['profile']+': '+r['review']+' SHA256 '+r['review_sha256'])
 lines +=['Coldsource/actual9framecontext: '+str(a.pending/'proof.json'),'Visualreview: '+str(a.output/'visual-review.json'),'Ledgercomponents: '+str(a.output/'ledger-components.json')]
 report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 summary=dict(passed=True,component_only=True,goal_complete=False,ROM_sha256=CURRENT,native_launches=5,retries=0,native_worker_released=True,actual_profiles=rows,totals=dict(totals),min_sampled_SP=193,agent_selected_frame_review_sha256=sha(a.output/'visual-review.json'),ledger_components_sha256=sha(a.output/'ledger-components.json'),ready_sha256=sha(a.ready/'proof.json'),ready_bindings_verified=bound,report_sha256=sha(report),complete_powerup_cells=False)
 put(a.output/'summary.json',summary)
 checkpoint=ROOT/'docs/qa/checkpoints/2026-10-26/remaining731-acquired-abilities';checkpoint.mkdir(parents=True,exist_ok=False)
 for name in ['summary.json','visual-review.json','ledger-components.json']:shutil.copy2(a.output/name,checkpoint/name)
 (checkpoint/'README.txt').write_text('Five narrowcurrent731Aphysical/Bcontrolled-acquired-use components,actualnumericmodes,52plans. No retries,workerreleased. Rawlosslesscaptures remainexternal. Exactnativeproofs,source/frame/epoch/selection paths andlimits in summary/visualreview. Completepowerupcells remainFALSE;oldreceipts untouched.\n',encoding='utf-8')
 files.update([Path(__file__),report,a.ready/'proof.json',a.ready/'manifest.json',a.output/'summary.json',a.output/'visual-review.json',a.output/'ledger-components.json']);files.update(f for f in a.pending.rglob('*')if f.is_file());files.update(f for f in checkpoint.iterdir()if f.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files,key=str)]))
 put(checkpoint/'manifest.json',dict(bindings=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in checkpoint.iterdir()if f.is_file()]))
 final=dict(**summary,manifest_sha256=sha(a.output/'manifest.json'),manifest_bindings=len(files),checkpoint_manifest_sha256=sha(checkpoint/'manifest.json'))
 put(a.output/'proof.json',final);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),report_sha256=sha(report),checkpoint_manifest_sha256=sha(checkpoint/'manifest.json')),indent=2))

if __name__=='__main__':main()
