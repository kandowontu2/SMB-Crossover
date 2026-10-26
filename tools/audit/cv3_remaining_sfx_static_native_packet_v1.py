"""Freeze exactly two granted native static replays and full historical equality."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=a.evidence/'freeze-v1/readiness-lua-only.json';r=json.loads(ready.read_text());assert sha(ready)=='c3c9fe38b70cf774e8426a6e9da17d5fdd80fbc1e4d0f5e2b3f0e8700331bf3c'
 for name,h in r['frozen_tools'].items():assert sha(ROOT/name)==h,name
 eqpath=a.evidence/'native-equivalence-v1/proof.json';eq=json.loads(eqpath.read_text());assert eq['passed']and eq['native_observation_equivalent'];launches=[];artifacts={}
 for name,draws,minimum in[('baseline50b',138,213),('held0802',137,212)]:
  receipt=a.evidence/'native-launch-v1'/name/'proof.json';z=json.loads(receipt.read_text());assert z['passed']and z['exit_code']==0 and z['retries']==0 and z['observation_mismatches']==[] and z['settings_before_sha256']==z['settings_after_sha256'];launches.append(dict(path=str(receipt),sha256=sha(receipt),**z))
  q=a.evidence/'replay-packet-v1'/name;proof=json.loads((q/'proof.json').read_text());assert proof['updates']==140 and proof['draws']==draws and proof['strict_completed_DMA']==draws and proof['min_sp']==minimum and proof['nmis']==140 and proof['irq_scroll_writes']==280 and proof['hardware_chr_checks']==1680
  artifacts[name]={f.name:sha(f)for f in sorted(q.iterdir())if f.is_file()}
 frozen=a.output/'frozen-tools';frozen.mkdir();tools={}
 for name in['cv3_remaining_sfx_static_launch_v1.py','cv3_remaining_sfx_static_verify_v1.py','cv3_remaining_sfx_static_native_packet_v1.py']:
  f=ROOT/'tools/audit'/name;tools[f.relative_to(ROOT).as_posix()]=sha(f);shutil.copyfile(f,frozen/name)
 report=ROOT/'docs/qa/cv3-remaining-sfx-static-observer-native-2026-10-25.txt';assert not report.exists();report.write_text('''CV3 startup-static observer: EXACT two native historical replay qualification
Local date2026-10-25; UTC launches2026-10-26 01:56:33..01:56:51.
One sequential project Mesen grant used for exactly2 cases. Worker RELEASED.
No retry, host failure, native assertion or observation mismatch occurred.
No0c45/new-gameplay execution, game/source/art/ROM install or adoption occurred.

Frozen source/Lua readiness remains unchanged:c3c9fe38b70cf774e8426a6e9da17d5fdd80fbc1e4d0f5e2b3f0e8700331bf3c.
Frozen replay packet52e81d27d8971f99fe46c868c0451a3e6c89369750e7a0cc9153148701d2a172.
Exact sequential launches:
-50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363,
  script8e173f297b7d1da600c0d63a7b91858f455e0e5a3fa35ba31292ccff7416ba03.
-HELD0802527d8a2e0cf8f9584e854d6dd263b72e330c3c89d30921abddc1b10c5790,
  script784f86a5d5cecd2a1d97934fc9f5e514f62abf820967e356da08d5dea9fd1148.
Both use literal frozen packet commands/options, original Cold Easy mode0,
Sypha lightning/basic140-update controller/workload/actor/resource fixture.
The unsafe dynamic observers were NOT rerun; each new static run compares
against the original completed immutable historical recording.

Actual full-observation equivalence PASSED:
-Every actors/APU/cadence/deadline/DMC-fetch/native-cycle/request/source-voice
  CSV byte matches the saved original for its same ROM.
-Complete245,760-byte case-end ARGB capture matches for each run.
-All276/274 DMA JSONL events, last-case state and entire native proof objects
  are semantically equal. JSON key serialization order alone may differ; raw
  hardware/source bytes, data-write counts and PPU/cycle stamps are identical.
-Baseline140 updates/138 draws/138 strict completed256-byteDMA; HELD0802
 140 updates/137 draws/137 strictDMA. Its old one-draw deficit remains FALSE
  for cadence acceptance. Observer qualification does not rehabilitate0802.
-Both actual mode0,140 NMI entries,280 visible IRQ scroll stores,1,680 CHR
  hardware checks, minSP213/212. Complete bank/shadow/fiveSMC/stack/source/APU/
  DMC/register/raw400F/entire256-byteOAM/strictPPU/deadline guards remain exact.

Environment and sprite hardware limit:
-Frozen exe/CoreDLL/scripts/settings/commands are bound in the native receipts.
-NES RemoveSpriteLimit=false, AdaptiveSpriteLimit=false. No option enabled
  unlimited/adaptive sprites. settings.json byte hash stayed exactly
 d10b4fbc3903cd1c71e2df28f6c33dfdb9dae4aacaf32426bbfc1224e748f5d4
  before/after BOTH runs. No settings/state/workload alteration.
-A read-only settings preflight first used the locale decoder and encountered
  its UTF8 BOM; corrected explicit utf-8-sig decoding confirmed the settings
  BEFORE any emulator launch. This was not a native run/failure/retry.

Complete frozen comparator proof:
native-equivalence-v1/proof.json SHA
9e2cff9dfc55799380c8ec8f7a66ce854d7cf52f531b1341c41ff7c313300b77.
Launch logs/receipts and every generated trace hash are preserved separately
from immutable source/Lua readiness. No task Mesen process remained at release.

Qualified scope: this static registration observer preserves every measured
observation in the two exact historical same-input controls. It is suitable
as the observer basis for future separately frozen fixtures, pending review.
No0c45 native gate, other-profile equivalence, new ability behavior, waveform,
full campaign, production adoption or general no-lag verdict is implied.
''',encoding='utf-8',newline='\n')
 result=dict(passed=True,status='EXACT_TWO_HISTORICAL_STATIC_NATIVE_REPLAYS_OBSERVATION_EQUIVALENT',native_runs=2,native_retries=0,worker_released=True,no0c45_execution=True,held0802_cadence_accepted=False,source_readiness_sha256=sha(ready),equivalence_proof=dict(path=str(eqpath),sha256=sha(eqpath)),launches=launches,all_native_artifacts=artifacts,tools=tools,report=dict(path=report.relative_to(ROOT).as_posix(),sha256=sha(report)),tool_sha256=sha(__file__))
 (a.output/'qualification-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['launches','all_native_artifacts','tools']},indent=2))
if __name__=='__main__':main()
