"""Bind full 16-bit caller snapshot to genuine existing leaf return; no native."""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,shutil,sys
from final_samus_hard_gallery_source_v1 import D,ROOT,PARENT,SHA
from final_samus_hard_gallery_prepare_v2 import phase_models
from final_samus_hard_gallery_pool_prepare_v1 import setups
from final_samus_hard_gallery_freeze_clock_controls_v1 import controls
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_run import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from parodius_visibility_hud_static_startup_v1 import MOCK
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
OLD=D/'current3b112-samus-hard-pool-ready-v1'
def models(LuaRuntime,script,cfg):
 pre=MOCK+'''
L={};OUTPUT='mock/';mem={};BANKA=6;emu.memType.nesPrgRom=6
emu.read=function(a,t)return mem[a]or 0 end
emu.write=function()error('Clock observer never mutates emulated state')end
emu.convertAddress=function(a)local b=a>=0xe000 and 127 or a>=0xc000 and 13 or a>=0xa000 and BANKA or a>=0x8000 and 4 or 0;return{address=b*8192+a%8192}end
emu.getScreenBuffer=function()error('Clock observation has no synthetic screen outcome')end
'''
 export='''
function TEST_INIT(v)
 entered=true;phase='run';updates=1200;wall=1590;drawContext=nil;freezeClockBefore=nil
 current={q=C.cases[5],t=C.cases[5].tasks[1],stage={freezeSteps=0,thaws=0}}
 mem[L.AvFrozen]=v%256;mem[L.AvFrozenHi]=v//256;mem[L.RgEnemyStun]=0;mem[L.LsrFrozenPose]=0
 state['cpu.x']=0;state['cpu.sp']=231;BANKA=6
 mem[488]=0x7f;mem[489]=0xab
end
function TEST_HOOK(n)local h=C.hooks[n];state['cpu.pc']=h.address;for _,q in ipairs(callbacks)do if q.kind==2 and q.lo==h.address and q.hi==h.address then q.fn()end end end
function TEST_VALUE(v)mem[L.AvFrozen]=v%256;mem[L.AvFrozenHi]=v//256 end
function TEST_RETURN()state['cpu.pc']=0xab80;callbacks[#callbacks].fn(0xab80)end
function TEST_STEPS()return current.stage.freezeSteps end
function TEST_EPOCH()updates=updates+1 end
function TEST_STAGE()current.stage={freezeSteps=0,thaws=0}end
'''
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(pre+script+export);mem=rt.globals().mem
 for h in cfg['hooks'].values():
  for i,v in enumerate(h['bytes']):mem[h['address']+i]=v
 count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535');rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 def invoke(v,partial,after,*,caller=True,epoch=False,stage=False,slot=0):
  rt.globals().TEST_INIT(v);rt.execute(f"state['cpu.x']={slot}")
  if caller:rt.globals().TEST_HOOK('RemainingWeapons::Freeze')
  rt.execute("state['cpu.x']=0")
  if epoch:rt.globals().TEST_EPOCH()
  if stage:rt.globals().TEST_STAGE()
  rt.globals().TEST_VALUE(partial);rt.globals().TEST_HOOK('SamusFrozenDecrement');rt.globals().TEST_VALUE(after);rt.execute("state['cpu.sp']=233");rt.globals().TEST_RETURN();assert rt.globals().TEST_STEPS()==1
 rows=[]
 for v,partial,after in[(360,360,359),(257,257,256),(256,0,255),(255,255,254),(1,1,0)]:invoke(v,partial,after);rows.append(dict(before=v,leaf_partial=partial,after=after,passed=True,expected='accept'))
 for name,args in[
  ('missing-caller',dict(v=256,partial=0,after=255,caller=False)),('wrong-update',dict(v=256,partial=0,after=255,epoch=True)),('wrong-stage',dict(v=256,partial=0,after=255,stage=True)),('wrong-caller-slot',dict(v=256,partial=0,after=255,slot=1)),('missing-high-borrow',dict(v=256,partial=256,after=255)),('wrong-final-decrement',dict(v=256,partial=0,after=254)),('wrong-unneeded-borrow',dict(v=257,partial=1,after=256)),('zero-leaf-admission',dict(v=0,partial=0,after=255))]:
  try:invoke(**args);got=True
  except Exception:got=False
  assert not got,name;rows.append(dict(kind=name,passed=True,expected='reject'))
 for name in['return-SP','return-bank']:
  rt.globals().TEST_INIT(256);rt.globals().TEST_HOOK('RemainingWeapons::Freeze');rt.globals().TEST_VALUE(0);rt.globals().TEST_HOOK('SamusFrozenDecrement');rt.globals().TEST_VALUE(255)
  rt.execute("state['cpu.sp']=232"if name=='return-SP'else"state['cpu.sp']=233;BANKA=7");rt.globals().TEST_RETURN();assert rt.globals().TEST_STEPS()==0
  rt.execute("state['cpu.sp']=233;BANKA=6");rt.globals().TEST_RETURN();assert rt.globals().TEST_STEPS()==1;rows.append(dict(kind=name,passed=True,expected='defer then accept genuine'))
 assert rt.eval('#callbacks')==count
 return dict(passed=True,models=rows,callbacks=count,positive_models=5,negative_models=10,no_runtime_registration=True,no_emulated_writes=True)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert verify_manifest(OLD/'manifest.json')==992
 old=OLD/'native';oldproof=json.loads((old/'proof.json').read_text());assert oldproof['passed']is False and oldproof['dependencies_unchanged'];b=scoped_load(old/'candidate.nes');cfg=json.loads((old/'config.json').read_text());oldcfg=copy.deepcopy(cfg)
 name='RemainingWeapons::Freeze';at=location(b,name);cfg['hooks'][name]=dict(address=address(b,name),physical_bank=(at-16)//8192,bytes=list(b['raw'][at:at+3]));assert cfg['hooks'][name]['address']==0xab6a and cfg['hooks'][name]['physical_bank']==6
 oldmodule=(ROOT/'tools/audit/final_samus_hard_gallery_native_v3.lua').read_text();newmodule=(ROOT/'tools/audit/final_samus_hard_gallery_native_v4.lua').read_text();oldscript=(old/'run.lua').read_text();assert oldscript.count(oldmodule)==1
 first,tail=oldscript.split('\n',1);assert first=='FINAL_ITEM_PROGRESSIVE='+lua(oldcfg);script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+tail.replace(oldmodule,newmodule);assert script.replace(newmodule,oldmodule).split('\n',1)[1]==tail
 compare=copy.deepcopy(cfg);del compare['hooks'][name];assert compare==oldcfg
 (a.output/'observer.patch').write_text(''.join(difflib.unified_diff(oldmodule.splitlines(True),newmodule.splitlines(True),fromfile='native_v3.lua',tofile='native_v4.lua')),encoding='utf-8')
 cpu=controls(b);put(a.output/'compiled-clock-controls.json',cpu);sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 mock=models(LuaRuntime,script,cfg);put(a.output/'clock-observer-models.json',mock)
 u,_=setups(LuaRuntime,oldscript,oldcfg,b['raw']);v,_=setups(LuaRuntime,script,cfg,b['raw']);assert u==v and len(v)==27
 phases=phase_models(LuaRuntime,script);assert len(phases['models'])==32;put(a.output/'source-controls.json',dict(passed=True,unchanged_actual_setup_tasks=27,all_setup_RAM_and_write_streams_exact=True,unchanged_phase_models=32,phase_models=phases,only_config_delta='One genuine pre-borrow caller hook; all source body/effect/physical metadata and plans unchanged.',original_assertions='Full before>0 and after==before-1 retained, now bound before caller highDEC. Exact360committed steps/one natural thaw/STOP release retained.',CPU_complete_boundary_cells=11,source_created_360_episode=True,observer_models=15,callbacks=mock['callbacks']))
 out=a.output/'native';out.mkdir()
 for ext in['nes','dbg','lbl','map']:shutil.copy2(old/('candidate.'+ext),out/('candidate.'+ext))
 put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');shutil.copy2(old/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua')
 for n in['plans.json','seed-policy.json']:shutil.copy2(OLD/n,a.output/n)
 runtime=a.output/'emulator';runtime.mkdir()
 for q in(OLD/'emulator').iterdir():
  if q.is_file():shutil.copy2(q,runtime/q.name)
 env=copy.deepcopy(json.loads((OLD/'proof.json').read_text())['environment']);env['emulator']=str(runtime/'Mesen.exe');env['user_settings_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(runtime/'Mesen.exe')==env['emulator_sha256']and sha(runtime/'settings.json')==env['worker_settings_sha256'];put(a.output/'environment.json',env)
 report=ROOT/'docs/qa/final-samus-hard-gallery-freeze-clock-2026-10-26.txt';report.write_text('Samus Hard full-clock observer correction\n26 October 2026. Source/static only, no nativegrant/launch. ExactROM '+SHA+' unchanged.\n\nOriginal pool-ready native54cc2f83d1472d99ea1fb9cb727396aa50d8dad0535d1ed0941d6c35bec9c010 staysFALSE; dependenciesunchangedTRUE. It completed all15subphases in first4cases, then froze a real Goomba at1491/update1117 for360. At next update1222 after last completePPU1596 it failed the leaf-only decrement assertion at actualreturnAB80, A255. Original low/high operands were not dumped and are not backfilled.\n\nComplete caller RemainingWeapons::FreezeAB6A captures16bitbefore; caller performs highDEC whenlow0 before invoking SamusFrozenDecrementBFD2. SourceCPU proves before256→leafpartial0→return255 at actualAB80, which invalidates old leaf-only before-1 oracle. One source-emitted/contact-created360 episode through360fullProc gateways plus11boundary cells prove exactdecrements/STOP-release.\n\nONE added genuine pre-borrow hook/read-only Lua snapshot records full before; existing genuine leafreturn still asserts full before>0/after=before-1, plus new check that intermediate state is exact source borrow. Boundary/thaw event records before/partial/after; no timer/resource/input writes.5positive+10negative/defer Lua models cover256boundary, missing/wrongowner/update/stage/slot/partial/finalvalue/returnSP/bank. All27setup RAM/write streams and32phase models identical; allothercontroller/ability/cost/contact/cleanup/360duration/strictNMI/IRQ/DMA/E008/CHR/stack/bank/SMC checks unchanged. Runtime top-level-only. B seeded use never acquisition; nativewholeunit/unrunIcecompletion/Wave/Varia/Screw remainopen.\n',encoding='utf-8')
 files={Path(z['path'])for z in json.loads((OLD/'manifest.json').read_text())['bindings']};files.update({Path(__file__),ROOT/'tools/audit/final_samus_hard_gallery_freeze_clock_controls_v1.py',ROOT/'tools/audit/final_samus_hard_gallery_native_v4.lua',report,OLD/'proof.json',OLD/'manifest.json',old/'proof.json',old/'first-failure.json'});files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));count=verify_manifest(a.output/'manifest.json');command='python -B tools/audit/final_samus_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant';put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='samus-hard',mode_value=1,maximum_cases=8,maximum_launches=1,maximum_owned_workers=1,retry=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=count,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,source_controls_sha256=sha(a.output/'source-controls.json'),stable_command=command,source_freeze_sha256=sha(PARENT/'ROOT-source-readiness.json'),original_FALSE_sha256=sha(old/'proof.json'),observer_only=True,report_sha256=sha(report)));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),script_sha256=sha(out/'run.lua'),bindings=count,stable_command=command),indent=2))
if __name__=='__main__':main()
