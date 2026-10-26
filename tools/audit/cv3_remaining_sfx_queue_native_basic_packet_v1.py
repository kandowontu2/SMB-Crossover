"""Freeze remaining13 BASIC cells plus same-input50b static counterparts; no native grant."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return dict(path=str(p),sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);first=D/'cv3-remaining-queue-native-v1/native-freeze-v1/qualification-native.json';assert sha(first)=='debd4c116ad6db88f4b3714577647b89937b1f3b5153072b4e1c0bee672dcf1c';oldready=D/'cv3-remaining-queue-native-v1/freeze-v1/readiness-source-only.json';old=json.loads(oldready.read_text());rom=Path(old['ROM']['path']);assert sha(rom)==old['ROM']['sha256'];base=D/'cv3-remaining-current50b-v1/baseline.nes';assert sha(base)=='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
 receipts={}
 for n in['source-matrix-v1/proof.json','verifier-v1/proof.json','legacy-control-v1/proof.json','legacy-verifier-v2/proof.json','baselines-v1/proof.json']:
  z=json.loads((a.prepared/n).read_text());assert z['passed']and z['native_executed']is False;receipts[n]=sha(a.prepared/n)
 matrix=json.loads((a.prepared/'source-matrix-v1/proof.json').read_text());assert len(matrix['cells'])==13 and matrix['real_assembled_producer_consumer_cases']==39
 future=[];generated={};native_template=old['future_explicit_grant_command']
 for cell in matrix['cells']:
  name=cell['name'];candidate=a.prepared/name;baseline=a.prepared/'baselines-v1'/name;cfg=json.loads((candidate/'configuration.json').read_text());bcfg=json.loads((baseline/'configuration.json').read_text());assert cfg['cases']==bcfg['cases']and cfg['mode']==bcfg['mode']==cell['mode']and cfg['variant']==bcfg['variant'];assert not(candidate/'proof.json').exists()and not(baseline/'proof.json').exists()
  row=dict(name=name,event=cell['event'],cold_numeric_mode=cell['mode'],updates=140,expected_actor_count=cfg['expected_actors'],expected_committed_cue_count=cfg['expected_cues'],new_original_ordered_image_contract=cfg['expected_cue']!=6,legacy1F_declared_adapter_order=[0x400e,0x400f,0x400c]if cfg['expected_cue']==6 else None,cpu_receipt=cell['cpu'],candidate_startup_receipt=cell['startup'])
  for label,dest,r in[('candidate',candidate,rom),('baseline',baseline,base)]:
   command=list(native_template);command[command.index('--output')+1]=str(dest);command[command.index('--emulator')+2]=str(dest/'run.lua');command[command.index('--emulator')+3]=str(r);assert not any('sprite'in t.lower()for t in command);row[label]=dict(ROM=bind(r),script=bind(dest/'run.lua'),configuration=bind(dest/'configuration.json'),preparation=bind(dest/'preparation.json'),future_separately_granted_command=command)
   for f in dest.iterdir():
    if f.is_file():generated[str(f)]=sha(f)
  future.append(row)
 names=['cv3_remaining_sfx_queue_native_v2.lua','cv3_remaining_sfx_queue_native_prepare_v2.py','cv3_remaining_sfx_queue_native_prepare_v3.py','cv3_remaining_sfx_queue_native_cpu_v3.py','cv3_remaining_sfx_queue_native_cpu_v4.py','cv3_remaining_sfx_queue_native_startup_v2.py','cv3_remaining_sfx_queue_native_verify_v3.py','cv3_remaining_sfx_queue_native_verify_v4.py','cv3_remaining_sfx_queue_native_verify_v5.py','cv3_remaining_sfx_queue_native_basic_source_v1.py','cv3_remaining_sfx_queue_native_basic_verify_test_v1.py','cv3_remaining_sfx_queue_native_basic_baseline_v1.py','cv3_remaining_sfx_queue_native_legacy_control_v1.py','cv3_remaining_sfx_queue_native_legacy_verify_test_v1.py',Path(__file__).name]
 frozen=a.output/'frozen-tools';frozen.mkdir();tools=dict(old['frozen_tools'])
 for n in names:
  f=ROOT/'tools/audit'/n;tools[f.relative_to(ROOT).as_posix()]=sha(f);shutil.copyfile(f,frozen/n)
 for f,h in old['frozen_tools'].items():assert sha(ROOT/f)==h,f
 for n in['cv3_remaining_sfx_complete_cpu_v1.py','cv3_dmc_complete_cpu_v1.py','robots_weapon_cpu_v1.py']:
  f=ROOT/'tools/audit'/n;tools[f.relative_to(ROOT).as_posix()]=sha(f);shutil.copyfile(f,frozen/n)
 settings=Path('C:/Mesen2/settings.json');s=json.loads(settings.read_text(encoding='utf-8-sig'));assert s['Nes']['RemoveSpriteLimit']is False and s['Nes']['AdaptiveSpriteLimit']is False
 failures={}
 prior=D/'cv3-remaining-queue-native-basic-v2'
 for n in['easy-bat-cpu-v1','easy-fireball-cpu-v1','source-matrix-v1']:
  for f in(prior/n).rglob('*'):
   if f.is_file():failures[str(f)]=sha(f)
 for f in(a.prepared/'legacy-verifier-v1').iterdir():
  if f.is_file():failures[str(f)]=sha(f)
 report=ROOT/'docs/qa/cv3-remaining-sfx-queue-basic-ready-2026-10-25.txt';assert not report.exists();report.write_text('''CV3 remaining BASIC effects: SOURCE/CPU/static-observer readiness, NOT native
Candidate remains exact0c45; production untouched. Native grant absent.
The ONE prior Easy lightning140 profile passed strict native/source/cadence
and is frozen separately (debd4c11...). This readiness is not full completion.

Remaining13 BASIC140 cells prepared in literal old-controller arenas:
Effect/source        Easy0      Hard1       Real source owner/cue count
Grant dagger13       ready      ready       actual projectile1 /1
Grant axe15          ready      ready       actual projectile2 /1
Sypha flame24        ready      ready       actual projectile3 /1
Sypha ice21          ready      ready       actual triple projectile4 /3
Sypha lightning1E    nativePASS ready       actual triple projectile5 /3
Alucard fireball1F   control    control     actual primary projectile6 /1
Alucard bat2F        ready      ready       actual movement/BatEnter /1
No CV3 cross14 ability owner exists: companions use stopwatch in that slot.
Base Simon's existing CV1 cross is a different authenticated family/owner.

Genuine source ownership and static safety:
-Existing frozen single-case observer remains unchanged. New v2 BASIC-only
 module observes authentic Cv3Spawn->ProducerFast, STA-slot->finalINC-head,
 NMI AudioUpdate->Drain, committed byte sequence and genuine tail publication.
-Bat uses actual Cv3BatUpdate->Cv3FxBatEnter->Cv3FxQueueCommand caller/stack,
 not a fake projectile or compatibility entry. Compatibility FxSpawn remains
 explicitly unused. Main command/ring writes are forbidden inside NMI audio.
-Every new effect retains exact ordered ORIGINAL source-image stores plus
 original values/raw400F and adapted ascending owned-voice hardware flush.
 The remaining decoder/private emission boundary opcodes/physical banks are
 linked from exact candidate debug data. No new game RAM write is added.
-All old controller, resources, arena, numeric mode menu/readback and hardware
 guards are literal. The one intentional old-observer change excludes NMI
 Av26 legacy transfer from logical main-request count; the real transfer is
 separately bound to its actual Drain STA/audio owner, not silently omitted.
-Old strict whole256-byteDMA/PPU/CHR/IRQ/viewport/banks/fiveSMC/stack/rawAPU/
 DMC owner/deadline/publication/real draw branch observations remain present.
 All callbacks are installed at startup; final broad return dispatcher LAST.
 No runtime native callback registration/removal. Source1F Continue captures
 only actual source emission; final host-music restoration is not mislabeled
 as an original-source write. No state, gameplay or sprite-limit bypass.

Explicit EXISTING1F adapter/control contract, as reviewed by ROOT:
-Original buffered writes use400C(volume),400F(high),400E(period). The prior
 accepted adapter uses400E,400F,400C, then normal ascending hardware flush.
 This intermediate RAM order is deliberately NOT called original-order equal.
-The initially failing ordered-source trace remains immutable. No production
 change was made merely to reorder preflush buffered RAM. The designated
 comparator explicitly declares established1F image order and compares every
 original raw byte (including all400Fbits), every source-emission frame and
 full ordered owned hardware output. Other effects keep original image order.
-Fresh actual primary release +100 wholeAudioUpdates BOTH modes compares50b
 against0c45: complete raw hardware stream and legacy image/index/lifetime
 identical. Original28 source-image writes finish at frame27; existing host
 music restoration is frame28. All raw bytes equal ORIGINAL source effect.
-Future native1F validation additionally requires the ENTIRE ordered audio
 hardware stream vs its same-input baseline bound to actual AudioEpoch,
 including4000..4013/4015/4017, with no value masks.4014DMA and4016controller
 writes retain their separate original hardware guards. New effects' native
 baseline lacks added cues, so their sound compares to ORIGINAL executable.

Source-only qualification PASSED:
-39 actual assembled release/full real lagNMI interference scenarios:
 no interrupt; NMI after slot before commit; NMI after first commit.13 cells
 span real cold-mode configuration0/1, every genuine attack/transform owner,
 actor counts, source IDs, commits, native consumer and complete source life.
-13 complete candidate439-frame inactive Lua5.4 startups;13 prepared same-input
50b counterpart startups. Normal hardware sprite limit remains enabled.
 No inactive emulated writes or runtime callback add/remove occurred.
-Future source/hardware validator components pass all39 actual CPU scenarios
 and234 meaningful failures: raw400F image/hardware bits, missing/duplicate
 stores, image sequence and wrong consumed cue.1F's declared image order is
 separately labeled. Newv5 source/cadence function bodies equal testedv4.
-Full1F hardware comparator adds10 meaningful failures across both modes,
 including altered epoch, raw400F, host-music byte, missing store and extra
 APU4017framecounter write. No native proof is fabricated for these tests.

Preparation issues retained, not native failures/retries:
-The first extracted bat CPU fixture stopped before dispatching synthetic
 return-sentinel event, leaving the old read-only bat-return hook pending;
 corrected source runner dispatches that event once. Actual game return is ROM.
-Initial ice metadata expected1actor; actual authenticated Ice code creates3.
 Failure/old fixtures retained; new prepare_v3 declares the proven3actors.
-Initial legacy1F ordered-image failure is retained and contract separated as
 above, never retroactively retagged original-orderPASS.
-Initial full-hardware comparator misclassified4017writes as controller-only;
 corrected designated v5 includes APUframecounter writes and explicit rejection.
 Original draft/receipt/erratum retained. No original negative was removed.

Future qualification:
-Prepared13 candidate/baseline command pairs have the original deterministic
 RAM/alignment options only; normal8sprite hardware limit ON, adaptive OFF.
-Each must prove actual cold menu/readback,140updates, real attack/transform,
 complete source/lifecycle, original strict hardware guards and conservative
 per-frame draw prefixes/stalls/totals vs matching baseline. Any failure or
 deferral remains HELD with no retry/oracle mask. Existing historical negatives
 remain saved. No executable command in this packet is a grant to launch it.
-Suggested first remaining pilots: Hard ice, Easy ice, Hard lightning, then
 both legacy1F controls; ROOT decides bounded explicit grant/order.
-Lifecycle/priority/pause/death/scene and pressure controls remain REQUIRED
 after BASIC coverage; no full roster, waveform, campaign, no-lag, final merge
 or production adoption claim is made by this readiness packet.
''',encoding='utf-8',newline='\n')
 result=dict(passed=True,status='THIRTEEN_REMAINING_BASIC_CELLS_SOURCE_READY_NATIVE_PENDING',native_executed=False,native_grant=False,production_source_modified=False,prior_single_native_qualification=bind(first),prior_single_source_readiness=bind(oldready),candidate_ROM=bind(rom),candidate_debug=bind(rom.with_suffix('.dbg')),candidate_labels=bind(rom.with_suffix('.lbl')),baseline_ROM=bind(base),baseline_debug=bind(base.with_suffix('.dbg')),baseline_labels=bind(base.with_suffix('.lbl')),source_receipts=receipts,future_cells=future,future_native_validator=str(ROOT/'tools/audit/cv3_remaining_sfx_queue_native_verify_v5.py'),frozen_tools=tools,generated_bindings=generated,external_environment=old['external_environment'],retained_preparation_failure_artifacts=failures,all_13_basic_cells_have_same_input_baseline=True,actual_numeric_mode_configuration=[0,1],hardware_sprite_limit_enabled=True,adaptive_sprite_limit_disabled=True,no_runtime_callback_API_growth=True,remaining_required_after_basic=['actual native priority per voice','pause/resume/cue while muted','actual scene immediate cancellation with new queue ownership','death and injury/primaryDMC preemption controls','legacy1F and unrelated no-source pressure cadence','full current-parent composition and independent qualification'],report=bind(report),tool_sha256=sha(__file__))
 (a.output/'readiness-source-only.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,cells=13,paired_fixtures=26,tools=len(tools),readiness=bind(a.output/'readiness-source-only.json'),report=bind(report)),indent=2))
if __name__=='__main__':main()
