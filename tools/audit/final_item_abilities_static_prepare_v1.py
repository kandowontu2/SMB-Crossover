"""Prepare unchanged acquired-ability mechanics with startup-only return callbacks.

SOURCE/MOCK/CPU only. This tool has no native-run switch.
"""
from pathlib import Path
import argparse,difflib,hashlib,json,subprocess,sys
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from verify_native_relocation import NesMPU
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
CURRENT='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def old_core(module):
 start=module.index('local pendingReturns,installedReturns={},{}')
 end=module.index('local function stageEnemy(raised)',start)
 return module[start:end]

def core_tests(LuaRuntime,old,new):
 results=[]
 # Compare the intended original callback order under a host-only snapshot
 # model. This does not emulate the unsafe C++ vector reallocation itself.
 pre='''
 callbacks={};mem={};banks={};state={['cpu.sp']=253};out={};runtime=false
 emu={memType={nesDebug=1},callbackType={exec=2}}
 emu.getState=function()return state end
 emu.read=function(a)return mem[a]or 0 end
 emu.addMemoryCallback=function(fn,kind,lo,hi)
  if runtime and STATIC then error('Runtime callback mutation')end
  callbacks[#callbacks+1]={fn=fn,kind=kind,lo=lo,hi=hi or lo}
 end
 local function bank(pc)return banks[pc]or 1 end
 function stack(sp,ret,b)
  state['cpu.sp']=sp;local word=(ret-1)%65536
  mem[256+(sp+1)%256]=word%256;mem[256+(sp+2)%256]=word//256;banks[ret]=b or 1
 end
 function dispatch(pc,sp,b)
  state['cpu.sp']=sp;banks[pc]=b or 1
  local n=#callbacks
  for i=1,n do local q=callbacks[i];if pc>=q.lo and pc<=q.hi then q.fn(pc)end end
 end
 function emit(s)out[#out+1]=s end
 '''
 scenarios=[
  ('wrong_pc_sp_bank',"stack(251,0x8123,3);onReturn('a',function()emit('ok')end);dispatch(0x8124,253,3);dispatch(0x8123,252,3);dispatch(0x8123,253,2);assert(#out==0);dispatch(0x8123,253,3);dispatch(0x8123,253,3)",['ok']),
  ('same_pc_first_registration_order',"stack(251,0x8123);onReturn('a',function()emit('a')end);onReturn('b',function()emit('b')end);onReturn('a',function()emit('a-replaced')end);dispatch(0x8123,253)",['a-replaced','b']),
  ('same_key_nested_preserves_old_overwrite',"stack(251,0x8123);onReturn('a',function()emit('outer')end);stack(247,0x8123);onReturn('a',function()emit('inner')end);dispatch(0x8123,253);assert(#out==0);dispatch(0x8123,249);dispatch(0x8123,253)",['inner']),
  ('different_key_nested_depth',"stack(251,0x8123);onReturn('outer',function()emit('outer')end);stack(247,0x8123);onReturn('inner',function()emit('inner')end);dispatch(0x8123,249);dispatch(0x8123,253)",['inner','outer']),
  ('reentrant_existing_slot',"stack(251,0x8123);onReturn('a',function()emit('first');stack(251,0x8123);onReturn('a',function()emit('second')end)end);dispatch(0x8123,253);assert(#out==1);dispatch(0x8123,253)",['first','second']),
  ('new_slot_waits_for_next_exec',"stack(251,0x8123);onReturn('a',function()emit('first');stack(251,0x8123);onReturn('b',function()emit('new')end)end);dispatch(0x8123,253);assert(#out==1);dispatch(0x8123,253)",['first','new']),
  ('stack_and_pc_wrap',"stack(255,0);onReturn('wrap',function()emit('wrap')end);dispatch(0,0);assert(#out==0);dispatch(0,1)",['wrap']),
  ('multiple_return_addresses',"stack(251,0x8123);onReturn('a',function()emit('left')end);stack(249,0xc123,116);onReturn('a',function()emit('right')end);dispatch(0xc123,251,116);dispatch(0x8123,253)",['right','left'])]
 for name,body,expected in scenarios:
  outputs=[]
  for static,core in [(False,old),(True,new)]:
   rt=LuaRuntime(unpack_returned_tuples=True)
   rt.execute('STATIC='+('true'if static else'false')+'\n'+pre+core+'\nTEST_ON_RETURN=onReturn')
   if static:rt.execute('FINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS();runtime=true')
   rt.execute(body.replace('onReturn(','TEST_ON_RETURN('))
   out=[rt.globals().out[i]for i in range(1,len(rt.globals().out)+1)];assert out==expected,(name,static,out,expected)
   outputs.append(out)
   if static:assert rt.eval('#callbacks')==1
  assert outputs[0]==outputs[1];results.append(dict(name=name,passed=True,expected=expected))
 return results

def actual_calls(bundle):
 """Execute genuine linked JSR instructions and the real callee through RTS.

 This is a finite actual-CPU call/return ownership test, not gameplay reachability.
 Pit's genuine resident farcall JSR is executed with its actual target operand.
 """
 cases=[]
 def run_site(q,site,child,setup=None):
  m=q.m;pc=site;window=(pc-0x8000)//8192
  pos=None
  # Caller is already mapped by the owner below. The instruction must be JSR.
  assert m[pc]==0x20
  if setup:setup()
  c=NesMPU(memory=m,pc=pc);c.sp=0xf1;c.p=0x30;c.a=0;c.x=0;c.y=0
  c.step();assert c.pc==address(bundle,child),(child,hex(c.pc))
  sp=c.sp;ret=(m[256+(sp+1)%256]+256*m[256+(sp+2)%256]+1)%65536
  assert ret==site+3 and sp==0xef
  bank=m.banks[(ret-0x8000)//8192]
  entry=dict(pc=c.pc,physical_bank=m.banks[(c.pc-0x8000)//8192],sp=sp,return_pc=ret,return_bank=bank)
  for step in range(100000):
   if c.pc==ret:
    assert c.sp==0xf1 and m.banks[(ret-0x8000)//8192]==bank
    cases.append(dict(child=child,actual_JSR_pc=site,JSR_bytes=[m[site+i]for i in range(3)],entry=entry,return_sp=c.sp,steps=step,passed=True));return
   c.step()
  raise AssertionError(('return timeout',child,c.pc))
 # Same-bank real source calls have unambiguous exact compiled JSR bytes.
 for owner,child,char,values in [
   ('ScroogeMovement','ScroogeMovement::Bounce',12,dict(ScPogo=1,Player_State=0,SavedJoypadBits=0x44)),
   ('MegaManWeapons','MegaManWeapons::DamageEnemy',6,dict(MmBulletType=38))]:
  q=Arena(bundle,char);q.put(**values);s=bundle['syms'][owner];g=bundle['segs'][s['seg']];bank=(int(g['ooffs'],0)-16)//8192;at=address(bundle,owner);window=(at-0x8000)//8192;q.m.page(window,bank)
  if window in (1,2):q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
  target=address(bundle,child);pat=bytes([0x20,target&255,target>>8]);code=bundle['raw'][location(bundle,owner):location(bundle,owner)+int(s['size'],0)]
  hits=[i for i in range(len(code)-2)if code[i:i+3]==pat];assert len(hits)==1,(owner,hits)
  run_site(q,at+hits[0],child)
 # Pit entry is reached through the real assembled ExpandedMovement owner,
 # including its farcall setup. Capture actual entry, then its genuine return.
 q=Arena(bundle,6);q.put(PlayerStatus=2,Player_State=1,XgPitFuel=60,XgPitFlight=1,A_B_Buttons=128,SavedJoypadBits=0,MmUnderwater=0)
 owner='ExpandedMovement';s=bundle['syms'][owner];g=bundle['segs'][s['seg']];pc=address(bundle,owner);q.m.page((pc-0x8000)//8192,(int(g['ooffs'],0)-16)//8192)
 q.set('CurrentBank',q.m.banks[1]|128)
 c=NesMPU(memory=q.m,pc=pc);c.sp=0xfd;c.p=0x30;c.stPushWord(0x5aff);found=None
 for step in range(100000):
  if c.pc==address(bundle,'PitFlightUpdate') and q.m.banks[(c.pc-0x8000)//8192]==(location(bundle,'PitFlightUpdate')-16)//8192:
   sp=c.sp;ret=(q.m[256+(sp+1)%256]+256*q.m[256+(sp+2)%256]+1)%65536
   assert q.m[ret-3]==0x20 and q.m[ret-2]+256*q.m[ret-1]==c.pc
   found=dict(child='PitFlightUpdate',actual_JSR_pc=ret-3,JSR_bytes=[q.m[ret-3+i]for i in range(3)],entry=dict(pc=c.pc,sp=sp,physical_bank=q.m.banks[(c.pc-0x8000)//8192],return_pc=ret,return_address_kind='internal_RAM'if ret<0x2000 else'other',return_bank=None if ret<0x8000 else q.m.banks[(ret-0x8000)//8192]),expected_return_sp=(sp+2)%256)
  elif found and c.pc==found['entry']['return_pc']:
   assert c.sp==found['expected_return_sp'];found.update(return_sp=c.sp,steps=step,passed=True);cases.append(found);break
  assert c.pc!=0x5b00 or found,'Real ExpandedMovement did not reach PitFlightUpdate'
  c.step()
 else:raise AssertionError('Pit owner CPU timeout')
 return cases

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 rom=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq/candidate.nes';assert sha(rom)==CURRENT
 sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 module=ROOT/'tools/audit/final_item_abilities_native.lua';newfile=ROOT/'tools/audit/final_item_abilities_static_return_v1.lua'
 oldtext=module.read_text();old=old_core(oldtext);new=newfile.read_text()+'\n';repaired=oldtext.replace(old,new);assert repaired.replace(new,old)==oldtext
 (a.output/'ability-module-original.lua').write_bytes(module.read_bytes());(a.output/'ability-module-static.lua').write_text(repaired,encoding='utf-8')
 (a.output/'observer-only.patch').write_text(''.join(difflib.unified_diff(oldtext.splitlines(True),repaired.splitlines(True),fromfile='immutable-original-module',tofile='versioned-static-module')),encoding='utf-8')
 tests=core_tests(LuaRuntime,old,new);bundle=scoped_load(rom);calls=actual_calls(bundle)
 profiles=[];bindings={}
 def bind(p):
  p=Path(p);bindings[str(p.resolve())]=dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size)
 for family in ['pit','rygar','scrooge']:
  for mode in ['easy','hard']:
   out=a.output/(family+'-'+mode)
   result=subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/final_item_abilities_run.py'),'--rom',str(rom),'--expected-sha256',CURRENT,'--output',str(out),'--family',family,'--mode',mode],capture_output=True,text=True)
   assert result.returncode==0,(result.stdout,result.stderr)
   script=out/'run.lua';dynamic=script.read_text(encoding='utf-8');assert dynamic.count(old)==1
   (out/'dynamic-control-run.lua').write_bytes(script.read_bytes())
   suffix='\n-- Installed last, after every original static hook and event.\nFINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS()\n'
   static=dynamic.replace(old,new)+suffix;assert static[:-len(suffix)].replace(new,old)==dynamic
   script.write_text(static,encoding='utf-8')
   # Full generated startup, all original guards/controllers retained. All real
   # emulator mutations are forbidden in this synthetic inactive-state mock.
   from parodius_visibility_hud_static_startup_v1 import MOCK
   rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Unexpected fixture write during startup")end')
   rt.execute(static);count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].kind==2 and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
   rt.execute('emu.addMemoryCallback=function()error("Runtime callback registration forbidden")end;emu.removeMemoryCallback=function()error("Runtime callback removal forbidden")end;callbacks[#callbacks].fn(0xe008)')
   assert rt.eval('#callbacks')==count
   q=json.loads((out/'preparation.json').read_text());q.update(status='source_prepared_static_observer_not_native',passed=False,native_run=False,dynamic_control_script_sha256=sha(out/'dynamic-control-run.lua'),script_sha256=sha(script),static_core_sha256=sha(newfile),original_module_sha256=sha(module),reverse_normalization_exact=True,static_memory_callbacks=count,return_dispatcher_installed_last=True,full_generated_Lua_startup_mock_passed=True)
   (out/'static-preparation.json').write_text(json.dumps(q,indent=2)+'\n')
   profiles.append(dict(family=family,mode=mode,actual_numeric_requested=int(mode=='hard'),preparation=str(out/'static-preparation.json'),script_sha256=sha(script),static_memory_callbacks=count,planned_ability_cases=len(q['abilities'])))
   for f in out.iterdir():
    if f.is_file():bind(f)
 proof=dict(passed=True,source_mock_CPU_only=True,native_launches=0,ROM_sha256=CURRENT,Lua_runtime=rt.eval('_VERSION'),original_module_sha256=sha(module),static_core_sha256=sha(newfile),old_module_unchanged=True,mechanics_reverse_normalization_exact=True,profiles=profiles,return_core_model_cases=tests,genuine_compiled_call_returns=calls,
  limits=['No native same-input equivalence or current ability qualification is claimed. Six profiles are source/mock prepared only and require full observer reconciliation and separately reviewed native grant.','Full generated scripts preserve original mechanics/assertions and numeric mode request/readback; inherited old DMA observation protocol is not a newly qualified current complete-hardware lease observer.','Legacy same-name/same-return nested pending overwrite is intentionally preserved, not silently changed into a stack. Host-only snapshot model describes intended callbacks, not unsafe vector mutation behavior.','CPU tests execute genuine assembled calls/callees; Scrooge/MM start at the actual JSR, Pit reaches it from real ExpandedMovement. These are not full GameLoop reachability proofs. Pit returns to internal-RAM farcall code, not a ROM bank; the unchanged Lua convertAddress bank predicate is mock-tested, not newly measured in native Mesen.'])
 for f in [Path(__file__),module,newfile,ROOT/'tools/audit/final_item_abilities_run.py',ROOT/'tools/audit/final_item_matrix_progressive.lua',ROOT/'tools/audit/parodius_visibility_hud_static_startup_v1.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/verify_native_relocation.py',Path(sys.modules['lupa'].__file__),Path(sys.modules[LuaRuntime.__module__].__file__),rom,rom.with_suffix('.dbg')]:bind(f)
 (a.output/'controls.json').write_text(json.dumps(proof,indent=2)+'\n');bind(a.output/'controls.json');bind(a.output/'observer-only.patch');bind(a.output/'ability-module-original.lua');bind(a.output/'ability-module-static.lua')
 (a.output/'manifest.json').write_text(json.dumps(dict(bindings=list(bindings.values())),indent=2)+'\n')
 final=dict(passed=True,native_launches=0,ROM_sha256=CURRENT,controls_sha256=sha(a.output/'controls.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),profiles=6,ability_plans=62,old_module_sha256=sha(module))
 (a.output/'proof.json').write_text(json.dumps(final,indent=2)+'\n');print(json.dumps(final))

if __name__=='__main__':main()
