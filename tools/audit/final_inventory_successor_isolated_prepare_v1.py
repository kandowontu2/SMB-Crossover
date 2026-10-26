"""Fixture-only successor: isolated drop/refusal setup and exact native debit/credit ledger. NO RUN."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,sys
from final_item_abilities_static_prepare_v2 import D,ROOT
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_run import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from parodius_visibility_hud_static_startup_v1 import MOCK
SHA='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
DROPS=['InvDropKind','InvDropX','InvDropPage','InvDropY','InvDropVY','InvDropVYMid','InvDropVYHi','InvDropFraction','InvDropFractionHi','InvDropAge','InvDropAgeHi','AvDropItem']
EXTRA=['InvRefillTick','InvDropAmount','AvRefillItem','InvDropEnemy','InvDropSlot','TimerControl']+DROPS
HELPERS='''-- Fixture-only accounting: zero is witnessed at a real source debit, while
-- later native earned capsule credits remain allowed and explicitly counted.
local function fundedDebit(item,cost,before,after,paid)
 if current.component~='funded' or current.q.item==0 then return end
 assert(item==current.q.item,'Funded native spend belongs to selected seeded weapon')
 if paid then
  current.nativeSpent=current.nativeSpent+cost
  if after==0 then
   current.zeroWitness={item=item,before=before,cost=cost,after=after,wall=wall,update=updates}
   event('actual-funded-debit-zero',current.zeroWitness);capture(current.q.name..'-actual-debit-zero')
  end
 end
end
local function fundedCredit(before,refill,tick,remain)
 if current.component~='funded' or current.q.item==0 then return end
 local after=stock()
 if after==before then return end
 assert(refill==144+current.q.item and tick==1 and remain>=4,'Credit begins at genuine selected native refill tick')
 assert(after==math.min(112,before+4),'Native refill credit is exact four-unit capped increment')
 assert(r('InvRefillRemain')==(remain-4)%256 and r('InvRefillTick')==3,'Native refill remaining/tick continuation')
 local finished=after==112 or remain==4
 assert(r('InvRefill')==(finished and 0 or refill),'Native refill completion/index continuation')
 current.nativeCredits=current.nativeCredits+after-before
 event('actual-funded-refill-credit',{before=before,after=after,amount=after-before,index=refill,remaining_before=remain,remaining_after=r('InvRefillRemain'),total_credits=current.nativeCredits,source='full actual InventoryUiTick return'})
 capture(current.q.name..'-earned-credit-'..current.nativeCredits)
end
local function fundedBalance()
 assert(current.zeroWitness and current.nativeSpent>=current.q.initial_stock,'Actual source debit exhausts at least seeded stock to zero')
 assert(stock()==current.beforeStock-current.nativeSpent+current.nativeCredits,'Exact funded balance includes every native debit and earned refill credit')
end
hook('InventoryUiTick',function()
 if not entered or not current or current.component~='funded' or current.q.item==0 then return end
 local owner=current;local before=stock();local refill,tick,remain=r('InvRefill'),r('InvRefillTick'),r('InvRefillRemain')
 onReturn('bass-funded-refill',function()
  assert(current==owner,'Refill return retains actual current case owner')
  fundedCredit(before,refill,tick,remain)
 end)
end)
'''

def transform(old):
 changes=[]
 def rep(before,after):
  nonlocal old
  assert old.count(before)==1,before[:100];old=old.replace(before,after);changes.append(dict(before=before,after=after))
 rep('local function clearArena()\n',HELPERS+'local function clearArena()\n')
 anchor=" w('Player_MovingDir',current.q.face);w('PlayerFacingDir',current.q.face);w('Player_CollisionBits',255)"
 reset=" -- Complete B fixture setup only; no drops are removed during native funded play.\n for _,n in ipairs(C.isolated_drop_arrays)do for i=0,3 do w(n,0,i)end end\n for _,n in ipairs({'InvRefillTick','InvDropAmount','AvRefillItem','InvDropEnemy','InvDropSlot','TimerControl'})do w(n,0)end\n"
 rep(anchor,reset+anchor)
 rep("local function setup(kind)\n writeBoundary=true;clearArena()","local function setup(kind)\n local prior={kind=kind,ammo=current.q.item>0 and stock()or 0,refill=r('InvRefill'),remaining=r('InvRefillRemain'),drops={}}\n for i=0,3 do prior.drops[#prior.drops+1]={kind=r('InvDropKind',i),x=r('InvDropX',i),page=r('InvDropPage',i),y=r('InvDropY',i)}end\n event('isolated-native-boundary-component-reset',prior)\n writeBoundary=true;clearArena()")
 rep(" elseif kind=='pool'then"," elseif kind=='empty'then\n  if current.q.item>0 then w('InvAmmo',0,144+current.q.item)end\n elseif kind=='pool'then")
 rep(" current.beforeStock=current.q.item>0 and stock()or 0"," current.beforeStock=current.q.item>0 and stock()or 0\n current.nativeSpent=0;current.nativeCredits=0;current.zeroWitness=nil")
 rep("  event('actual-source-spend',current.spends[#current.spends]);capture(current.q.name..'-cost-'..#current.spends)","  event('actual-source-spend',current.spends[#current.spends]);fundedDebit(item,cost,before,after,paid);capture(current.q.name..'-cost-'..#current.spends)")
 rep("   if q.item>0 then assert(stock()==0,'Funded source actions exhaust exact seeded stock')end","   if q.item>0 then fundedBalance()end")
 return old,changes

def mechanics_models(LuaRuntime,module,cfg):
 pre='''
mem={};testHooks={};testEvents={};entered=true;wall=99;updates=80;writeBoundary=false
local C=CFG
local function r(n,i)return mem[n..':'..(i or 0)]or 0 end
local function w(n,v,i)assert(writeBoundary,'Boundary only');mem[n..':'..(i or 0)]=v end
local function hook(n,fn)testHooks[n]=fn end
local function event(n,z)testEvents[#testEvents+1]={kind=n,data=z}end
local function capture()end
local function arena()end
local function tile()end
local function onReturn(n,fn)fn()end
'''
 tests='''
local function case(stockValue)
 current={component='funded',q={name='kick-face1',item=5,initial_stock=4,face=1},nativeSpent=0,nativeCredits=0,beforeStock=4}
 mem['InvAmmo:149']=stockValue
end
local function reject(fn)local ok=pcall(fn);assert(not ok,'Invalid accounting accepted')end
case(0);fundedDebit(5,4,4,0,true);fundedBalance()
case(0);fundedDebit(5,4,4,0,true)
for i=1,10 do local before=(i-1)*4;mem['InvAmmo:149']=i*4;mem['InvRefillRemain:0']=40-i*4;mem['InvRefillTick:0']=3;mem['InvRefill:0']=i==10 and 0 or 149;fundedCredit(before,149,1,44-i*4)end
assert(current.nativeCredits==40 and current.nativeSpent==4);fundedBalance()
case(0);reject(fundedBalance)
case(0);fundedDebit(5,4,4,0,true);mem['InvAmmo:149']=40;reject(fundedBalance)
case(4);reject(function()fundedCredit(0,148,1,40)end)
case(4);reject(function()fundedCredit(0,149,2,40)end)
case(8);reject(function()fundedCredit(0,149,1,40)end)
case(4);mem['InvRefillRemain:0']=36;mem['InvRefillTick:0']=3;mem['InvRefill:0']=149;fundedCredit(0,149,1,40);reject(fundedBalance)
case(0);reject(function()fundedDebit(4,4,4,0,true)end)
case(40);mem['InvRefill:0']=149;mem['InvRefillRemain:0']=36;mem['InvRefillTick:0']=2;mem['TimerControl:0']=2
for _,n in ipairs(C.isolated_drop_arrays)do for i=0,3 do mem[n..':'..i]=255 end end
setup('empty')
assert(r('InvAmmo',149)==0 and r('InvRefill')==0 and r('InvRefillRemain')==0 and r('InvRefillTick')==0 and r('TimerControl')==0)
for _,n in ipairs(C.isolated_drop_arrays)do for i=0,3 do assert(r(n,i)==0,'All four complete pickup slots reset')end end
assert(not writeBoundary and phase=='empty'and current.beforeStock==0)
setup('funded');assert(r('InvAmmo',149)==4 and phase=='funded')
setup('pool');assert(r('InvAmmo',149)==112 and phase=='pool')
return {positive_zero_debit=true,positive_native40credit_balance=true,rejected_missing_zero=true,rejected_unaccounted_credit=true,rejected_wrong_refill_index=true,rejected_wrong_tick=true,rejected_wrong_delta=true,rejected_credit_without_exhaustion=true,rejected_wrong_item=true,all48dropbytes_reset_at_boundary=true,empty_explicit_zero_no_refill=true,funded_seed4_pool112_preserved=true}
'''
 rt=LuaRuntime(unpack_returned_tuples=True);z=rt.execute('CFG='+lua(cfg)+'\n'+pre+module+'\n'+tests);return{k:v for k,v in z.items()}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old=D/'current3b112-bass-gallery-ready-v1';ready=json.loads((old/'proof.json').read_text());verify_manifest(old/'manifest.json');assert ready['ROM_sha256']==SHA
 final=D/'current3b112-bass-gallery-negative-final-v1';assert json.loads((final/'proof.json').read_text())['native_aggregate_remains_FALSE'];verify_manifest(final/'manifest.json')
 source=D/'root-current-roster-composition-v1';b=scoped_load(source/'candidate.nes');assert sha(source/'candidate.nes')==SHA
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 files={Path(__file__),old/'proof.json',old/'manifest.json',final/'proof.json',final/'manifest.json',source/'ROOT-source-readiness.json'}
 # Retain every original dependency binding; no old bytes are rewritten.
 files.update(Path(q['path'])for q in json.loads((old/'manifest.json').read_text())['bindings'])
 profiles=[];controls=[];oldmodule=None;newmodule=None;changes=None
 for z in ready['profiles']:
  oldout=Path(z['output']);cfg=json.loads((oldout/'config.json').read_text());script=(oldout/'run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n';assert script.startswith(prefix);body=script[len(prefix):];start=body.index('-- Controlled B-only gallery.');end=body.index('local saved=nil',start);module=body[start:end]
  if oldmodule is None:oldmodule=module;newmodule,changes=transform(module)
  else:assert module==oldmodule
  cfg['isolated_drop_arrays']=DROPS
  for n in EXTRA:cfg['ram'][n]=address(b,n)
  n='InventoryUiTick';pos=location(b,n);cfg['hooks'][n]=dict(address=address(b,n),physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+3]))
  out=a.output/'profiles'/z['profile']/'native';out.mkdir(parents=True)
  newbody=body[:start]+newmodule+body[end:];assert newbody[:start]==body[:start]and newbody[start+len(newmodule):]==body[end:]
  restored=newmodule
  for q in reversed(changes):assert restored.count(q['after'])==1;restored=restored.replace(q['after'],q['before'])
  assert restored==oldmodule
  for ext in['.nes','.dbg','.lbl','.map']:shutil.copy2(source/('candidate'+ext),out/('candidate'+ext))
  for name in['inherited-NMI-stack-APU-guards.lua']:shutil.copy2(oldout/name,out/name)
  put(out/'config.json',cfg);(out/'run.lua').write_text('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+newbody,encoding='utf-8')
  models=mechanics_models(LuaRuntime,newmodule,cfg);assert len(models)==12 and all(models.values())
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end');rt.execute((out/'run.lua').read_text());count=rt.eval('#callbacks');assert count==73 and rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')and rt.eval('#events[emu.eventType.endFrame]')==3
  rt.execute('emu.addMemoryCallback=function()error("Runtime callback registration")end;emu.removeMemoryCallback=function()error("Runtime callback removal")end')
  controls.append(dict(profile=z['profile'],module_reverse_normalization_exact=True,all_non_module_body_bytes_exact=True,original_default_oracle_and_strict_module_exact=True,models=models,startup_callbacks=count,dispatcher_last=True,endFrame_callbacks=3))
  profiles.append(dict(profile=z['profile'],mode_value=cfg['mode_value'],plans=16,output=str(out),script_sha256=sha(out/'run.lua'),callbacks=count,maximum_launches=1,original_NMI_stack_bank_5SMC_APU_guards_sha256=sha(out/'inherited-NMI-stack-APU-guards.lua')))
 (a.output/'original-module.lua').write_text(oldmodule,encoding='utf-8');(a.output/'isolated-module.lua').write_text(newmodule,encoding='utf-8');(a.output/'fixture-only.patch').write_text(''.join(difflib.unified_diff(oldmodule.splitlines(True),newmodule.splitlines(True),fromfile='frozen3b-gallery-original',tofile='isolated-fixture-successor')),encoding='utf-8');put(a.output/'exact-transformations.json',changes)
 put(a.output/'source-controls.json',dict(passed=True,native_run=False,ROM_sha256=SHA,profiles=controls,original_native_FALSE_proof_sha256=sha(old/'profiles/bass-easy/native/proof.json'),frozen_negative_sha256=sha(final/'proof.json'),compiled_source_refill_controls=dict(path=str(D/'current3b112-bass-gallery-negative-v2/compiled-refill-controls.json'),sha256=sha(D/'current3b112-bass-gallery-negative-v2/compiled-refill-controls.json')),no_game_code_changes=True,limits='Source/mock fixture correction only. Native original3759FALSE retained; positive native gallery/Hard/timing not inferred.'))
 env=dict(ready['environment']);runtime=Path(env['emulator']).parent;isolated=a.output/'emulator';isolated.mkdir()
 for f in runtime.iterdir():
  if f.is_file():shutil.copy2(f,isolated/f.name);files.add(f)
 env.update(emulator=str(isolated/'Mesen.exe'),emulator_sha256=sha(isolated/'Mesen.exe'),core_sha256=sha(isolated/'MesenCore.dll'),worker_settings_sha256=sha(isolated/'settings.json'),user_context_sha256=sha(Path('C:/Mesen2/settings.json')))
 assert env['worker_settings_sha256']==ready['environment']['worker_settings_sha256']and env['user_context_sha256']==ready['environment']['user_context_sha256'];put(a.output/'environment.json',env)
 for name in['plans.json','seed-policy.json']:shutil.copy2(old/name,a.output/('original-'+name))
 put(a.output/'seed-policy-addendum.json',dict(lane='B',acquisition=False,original_seeds_unchanged_except=['All four complete InvDrop slots including AvDropItem cleared only at declared native-boundary component setup; prior earned actors explicitly logged before clear.','Empty/refusal component explicitly seeds selected weapon stock0, no drops/refill/tick/TimerControl; funded earned pickups are NOT suppressed or removed during native play.'],funded_assertions=['Actual InventorySpend exact before-cost=after reaches0; enough seeded stock debited.','Live balance equals initial stock minus all accepted native spends plus every full InventoryUiTick native refill credit.','Credit must be current index, tick1, exact+4/cap112 and native remain/tick/completion continuation.'],all_other_controller_contacts_caps_deadlines_untouched=True))
 commands={q['profile']:'python -B tools/audit/final_inventory_successor_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --profile '+q['profile']+' --native-grant'for q in profiles};put(a.output/'commands.json',commands)
 files.update(f for f in a.output.rglob('*')if f.is_file());files.update([Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__),ROOT/'tools/audit/final_inventory_successor_gallery_run_v1.py'])
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]));put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profiles=profiles,plans=32,manifest_sha256=sha(a.output/'manifest.json'),manifest_bindings=len(files),source_controls_sha256=sha(a.output/'source-controls.json'),environment=env,commands=commands,maximum_owned_workers=1,maximum_launches_per_profile=1,retries=False,automatic_next_profile=False,limits=['Fixture-only B lane; no source/default/settings changes/acquisition/gamebug claim.','OriginalFALSE3759 remains. Separate native grant required; Easy first, Hard conditional.','All original controller/caps/contacts/pool/deadline/PPU/DMA/CHR/5SMC/stack/default oracle preserved except the explicitly source-correct funded balance and isolated empty/drop setup.','Actual hardware/raster/16case outcomes remain unobserved; source/mock assertions do not establish native coverage.']))
 verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),commands=commands),indent=2))
if __name__=='__main__':main()
