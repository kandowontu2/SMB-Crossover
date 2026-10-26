"""Freeze startup-static Lua-only readiness; native observation equivalence remains pending."""
from pathlib import Path
import argparse,hashlib,json,py_compile,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);packet=a.evidence/'replay-packet-v1/preparation.json';z=json.loads(packet.read_text());receipts={};bindings={}
 for n in['baseline50b-cpu-v1','baseline50b-dma-v1','held0802-cpu-v1','held0802-dma-v1','startup-v2']:
  f=a.evidence/n/'proof.json';r=json.loads(f.read_text());assert r['passed']and not r['native_executed'];receipts[str(f.relative_to(a.evidence))]=sha(f)
 for e in z['cases']:
  original=Path(e['original_completed_case']);static=Path(e['static_script']);assert sha(original/'run.lua')==e['original_script_sha256']and sha(static)==e['static_script_sha256'];bindings[str(static)]=sha(static);bindings[str(original/'run.lua')]=sha(original/'run.lua');bindings[str(static.with_name('configuration.json'))]=sha(static.with_name('configuration.json'));assert sha(e['ROM'])==e['ROM_sha256']
  for name,digest in e['historical_artifact_hashes'].items():assert sha(original/name)==digest,(e['name'],name)
 tools=sorted((ROOT/'tools/audit').glob('cv3_remaining_sfx_static_*'));frozen=a.output/'frozen-tools';frozen.mkdir();hashes={}
 for f in tools:
  if f.suffix not in['.py','.lua']:continue
  if f.suffix=='.py':py_compile.compile(str(f),cfile=str(frozen/(f.stem+'.pyc')),doraise=True)
  shutil.copyfile(f,frozen/f.name);hashes[f.relative_to(ROOT).as_posix()]=sha(f)
 for f in[ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/parodius_visibility_hud_static_startup_v1.py']:
  shutil.copyfile(f,frozen/f.name);hashes[f.relative_to(ROOT).as_posix()]=sha(f)
 report=ROOT/'docs/qa/cv3-remaining-sfx-static-observer-2026-10-25.txt';assert not report.exists()
 report.write_text('''CV3 native observer: startup-static successor, source/Lua-only readiness
Date:2026-10-25. NO Mesen worker grant used, NO emulator launched.
No game/source/art/ROM/install/Git/Downloads mutation.0c45 remains unadopted.

The historical observer installed a completion exec callback from inside4014,
and onReturn installed exec callbacks from audio/source/performance callbacks.
The new observer changes only those registrations. Pending name:return-PC keys,
replacement semantics, expected physical bank/SP and resident125/127 alias rules
stay exact. Lua-only slots retain first-registration order per PC, including
persistent DMA completion slots. The one broad exec0..FFFF dispatcher is the
last callback installed before runtime. New slots do not grow the host vector.
All original controller/input/arena/guard/output bytes reverse-transform exactly.
The core is defined before4014 to preserve lexical capture; it registers nothing
until the final startup install call. No source/FX cadence is changed by code.

Prepared native equivalence controls:
-Reuse the already completed Easy/lightning basic original controls from
  cv3-remaining-resident-v4/native-v1/baseline-easy-lightning (50b) and
  candidate-easy-lightning (HELD0802). Original scripts/config/output hashes stay
  immutable. Only the new static observer will need to run; no unsafe dynamic
  observer retry is required. No0c45 gameplay retry has been prepared/launched.
-Both new scripts retain exact original cold menu/mode0/character/ability/input,
 140-update arena, IRQ/SMC/stack/bank/source/DMC/raw400F/entire256-byteDMA/CHR/
  visiblePPU/deadline/publication/draw/cadence logic. No guard weakening.
-The future verify tool requires every CSV/rawARGB byte, every JSONL event,
  last-case state and complete proof to equal the immutable original run.
  Metadata-only bindings/native-proof differ by script path/hash and are not
  gameplay observations. HELD0802 cadence rejection must remain unchanged.

Actual Lua5.4 source-only qualification:
-Each exact prepared script passes13,388 deterministic old/new callback-stream
  operations.6,067 logged events match after EVERY operation; old dynamic
  callbacks grow to1,760 while the new core keeps1 fixed broad dispatcher.
  Pending replacement, shared-PC order, stack/16-bit wrapping, nested expected
  SP, bank misses, every relevant E125/127 overlay boundary and persistent DMA
  interleaving retain original behavior. These repeat the same operation set
  for the two exact complete fixtures, rather than claiming double coverage.
-Each exact script's unchanged actual strictDMA callbacks pass22 controls,
  including16 expected failures for active-render starts/ends, wrong next
  opcode/operand, incomplete/extra256 writes and corrupted bytes0/127/255.
  Wrong physical bank defers without consuming pending, then completes once
  in the bound bank. All256 source/hardware bytes and semantic event rows match;
  original assertion messages remain. Raw failed old/new controls are retained.
-Both complete generated scripts load with actual linked labels, then execute
 439 inactive-game frames and the original controller policy under forbidden
  runtime registration/removal/game writes. Every original output/header and
  controller input stream equals after each frame. Static fixed callbacks are
 38/43 versus old startup37/42, always with the broad dispatcher installed last.
  All fixed exec hooks also execute under inactive/bank-miss mocks. Active
  return/DMA callback paths are covered separately above. This is not emulation.

Runtime/API binding:
-Source tests use the pinned external lupa.lua54 native module; exact module
  path/hash and Lua_VERSION are saved. MesenCore.dll contains its Lua5.4 marker.
-Current Mesen.exe SHA8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9
  matches both original recorded native bindings. Current MesenCore.dll SHA
 4bd40dfc6512328d56d8ad0563263b52be57bac726d8804f0720e461e558cd41 is now pinned.
  The historical native receipt did not independently hash that DLL; no
  retroactive historical DLL-hash claim is made. The original API calls/enum
  names are unchanged; the one fixed exec-range registration follows the
  already qualified same-host static observer pattern. Actual native API event
  equivalence is still the next required gate, not established by Lua mocks.

Readiness/source package is frozen. A future explicit grant may run only the
two static replays and exact-output comparator, then qualify the observer.
No native execution,0c45 cadence/IRQ/DMA/PPU pass, waveform, campaign, adoption,
or repaired remaining-SFX gameplay is claimed by this packet.
''',encoding='utf-8',newline='\n')
 result=dict(passed=True,status='LUA_SOURCE_READY_NATIVE_OBSERVATION_EQUIVALENCE_PENDING',native_executed=False,native_grant=False,production_source_modified=False,packet=dict(path=str(packet),sha256=sha(packet)),receipts=receipts,generated_script_bindings=bindings,frozen_tools=hashes,report=dict(path=report.relative_to(ROOT).as_posix(),sha256=sha(report)),emulator=z['emulator'],core=z['core'],Python=dict(executable=sys.executable,version=sys.version),future_runs=2,future_scope='Static replays of immutable completed50b/HELD0802 Easy-lightning controls only; compare complete observations, not0c45 gameplay.',tool_sha256=sha(__file__))
 (a.output/'readiness-lua-only.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['frozen_tools','generated_script_bindings','receipts','Python']},indent=2))
if __name__=='__main__':main()
