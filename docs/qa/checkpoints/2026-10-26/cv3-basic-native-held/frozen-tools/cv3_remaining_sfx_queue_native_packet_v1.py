"""Freeze ONE source-prepared0c45 strict static fixture; explicitly no native grant/run."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def binding(p):return dict(path=str(p),sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);fixture=a.evidence/'fixture-v1';prep=json.loads((fixture/'preparation.json').read_text());assert prep['native_executed']is False and not(fixture/'proof.json').exists();assert sha(fixture/'run.lua')==prep['script_sha256']=='6b51694e3f209c4817396881c8ad34d41d7459656dc3a9ad0fe1eb96b3eb40c6';assert sha(fixture/'configuration.json')==prep['configuration_sha256'];assert sha(prep['ROM'])==prep['ROM_sha256']=='0c45ce16fa189debc2303f4df664a0e75f326a807a64bf23280797734615339c'
 cfg=json.loads((fixture/'configuration.json').read_text());assert cfg['mode']==0 and cfg['cases']==[dict(name='basic-source1e-coldmode0',kind='sub',profile='basic',mode=0,sub=3,event=30,updates=140)]
 receipts={}
 for name in['cpu-v1/proof.json','cpu-v2/proof.json','startup-v1/proof.json','verifier-v3/proof.json']:
  z=json.loads((a.evidence/name).read_text());assert z['passed']and z['native_executed']is False;receipts[name]=sha(a.evidence/name)
 startup=json.loads((a.evidence/'startup-v1/proof.json').read_text());assert startup['fixed_startup_callbacks']==57 and startup['runtime_registration_removal_game_writes']==0
 tests=json.loads((a.evidence/'verifier-v3/proof.json').read_text());assert tests['component_negative_controls']==18 and tests['historical0802_rejection']['passed']is False
 source=D/'cv3-remaining-queue256-v1/freeze-v1/readiness-source-only.json';assert sha(source)=='9d660c4bf1adf11d8979b618aa3a2dfd43e0f0bed58a865bbe209c8a99aa01ad';static=D/'cv3-remaining-static-observer-v1/native-freeze-v1/qualification-native.json';assert sha(static)=='d2d493171a34ef67053499da4806c8331c75e142532f5acc4aba0f9b401fe9b5'
 names=['cv3_remaining_sfx_queue_native_prepare_v1.py','cv3_remaining_sfx_queue_native_v1.lua','cv3_remaining_sfx_queue_native_cpu_v1.py','cv3_remaining_sfx_queue_native_cpu_v2.py','cv3_remaining_sfx_queue_native_startup_v1.py','cv3_remaining_sfx_queue_native_verify_v1.py','cv3_remaining_sfx_queue_native_verify_v2.py','cv3_remaining_sfx_queue_native_verify_test_v1.py',Path(__file__).name,'cv3_remaining_sfx_static_core_v1.lua','cv3_primary_sfx_source_v1.py','cv3_remaining_sfx_queue256_support_v1.py','check_tmnt_render_oa.py','check_tmnt_audio_fallback_oc.py','observe_chip_committed_write.py','verify_native_relocation.py','parodius_visibility_hud_static_startup_v1.py','run_mesen_isolated.py']
 frozen=a.output/'frozen-tools';frozen.mkdir();tools={}
 for name in names:
  q=ROOT/'tools/audit'/name;tools[q.relative_to(ROOT).as_posix()]=sha(q);shutil.copyfile(q,frozen/name)
 tools['tools/run_mesen.py']=sha(ROOT/'tools/run_mesen.py');shutil.copyfile(ROOT/'tools/run_mesen.py',frozen/'run_mesen.py')
 old=D/'cv3-remaining-static-observer-v1/replay-packet-v1';packet=json.loads((old/'preparation.json').read_text());command=list(packet['cases'][1]['future_explicit_grant_command']);command[command.index('--output')+1]=str(fixture);command[command.index('--emulator')+2]=str(fixture/'run.lua');command[command.index('--emulator')+3]=prep['ROM'];assert not any('sprite'in t.lower()for t in command)
 settings=Path('C:/Mesen2/settings.json');s=json.loads(settings.read_text(encoding='utf-8-sig'));assert s['Nes']['RemoveSpriteLimit']is False and s['Nes']['AdaptiveSpriteLimit']is False
 report=ROOT/'docs/qa/cv3-remaining-sfx-queue-native-2026-10-25.txt';assert not report.exists();report.write_text('''CV3 real queue-owner observer: ONE0c45 strict native fixture SOURCE READY
No emulator execution, native grant, production/game/art/ROM install or adoption.

Exact candidate0c45ce16fa189debc2303f4df664a0e75f326a807a64bf23280797734615339c
retains the separately frozen source-only queue256 readiness9d660c4b...
Prepared run.lua6b51694e3f209c4817396881c8ad34d41d7459656dc3a9ad0fe1eb96b3eb40c6.
ONE literal historical cold Easy0 / Sypha / Up+B lightning / basic140-update
arena. Historical case object, resources, arena seeds, controller behavior,
input ages, numeric cold-menu mode/readback and all old guard code are exact.
The generated script reverses byte-exact to qualified static held0802
784f86a5... by removing only this explicit read-only module, its two boundary
calls and two log closes; configuration rebinds actual new opcodes/addresses.

Legitimate protocol changes require legitimate observations:
-Main real Cv3Spawn directly calls Cv3FxProducerFast. Its actual stack return,
 physical owner, actor index/type, original assembled STA-slot and INC-head
 writers are bound. A prior slot byte must exist before the atomic head commit.
 RMW same-value dummy writes are distinguished. No fake wrapper alias is used.
-Unused genuine compatibility Cv3FxSpawn is guarded against entry in THIS
 one fixture; old source-marker hooks remain present and cannot certify a cast.
-Requests now record source1E/rawcue5 at actual head publication, with cueEpoch
 referring to next actual AudioUpdate. TypedAv26..32 is forbidden in this basic
 fixture. Actual NMI Drain entry/return records committed bytes and real consumer
 epochs independently. Tail/voice state remains NMI-owned; producer never runs
 inside audio. Finish requires3real actors/3commits/3consumed/3requests, empty
 ring, zero overflow and complete source lifetime. No new emulated RAM writes.
-Source image stores are captured at actual private Decode/resident NC15
 boundaries, not invented callable labels. Ordered raw400F is never masked.
 Existing raw hardware APU/source-voice/DMC logs are unchanged. Future validator
 replays ORIGINAL executable1E requests on observed consumer epochs, compares
 every ordered source-image store, then actual ascending owned-voice hardware
 flush. Released voices may restore the existing host song.
-Only new perf hooks are genuine ProducerFast/Drain/DrainGate. All old timing,
 NMI stackedPC/publication/draw decision, fiveSMC, stack, physical mapper/E125/
 E127, DMC sample/fetch, viewport/IRQ/CHR, entire256byteOAM and strict hardware
 DMA-phase guards remain. The old all-source/old-source raw logs are retained.

Startup-static observer qualification remains exact finite historical scope:
source c3c9fe38..., native2case d2d49317... . All9CSV+ARGB and complete GAMEproof/
state matched their historical originals; old host wrapper receipts were not
recreated. 0802 one-draw deficit remains held. No historical negatives changed.
This new fixture uses57 startup-fixed callbacks, broad0..FFFF dispatcher LAST.
There is no runtime add/remove callback. Lua-only ordered return slots preserve
the qualified physical bank/SP behavior. Complete439-frame inactive controller
startup passed; no runtime registration/removal or emulated game write.

Active source instrumentation checks (not native gameplay):
-Actual assembled0c45 Cv3WeaponsGate triple cast and complete lagNMI ISR replay
 into this read-only module/qualified Lua5.4 core. Cases: no interrupt; realNMI
 after slot/before commit; realNMI after first commit. Optional INC dummy bus
 events modeled explicitly. All3actors/3commits/3consumed percase,60/61/61 actual
 full NMIs,129/129/134 ordered source-image writes. Original executable matches
 every store including raw400F; split publication correctly preserves phase.
-v2 additionally records actual assembled hardware stores. Future validator
 components compare original ordered source and all owned hardware values over
 60/60/61 epochs;18 meaningful negative controls reject raw400F image/hardware
 corruption, missing/duplicate writes, reordered source stores, wrong cue.
 Historical baseline cadence self passes and actual held0802 remains rejected;
 a synthetic equal-total prefix deferral also remains held. No native proof
 object was fabricated or used for these source-only component tests.
-Future main validator remains UNEXECUTED pending explicit native grant. It
 requires actual mode0/140updates and all original native guards, compares
 final complete GAMEproof totals plus per-frame cumulative draw prefixes,
 longest no-draw/no-update runs, skipped draws and physical frames. Any prefix
 deferral is conservatively held for review, not hidden by aggregate totals.
 Historical endFrame CSV omits final callback's update/draw: baseline CSV139/
 137 vs complete GAMEproof140/138; held0802 CSV139/136 vs final140/137. Both
 representations are retained separately and correctly labeled.

Retained preparation failures (not emulator failures/retries):
-Initial v2 Python factoring indentation compile error saved as a .py.txt draft.
-One wrong-cue source negative found that choosing firstvalid5 could skip an
 earlier invalid4. Fixed component validates ALL consumed cue vocabulary first;
 actual Lua already rejected4. Failed source receipt/draft are retained.
-Initial test equated CSV subtotal to final GAMEproof total; failed receipt and
 original test draft retained; current test explicitly validates both layers.
Old verifier-v1 preliminary draft remains preserved and is NOT designated for
future native use. Final designated validator is verify_v2, component-tested.

Future ONE launch command/environment/bindings are in readiness JSON. The command
has original deterministic options only, normal NES hardware sprite limit ON,
adaptive sprites OFF. Full settings/exe/CoreDLL/Python/Lua54 hashes are bound.
No retry or launch is authorized by this readiness artifact. A separate explicit
native grant and unchanged preflight hashes are required before execution.
''',encoding='utf-8',newline='\n')
 artifacts={str(f.relative_to(a.evidence)):sha(f)for f in a.evidence.rglob('*')if f.is_file()and a.output not in f.parents}
 generated={str(p):sha(p)for p in[fixture/'run.lua',fixture/'configuration.json',fixture/'preparation.json',fixture/'candidate.lbl',fixture/'qualified-static-parent.lua']};rom=Path(prep['ROM']);external=[Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path(sys.executable),settings,D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1/lupa/lua54.cp314-win_amd64.pyd',Path('C:/NES/Castlevania III - Dracula\'s Curse (USA).nes')]
 result=dict(passed=True,status='ONE0C45_EASY_LIGHTNING_BASIC140_STATIC_FIXTURE_SOURCE_READY_NATIVE_PENDING',native_executed=False,native_grant=False,production_source_modified=False,ROM=binding(rom),ROM_dbg=binding(rom.with_suffix('.dbg')),ROM_lbl=binding(rom.with_suffix('.lbl')),prior_source_readiness=binding(source),qualified_static_observer_native=binding(static),receipts=receipts,frozen_tools=tools,generated_bindings=generated,external_environment=[binding(p)for p in external],future_explicit_grant_command=command,future_native_validator=str(ROOT/'tools/audit/cv3_remaining_sfx_queue_native_verify_v2.py'),original_static_parent_script_sha256=prep['qualified_parent_script_sha256'],actual_numeric_mode=0,expected_actual_updates=140,new_callback_count=57,all_original_guard_workload_code_retained=True,real_genuine_owner_hooks=cfg['hooks'],real_writers=cfg['queue_writers'],actual_caller_return=cfg['producer_caller_return'],intentional_protocol_timing_changes=prep['intentional_timing'],hardware_sprite_limit_enabled=True,adaptive_sprite_limit_disabled=True,all_source_evidence_artifacts=artifacts,report=binding(report),tool_sha256=sha(__file__))
 (a.output/'readiness-source-only.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,readiness=binding(a.output/'readiness-source-only.json'),report=binding(report),tools=len(tools),receipts=len(receipts)),indent=2))
if __name__=='__main__':main()
