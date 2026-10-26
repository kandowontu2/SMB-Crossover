"""Prepare ONE unrun PitEasy731 native pilot; no emulator or settings mutations."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,sys
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True,exist_ok=False)
 frozen=D/'current731-abilities-observer-v4';old=frozen/'pit-easy';z=json.loads((frozen/'proof.json').read_text());assert z['passed']and z['ROM_sha256']==CURRENT
 files=set()
 for folder in [frozen,frozen/'static-return-control']:
  for q in json.loads((folder/'manifest.json').read_text())['bindings']:
   f=Path(q['path']);assert sha(f)==q['sha256']and f.stat().st_size==q['bytes'];files.add(f)
  files.add(folder/'proof.json');files.add(folder/'manifest.json');files.add(folder/'controls.json')
 out=a.output/'native';out.mkdir()
 for n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','config.json','run.lua']:shutil.copy2(old/n,out/n)
 cfg=json.loads((out/'config.json').read_text());assert(cfg['family'],cfg['hard'],cfg['mode_value'],cfg['character'],cfg['slot'],len(cfg['abilities']))==('pit',False,0,6,6,10)
 assert [(q['before'],q['after'])for q in cfg['steps']]==[(0,1),(1,2)]
 assert [q['kind']for q in cfg['abilities']].count('hammer')==6
 assert [q['kind']for q in cfg['abilities']].count('flight_gate')==2
 assert [q['kind']for q in cfg['abilities']].count('flight_full')==[q['kind']for q in cfg['abilities']].count('flight_release')==1
 original=(old/'run.lua').read_text();capture=ROOT/'tools/audit/final_item_abilities_pit731_ppu_v1.lua';capture_text=capture.read_text()+'\n'
 anchor='emu.addEventCallback(function()\n wall=wall+1\n';assert original.count(anchor)==1
 text=original.replace(anchor,capture_text+anchor);assert text.replace(capture_text,'',1)==original
 assert text.rstrip().endswith('FINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS()')
 assert not any(q in text for q in ['emu.setState(','emu.loadSavestate(','emu.reset('])
 assert not any("w('"+n+"'"in text for n in ['PlayerStatus','XgPitFuel','XgPitFlight','XgPitBlocked'])
 (out/'run.lua').write_text(text,encoding='utf-8');assert sha(out/'candidate.nes')==CURRENT
 lua_root=D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1';sys.path.insert(0,str(lua_root));from lupa.lua54 import LuaRuntime
 from parodius_visibility_hud_static_startup_v1 import MOCK
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end')
 rt.execute(text);assert rt.eval('#callbacks')==32 and rt.eval('callbacks[#callbacks].kind==2 and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
 assert rt.eval('#events[emu.eventType.endFrame]')==2
 rt.execute('emu.addMemoryCallback=function()error("Runtime callback registration forbidden")end;emu.removeMemoryCallback=function()error("Runtime callback removal forbidden")end')
 for frame in [1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.endFrame)")
 assert rt.eval('#callbacks')==32
 runtime=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator';isolated=a.output/'emulator';isolated.mkdir()
 for f in runtime.iterdir():
  if f.is_file():shutil.copy2(f,isolated/f.name);files.add(f)
 worker=runtime/'settings.json';user=Path('C:/Mesen2/settings.json');settings=json.loads(worker.read_bytes().decode('utf-8-sig'))
 effective={k:settings['Nes'][k]for k in ['Region','DisableSprites','DisableBackground','RemoveSpriteLimit','AdaptiveSpriteLimit','RandomizeMapperPowerOnState','RandomizeCpuPpuAlignment','RamPowerOnState','PpuExtraScanlinesBeforeNmi','PpuExtraScanlinesAfterNmi','InputScanline','EnablePpuOamRowCorruption','EnablePpuSpriteEvalBug']};effective.update(settings['Emulation'])
 for k,v in dict(Region='Auto',DisableSprites=False,DisableBackground=False,RemoveSpriteLimit=False,AdaptiveSpriteLimit=False,RandomizeMapperPowerOnState=False,RandomizeCpuPpuAlignment=False,PpuExtraScanlinesBeforeNmi=0,PpuExtraScanlinesAfterNmi=0,RunAheadFrames=0,EmulationSpeed=100).items():assert effective[k]==v,(k,effective[k])
 (a.output/'environment').mkdir();shutil.copy2(user,a.output/'environment/user-settings.json');shutil.copy2(worker,a.output/'environment/source-worker-settings.json')
 options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false']
 env=dict(emulator=str(isolated/'Mesen.exe'),emulator_sha256=sha(isolated/'Mesen.exe'),core_sha256=sha(isolated/'MesenCore.dll'),isolated_worker_settings=str(isolated/'settings.json'),worker_settings_sha256=sha(worker),source_runtime=str(runtime),user_context=str(user),user_context_sha256=sha(user),effective_persisted_conditions=effective,actual_command_overrides=options,notes='Persisted RAMRandom is overridden by actual AllZeros command. Hardware8sprites/adaptiveoff/noextraPPUlines/runahead0/speed100. Portable runtime copied fresh; no user/source worker settings write. Existing emulator accuracy flags retained, not a hardware-console fidelity claim.')
 (a.output/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
 seeds=dict(track_A='Real head/block/reveal/full rise and60-update transforms0→1→2; mature actor is repositioned for contact only after full rise. Not an unassisted route.',track_B='Actual controller/native dispatch at cold0/acquired1/acquired2; legal world/player/motion/target setup at GameLoop entry, no tier/fuel/flight/pogo/reach outcome seeds.',world='Logical Block_Buffer_1/MmSolidTerrain/MmBrickHealth cleared; staged floor and matching live nametable/metatile graphics; visible question block before real head hit.',player='Position112,Y176/page0/high1, facing and velocities/fractions, collision and scroll readiness reset in bounded native update arenas.',protection='InjuryTimer and StarInvincibleTimer cleared in arena setup; controlled healthy use, not earned depletion or an injury test.',pools='Old block/bullet/expanded-shot pools reset only after native previous ability cleanup assertions; no active result rewritten.',targets='Six enemy slots cleared at arena entry; hammer case introduces native GoombaID6/high1/defaultHealth0, raisedY168 with valid support, x136/right or88/left; enemy flags/state/speed/collision scaffolding explicitly staged.',forbidden_writes=['PlayerStatus','XgPitFuel','XgPitFlight','XgPitBlocked'],real_native_checks='All original hammer active window/single hit/defeat/cleanup; tier0/1 flight refusal; tier2 exact60burn/FE8000 lift/exhaust/landing60recharge/nextjump; release cancels partial flight and recharges.',planned_cases=cfg['abilities'])
 (a.output/'seed-policy.json').write_text(json.dumps(seeds,indent=2)+'\n')
 static=dict(passed=True,native_run=False,Lua_runtime=rt.eval('_VERSION'),script_sha256=sha(out/'run.lua'),original_current_observer_script_sha256=sha(old/'run.lua'),read_only_capture_insertion_only=True,mechanics_and_controller_normalize_exact=True,static_memory_callbacks=32,dispatcher_last=True,endFrame_callbacks=2,capture_before_original_stop=True,inactive_full_PPU_mock_frames=3,actual_mode_required=0,planned_cases=10,E008_protocol=cfg['dma_protocol'])
 (a.output/'static-proof.json').write_text(json.dumps(static,indent=2)+'\n')
 for f in [capture,Path(__file__),ROOT/'tools/audit/final_item_abilities_pit731_run_v1.py',ROOT/'tools/audit/parodius_visibility_hud_static_startup_v1.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py',Path(sys.executable),Path(sys.modules['lupa'].__file__),Path(sys.modules[LuaRuntime.__module__].__file__),user]:files.add(f)
 source=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq/source'
 for rel,h in json.loads((source.parent/'source-manifest.json').read_text()).items():
  f=source/rel;assert sha(f)==h;files.add(f)
 files.add(source.parent/'source-manifest.json')
 # Bind local Python imports transitively, including source/CPU mock helpers.
 pending=[Path(__file__),ROOT/'tools/audit/final_item_abilities_pit731_run_v1.py'];seen=set()
 while pending:
  f=pending.pop()
  if f in seen:continue
  seen.add(f);files.add(f)
  for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   mods=[node.module]if isinstance(node,ast.ImportFrom)else[q.name for q in node.names]if isinstance(node,ast.Import)else[]
   for n in mods:
    if n:
     dep=ROOT/'tools/audit'/(n.split('.')[0]+'.py')
     if dep.is_file():pending.append(dep)
 files.update(f for f in a.output.rglob('*')if f.is_file())
 bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files,key=str)]
 (a.output/'manifest.json').write_text(json.dumps(dict(bindings=bindings),indent=2)+'\n')
 command='python -B tools/audit/final_item_abilities_pit731_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant'
 proof=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=CURRENT,profile='pit-easy',actual_mode_required=0,output=str(out),planned_ability_cases=10,physical_collections_required=2,committed_transform_updates_required=120,maximum_launches=1,retry=False,other_profiles_authorized=False,script_sha256=sha(out/'run.lua'),static_proof_sha256=sha(a.output/'static-proof.json'),source_observer_proof_sha256=sha(frozen/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),manifest_bindings=len(bindings),environment=env,stable_command=command,post_run_required=['native-abilities.json','ppu-capture-native-result.json','ability-dma-epochs.jsonl','actual-ppu.argb','actual-ppu-index.csv','original case screenshots','independent raw/source/hardware checks','separate selected whole-PPU/interaction review'],limits='Source/runtime preparation only, no grant/run/pass. A physical prefix includes disclosed post-rise contact placement; B arenas reset world/motion/pools/protection and explicitly stage Goomba. No tier/fuel/flight/resource outcome writes. No Hard/otherfamilies/campaign/everyitem/waveform or global visual claim.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 for q in bindings:assert sha(q['path'])==q['sha256']
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),script_sha256=sha(out/'run.lua'),stable_command=command),indent=2))

if __name__=='__main__':main()
