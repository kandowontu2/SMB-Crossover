"""Bind genuine full Samus draw completion; no mechanics/source/native mutation."""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,shutil,sys
from final_samus_hard_gallery_source_v1 import D,ROOT,PARENT,SHA
from final_samus_hard_gallery_prepare_v2 import phase_models
from final_samus_hard_gallery_pool_prepare_v1 import setups
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_run import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from parodius_visibility_hud_static_startup_v1 import MOCK
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
OLD=D/'current3b112-samus-hard-wave-ready-v1'
CPU=D/'current3b112-samus-hard-publication-controls-v1/proof.json'
def models(LuaRuntime,script,cfg,cpu):
 pre=MOCK+'''
L={};OUTPUT='mock/';mem={};hardware={};BANKA=4;CB=13;emu.memType.nesPrgRom=6
emu.read=function(a,t)if t==3 then return hardware[a]or 0 else return mem[a]or 0 end end
emu.write=function()error('Publication observer never writes emulated state')end
emu.convertAddress=function(a)local b=a>=0xe000 and 127 or a>=0xc000 and CB or a>=0xa000 and BANKA or a>=0x8000 and 126 or 0;return{address=b*8192+a%8192}end
emu.getScreenBuffer=function()error('No synthetic PPU images in publication models')end
'''
 export='''
function TEST_INIT(update)
 entered=true;done=false;phase='publication-model';updates=update;wall=200;samusPublicationScope=nil
 bodyPrepared={stale_prior_body=true};bodyPublished=nil;bodyDma=nil;bodyDisplayed=nil;published=nil;dma=nil
 mem[L.SelectedCharacter]=2;mem[L.CrossoverBehaviorVersion]=1;mem[L.GuestOamRotationActive]=0
end
function TEST_HOOK(n)local h=C.hooks[n];state['cpu.pc']=h.address;for _,q in ipairs(callbacks)do if q.kind==2 and q.lo==h.address and q.hi==h.address then q.fn()end end end
function TEST_RETURN(pc,sp)state['cpu.pc']=pc;state['cpu.sp']=sp;callbacks[#callbacks].fn(pc)end
function TEST_BODY(b)bodyPrepared=b end
function TEST_PUBLISHED(t)local s={};for i=1,#t do s[i]=string.char(t[i])end;return published==table.concat(s)end
function TEST_BODY_PUBLISHED(b)return bodyPublished==b end
function TEST_SERIAL()return samusPublicationSerial end
function TEST_EXPECTED_BODY()return bodyDisplayed end
function TEST_EPOCH()updates=updates+1 end
function TEST_MEMORY_CALLBACK(kind,a,v)state['cpu.pc']=a;for _,q in ipairs(callbacks)do if q.kind==kind and a>=q.lo and a<=q.hi and q.lo~=0 then q.fn(a,v)end end end
'''
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(pre+script+export);mem=rt.globals().mem;hardware=rt.globals().hardware
 for h in cfg['hooks'].values():
  for i,v in enumerate(h['bytes']):mem[h['address']+i]=v
 for i,v in enumerate(cfg['dma_protocol']['window_bytes']):mem[cfg['dma_protocol']['window_start']+i]=v
 count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535');rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 def stack(entry,endpoint):
  sp=entry['sp'];ret=endpoint[0]-1;rt.execute(f"state['cpu.sp']={sp};BANKA=4;CB=13");mem[256+((sp+1)&255)]=ret&255;mem[256+((sp+2)&255)]=ret>>8
 def fill(source):
  for i,v in enumerate(source):mem[512+i]=v
 def native_body(z):
  q=z['body'];return rt.table_from(dict(logical=q['logical'],physical=cfg['legacy_chr'][q['logical']],pose=q['pose'],pointer=q['pointer'],bank=q['bank'],update=10))
 def begin(z):
  rt.globals().TEST_INIT(10);mem[cfg['ram']['SmFreezeRenderState']]=int(z['postFinish']);stack(z['entry'],z['outer_endpoint']);rt.globals().TEST_HOOK('SamusFreezeDrawAll');stack(z['inner_entry'],z['inner_endpoint']);rt.globals().TEST_HOOK('DrawAllMetasprites');body=native_body(z);rt.globals().TEST_BODY(body);return body
 def returned(endpoint):
  pc,bank,sp=endpoint;rt.execute(f'BANKA={bank if pc>=0xa000 and pc<0xc000 else 4};CB={bank if pc>=0xc000 and pc<0xe000 else 13}');rt.globals().TEST_RETURN(pc,sp)
 def complete(z):
  body=begin(z);fill(z['inner_source']);returned(z['inner_endpoint'])
  if z['postFinish']:fill(z['source']);returned(z['outer_endpoint'])
  assert rt.globals().TEST_PUBLISHED(rt.table_from(z['source']))and rt.globals().TEST_BODY_PUBLISHED(body);return body
 results=[]
 for row in cpu['rows']:
  for repeat,z in enumerate(row['completed']):complete(z);results.append(dict(owned=row['owned'],face=row['face'],pose=row['pose'],postFinish=z['postFinish'],repeat=repeat,passed=True))
 z=next(q['completed'][0]for q in cpu['rows']if q['owned']==129 and not q['freeze']and q['pose']=='standing');zf=next(q['completed'][0]for q in cpu['rows']if q['owned']==137 and q['freeze']and q['pose']=='standing')
 def expect_reject(name,fn):
  try:fn();accepted=True
  except Exception:accepted=False
  assert not accepted,name;results.append(dict(kind=name,expected='reject',passed=True))
 def nested():begin(z);rt.globals().TEST_HOOK('SamusFreezeDrawAll')
 expect_reject('nested-wrapper',nested)
 def missing():rt.globals().TEST_INIT(10);rt.globals().TEST_HOOK('DrawAllMetasprites')
 expect_reject('DrawAll-without-wrapper',missing)
 for name in['wrong-update','wrong-character','wrong-rotation']:
  def invalid(name=name):
   begin(z)
   if name=='wrong-update':rt.globals().TEST_EPOCH()
   else:mem[cfg['ram']['SelectedCharacter']if name=='wrong-character'else cfg['ram']['GuestOamRotationActive']]=1
   fill(z['source']);returned(z['outer_endpoint'])
  expect_reject(name,invalid)
 for name in['inner-wrong-SP','inner-wrong-bank','outer-wrong-SP','outer-wrong-bank']:
  base=zf if name.startswith('inner')else z;begin(base);fill(base['inner_source']);ep=list(base['inner_endpoint']if name.startswith('inner')else base['outer_endpoint']);before=rt.globals().TEST_SERIAL()
  if name.endswith('SP'):ep[2]-=1
  elif 0xa000<=ep[0]<0xc000:ep[1]^=1
  else:
   # Genuine RAM return-bank remains0, so a wrong PC cannot alias it.
   ep[0]+=1
  returned(ep);assert rt.globals().TEST_SERIAL()==before
  if base['postFinish']:returned(base['inner_endpoint']);fill(base['source']);returned(base['outer_endpoint'])
  else:returned(base['outer_endpoint'])
  assert rt.globals().TEST_SERIAL()==before+1;results.append(dict(kind=name,expected='defer then genuine',passed=True))
 # Source wrapper State1 cannot publish its pre-Finish256 snapshot.
 begin(zf);fill(zf['inner_source']);before=rt.globals().TEST_SERIAL();returned(zf['inner_endpoint']);assert rt.globals().TEST_SERIAL()==before;fill(zf['source']);returned(zf['outer_endpoint']);assert rt.globals().TEST_PUBLISHED(rt.table_from(zf['source']));results.append(dict(kind='Finish-mutated-OAM-publishes-only-outer',passed=True))
 # A prior body cannot survive a new DrawAll that emits no current body.
 begin(z);rt.globals().TEST_BODY(None);fill(z['source']);returned(z['outer_endpoint']);assert rt.globals().TEST_BODY_PUBLISHED(None);results.append(dict(kind='no-current-body-does-not-admit-stale',passed=True))
 # NMI-like wrong-stack arrival and repeated old return do not publish.
 begin(z);fill(z['source']);before=rt.globals().TEST_SERIAL();ep=list(z['outer_endpoint']);ep[2]-=3;returned(ep);assert rt.globals().TEST_SERIAL()==before;returned(z['outer_endpoint']);assert rt.globals().TEST_SERIAL()==before+1;returned(z['outer_endpoint']);assert rt.globals().TEST_SERIAL()==before+1;results.append(dict(kind='NMI-stack-interruption-and-reused-return',passed=True))
 # Two completed publication/DMA generations; foreground publication cannot
 # replace already displayed hardware/body before a real complete transfer.
 def dma(z):
  rt.execute("state['cpu.pc']=0xe005;state['ppu.scanline']=-1;state['ppu.cycle']=40;state['ppu.spriteRamAddr']=0")
  # write callbacks see the actual store's post-PC, unlike EXEC callbacks.
  for q in rt.globals().callbacks.values():
   if q['kind']==1 and q['lo']==0x4014:q['fn'](0x4014,2)
  for i,v in enumerate(z['source']):
   rt.execute(f"state['ppu.spriteRamAddr']={i}");hardware[i]=v
   for q in rt.globals().callbacks.values():
    if q['kind']==1 and q['lo']==0x2004:q['fn'](0x2004,v)
  rt.execute("state['cpu.pc']=0xe008;state['ppu.spriteRamAddr']=0")
  rt.globals().TEST_MEMORY_CALLBACK(2,0xe008,None)
 def start(physical):rt.execute(f"state['mapper.chrBanks0']={physical}");rt.globals().runevents(0)
 body=complete(z);dma(z);start(body['physical']);assert rt.globals().TEST_EXPECTED_BODY()==body
 # Start a new wrapper without resetting the already displayed body/DMA.
 oldbody=body;mem[cfg['ram']['SmFreezeRenderState']]=1;stack(zf['entry'],zf['outer_endpoint']);rt.globals().TEST_HOOK('SamusFreezeDrawAll');stack(zf['inner_entry'],zf['inner_endpoint']);rt.globals().TEST_HOOK('DrawAllMetasprites');newbody=native_body(zf);rt.globals().TEST_BODY(newbody);fill(zf['inner_source']);returned(zf['inner_endpoint']);fill(zf['source']);returned(zf['outer_endpoint']);start(oldbody['physical']);assert rt.globals().TEST_EXPECTED_BODY()==oldbody;dma(zf);start(newbody['physical']);assert rt.globals().TEST_EXPECTED_BODY()==newbody
 expect_reject('wrong-completed-body-physical-CHR',lambda:start(newbody['physical']^1));start(newbody['physical']);results.append(dict(kind='two-actual-DMA-generations-and-previous-visible-body',passed=True))
 assert rt.eval('#callbacks')==count
 return dict(passed=True,models=results,complete_compiled_return_models=88,additional_models=len(results)-88,callbacks=count,fixed_registration_inventory=True,no_emulated_writes=True,limits='Synthetic hardware values exercise actual unchanged observer code. These are not native publication/physicalCHR observations.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert verify_manifest(OLD/'manifest.json')==1049;old=OLD/'native';assert not json.loads((old/'proof.json').read_text())['passed'];b=scoped_load(old/'candidate.nes');oldcfg=json.loads((old/'config.json').read_text());cfg=copy.deepcopy(oldcfg)
 name='SamusFreezeDrawAll';pos=location(b,name);cfg['hooks'][name]=dict(address=address(b,name),physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+3]));cfg['ram']['GuestOamRotationActive']=address(b,'GuestOamRotationActive')
 before=(ROOT/'tools/audit/final_samus_hard_gallery_native_v5.lua').read_text();after=(ROOT/'tools/audit/final_samus_hard_gallery_native_v6.lua').read_text();previous=(old/'run.lua').read_text();assert previous.count(before)==1;first,tail=previous.split('\n',1);assert first=='FINAL_ITEM_PROGRESSIVE='+lua(oldcfg);script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+tail.replace(before,after);assert script.split('\n',1)[1].replace(after,before)==tail
 reverse=copy.deepcopy(cfg);del reverse['hooks'][name];del reverse['ram']['GuestOamRotationActive'];assert reverse==oldcfg
 (a.output/'observer.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='native_v5.lua',tofile='native_v6.lua')),encoding='utf-8');cpu=json.loads(CPU.read_text());assert cpu['passed']and cpu['actual_wrapper_returns']==88
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 modeled=models(LuaRuntime,script,cfg,cpu);put(a.output/'publication-observer-models.json',modeled);u,_=setups(LuaRuntime,previous,oldcfg,b['raw']);v,_=setups(LuaRuntime,script,cfg,b['raw']);assert u==v and len(v)==27;phases=phase_models(LuaRuntime,script);assert len(phases['models'])==32;put(a.output/'source-controls.json',dict(passed=True,complete_GameLoop_cells=44,actual_wrapper_returns=88,final_OAM_Finish_changes=44,observer_models=len(modeled['models']),all27setup_RAM_writes_exact=True,original32phase_models=phases,all_other_script_config_guard_mechanics_reverse_exact=True,only_delta='One authentic wrapper hook + one rotation RAM label; full wrapper/inner current-owner return handshake publishes final256/body only after both genuine endpoints. All old rawE008/hardware/latch/counter/bodyCHR checks retained.'))
 out=a.output/'native';out.mkdir()
 for ext in['nes','dbg','lbl','map']:shutil.copy2(old/('candidate.'+ext),out/('candidate.'+ext))
 put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');shutil.copy2(old/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua')
 for f in['plans.json','seed-policy.json']:shutil.copy2(OLD/f,a.output/f)
 runtime=a.output/'emulator';runtime.mkdir()
 for q in(OLD/'emulator').iterdir():
  if q.is_file():shutil.copy2(q,runtime/q.name)
 env=copy.deepcopy(json.loads((OLD/'proof.json').read_text())['environment']);env['emulator']=str(runtime/'Mesen.exe');env['user_settings_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(runtime/'Mesen.exe')==env['emulator_sha256']and sha(runtime/'settings.json')==env['worker_settings_sha256'];put(a.output/'environment.json',env)
 report=ROOT/'docs/qa/final-samus-hard-gallery-publication-observer-2026-10-26.txt';report.write_text('Samus full draw/publication observer correction\n26 October2026. Source/static only; native grant not inferred. ROM '+SHA+' unchanged.\n\nOriginal wave-ready native4508f6da staysFALSE after27actualmechanic completions. RosterOamReady isrotated-only; Samus2 useslegacytail JMP OAMClear→RTS. Legacy dmaChecks0 andbodyDisplayed neverbound even though2671rawE008full256/2354safe checks pass. Alloldfails retained.\n\nNewv6 observes genuineSamusFreezeDrawAllentry andfullinnerDrawAll/OAMClear return through fixedstartupdispatcher. State0 tailJMP sharesrealouterreturn; State1 innerJSR return precedesgenuineSamusFreezeRenderFinish rewritingOAM thenouterreturn. A two-endpointhandshake publishesexact256Sprite_Data/currentbodyPrepared ONLYatobservedouterreturnPC/SP/physicalbank afteractualinnercompletion. Innerentry clearspriorbodyPrepared; scope/update/character/nonrotation/endpointguards rejectstale/reentrant owners. Oldrotatedhook remainsuncountedforSamus; originalrawE008/order/renderoff/CHR/counter/bodyepochasserts retained. No perframe gamecodechange or emulatedwrites.\n\n44completecompiledGameLoopcells/88genuinereturns cover8ownedforms,bothfacings,standing pluscrouch/Morph/spin,uncached/repeatandbothwrapperbranches;44realFinish paths alterOAMafterinnerreturn. Existing96outlinepresentationcells remainseparate. Actualreturn-derived88Luamodels + finiteowner/return/NMI-stack/reusedreturn/stalebody/Finish/physicalepochnegatives pass. Two realmodeledcomplete256DMAs proveforegroundnewpublicationcannotreplaceoldvisiblebodybeforecompletion; wrongcompletedCHR rejects. These areSOURCE/mocks,notnativepublicationproof. All27setupRAM/writestreams/32phase models unchanged; reverse-normalizationkeepsothermechanics/inputs/caps/strictguards exactly.\n\nSame8cases/27subphases/numericHard1/Bseededuse; no acquisition/Easy/randompool/star1up/campaign/waveform/globalFPS/crowdedflickerclaim.12actualprior sheets151placements/193captureoccurrences reviewedseparatelywithoriginalterminalFALSE retained. No production/default/settings/Git edits.\n',encoding='utf-8')
 files={Path(z['path'])for z in json.loads((OLD/'manifest.json').read_text())['bindings']};files.update({Path(__file__),ROOT/'tools/audit/final_samus_hard_gallery_native_v6.lua',ROOT/'tools/audit/final_samus_hard_gallery_publication_controls_v1.py',CPU,report,OLD/'proof.json',OLD/'manifest.json',old/'proof.json',old/'first-failure.json',D/'current3b112-samus-hard-wave-terminal-final-v1/proof.json',D/'current3b112-samus-hard-wave-terminal-final-v1/manifest.json'});files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));count=verify_manifest(a.output/'manifest.json');command='python -B tools/audit/final_samus_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant';put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='samus-hard',mode_value=1,maximum_cases=8,maximum_launches=1,maximum_owned_workers=1,retry=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=count,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,source_controls_sha256=sha(a.output/'source-controls.json'),stable_command=command,source_freeze_sha256=sha(PARENT/'ROOT-source-readiness.json'),original_FALSE_sha256=sha(old/'proof.json'),observer_only=True,report_sha256=sha(report)));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),script_sha256=sha(out/'run.lua'),bindings=count,stable_command=command),indent=2))
if __name__=='__main__':main()
