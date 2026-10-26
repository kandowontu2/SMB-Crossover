"""Source/runtime preparation of five unrun current731 acquired-ability profiles."""
from pathlib import Path
import argparse,ast,hashlib,json,re,shutil,sys
from final_item_abilities_remaining731_run_v1 import PROFILES
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True,exist_ok=False)
 frozen=D/'current731-abilities-observer-v4';files=set()
 for folder in [frozen,frozen/'static-return-control']:
  for q in json.loads((folder/'manifest.json').read_text())['bindings']:
   f=Path(q['path']);assert sha(f)==q['sha256'] and f.stat().st_size==q['bytes'];files.add(f)
  files.update(folder/n for n in ['proof.json','manifest.json','controls.json'])
 pilot=D/'current731-pit-easy-pilot-final-v1';pilotproof=json.loads((pilot/'proof.json').read_text());assert pilotproof['passed']and pilotproof['ROM_sha256']==CURRENT and pilotproof['actual_numeric_mode']==0
 files.update(pilot/n for n in ['proof.json','summary.json','manifest.json','visual-review.json','ledger-component.json'])
 capture=ROOT/'tools/audit/final_item_abilities_pit731_ppu_v1.lua';capture_text=capture.read_text()+'\n';sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
 from parodius_visibility_hud_static_startup_v1 import MOCK
 profiles=[];seed_profiles=[]
 for name,(family,hard,mode,count)in PROFILES.items():
  old=frozen/name;out=a.output/'profiles'/name/'native';out.mkdir(parents=True)
  for n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','config.json','run.lua']:shutil.copy2(old/n,out/n)
  cfg=json.loads((out/'config.json').read_text());assert (cfg['family'],cfg['hard'],cfg['mode_value'],len(cfg['abilities']))==(family,hard,mode,count)
  assert cfg['hard']is hard and cfg['mode_value']==int(hard)
  assert [(q['before'],q['after'])for q in cfg['steps']]==[(0,1),(1,2)]
  original=(old/'run.lua').read_text();anchor='emu.addEventCallback(function()\n wall=wall+1\n';assert original.count(anchor)==1
  text=original.replace(anchor,capture_text+anchor);assert text.replace(capture_text,'',1)==original
  assert text.rstrip().endswith('FINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS()')
  assert not any("w('"+n+"'"in text for n in ['PlayerStatus','XgPitFuel','XgPitFlight','XgDiskReach','XgDiskReturning','ScPogo'])
  (out/'run.lua').write_text(text,encoding='utf-8');assert sha(out/'candidate.nes')==CURRENT
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end');rt.execute(text)
  assert rt.eval('#callbacks')==32 and rt.eval('callbacks[#callbacks].kind==2 and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')and rt.eval('#events[emu.eventType.endFrame]')==2
  rt.execute('emu.addMemoryCallback=function()error("Runtime callback registration forbidden")end;emu.removeMemoryCallback=function()error("Runtime callback removal forbidden")end')
  for frame in [1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.endFrame)")
  assert rt.eval('#callbacks')==32
  b=scoped_load(out/'candidate.nes');source=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq/source'
  owners={'pit':[('expanded_weapons.s','PitFlightUpdate'),('megaman_weapons.s','MegaManWeapons::DamageEnemy')],
   'rygar':[('expanded_weapons.s','ExpandedWeapons::MoveShot'),('expanded_weapons.s','ExpandedWeapons::CatchDisk'),('megaman_weapons.s','MegaManWeapons::DamageEnemy')],
   'scrooge':[('scrooge.s','ScroogeMovement'),('scrooge.s','ScroogeMovement::Bounce'),('scrooge.s','ScroogePogoContact'),('megaman_weapons.s','MegaManWeapons::DamageEnemy')]}[family]
  refs=[]
  for file,symbol in owners:
   f=source/'src'/file;part=symbol.split('::')[-1];lines=f.read_text().splitlines();line=next(i for i,s in enumerate(lines,1)if re.search(r'(?:\.proc\s+|^\s*)'+re.escape(part)+r'(?:\s|:|$)',s))
   refs.append(dict(path=str(f),source_sha256=sha(f),line=line,symbol=symbol,CPU_address=address(b,symbol),physical_bank=(location(b,symbol)-16)//8192,first3bytes=list(b['raw'][location(b,symbol):location(b,symbol)+3])))
  difference={'pit':'10plans:6hammer bothfacings/tier0..2;2lower-tier flight refusals;full60fuel and partial release. Actual source liftFE8000 and ground60recharge.',
   'rygar':'12plans:free/hit x bothfacings x3tiers. Native source extension/retraction24..40/64/88..20, hand anchor and catch; one live disk. No flight/pogo.',
   'scrooge':'9plans:ground-pogo/release plus enemy-contact bothfacings at eachtier. Native dry launchFA2500 and no injury; cane/pogo ability does not become stronger by tier.'}[family]
  setup={'pit':'Six raised stationary GoombaID6/high1/defaultHP0 targets, facing-relative x136/88,y168 and legal support. No fuel/flight writes.',
   'rygar':'Six disk-hit cases introduce the same raised native Goomba; six free-disk cases have no target. Prior disk must actually catch/reach0 before arena reset. No reach/returning writes.',
   'scrooge':'Ground-pogo cases have no target. Six enemy cases introduce Goomba below x112/y184 only AFTER real airborne motion and adequate separation (Y+32<192); no forced airborne/pogo state. Prior native pogo/attack cleanup asserted.'}[family]
  seed=dict(profile=name,family=family,actual_mode_required=mode,behavior_difference=difference,source_owners=refs,common_A_setup='Actual cold selection,two real head/block/reveal/fullrise/no-premature-grant collections0→1→2/two60transforms. Explicit post-rise contact alignment; no tier write.',common_B_setup='World logical/visible floor/questionblock; playerposition/motion/fractions/facing/scroll readiness; empty prior shot/block pools and protection timers staged at guarded GameLoop entry. No resource/ability outcome acquisition claimed from setup.',family_target_setup=setup,all_tier_fuel_flight_reach_pogo_outcome_writes_forbidden=True,planned_cases=cfg['abilities'])
  seed_profiles.append(seed)
  profile=dict(profile=name,family=family,mode='hard'if hard else'easy',actual_mode_required=mode,planned_ability_cases=count,physical_collections_required=2,committed_transform_updates_required=120,output=str(out),script_sha256=sha(out/'run.lua'),source_template_sha256=sha(old/'run.lua'),read_only_PPU_capture_module_sha256=sha(capture),mechanics_and_controller_normalize_exact=True,static_callbacks=32,dispatcher_last=True,capture_before_original_stop=True,Lua_runtime=rt.eval('_VERSION'),inactive_PPU_mock_frames=3,source_owners=refs,maximum_launches=1)
  profiles.append(profile)
 assert len(profiles)==5 and sum(p['planned_ability_cases']for p in profiles)==52
 runtime=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator';isolated=a.output/'emulator';isolated.mkdir()
 for f in runtime.iterdir():
  if f.is_file():shutil.copy2(f,isolated/f.name);files.add(f)
 worker=runtime/'settings.json';user=Path('C:/Mesen2/settings.json');settings=json.loads(worker.read_bytes().decode('utf-8-sig'))
 effective={k:settings['Nes'][k]for k in ['Region','DisableSprites','DisableBackground','RemoveSpriteLimit','AdaptiveSpriteLimit','RandomizeMapperPowerOnState','RandomizeCpuPpuAlignment','RamPowerOnState','PpuExtraScanlinesBeforeNmi','PpuExtraScanlinesAfterNmi','InputScanline','EnablePpuOamRowCorruption','EnablePpuSpriteEvalBug']};effective.update(settings['Emulation'])
 for k,v in dict(Region='Auto',DisableSprites=False,DisableBackground=False,RemoveSpriteLimit=False,AdaptiveSpriteLimit=False,RandomizeMapperPowerOnState=False,RandomizeCpuPpuAlignment=False,PpuExtraScanlinesBeforeNmi=0,PpuExtraScanlinesAfterNmi=0,RunAheadFrames=0,EmulationSpeed=100).items():assert effective[k]==v,(k,effective[k])
 (a.output/'environment').mkdir();shutil.copy2(user,a.output/'environment/user-settings.json');shutil.copy2(worker,a.output/'environment/source-worker-settings.json')
 env=dict(emulator=str(isolated/'Mesen.exe'),emulator_sha256=sha(isolated/'Mesen.exe'),core_sha256=sha(isolated/'MesenCore.dll'),worker_settings_sha256=sha(worker),user_context=str(user),user_context_sha256=sha(user),effective_persisted_conditions=effective,actual_command_overrides=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'],notes='New isolated portable runtime; one sequential worker shared by these five one-shot profiles only after grant. Persisted RAMRandom overridden by actual AllZeros; no saves/user/sourceworker config writes. Existing accuracy flags recorded, not physical-console fidelity.')
 put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n')
 put(a.output/'environment.json',env);put(a.output/'seed-policies.json',seed_profiles);put(a.output/'static-controls.json',dict(passed=True,native_run=False,profiles=profiles,total_plans=52,Lua_runtime='Lua 5.4',full_generated_inactive_mock_frames=15))
 commands={p['profile']:'python -B tools/audit/final_item_abilities_remaining731_run_v1.py --ready "'+a.output.as_posix()+'" --profile '+p['profile']+' --native-grant'for p in profiles}
 put(a.output/'commands.json',commands)
 for f in [Path(__file__),capture,ROOT/'tools/audit/final_item_abilities_remaining731_run_v1.py',ROOT/'tools/audit/parodius_visibility_hud_static_startup_v1.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py',Path(sys.executable),Path(sys.modules['lupa'].__file__),Path(sys.modules[LuaRuntime.__module__].__file__),user]:files.add(f)
 source=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq/source'
 for rel,h in json.loads((source.parent/'source-manifest.json').read_text()).items():f=source/rel;assert sha(f)==h;files.add(f)
 files.add(source.parent/'source-manifest.json')
 pending=[Path(__file__),ROOT/'tools/audit/final_item_abilities_remaining731_run_v1.py'];seen=set()
 while pending:
  f=pending.pop()
  if f in seen:continue
  seen.add(f);files.add(f)
  for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   mods=[node.module]if isinstance(node,ast.ImportFrom)else[q.name for q in node.names]if isinstance(node,ast.Import)else[]
   for n0 in mods:
    if n0:
     dep=ROOT/'tools/audit'/(n0.split('.')[0]+'.py')
     if dep.is_file():pending.append(dep)
 files.update(f for f in a.output.rglob('*')if f.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files,key=str)]))
 ready=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=CURRENT,profiles=profiles,total_planned_abilities=52,maximum_launches_per_profile=1,automatic_next_profile=False,retries=False,maximum_owned_workers=1,maximum_project_workers=2,environment=env,manifest_sha256=sha(a.output/'manifest.json'),manifest_bindings=len(files),static_controls_sha256=sha(a.output/'static-controls.json'),seed_policies_sha256=sha(a.output/'seed-policies.json'),commands=commands,pilot_current_narrow_proof_sha256=sha(pilot/'proof.json'),limits='Source/runtime preparation ONLY; none of these five profiles launched/granted. Exact original family-specific input/mechanics/guards preserved, same fullPPU/E008256/startupstatic observer as qualified PitEasy. Physical prefixes have disclosed post-rise contact alignment; B controlled arenas/targets/protection/pools. No completepowerup/star/1up/Hard-from-Easy/sourceaudio/allpixel/campaign claim.')
 put(a.output/'proof.json',ready)
 for q in json.loads((a.output/'manifest.json').read_text())['bindings']:assert sha(q['path'])==q['sha256']
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),profiles=5,planned_abilities=52,commands=commands),indent=2))

if __name__=='__main__':main()
