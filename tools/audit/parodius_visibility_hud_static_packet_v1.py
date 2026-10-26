"""Freeze source-only static-observer readiness and the immutable host negatives."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 packet=a.parent/'hud-static-native-diagnostic-v1/twinbee-easy';z=json.loads((packet/'preparation.json').read_text());old=a.parent/'hud-scroll-native-remaining-v1/twinbee-easy';oz=json.loads((old/'preparation.json').read_text());newrun=Path(z['script']);oldrun=Path(oz['script']);original=ROOT/'tools/audit/parodius_visibility_observer.lua';module=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua'
 text=oldrun.read_text(encoding='utf-8').replace(original.read_text(encoding='utf-8'),module.read_text(encoding='utf-8')).replace(oldrun.parent.as_posix(),newrun.parent.as_posix()).replace((old/'controller').as_posix(),(packet/'controller').as_posix())
 tail='\n-- FINAL startup registration: all HUD/scroll/controller static hooks precede returns.\nPARODIUS_STATIC_INSTALL_RETURNS()\n';assert newrun.read_text(encoding='utf-8')==text+tail
 for f in ['inputs.csv','harness.lua','native-guard.lua','manifest.json']:assert sha(old/'controller'/f)==sha(packet/'controller'/f)
 assert (packet/'controller/policy.lua').read_text()==(old/'controller/policy.lua').read_text().replace((old/'controller').as_posix(),(packet/'controller').as_posix())
 for ext in ['.nes','.dbg','.lbl','.map']:assert sha(newrun.with_name('candidate'+ext))==sha(oldrun.with_name('candidate'+ext))
 checks={}
 for name in ['hud-static-observer-build-v1','hud-static-observer-cpu-v1','hud-static-startup-cpu-v2']:
  f=a.parent/name/'proof.json';q=json.loads(f.read_text());assert q['passed'];checks[name]=dict(path=str(f),sha256=sha(f))
 failed=a.parent/'hud-static-startup-cpu-v1';assert not(failed/'proof.json').exists();shutil.copy2(ROOT/'tools/audit/parodius_visibility_hud_static_startup_v1.py',failed/'failed-tool.py');(failed/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,classification='MOCK_SETUP_ERROR',failure="Complete-script Lua startup failed at controller policy.lua1383 because first mock omitted global L; actual native runner injects compiled labels before loading run.lua.",correction='Separate v2 exposes actual candidate.lbl labels. No observer/controller/ROM change.'),indent=2)+'\n',encoding='utf-8')
 paths=[]
 for tree in [packet,a.parent/'hud-static-observer-build-v1',a.parent/'hud-static-observer-cpu-v1',a.parent/'hud-static-startup-cpu-v1',a.parent/'hud-static-startup-cpu-v2']:
  paths.extend(f for f in tree.rglob('*')if f.is_file())
 for name in ['hud-scroll-host-failure-v1','hud-scroll-readiness-v1','hud-scroll-initial-packet-v1','hud-hard-crash-comparison-v2']:
  for leaf in ['proof.json','manifest.json']:
   f=a.parent/name/leaf
   if f.exists():paths.append(f)
 paths.extend(ROOT/'tools/audit'/n for n in ['parodius_visibility_hud_static_build_v1.py','parodius_visibility_hud_static_observer_v1.lua','parodius_visibility_hud_static_cpu_v1.py','parodius_visibility_hud_static_prepare_v1.py','parodius_visibility_hud_static_startup_v1.py','parodius_visibility_hud_static_startup_v2.py','parodius_visibility_hud_static_packet_v1.py','parodius_visibility_hud_host_freeze_v1.py'])
 paths.extend(f for f in(a.parent/'static-observer-lua-deps-v1').rglob('*')if f.is_file()and f.suffix not in ['.pyc'])
 manifest={str(f.resolve()):dict(sha256=sha(f),bytes=f.stat().st_size)for f in paths};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 q=dict(ready_for_parent_review=True,native_run=False,native_authorized=False,goal_complete=False,ROM_sha256=z['ROM_sha256'],production_unchanged=True,static_observer_sha256=sha(module),original_observer_sha256=sha(original),prepared_profile=dict(path=str(packet),mode=z['mode'],variant=z['variant'],preparation_sha256=sha(packet/'preparation.json'),script_sha256=sha(newrun)),same_frozen_ROM_and_controller=True,exact_only_five_registration_source_transforms=True,all_prior_guards_and_output_schemas_retained=True,dispatcher_registered_last_after_controller=True,checks=checks,manifest_sha256=sha(a.output/'manifest.json'),manifest_bindings=len(manifest),host_cause='Strongly supported callback-vector invalidation: original onReturn adds unique profile callbacks inside exec callback; official Mesen source push_back mutates the vector iterated by InternalCallMemoryCallback. Parent independently matched actual DLL RVA12F820 to that callback loop. No ROM clearance inferred.',upstream_sources=['https://github.com/SourMesen/Mesen2/blob/master/Core/Debugger/ScriptingContext.cpp','https://github.com/SourMesen/Mesen2/blob/master/Core/Debugger/ScriptingContext.h'],limits='Separate observation-layer proposal only. Actual Lua5.5 unit/mocked startup is not the Mesen runtime. Both host AVs remain failed immutable runs. Await ROOT review and explicit grant, then require same-input flushed-prefix/PPU equality and full strict native guards. No game patch, no body-order trial or lifecycle broadening.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(manifest),ROM_sha256=q['ROM_sha256'])))

if __name__=='__main__':main()
