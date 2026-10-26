"""Freeze faithful steady optimization and identical BASIC native readiness, never launch."""
from pathlib import Path
import argparse,hashlib,json,py_compile,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASIC=D/'cv3-remaining-queue-native-basic-v3'
ROM='eaa36e56c09e87f58a85db312894f14bfd7fb5838be139fc508ae6121c9e0732'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return dict(path=str(p),sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(a.prepared/'candidate.nes')==ROM;allbind={};receipts={}
 def keep(p):allbind[str(p)]=sha(p);return bind(p)
 for name in['cpu-v1','queue-v1','irq-v1','ordinary-v1','mute-v1','layout-v1','images-v1','controls-v1','lifecycle-v1','dmc-v3','priorities-v1']:
  f=a.prepared/name/'proof.json';r=json.loads(f.read_text());assert r['passed']and r['ROM_sha256']==ROM;receipts[name]=keep(f)
 layout=json.loads((a.prepared/'layout-v1/proof.json').read_text());manifest=a.prepared/'layout-v1/all-deployable-files.json';assert sha(manifest)==layout['all_deployable_manifest_sha256'];keep(manifest)
 for row in json.loads(manifest.read_text()):p0=a.prepared/'source'/row['path'];assert sha(p0)==row['sha256'];keep(p0)
 for name in['incremental-from0c45.patch','implementation-from50b.patch']:keep(a.prepared/'layout-v1'/name)
 dead=D/'cv3-remaining-steady-v2/deadline-v1/proof.json';deadline=json.loads(dead.read_text());assert deadline['passed']and deadline['minimum_publication_recovery_cycles']==35;keep(dead)
 matrixpath=a.fixtures/'proof.json';matrix=json.loads(matrixpath.read_text());assert matrix['passed']and len(matrix['cells'])==14;keep(matrixpath)
 for cell in matrix['cells']:
  for f in[a.fixtures/cell['name']/n for n in['run.lua','configuration.json','preparation.json','candidate.lbl']]:keep(f)
  for label in['CPU','startup']:keep(a.fixtures/label/cell['name']/'proof.json')
 oldready=BASIC/'freeze-v1/readiness-source-only.json';old=json.loads(oldready.read_text());assert sha(oldready)=='2cc9dc9d2aab9759e5d6223fb969bf9d5bc40114dc50cb6981ac4eeb6e319b00';keep(oldready)
 env=BASIC/'environment-v1/environment-addendum.json';e=json.loads(env.read_text());assert sha(env)=='357104cb1bdb76ba3e5154a31917cba3c4ca58a3172d71c1b8a114166d15e4be';keep(env)
 settings=Path('C:/Mesen2/settings.json');assert sha(settings)==e['current_settings_source_sha256']=='8a439e0a5eeddc2d4776e516aacfc224c03048b9c7d23d9926a463460a7e748a';keep(settings);shutil.copyfile(settings,a.output/'settings.current.json');keep(a.output/'settings.current.json')
 for q in e['unchanged_binding_checks']:assert sha(q['path'])==q['sha256'];keep(Path(q['path']))
 native=BASIC/'native-freeze-v1/qualification-native.json';n=json.loads(native.read_text());assert sha(native)=='81c39fd576a61e007d937cb3e70d292cc6339fffa0312f4148eb164f170c96d5'and n['strict_cadence_failures']==['hard-ice'];keep(native)
 # Reuse the thirteen genuinely fresh matching8a-baseline observations, not
 # the oldd10 Easy-lightning observation. Bind every original GAME artifact.
 baseline_refs={}
 for cell in old['future_cells']:
  name=cell['name'];dest=Path(cell['baseline']['script']['path']).parent;cfg=json.loads((dest/'configuration.json').read_text());assert cfg['cases'][0]['updates']==140
  files=n['all_native_fixture_artifacts'][name+'-baseline']
  for leaf,h in files.items():assert sha(dest/leaf)==h;keep(dest/leaf)
  launch=BASIC/'native-v1'/(name+'-baseline')/'proof.json';l=json.loads(launch.read_text());assert l['native_guard_passed']and l['settings_before_sha256']==l['settings_after_sha256']==sha(settings);keep(launch);baseline_refs[name]=dict(fixture=str(dest),complete_GAMEproof=bind(dest/'proof.json'),launch=bind(launch),settings_sha256=sha(settings),all_GAME_artifacts=files)
 template=old['future_cells'][0]['candidate']['future_separately_granted_command'];future=[]
 def command(dest,rom):
  cmd=list(template);cmd[cmd.index('--output')+1]=str(dest);cmd[cmd.index('--emulator')+2]=str(dest/'run.lua');cmd[cmd.index('--emulator')+3]=str(rom);assert not any('sprite'in t.lower()for t in cmd);return cmd
 # One genuinely required new baseline: same historical Easy-lightning
 # controller/arena, now under the current8a environment; no settings changes.
 historical=D/'cv3-remaining-static-observer-v1/replay-packet-v1/baseline50b';fresh=a.fixtures/'fresh-baseline-easy-lightning-v2';fresh.mkdir()
 for leaf in['run.lua','configuration.json','candidate.lbl']:
  shutil.copyfile(historical/leaf,fresh/leaf);keep(fresh/leaf)
 priorprep=dict(script=str(fresh/'run.lua'),script_sha256=sha(fresh/'run.lua'),configuration_sha256=sha(fresh/'configuration.json'),prepared=True,native_executed=False,source_lineage=dict(script=bind(historical/'run.lua'),configuration=bind(historical/'configuration.json'),HISTORICAL_ONLY_GAMEproof=bind(historical/'proof.json')),scope='Exact qualified historical50b Easy-lightning script/config/body, relocated source-only for ONE future separately granted fresh8a baseline. Oldd10 native result is not relabeled. Historical static packet has no preparation.json; genuine existing script/config/GAMEproof lineage is explicit.');(fresh/'preparation.json').write_text(json.dumps(priorprep,indent=2)+'\n');keep(fresh/'preparation.json')
 baseline=D/'cv3-remaining-current50b-v1/baseline.nes';keep(baseline);keep(baseline.with_suffix('.dbg'));keep(baseline.with_suffix('.lbl'));keep(a.prepared/'candidate.nes');keep(a.prepared/'candidate.dbg');keep(a.prepared/'candidate.lbl')
 future.append(dict(name='fresh-baseline-easy-lightning',version='baseline',mode=0,event=0x1e,fixture=str(fresh),ROM=bind(baseline),script=bind(fresh/'run.lua'),future_separately_granted_command=command(fresh,baseline)))
 for cell in matrix['cells']:
  dest=Path(cell['fixture']);same=fresh if cell['name']=='easy-lightning'else Path(baseline_refs[cell['name']]['fixture']);cfg=json.loads((dest/'configuration.json').read_text());bcfg=json.loads((same/'configuration.json').read_text());assert cfg['mode']==bcfg['mode']==cell['mode']and cfg['variant']==bcfg['variant']and cfg['cases']==bcfg['cases'];assert not(dest/'proof.json').exists()
  future.append(dict(name=cell['name'],version='candidate',mode=cell['mode'],event=cell['event'],fixture=str(dest),same_input_baseline=str(same),ROM=bind(a.prepared/'candidate.nes'),script=bind(dest/'run.lua'),future_separately_granted_command=command(dest,a.prepared/'candidate.nes')))
 # Complete frozen old dependency closure plus every new steady tool, including
 # retained failed preparation versions. No mutable observer/import is hidden.
 tools=dict(old['frozen_tools']);new=list(sorted((ROOT/'tools/audit').glob('cv3_remaining_sfx_steady_*')))
 for f in new:
  if f.suffix in['.py','.lua']:tools[f.relative_to(ROOT).as_posix()]=sha(f)
 frozen=a.output/'frozen-tools';frozen.mkdir()
 for path,h in tools.items():
  f=ROOT/path;assert sha(f)==h,path;keep(f);shutil.copyfile(f,frozen/f.name)
  if f.suffix=='.py':py_compile.compile(str(f),cfile=str(frozen/(f.stem+'.pyc')),doraise=True)
 negatives={}
 for f in[D/'cv3-remaining-steady-v1/build.host.log',D/'cv3-remaining-steady-v2/cpu-v4/proof.json',D/'cv3-remaining-steady-v2/prepared.json',D/'cv3-remaining-steady-native-v1/progress.json']:
  assert f.exists();negatives[str(f)]=sha(f);keep(f)
 report=ROOT/'docs/qa/cv3-remaining-sfx-steady-ready-2026-10-26.txt';assert not report.exists();report.write_text('''CV3 remaining effects: faithful steady successor SOURCE-ONLY readiness
No native launch/grant, production edit/install or adoption. Parent0c45 stays
HELD for Hard-ice140updates/137draws against50b140/138. Accepted50b unchanged.
Private eaa36e56 candidate preserves every source event/tick/voice/APU byte.

Exact causal target, rather than broad audio subtraction:
The retained actual Hard-ice NMI starts14024255 with stacked nextPC84A1.
Subtract7 hardware-entry cycles: last foreground acceptance boundary14024248.
Matched uninterrupted publication14024076+207=14024283: recovery target35.
The retained compiled Ctrl0/no-parser/no-scroll tail takes35cycles; Ctrl6
alternative21 is disclosed. No midframeRAM snapshot was recorded. The later
NMI handler's NmiDisable read supplies no foreground slack. This is an exact
source/trace reconstruction under matched foreground work, NOT native success.

Narrow optimization:
-Tick's genuine negative-active route tries a resident C28-only steady path.
 All fallback states retain real generic service/priority/queue/lifecycle.
-Successful path keeps liveAXYP/SP, source/store order, source pointer/index,
 final images/flags and mapper state. Saved52 is reused for savedY only while
 its former bank-cache value is dead. Generic still writes CurrentBank before
 its own restore read; steady savesY before its own read. No new RAM/CHR.
-Pure emission body fitsDB3A..DBDF (165B of declared198B tail); dirty-music
 values are cached exactly. Source overwrite removes redundant temporary
 restore/clear work; the final volume-only frame explicitly restores/clears
 period/high first. The genuine old ResidentNoise callable wrapper normalizes
 Active80 exactly for all tested inputs0/80/FF. No source-effect tick is cut.
-318bytes only bank28 differ from0c45. Every other bank/header/CHR,125/127
 samples/E-mirror, Mac/Mike/Roll/P-bar/queue/stubs/producer and old public PCs
 remain exact.61123 qualified symbols retained;6 obsolete private Noise branch
 labels genuinely removed, declared with no external refs or fake aliases.
 Expanded clean rebuild exact; both ordinary flag-off mapper hashes exact.

Source/CPU results on this EXACT hash:
4128 public wrapper ABI/state cases;256 successful hot state cases;
1400 complete old/new AudioUpdates;1200 ORIGINAL ordered voice-image updates
plus complete composed host hardware flush. Raw400F is never masked.
686 full-state priority schedules/2744 updates;343 original priority cases;
384 full real lag-NMI producer boundaries;780 command boundaries;
1536 menu resets,84 active lifecycle,70 pending,288 full spawn caller cases;
112 pending mute controls/448 ORIGINAL resume frames;1024 finite ingress runs;
512 continued original mixed updates;9472 ordinary whole updates/37 identities;
80 genuine CV1 cross updates;8192 whole menu music updates never read dead52;
42238 actual IRQ/RTI boundaries across125/127 code aliases;
DMC6048 source priorities/72 actual owners/1152 held-DAC tails/5024 ordinary.
The DMC diagnostic+28 compares deliberately DIFFERENT ordinary/source DMC
owners, not a new eaa-vs0c same-owner penalty. Ordinary same-owner deltas0.
No waveform, physical DMC stealing, campaign or native scheduling claim.

Actual assembled cost and remaining risk:
No-dirty nonfinal steady route saves35cycles versus0c45. Other source states
have real costs, including9..17 extra cycles; full same-state priority delta
range -52..+17. Legacy1F complete schedules and ordinary owners cost0 delta.
The35-cycle target has NO claimed safety margin; new native entry/publication
and draw evidence is REQUIRED. Do not substitute aggregate draw totals or
change controller/workload, source timing, sprite limit or strict cadence gate.

Native SOURCE preparation only:
All14 identical BASIC140 Easy0/Hard1 cells:42 real assembled ability/fullNMI
replays and14 complete439-frame inactive Lua5.4 startups pass. Literal old
controller/resources/arena/seed and all hardware guards are unchanged. Sole
image-hook change is genuine new ResidentBody::Emit replacing removedNC15;
two read-only genuine SteadyTry/Body performance hooks add causal attribution.
All callbacks stay startup-static; final broad return dispatcher LAST. No
runtime callback add/remove. Full256DMA/PPU/CHR/IRQ/bank/SMC/stack/rawAPU/DMC/
actual mode/publication/draw/cadence guards remain. No source400F mask.

Frozen possible launches (NOT a grant):
Reuse the13 exact matching fresh8a439 settings baseline observations from the
completed26-run matrix, all original GAME artifacts and launch bindings checked.
Old Easy-lightning baseline usedd10 settings, so prepare ONE fresh matching
8a baseline plus14 candidates=15 possible sequential launches. Settings remain
hardware8sprite ON/adaptiveOFF/no extra scanlines/runAhead0 and original exact
RAM/alignment overrides; raw current settings copied/bound, never overwritten.
Designated verifier_v5 unchanged: all ordered new-source values/hardware,
per-prefix draws/totals/stalls, and full legacy1F hardware control.1F buffered
order remains explicitly established adapter order, not original-order equal.

Retained negatives/fixture corrections:
First private compile had a forward-scope ca65 failure; initial CPU physical
bank harness and aliasedActive fixture mistakes remain archived. Priorv2
semantics passed but33cycle saving missed35target; it stays budgetFAIL.
First native-matrix source catalog assumed old Easy-lightning v1 metadata
equal v3; assertion retained. v2 generates the unchanged frozen0c45 v3 source
counterpart (no native run) before comparison. Actual controller cases match.
First readiness draft expected preparation.json in the historical static packet,
which has only script/config/GAMEproof; failed draft remains unchanged. Final
readiness binds the genuine available lineage and creates fresh metadata.
First DMC invocation used source-code path instead of original-golden path
and stopped before CPU execution; second omitted optional completion rows;
finalv3 includes all1152. No native retry or historical failure retagging.

After BASIC, actual priority/pause/scene/death/mute/DMC-preemption/pressure
readiness and native qualification remain REQUIRED. No full completion or
adoption is certified by this source packet. ROOT reviews/grants separately.
''',encoding='utf-8',newline='\n');keep(report)
 r=dict(passed=True,accepted=False,status='FAITHFUL_STEADY_SOURCE_READY_NATIVE_PENDING',native_executed=False,native_grant=False,production_mutated=False,candidate_ROM=bind(a.prepared/'candidate.nes'),parent_ROM=bind(a.prepared/'baseline.nes'),source=str(a.prepared/'source'),source_layout=receipts['layout-v1'],source_receipts=receipts,deadline=bind(dead),same_input_native_source_matrix=bind(matrixpath),unchanged_held_parent_native=bind(native),settings=bind(settings),environment=bind(env),reuse_13_native_baselines=baseline_refs,future_launches=future,designated_native_validator=str(ROOT/'tools/audit/cv3_remaining_sfx_queue_native_verify_v5.py'),frozen_tools=tools,all_frozen_bindings=allbind,retained_preparation_negatives=negatives,report=bind(report),actual_steady_saved_cycles=35,reconstructed_recovery_target=35,native_margin_proven=False,real_nonhot_cost_increase_max=17,remaining_required=['strict same-input new native deadline/cadence','actual priority per voice','pause/resume and cue while muted','scene cancel atomic ownership','death/injury/primaryDMC preemption','legacy1F and unrelated pressure','fresh current-parent composition and independent qualification'],tool_sha256=sha(__file__))
 (a.output/'readiness-source-only.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,ROM=ROM,possible_launches=len(future),frozen_bindings=len(allbind),readiness=bind(a.output/'readiness-source-only.json'),report=bind(report)),indent=2))
if __name__=='__main__':main()
