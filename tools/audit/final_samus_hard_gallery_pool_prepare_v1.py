"""One missing complete-pool setup correction; source/static only."""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,shutil,sys
from final_samus_hard_gallery_source_v1 import ROOT,D,PARENT,SHA,TraceArena
from final_samus_hard_gallery_prepare_v2 import phase_models
from final_item_abilities_remaining731_run_v1 import verify_manifest
from link_pit_rygar_sophia_audit_cpu import scoped_load
from parodius_visibility_hud_static_startup_v1 import MOCK
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
OLD=D/'current3b112-samus-hard-outline-ready-v2'
NEG=D/'current3b112-samus-hard-pool-negative-v2'

def setups(LuaRuntime,script,cfg,raw):
 rt=LuaRuntime(unpack_returned_tuples=True)
 pre=MOCK+'''
L={};OUTPUT='mock/';mem={};ppu={};writes={};rom={}
emu.memType.nesPrgRom=6
emu.read=function(a,t)if t==6 then return rom[a]or 0 elseif t==2 then return ppu[a]or 0 else return mem[a]or 0 end end
emu.write=function(a,v,t)local m=t==2 and ppu or mem;m[a]=v;writes[#writes+1]={a,v,t}end
emu.getScreenBuffer=function()error('Setup models do not synthesize a PPU outcome')end
'''
 export='''
function TEST_SETUP(case,task)
 mem={};ppu={};writes={};entered=true;done=false;phase='setup';wall=374;updates=1;age=0;index=case;taskIndex=task
 current={q=C.cases[case],t=C.cases[case].tasks[task],stages={}}
 mem[L.CrossoverBehaviorVersion]=1;mem[L.SelectedCharacter]=2;mem[L.InvSelected+2]=2
 assert(setupTask());return true
end
'''
 rt.execute(pre+script+export);rom=rt.globals().rom
 for q in cfg['art'].values():
  for i in range(256):rom[q['bank']*8192+q['address']%8192+i]=raw[16+q['bank']*8192+q['address']%8192+i]
 rows=[]
 for case,q in enumerate(cfg['cases'],1):
  for task,t in enumerate(q['tasks'],1):
   rt.globals().TEST_SETUP(case,task);m=rt.globals().mem;w=rt.globals().writes
   rows.append(dict(case=case,task=task,kind=t['kind'],face=t['face'],RAM={int(k):int(v)for k,v in m.items()},writes=[[int(v[i])for i in[1,2,3]]for _,v in w.items()],shots=[dict(type=m[cfg['ram']['SmShotType']+i]or 0,x=m[cfg['ram']['SmShotX']+i]or 0,page=m[cfg['ram']['SmShotPage']+i]or 0,y=m[cfg['ram']['SmShotY']+i]or 0,dir=m[cfg['ram']['SmShotDir']+i]or 0,age=m[cfg['ram']['SmShotAge']+i]or 0,impact=m[cfg['ram']['SmShotImpact']+i]or 0,bombAge=m[cfg['ram']['SmBombAge']+i]or 0)for i in range(3)]))
 return rows,rt

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((OLD/'proof.json').read_text());assert sha(OLD/'proof.json')=='1eb8bb05fae359e4232d6ed40399d462a8988851da97817e7b084368a687eff9';verify_manifest(NEG/'manifest.json')
 old=OLD/'native';assert json.loads((old/'proof.json').read_text())['passed']is False
 entries=json.loads((OLD/'manifest.json').read_text())['bindings'];stable=[];drift=[]
 for z in entries:
  q=Path(z['path'])
  if q.stat().st_size==z['bytes']and sha(q)==z['sha256']:stable.append(q)
  else:drift.append(z)
 assert len(stable)==965 and len(drift)==1 and Path(drift[0]['path'])==OLD/'emulator/Debugger/candidate.cdl'
 cfg=json.loads((old/'config.json').read_text());b=scoped_load(old/'candidate.nes');oldmodule=(ROOT/'tools/audit/final_samus_hard_gallery_native_v2.lua').read_text();newmodule=(ROOT/'tools/audit/final_samus_hard_gallery_native_v3.lua').read_text()
 before=" if t.kind=='pool' then";after=" if t.kind=='pool' or t.kind=='missile-pool' then";assert oldmodule.count(before)==1 and newmodule==oldmodule.replace(before,after)
 oldscript=(old/'run.lua').read_text();assert oldscript.count(oldmodule)==1;script=oldscript.replace(oldmodule,newmodule);assert script.replace(newmodule,oldmodule)==oldscript
 (a.output/'fixture.patch').write_text(''.join(difflib.unified_diff(oldmodule.splitlines(True),newmodule.splitlines(True),fromfile='native_v2.lua',tofile='native_v3.lua')),encoding='utf-8')
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 oldrows,_=setups(LuaRuntime,oldscript,cfg,b['raw']);newrows,rt=setups(LuaRuntime,script,cfg,b['raw']);assert len(oldrows)==len(newrows)==27;models=[]
 for u,v in zip(oldrows,newrows):
  kind=v['kind']
  if kind!='missile-pool':assert u==v
  if kind in['pool','missile-pool']:
   assert all(z['type']==2 and z['x']==90+i*10 and z['y']==72 and z['dir']==v['face']and z['page']==z['age']==z['impact']==z['bombAge']==0 for i,z in enumerate(v['shots']))
  if kind=='missile-pool':assert all(z['type']==0 for z in u['shots'])and len(v['writes'])==len(u['writes'])+15
  models.append(dict(case=v['case'],task=v['task'],kind=kind,face=v['face'],passed=True,all_setup_writes_RAM_exact=kind!='missile-pool',shots=v['shots'],write_count=len(v['writes']),old_write_count=len(u['writes'])))
 # Actual complete UI/primary/Special dispatch proves the resource/pool rule;
 # native occupancy needs to exist before the unchanged real fresh Select.
 cpu=[]
 for face in[1,2]:
  for count in[0,3]:
   q=TraceArena(b);q.set('InvOwnedLo',133,2);q.set('InvSelected',2,2);q.set('InvAmmo',2,34);q.put(PlayerFacingDir=face,Player_PageLoc=0,ScreenLeft_PageLoc=0)
   for i in range(count):
    for name,value in[('SmShotType',2),('SmShotX',90+i*10),('SmShotY',72),('SmShotPage',0),('SmShotDir',face)]:q.set(name,value,i)
   q.put(A_B_Buttons=0,PreviousA_B_Buttons=0,SavedJoypadBits=32,SavedJoypad1Bits=32,InvPrevious=0);q.invoke('RlUiDispatch');assert q.get('InvFresh')==32;q.invoke('ProcFireball_Bubble')
   missile=sum(q.get('RgShotType',i)==41 for i in range(10));assert missile==(count==0)and q.get('InvAmmo',34)==(1 if count==0 else 2)
   cpu.append(dict(face=face,pool=count,passed=True,missiles=missile,ammo=q.get('InvAmmo',34),calls=q.calls))
 phases=phase_models(LuaRuntime,script);assert len(phases['models'])==32
 put(a.output/'source-controls.json',dict(passed=True,actual_Lua_setup_tasks=27,unchanged_tasks=26,changed_task=1,new_extra_complete_seed_writes=15,all_other_script_bytes_reverse_exact=True,config_semantics_exact=True,full_source_CPU_cases=cpu,setup_models=models,phase_models=phases))
 out=a.output/'native';out.mkdir()
 for ext in['nes','dbg','lbl','map']:shutil.copy2(old/('candidate.'+ext),out/('candidate.'+ext))
 shutil.copy2(old/'config.json',out/'config.json');shutil.copy2(old/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua');(out/'run.lua').write_text(script,encoding='utf-8')
 for f in['plans.json','seed-policy.json']:shutil.copy2(OLD/f,a.output/f)
 # Copy only the original immutable top-level runtime, not generated coverage.
 runtime=a.output/'emulator';runtime.mkdir()
 for q in(OLD/'emulator').iterdir():
  if q.is_file():shutil.copy2(q,runtime/q.name)
 env=copy.deepcopy(ready['environment']);env['emulator']=str(runtime/'Mesen.exe');env['user_settings_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(runtime/'Mesen.exe')==env['emulator_sha256']and sha(runtime/'settings.json')==env['worker_settings_sha256'];put(a.output/'environment.json',env)
 put(a.output/'dependency-correction.json',dict(previous_dependencies_unchanged_remains_FALSE=True,previous_manifest_unchanged=True,stable_inputs_verified=965,previous_mutable_CDL_expected=drift[0],future_runtime_top_level_only=True,excluded_previous_mutable_path=drift[0]['path'],no_emulated_or_ROM_change=True))
 report=ROOT/'docs/qa/final-samus-hard-gallery-pool-correction-2026-10-26.txt';report.write_text('Samus Hard missing-pool fixture correction\n26 October 2026. Source/static readiness only; no retry/grant.\n\nExact3b target '+SHA+' unchanged. Prior outline nativefac86ece1c6079da5a452c4a2da0c7e4298808d8ae6f4bed42835f3fe7f99c09 remains FALSE.14subphases completed; the last missile-pool setup accidentally did not populate the source shared cap. Native wall1468 has3empty native slots/stock2, wall1474 correctly spends2→1/spawns missile41. This is a setup omission, not a game defect.\n\nONE condition adds missile-pool to the existing complete3Long occupancy setup. All SamusRam was already cleared before these15seed writes; position/page/age/impact/bomb fields and facing are complete and source-valid.27 actual Lua setup tasks compare:26 write streams/final RAM identical; only missile-pool gains15 writes and three live Long records. Actual full RlUiDispatch→ProcFireball_Bubble controls for both facings, pool0/3 confirm correct missile cost/spawn vs refusal. All32phase models pass; zero-spawn/no-debit assertion remains literal. No other controller, pool, resources, metadata, observer, strict NMI/DMA/E008/IRQ/CHR/SP/SMC or output changes.\n\nPrevious readiness mistakenly copied/bound a generated Debugger/candidate.cdl. Its one runtime rewrite caused dependencies_unchangedFALSE; all965otherbindings stayed exact. Original manifest/result retained. This successor copies only original immutable top-level runtime files, without generated coverage dependencies; settings unchanged.\n\nActual missile HUD container matches source SWF frame7/ROM page229 patterns with deliberate fixedpalette3 brown quantization in sampled286opaque pixels; color/readability loss and three absent-OAM sample epochs remain explicit. No glyph/CHR/game-art fix. This remains controlled B use, not acquisition or all-item/wholepixel/60Hz/audio fidelity.\n',encoding='utf-8')
 files=set(stable);files.update({Path(__file__),ROOT/'tools/audit/final_samus_hard_gallery_native_v3.lua',report,OLD/'proof.json',OLD/'manifest.json',old/'proof.json',NEG/'proof.json',NEG/'manifest.json'});files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));count=verify_manifest(a.output/'manifest.json')
 command='python -B tools/audit/final_samus_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant';put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='samus-hard',mode_value=1,maximum_cases=8,maximum_launches=1,maximum_owned_workers=1,retry=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=count,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,source_controls_sha256=sha(a.output/'source-controls.json'),stable_command=command,source_freeze_sha256=sha(PARENT/'ROOT-source-readiness.json'),original_pool_FALSE_sha256=sha(old/'proof.json'),report_sha256=sha(report)));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),script_sha256=sha(out/'run.lua'),bindings=count,stable_command=command),indent=2))
if __name__=='__main__':main()
