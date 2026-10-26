"""Seal the ONE delegated age75->125 controller correction. Never runs Mesen."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
from final_item_abilities_run import lua
from final_item_abilities_static_prepare_v2 import ROOT
from final_item_abilities_remaining731_run_v1 import verify_manifest
from parodius_visibility_hud_static_startup_v1 import MOCK
from final_bass_delivery_run_v1 import SHA
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',required=True,type=Path);p.add_argument('--negative',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--lua-root',required=True,type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 verify_manifest(a.ready/'manifest.json');verify_manifest(a.negative/'manifest.json');oldproof=json.loads((a.ready/'proof.json').read_text());old=Path(oldproof['output']);negative=json.loads((old/'proof.json').read_text());assert negative['passed']is False and negative['runner_exit']==1 and negative['dependencies_unchanged'];failure=json.loads((old/'first-failure.json').read_text());assert failure['message']=='Bounded actual acquired use/cleanup'
 controls=json.loads((a.negative/'water-source-controls.json').read_text());assert controls['passed']and controls['ROM_sha256']==SHA and controls['cases']==5
 cfg=json.loads((old/'config.json').read_text());cfg['pickup_art']={int(k):v for k,v in cfg['pickup_art'].items()};script=(old/'run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n';assert script.startswith(prefix);body=script[len(prefix):]
 before='current.item==7 and age>=75 and age<80';after='current.item==7 and age>=125 and age<130';assert body.count(before)==1;new=body.replace(before,after);assert new.replace(after,before)==body
 assert "assert(age<650,'Bounded actual acquired use/cleanup')"in new
 out=a.output/'native';out.mkdir()
 for ext in['.nes','.dbg','.lbl','.map']:shutil.copy2(old/('candidate'+ext),out/('candidate'+ext))
 put(out/'config.json',cfg);assert(old/'config.json').read_bytes()==(out/'config.json').read_bytes();(out/'run.lua').write_text(prefix+new,encoding='utf-8');shutil.copy2(old/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua')
 assert sha(out/'candidate.nes')==SHA
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end')
 tests="""
current={item=7};phase='use'
for _,q in ipairs({{5,true},{11,true},{12,false},{74,false},{75,false},{79,false},{80,false},{124,false},{125,true},{129,true},{130,false}})do age=q[1];local v=deliveryInput();assert(not not v.b==q[2],'Exact bounded WATER pulse controller')end
"""
 rt.execute((out/'run.lua').read_text()+tests);assert rt.eval('#callbacks')==73 and rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')and rt.eval('#events[emu.eventType.endFrame]')==3
 rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 put(a.output/'controller-only-diff.json',dict(before=before,after=after,reverse_exact=True,all_other_script_body_config_ROM_guard_seed_input_bytes_exact=True,unchanged_case_use_deadline=650,source_controls_path=str(a.negative/'water-source-controls.json'),source_controls_sha256=sha(a.negative/'water-source-controls.json'),complete_source_control_cases=5,Lua_input_model_cases=11,static_callbacks=73,dispatcher_last=True,endFrame_callbacks=3,source_policy='Only WATER second press moves50updates later. Earlier four native rewards and all outside input policies remain untouched. No native outcome/arena/resource/result/RNG changes.'))
 env=oldproof['environment'];put(a.output/'environment.json',env)
 files={Path(q['path'])for q in json.loads((a.ready/'manifest.json').read_text())['bindings']};files.update([Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',old/'proof.json',old/'first-failure.json',a.negative/'proof.json',a.negative/'manifest.json',a.negative/'water-source-controls.json']);files.update(q for q in a.output.rglob('*')if q.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]))
 proof=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='bass-easy-four-rewards',mode_value=0,maximum_rewards=4,maximum_launches=1,maximum_owned_workers=1,retry=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),output=str(out),script_sha256=sha(out/'run.lua'),environment=env,source_freeze_sha256=oldproof['source_freeze_sha256'],source_controls_sha256=sha(a.output/'controller-only-diff.json'),preserved_native_FALSE_sha256=sha(old/'proof.json'),stable_command='python -B tools/audit/final_bass_delivery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant',authority_scope='ROOT delegated exactly one age75to125 input successor after frozen full-source hide/refusal/reveal/expand controls and reverse-exact other bytes. No other successor/profile/retry authorized.')
 put(a.output/'proof.json',proof);verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),script_sha256=sha(out/'run.lua'),stable_command=proof['stable_command']),indent=2))

if __name__=='__main__':main()
