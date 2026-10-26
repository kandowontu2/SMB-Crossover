"""Freeze the one granted Hard-ice pilot; narrow success is not full adoption."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return dict(path=str(p),sha256=sha(p))
def rows(p):return[{k:int(v)if v.lstrip('-').isdigit()else v for k,v in r.items()}for r in csv.DictReader(p.open())]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=D/'cv3-remaining-steady-v3/freeze-v2/readiness-source-only.json';assert sha(ready)=='e56d43409453ea54cd898637078498aa6d5d9b7ad3e08d46f4347ef9ed7b15cb';r=json.loads(ready.read_text())
 for path,h in r['all_frozen_bindings'].items():assert sha(path)==h,path
 fixture=D/'cv3-remaining-steady-native-v2/hard-ice';launch=fixture.parent/'native-hard-ice-v1/proof.json';l=json.loads(launch.read_text());assert l['native_guard_passed']and l['retries']==l['exit_code']==l['verification_exit']==0 and l['cell']=='hard-ice'and l['settings_before_sha256']==l['settings_after_sha256']==r['settings']['sha256'];g=json.loads((fixture/'proof.json').read_text());assert g['passed']and g['updates']==140 and g['draws']==g['strict_completed_DMA']==138 and g['cases'][0]['modeReadback']==1
 comp=launch.parent/'comparison/proof.json';c=json.loads(comp.read_text());assert c['passed']and c['cadence']['all_draw_prefix_deferrals']==[]and c['cadence']['candidate_max_no_draw']==c['cadence']['baseline_max_no_draw']==c['cadence']['candidate_max_no_update']==c['cadence']['baseline_max_no_update']==1
 dirs=dict(baseline=D/'cv3-remaining-queue-native-basic-v3/baselines-v1/hard-ice',held0c45=D/'cv3-remaining-queue-native-basic-v3/hard-ice',candidate=fixture);timings={k:rows(p0/'deadline-timing.csv')for k,p0 in dirs.items()};profiles={k:rows(p0/'native-cycles.csv')for k,p0 in dirs.items()};case={}
 for name in dirs:case[name]=dict(deadline=[q for q in timings[name]if q['kind']in['publication-write','NMI-entry','NoLagSoDraw','SkipDrawingCauseLagged']and 469<=q['wall']<=471],epoch34=[q for q in profiles[name]if q['audioEpoch']==34])
 pub=next(q for q in timings['candidate']if q['kind']=='publication-write'and q['audioEpoch']==34);nmi=next(q for q in timings['candidate']if q['kind']=='NMI-entry'and q['wall']==471);audio={k:next(q for q in case[k]['epoch34']if q['name']=='AudioUpdate')for k in dirs};assert pub['cpuCycle']==14024245 and nmi['cpuCycle']==14024252 and nmi['nmiDisable']==0 and nmi['cpuCycle']-pub['cpuCycle']==7;assert audio['held0c45']['cycles']-audio['candidate']['cycles']==35 and audio['candidate']['cycles']==4967
 assert all(next(q for q in case[k]['epoch34']if q['name']=='CvAudioPlay')['cycles']==2143 for k in dirs)
 (a.output/'exact-deadline.json').write_text(json.dumps(dict(actual=case,actual_publication=pub,actual_next_NMI_entry=nmi,publication_to_entry_cycles=7,hardware_entry_cycles_not_foreground_slack=7,additional_foreground_headroom_claimed=False,wholeAudioUpdate_saving=35,source_music_cycles_unchanged=2143),indent=2)+'\n')
 process=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name = 'Mesen.exe'\" | Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Compress"],capture_output=True,text=True);assert not process.returncode;(a.output/'post-run-process-inventory.json').write_text(process.stdout)
 report=ROOT/'docs/qa/cv3-remaining-sfx-steady-hard-ice-native-2026-10-26.txt';assert not report.exists();report.write_text('''CV3 steady successor: ONE GRANTED HARD-ICE PILOT PASSED
Exact eaa36e56; source readiness e56d4340. No adoption or production change.
Exactly1 new native launch/0retries; project worker RELEASED. All frozen1141
source/tool/environment/baseline inputs reverified. User settings8a439 unchanged.

Actual cold-menu Hard1 Sypha ice input creates3 real actors and3 committed
source cues, consumed by actual NMI. Every ordered ORIGINAL source image and
raw owned hardware byte including400F passes unchanged verify_v5. All original
bank/fiveSMC/stack/IRQ/CHR/viewport/APU/DMC/entire256DMA/PPU guards remain.
140 updates/138 draws/138 completed strictDMAs equals fresh matching50b baseline
140/138. Old0c45 staysHELD140/137. CSV sample139updates/137draws both; final
callback separately completes actual GAMEproof totals.140 physical frames,
zero draw-prefix deferrals; longest no-draw/no-update1 matches baseline.
140 actual NMIs/280 IRQscroll writes/1680 hardware CHRchecks/minSP213.

Actual former miss boundary:
Audio epoch34 old0c45 takes5002cycles; eaa takes4967, saving35. Original native
CvAudioPlay remains2143. New genuineSteadyTry169 versus oldDispatch204; pure
sourceBody105 versus oldNoise121. No source frame/voice/event/store is cut.
New NoLag begins14016337 vs old14016375 (38earlier includes frame phase).
Publication executes14024245, PPU241:5. Next NMIentry14024252, PPU241:27,
seesNmiDisable0. The7cycle interval is exactly hardware-entry cost; there is
NO asserted extra foreground safety margin. Source-only35cycle target was
actionable, but this narrow success is not an all-profile budget guarantee.
Old0c45 NMI14024255 saw255/stacked84A1 and published only after ISR14028213;
its real skipped draw remains frozen/rejected. No old failure is relabeled.

All13 other candidate BASIC cells and one fresh Easy-lightning baseline remain
UNLAUNCHED. Any further profile requires ROOT's separate explicit grant. Real
priority/pause/mute/scene/death/DMC-preemption/pressure and current composition
still remain required. No waveform/fullcampaign/all-character completion or
adoption claim. Current production remains50b5 throughout this pilot.
''',encoding='utf-8',newline='\n')
 result=dict(passed=True,accepted=False,qualification_scope='ONE_HARD_ICE_BASIC140_ONLY',native_launches=1,retries=0,worker_released=True,source_readiness=bind(ready),launch=bind(launch),complete_GAMEproof=bind(fixture/'proof.json'),comparison=bind(comp),exact_deadline=bind(a.output/'exact-deadline.json'),report=bind(report),candidate_artifacts={str(f):sha(f)for f in fixture.iterdir()if f.is_file()},launch_and_comparison_artifacts={str(f):sha(f)for f in launch.parent.rglob('*')if f.is_file()},post_run_process_inventory=bind(a.output/'post-run-process-inventory.json'),original_held_parent_native=r['unchanged_held_parent_native'],remaining_unlaunched_possible_profiles=14,source_original_raw400F_and_full_hardware_guards=True,strict_cadence_and_all_prefixes_pass=True,additional_foreground_margin_proven=False,production_mutated=False,tool_sha256=sha(__file__))
 shutil.copyfile(__file__,a.output/Path(__file__).name);(a.output/'qualification-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,scope=result['qualification_scope'],native_launches=1,worker_released=True,qualification=bind(a.output/'qualification-native.json'),report=bind(report)),indent=2))
if __name__=='__main__':main()
