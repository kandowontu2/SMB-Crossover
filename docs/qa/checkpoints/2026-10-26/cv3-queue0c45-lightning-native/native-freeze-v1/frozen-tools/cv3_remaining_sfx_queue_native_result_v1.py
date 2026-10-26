"""Freeze the ONE granted0c45 native outcome without changing source readiness."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=a.evidence/'freeze-v1/readiness-source-only.json';assert sha(ready)=='dcad0fac0eb07bcc97c7fe8cba25bb99645997ca2c3c3d1b1a94920d1a22d0b8';r=json.loads(ready.read_text())
 for f,h in r['frozen_tools'].items():assert sha(ROOT/f)==h,f
 for f,h in r['generated_bindings'].items():assert sha(f)==h,f
 launch=a.evidence/'native-launch-v1/proof.json';l=json.loads(launch.read_text());assert l['exit_code']==0 and l['native_guard_passed']and l['retries']==0 and l['settings_before_sha256']==l['settings_after_sha256'];verify=a.evidence/'native-verify-v1/proof.json';v=json.loads(verify.read_text());assert v['passed']and not v['accepted']and v['cadence']['all_draw_prefix_deferrals']==[]
 case=a.evidence/'fixture-v1';g=json.loads((case/'proof.json').read_text());assert g['passed']and g['updates']==140 and g['draws']==g['strict_completed_DMA']==138 and g['nmis']==140 and g['irq_scroll_writes']==280 and g['hardware_chr_checks']==1680 and g['min_sp']==213;q=g['cases'][0];assert q['modeReadback']==0 and q['queuePublished']==q['queueConsumed']==q['spawnCalls']==q['requests']==3 and q['queueCancels']==0 and q['queueDrains']==1 and q['sourceImageWrites']==129
 frozen=a.output/'frozen-tools';frozen.mkdir();tools={}
 for name in['cv3_remaining_sfx_queue_native_launch_v1.py',Path(__file__).name]:
  p0=ROOT/'tools/audit'/name;tools[p0.relative_to(ROOT).as_posix()]=sha(p0);shutil.copyfile(p0,frozen/name)
 report=ROOT/'docs/qa/cv3-remaining-sfx-queue-native-result-2026-10-25.txt';assert not report.exists();report.write_text('''CV3 real queue-owner observer: ONE0c45 native qualification result
One explicit grant, one run, no retry. Worker RELEASED after process exit.
Production remains unchanged; no adoption or full-SFX completion claim.

Exact source readiness dcad0fac... and6b51694e... script remain byte-exact.
ROM0c45ce16fa189debc2303f4df664a0e75f326a807a64bf23280797734615339c.
Literal cold Easy0/Sypha/Up+B lightning/basic140 test executed once at UTC
2026-10-26 02:26:58.755705..02:27:05.001721; native exit0, no host/assertion
failure. The frozen designated verify_v2 also passed without oracle changes.

Actual gameplay ownership and original source:
-3real Cv3Spawn calls to actual Cv3FxProducerFast,3committed rawcue5/source1E
 requests, one realNMI drain consuming3cues; queue empty/nooverflow/no cancel.
-129 ordered source-image writes, complete source lifetime; original executable
 model and owned-voice hardware values match across123 observed audio epochs.
 Full raw400F and write order retained. No masks, skipped source stores, fake
 wrapper aliases or queue injection. Hardware output and source-image capture
 are separately retained. No waveform claim or DMC-playback claim: this pulse/
 noise effect legitimately has0DMCstarts/0DMCpayloadchecks.

Native hardware/state guards PASSED:
-140updates/138draws/138complete strict256byteOAMDMA;140NMIs,280 actual visible
 IRQ scroll writes,1680hardwareCHRchecks, minSP213,101381stackwrites.
-Original fiveSMC/mapper/actualbank/stack/IRQ/viewport/CHR/rawAPU/DMC-owner
 controls and strict real DMA destination/phase guard remained enabled.
-Normal hardware sprite limit ON and adaptive sprites OFF. settings.json SHA
 d10b4fbc3903cd1c71e2df28f6c33dfdb9dae4aacaf32426bbfc1224e748f5d4
 unchanged before/after. Same frozen deterministic alignment/RAM options.

Same-work strict cadence PASSED against immutable50b Easy lightning control:
-Final complete GAMEproof140updates/138draws in BOTH;140physical observation
 frames, longest no-draw/no-update1 in BOTH, ZERO cumulative prefix deferrals.
-EndFrameCSV139updates/137draws/3zero-draw frames in BOTH. As documented in
 source readiness, final callback's update/draw occurs after finalCSVsample;
 final completeGAMEproof totals are compared separately, not conflated.
-This repairs the old0802 Easy lightning one-draw deficit in this one bounded
 test. Historical0802 remains rejected; no old negatives or settings rewritten.

Launch receipt, complete GAMEproof, all original observations and new owner/
ordered-source logs, source-model output and strict comparator are retained
and SHA-bound in qualification-native.json. No project Mesen worker remained
at release. A future remaining-effects matrix needs new source readiness and
explicit grant; this one passing profile does not qualify Hard, other spells,
dagger/axe, bat, lifecycle/priority, unrelated-pressure or full campaign.
''',encoding='utf-8',newline='\n')
 result=dict(passed=True,accepted=False,status='ONE0C45_EASY_LIGHTNING_BASIC140_NATIVE_SOURCE_HARDWARE_STRICT_CADENCE_PASS',worker_released=True,native_runs=1,native_retries=0,source_readiness=dict(path=str(ready),sha256=sha(ready)),launch=dict(path=str(launch),sha256=sha(launch)),comparison=dict(path=str(verify),sha256=sha(verify)),ROM_sha256=r['ROM']['sha256'],script_sha256=sha(case/'run.lua'),native_artifacts={f.name:sha(f)for f in sorted(case.iterdir())if f.is_file()},verifier_artifacts={f.name:sha(f)for f in sorted(verify.parent.iterdir())if f.is_file()},launch_artifacts={f.name:sha(f)for f in sorted(launch.parent.iterdir())if f.is_file()},tools=tools,report=dict(path=report.relative_to(ROOT).as_posix(),sha256=sha(report)),tool_sha256=sha(__file__))
 (a.output/'qualification-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,accepted=False,native_runs=1,worker_released=True,qualification_sha256=sha(a.output/'qualification-native.json'),report_sha256=sha(report)),indent=2))
if __name__=='__main__':main()
