"""Only move the overlapping Wave question block above the legal player body."""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,shutil,sys
from final_samus_hard_gallery_source_v1 import D,ROOT,PARENT,SHA
from final_samus_hard_gallery_prepare_v2 import phase_models
from final_samus_hard_gallery_pool_prepare_v1 import setups
from final_item_abilities_remaining731_run_v1 import verify_manifest
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
OLD=D/'current3b112-samus-hard-freeze-clock-ready-v1'
PREFIX=D/'current3b112-samus-hard-wave-prefix-v3/proof.json'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert verify_manifest(OLD/'manifest.json')==1020
 old=OLD/'native';n=json.loads((old/'proof.json').read_text());assert n['passed']is False and n['dependencies_unchanged'];cfg=json.loads((old/'config.json').read_text());b=scoped_load(old/'candidate.nes');assert sha(old/'candidate.nes')==SHA
 before=(ROOT/'tools/audit/final_samus_hard_gallery_native_v4.lua').read_text();after=(ROOT/'tools/audit/final_samus_hard_gallery_native_v5.lua').read_text();u="w('Block_Buffer_1',0xc1,9*16+15);tile(0,15,11,0xc1)";v="w('Block_Buffer_1',0xc1,7*16+15);tile(0,15,9,0xc1)";assert before.count(u)==1 and after==before.replace(u,v)
 previous=(old/'run.lua').read_text();assert previous.count(before)==1;script=previous.replace(before,after);assert script.replace(after,before)==previous
 (a.output/'fixture.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='native_v4.lua',tofile='native_v5.lua')),encoding='utf-8')
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 oldrows,_=setups(LuaRuntime,previous,cfg,b['raw']);newrows,_=setups(LuaRuntime,script,cfg,b['raw']);models=[]
 for x,y in zip(oldrows,newrows):
  changed=y['kind']=='wave-up';diff=[dict(index=i,old=p,new=q)for i,(p,q)in enumerate(zip(x['writes'],y['writes']))if p!=q];assert len(x['writes'])==len(y['writes'])
  if not changed:assert x==y
  else:
   assert len(diff)==6
   for z in diff:
    oldwrite,newwrite=z['old'],z['new'];assert oldwrite[1:]==newwrite[1:]
    if oldwrite[2]==1:assert oldwrite[0]==cfg['ram']['Block_Buffer_1']+9*16+15 and newwrite[0]==cfg['ram']['Block_Buffer_1']+7*16+15
    else:assert oldwrite[2]==2 and oldwrite[0]-newwrite[0]in[128,8]
   assert y['RAM'][cfg['ram']['Block_Buffer_1']+9*16+15]==0 and y['RAM'][cfg['ram']['Block_Buffer_1']+7*16+15]==193
  models.append(dict(case=y['case'],task=y['task'],kind=y['kind'],passed=True,changed_writes=diff,all_other_writes_and_RAM_exact=not changed))
 assert len(models)==27 and sum(bool(z['changed_writes'])for z in models)==2
 prefix=json.loads(PREFIX.read_text());assert prefix['passed']and prefix['ROM_sha256']==SHA
 legal=[q for q in prefix['results']if q['variant']=='block-above-player'];assert len(legal)==2 and all(q['page_crossings']==6 for q in legal)
 phases=phase_models(LuaRuntime,script);assert len(phases['models'])==32;put(a.output/'source-controls.json',dict(passed=True,actual_setup_tasks=27,unchanged_tasks=25,only_changed_tasks='Two wave-up scene setups; one logical tile write plus5PPU tile/attribute writes relocated in each.',setup_models=models,original_phase_models=phases,full_GameLoop_prefix_proof_sha256=sha(PREFIX),legal_upward_both_facings=dict(centers=[254,258],page_crossings_each=6,source_MegaManBlocks_calls=0,natural_expiry=True),future_Varia_Screw_initial_solid_overlap=False,future_stage_legality=prefix['future_stage_legality'],all_other_script_config_seeds_inputs_ability_oracles_strict_guards_exact=True))
 out=a.output/'native';out.mkdir()
 for ext in['nes','dbg','lbl','map']:shutil.copy2(old/('candidate.'+ext),out/('candidate.'+ext))
 for f in['config.json','inherited-NMI-stack-APU-guards.lua']:shutil.copy2(old/f,out/f)
 (out/'run.lua').write_text(script,encoding='utf-8')
 for f in['plans.json','seed-policy.json']:shutil.copy2(OLD/f,a.output/f)
 runtime=a.output/'emulator';runtime.mkdir()
 for q in(OLD/'emulator').iterdir():
  if q.is_file():shutil.copy2(q,runtime/q.name)
 env=copy.deepcopy(json.loads((OLD/'proof.json').read_text())['environment']);env['emulator']=str(runtime/'Mesen.exe');env['user_settings_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(runtime/'Mesen.exe')==env['emulator_sha256']and sha(runtime/'settings.json')==env['worker_settings_sha256'];put(a.output/'environment.json',env)
 report=ROOT/'docs/qa/final-samus-hard-gallery-wave-arena-2026-10-26.txt';report.write_text('Samus Hard Wave legal-arena fixture correction\n26 October 2026. Source/static only; no nativegrant inferred. ExactROM '+SHA+' unchanged.\n\nFourth native ddd3b354834a0d1013ec1ef0cd2bea8acdd0c4dba5635bf2ad18b83d7531fbc2 remainsFALSE. It completed bothIce subphases including actual before256/partial0/after255 and360natural thaw, then failed first upwardWave expectedworldcenter. Native actual position operands were not logged and are not backfilled.\n\nFull compiled GameLoop reproduces literal old scene: question tile atworld240..255/Y176..191 overlaps seeded playerX244/252/Y176. Native PlayerCtrl/background collision movesX255 before B, so actual muzzle/firstMove usesworld265/261 rather than254/258. Sourcehelper banks/stack/return correct; no Wave game defect is shown. First source-model draft misclassified JMP-entered fixed-page tail with its PHA payload as a JSR entry; retained source-only. Corrected source trace models its genuine stack payload and completes callerSP.\n\nONE line relocates only wave-up C1 logicalrow9→7/visibleY176→144 (tile row11→9), abovebody176..207 with16px clearance. Player/resources/position seeds,controller,Hard1,intended254/258worldcenter, fullWave/page/terrainbypass/cleanup assertions unchanged.27actualLua setup comparisons:25exact; only2wave-up tasks relocate1logical+5PPU tile/attribute writes, allotherwrites/seedvalues unchanged. FullcompiledGameLoop through realSpawn/Muzzle/Move inbothfacings preservesX244/252,sourcecenter254/258,6worldpagecrossings each,naturalexpiry andzero normalweaponblockqueries. SeparatehorizontalWaveblock task unchanged. Future4Varia/2Screw setups have no solids overlappingplayer; declaredfirebar/enemyhazard/bodycontacts remainintentional.32phase models pass.\n\nNo postsetup playerforcing,gamecode/default/settings/Git changes,nativepass/allitem/visual/audio/FPS claim. This remains B controlled use,not acquisition.\n',encoding='utf-8')
 files={Path(z['path'])for z in json.loads((OLD/'manifest.json').read_text())['bindings']};files.update({Path(__file__),ROOT/'tools/audit/final_samus_hard_gallery_native_v5.lua',ROOT/'tools/audit/final_samus_hard_gallery_wave_prefix_v1.py',ROOT/'tools/audit/final_samus_hard_gallery_wave_prefix_v2.py',ROOT/'tools/audit/final_samus_hard_gallery_wave_prefix_v3.py',PREFIX,report,OLD/'proof.json',OLD/'manifest.json',old/'proof.json',old/'first-failure.json'});files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));count=verify_manifest(a.output/'manifest.json');command='python -B tools/audit/final_samus_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant';put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='samus-hard',mode_value=1,maximum_cases=8,maximum_launches=1,maximum_owned_workers=1,retry=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=count,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,source_controls_sha256=sha(a.output/'source-controls.json'),stable_command=command,source_freeze_sha256=sha(PARENT/'ROOT-source-readiness.json'),original_FALSE_sha256=sha(old/'proof.json'),fixture_only=True,report_sha256=sha(report)));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),script_sha256=sha(out/'run.lua'),bindings=count,stable_command=command),indent=2))
if __name__=='__main__':main()
