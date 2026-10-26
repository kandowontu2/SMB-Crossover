"""Freeze two unrun shared-NMI controls; source preparation only, no Mesen launch."""
from pathlib import Path
import argparse, ast, hashlib, json, sys
from cv3_primary_sfx_source_v1 import CV3, CV3_SHA
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):assert not p.exists(),p;p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();O=a.prepared;a.output.mkdir(parents=True,exist_ok=False);q=get(O/'preparation.json');assert q['passed']and not q['native_run']
 ROM=Path(q['ROM']);P=ROM.parent;SHA=q['ROM_sha256'];assert sha(ROM)==SHA=='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
 assert not(O/'menu/baseline-early/launch.json').exists()and not(O/'menu/baseline-early/native-result.json').exists()and not(O/'hard1f/proof.json').exists()
 assert q['menu_hook_changes']==q['hard_hook_changes']==[]
 proof_paths=[O/name/'proof.json'for name in ['menu-static','menu-DMA-mock','menu-timing-mock','hard-startup','hard-observer']]
 assert all(get(f)['passed']for f in proof_paths)
 sm,dm,tm=get(proof_paths[0]),get(proof_paths[1]),get(proof_paths[2]);assert(sm['memory_callbacks'],sm['complete_generated_mock_frames'],sm['timing_finalizer_event_index'],sm['additional_finalizer_event_index'],sm['original_stop_event_index'])==(73,439,1,5,6);assert(dm['cases'],dm['intentional_rejections'])==(38,34);assert(tm['cases'],tm['intentional_rejections'])==(35,26)
 runtime=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator';settings=Path('C:/Mesen2/settings.json');worker=runtime/'settings.json';env=get(D/'parodius-menu-clean731-ready-v1/proof.json')['environment']
 assert sha(settings)==env['user_settings_sha256']=='8a439e0a5eeddc2d4776e516aacfc224c03048b9c7d23d9926a463460a7e748a';assert sha(worker)==env['worker_settings_sha256']=='627cd9c71a2011b4cf5fb03a0712d4d77f7890bc269b174d5757776034aab715'
 for folder in [runtime,Path('C:/Mesen2')]:
  assert sha(folder/'Mesen.exe')==env['emulator_sha256']and sha(folder/'MesenCore.dll')==env['core_sha256']
 for f in [settings,worker]:
  s=json.loads(f.read_text(encoding='utf-8-sig'));assert all(s['Nes'][n]is False for n in ['RemoveSpriteLimit','AdaptiveSpriteLimit','DisableSprites','DisableBackground','RandomizeMapperPowerOnState','RandomizeCpuPpuAlignment']);assert s['Emulation']['RunAheadFrames']==0 and s['Nes']['PpuExtraScanlinesBeforeNmi']==s['Nes']['PpuExtraScanlinesAfterNmi']==0
 assert sha(CV3)==CV3_SHA
 menu=O/'menu/baseline-early';hard=O/'hard1f';base=D/'root-clean731-hard1f-v1/fixture'
 baseline=get(base/'proof.json');assert baseline['passed']and baseline['updates']==240 and baseline['draws']==168 and baseline['cases'][0]['modeReadback']==1
 menusource=D/'parodius-menu-clean731-native-final-v1/proof.json';mz=get(menusource);assert mz['passed']and mz['ROM_sha256']=='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'and mz['ungated_completed_full256_DMAs']==1300
 options=['--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false','--option=--nes.removeSpriteLimit=false']
 profiles=[dict(name='menu',mode=0,limit=1800,output=str(menu),baseline=str(menusource),native_command=[sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_run.py'),'--packet',str(O/'menu'),'--emulator',str(runtime/'Mesen.exe'),'--timeout','900']),dict(name='hard1f',mode=1,updates=240,output=str(hard),baseline=str(base),native_command=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(hard),'--emulator','C:/Mesen2/Mesen.exe',str(hard/'run.lua'),str(ROM),'--timeout','180',*options])]
 files=set(f for f in O.rglob('*')if f.is_file());files.update([P/'ROOT-source-readiness.json',P/'ROOT-bindings.json',P/'source-manifest.json',P/'ROOT-composition-controls.json',CV3,settings,worker,Path(sys.executable),menusource,D/'parodius-menu-clean731-ready-v1/proof.json',D/'root-clean731-hard1f-v1/native-launch-v1/proof.json'])
 for n in ['proof.json','run.lua','configuration.json','preparation.json','apu.csv','cadence.csv']:files.add(base/n)
 for n in ['expected-hud-fonts.bin','expected-all5376-HUD-pixels.bin','expected-hud-art.json']:files.add(D/'parodius-menu-clean731-preparation-v1'/n)
 files.add(D/'parodius-menu-clean731-preparation-v1/menu/preparation.json');files.add(D/'parodius-menu-clean731-preparation-v1/menu/baseline-early/run.lua');files.add(D/'parodius-menu-clean731-preparation-v1/menu/baseline-early/config.json')
 for f in [P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',P/'candidate.map',P/'candidate.build.json',P/'candidate.cv3-mirror.json']:files.add(f)
 source=get(P/'source-manifest.json');assert len(source)==869
 for n,h in source.items():assert sha(P/'source'/n)==h;files.add(P/'source'/n)
 for path,h in get(P/'ROOT-bindings.json').items():
  expected=h['sha256']if isinstance(h,dict)else h;assert sha(path)==expected
  if isinstance(h,dict):assert Path(path).stat().st_size==h['bytes']
  files.add(Path(path))
 for folder in [runtime,Path('C:/Mesen2')]:files.update(folder.glob('*.dll'));files.add(folder/'Mesen.exe')
 for folder in [D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1',D/'final-tmnt-items-v1/lua-parser-deps-v1']:files.update(f for f in folder.rglob('*')if f.is_file()and'__pycache__'not in f.parts)
 pending=[ROOT/'tools/audit'/name for name in ['current3b_nmi_regression_prepare_v1.py','current3b_nmi_regression_ready_v1.py','current3b_nmi_regression_run_v1.py','parodius_visibility_run.py','run_mesen_isolated.py','parodius_visibility_menu59_static_v1.py','parodius_visibility_menub0_dma_mock_v1.py','parodius_visibility_menu59_timing_mock_v1.py','cv3_remaining_sfx_queue_native_startup_v2.py','cv3_remaining_sfx_legacy_wrapper_observer_v1.py','cv3_remaining_sfx_lifecycle_verify_v3.py']];seen=set()
 while pending:
  f=pending.pop()
  if f in seen:continue
  seen.add(f);files.add(f)
  for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   names=[node.module]if isinstance(node,ast.ImportFrom)and node.module else[x.name for x in node.names]if isinstance(node,ast.Import)else[]
   for n in names:
    local=ROOT/'tools/audit'/(n.split('.')[0]+'.py')
    if local.is_file():pending.append(local)
 files.add(ROOT/'tools/run_mesen.py');files.update(f for f in(D/'current3b-nmi-regression-ready-v1').iterdir()if f.is_file())
 for path,h in get(O/'menu/preparation.json')['dependencies'].items():assert sha(path)==h;files.add(Path(path))
 # Exact historical template body already embeds the fixed Lua modules; bind their original sources too.
 for pattern in ['parodius_visibility_*.lua','cv3_remaining_sfx_*native*.lua','cv3_remaining_sfx_static_core_v1.lua','cv3_remaining_sfx_lifecycle_queue_v1.lua']:
  files.update((ROOT/'tools/audit').glob(pattern))
 report=ROOT/'docs/qa/current3b-nmi-regression-readiness-2026-10-26.txt';assert not report.exists()
 report.write_bytes(('PREPARED ONLY: combined3b shared-NMI regression, no native grant/run\n\n'
 f'Exact private ROM:{SHA}\nSource readiness:{q["source_ready"]} SHA{q["source_readiness_sha256"]}\nPrepared:{O}\n\n'
 'Two finite profiles only. Menu: original qualified Easy0 allfourships1800 controller, titlecancel/reentry, full1651PPU capture window, original six mechanical/source/body/IRQ/scroll/font guards and ungated E008/full256/timing module. Hard1F: original staged Hard1F240 controller/actors/queue/source/DMC/raw400F/priority/mixer/SMC/stack/bank/full256DMA/render-enable/cadence guards, same numeric1 and180sec timeout. No resource/actor/outcome changes to either original fixture. The Hard arena still has its original explicit pre-arena staging; it is not a natural level playthrough.\n\n'
 'Only genuine ROM/output/compiled metadata rebound. Both hooks catalogs unchanged on actual3b; every RAM address, sample, queue writer, all131body records and5376HUD source references match. Controller and full observer/mechanics bodies normalize byte-exact after new output-path substitution. No fabricated callable aliases. Combined3b intentionally includes9ee robot-shot code; no claim its source equals the original3cee shot code.\n\n'
 'Source preparation controls pass: menu complete generated439 inactive epochs/73 fixed startup callbacks/last broad dispatcher; finalization slots timing1/pair5/originalstop6; DMA mocks38/34rejections; timing mocks35/26rejections. Hard full startup439 plus actual assembled cast, genuine queue publication/consumption and140 lagNMI/original-source control pass. Mock counter/actor setup stays outside prepared native scripts. No runtime callback addition/removal.\n\n'
 'Both runtime environments exactly match historical settings/executable/core bindings. Hardware sprite limit enabled, adaptiveoff, no extra PPU lines, runahead0. Original doNotSaveSettings/AllZeros/nonrandom overrides unchanged; no settings writes. Menu uses its original portable runtime and900sec bound; Hard uses original C:/Mesen2 and180sec bound. One worker sequentially, project cap2/user emulator isolated, stop firstfailure/no retry.\n\n'
 'Retained preparation-only schema FALSE: first readiness attempt expected flat digests, while ROOT-bindings uses {bytes,sha256}. It stopped before readiness/report or native launch; corrected consumer checks both hash and size. Original failed-tool/failure receipt retained.\n\n'
 'Historical731 menu1300 completed full256DMAs and Hard240updates/168totaldraws are separate baselines, not current3b passes. Hard comparator preserves its exact original strict prefix/no-worse-stall/fulltotal/complete hardware stream predicates. Menu original guards remain unchanged; actual completed counts/cadence and wholeframe review versus historical baseline remain explicit postrun review, not silently certified by component checks. No extra screenshot/public checkpoint bundle is generated here. Previous native negatives remain immutable.\n\n'
 f'Readiness:{a.output/"readiness.json"}\nOne-shot profile commands:{a.output/"command.json"}\nNO RUN UNTIL ROOT REVIEW AND EXPLICIT GRANT. No new source/ROM/settings/default/Git/Downloads mutation.\n').encode())
 files.add(report);bindings={str(f.resolve()):sha(f)for f in sorted(files,key=str)};put(a.output/'bindings.json',bindings)
 readiness=dict(passed=True,source_only=True,native_run=False,native_granted=False,adopted=False,ROM_sha256=SHA,preparation=str(O/'preparation.json'),preparation_sha256=sha(O/'preparation.json'),profiles=profiles,maximum_future_launches=2,sequential=True,stop_first_failure=True,retry_allowed=False,original_controller_and_all_guard_bodies_exact=True,menu_original_components=['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json'],hard_original_validator=str(ROOT/'tools/audit/cv3_remaining_sfx_lifecycle_verify_v3.py'),hard_baseline=str(base),baseline_Menu_full256DMAs=1300,baseline_Hard_draws=168,environment=env,bindings=len(bindings),bindings_sha256=sha(a.output/'bindings.json'),report=str(report),report_sha256=sha(report),scope='Only unrun two-profile same-input shared-NMI regression preparation on3b. No native timing/visual/source outcome transfer or adoption.')
 put(a.output/'readiness.json',readiness)
 commands={c['name']:[sys.executable,'-B',str(ROOT/'tools/audit/current3b_nmi_regression_run_v1.py'),'--ready',str(a.output),'--expected-readiness-sha256',sha(a.output/'readiness.json'),'--profile',c['name'],'--native-grant']for c in profiles};put(a.output/'command.json',commands)
 put(a.output/'seal.json',dict(passed=True,source_only=True,native_run=False,readiness_sha256=sha(a.output/'readiness.json'),bindings_sha256=sha(a.output/'bindings.json'),command_sha256=sha(a.output/'command.json'),preparation_sha256=sha(O/'preparation.json'),report_sha256=sha(report)))
 assert all(sha(f)==h for f,h in bindings.items())
 print(json.dumps(dict(readiness=str(a.output/'readiness.json'),sha256=sha(a.output/'readiness.json'),bindings=len(bindings),commands_sha256=sha(a.output/'command.json'),seal_sha256=sha(a.output/'seal.json')),indent=2))
if __name__=='__main__':main()
