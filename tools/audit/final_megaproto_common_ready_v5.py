"""One exact0a MegaHard common-special readiness; no native option."""
from pathlib import Path
import argparse,ast,copy,hashlib,json,shutil,sys
from final_megaproto_common_source_v2 import D,R,B,SHA,OLD
from final_samus_hard_gallery_source_v1 import TraceArena,OWNER_NAMES
from final_item_abilities_run import lua
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_current731_prepare_v1 import dma_mocks
from final_item_abilities_static_prepare_v2 import core_tests,old_core
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from parodius_visibility_hud_static_startup_v1 import MOCK
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def model_runtime(LuaRuntime,script,cfg,b):
 pre=MOCK+'''
L={};OUTPUT='mock/';mem={};ppu={};rom={};writes={};BANKA=63;CB=61
emu.memType.nesPrgRom=6
emu.read=function(a,t)if t==6 then return rom[a]or 0 elseif t==2 then return ppu[a]or 0 else return mem[a]or 0 end end
emu.write=function(a,v,t)local m=t==2 and ppu or mem;m[a]=v;writes[#writes+1]={a,v,t}end
emu.convertAddress=function(a)local b=a>=0xe000 and 127 or a>=0xc000 and CB or a>=0xa000 and BANKA or a>=0x8000 and 126 or 0;return{address=b*8192+a%8192}end
emu.getScreenBuffer=function()error('No synthetic PPU outcome')end
'''
 export='''
function TEST_CASE(k)
 entered=true;done=false;phase='funded';index=k;updates=1;age=1;wall=100
 current={q=C.cases[k],draws={},spawns={},spends={},hits=0,damageCalls=0,visibleTypes={},sourceSfx={},nativeSpent=0,nativeCredits=0}
 mem[L.SelectedCharacter]=C.character;mem[L.CrossoverBehaviorVersion]=1
end
function TEST_HOOK(n)local h=C.hooks[n];state['cpu.pc']=h.address;for i,v in ipairs(h.bytes)do mem[h.address+i-1]=v end;for _,q in ipairs(callbacks)do if q.kind==2 and q.lo==h.address and q.hi==h.address then q.fn()end end end
function TEST_RETURN(pc,sp)state['cpu.pc']=pc;state['cpu.sp']=sp;callbacks[#callbacks].fn(pc)end
function TEST_DRAWS(t)return current.draws[t]or 0 end
function TEST_GENERIC(pc)state['cpu.pc']=pc;for _,q in ipairs(callbacks)do if q.kind==2 and pc>=q.lo and pc<=q.hi then q.fn(pc)end end end
function TEST_SETUP(k,kind)
 TEST_CASE(k);mem={};ppu={};writes={};mem[L.SelectedCharacter]=C.character;mem[L.CrossoverBehaviorVersion]=1
 mem[L.InvSelected+C.character]=current.q.item;setup(kind)
end
'''
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(pre+script+export);mem,rom=rt.globals().mem,rt.globals().rom
 # Only immutable source tables/records actually consulted by these models.
 for q in cfg['art'].values():
  for i in range(256):rom[q['bank']*8192+q['address']%8192+i]=b['raw'][16+q['bank']*8192+q['address']%8192+i]
 for row in cfg['effect_records']:
  for q in row:
   for i,v in enumerate(q['bytes']):rom[q['bank']*8192+q['address']%8192+i]=v
 for key in['native_brick','native_chunk','buster_record']:
  q=cfg[key]
  for i,v in enumerate(q['bytes']):rom[q['bank']*8192+q['address']%8192+i]=v
 return rt
def renderer_models(LuaRuntime,script,cfg,b,compiled):
 rt=model_runtime(LuaRuntime,script,cfg,b);mem=rt.globals().mem;rom=rt.globals().rom;count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535');rt.execute('emu.write=function()error("Read-only art observer")end;emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 def case(item,face):return next(i for i,q in enumerate(cfg['cases'],1)if q['item']==item and q['face']==face)
 def field(n,v,i=0):mem[cfg['ram'][n]+i]=v
 def coord(row,z):
  rt.globals().TEST_CASE(case(row['item'],row['face']));rt.execute(f"BANKA={z['A_bank']};CB={z['C_bank']};state['cpu.sp']={z['sp']}")
  for n,v,i in [('RgSlot',z['slot'],0),('RgShotType',z['type'],z['slot']),('SsArt',z['art'],z['slot']),('RgShotDir',z['face'],z['slot']),('R0',z['pointer']&255,0),('R1',z['pointer']>>8,0)]:field(n,v,i)
 def returned(ep):
  pc,bank,sp=ep
  if 0xa000<=pc<0xc000:rt.globals().BANKA=bank
  if 0xc000<=pc<0xe000:rt.globals().CB=bank
  rt.globals().TEST_RETURN(pc,sp)
 results=[]
 for row in compiled['components']:
  for z in row['coords']:coord(row,z);rt.globals().TEST_HOOK('SpecialDrawShots::Coordinates');assert rt.globals().TEST_DRAWS(z['type'])==1;results.append(dict(item=row['item'],face=row['face'],kind='actual-full-render-Coordinates',slot=z['slot'],art=z['art'],passed=True))
  for z in row['water']:
   rt.globals().TEST_CASE(case(7,row['face']));rt.execute(f"BANKA={z['A_bank']};CB={z['C_bank']};state['cpu.sp']={z['sp']}");sp=z['sp'];ret=z['endpoint'][0]-1;mem[256+((sp+1)&255)]=ret&255;mem[256+((sp+2)&255)]=ret>>8
   for n,v,i in [('RgSlot',z['slot'],0),('RgShotType',17,z['slot']),('SsHidden',z['hidden'],z['slot']),('SsArt',z['art'],z['slot']),('CurrentOAMOffset',z['before'],0)]:field(n,v,i)
   rt.globals().TEST_HOOK('SpecialDrawWaterShot');field('CurrentOAMOffset',z['after']);returned(z['endpoint']);assert rt.globals().TEST_DRAWS(17)==int(z['before']!=z['after']);results.append(dict(item=7,face=row['face'],kind='actual-full-render-WATER-return',emitted=z['before']!=z['after'],passed=True))
 row=next(q for q in compiled['components']if q['item']==2 and q['face']==1);z=row['coords'][0]
 def reject(name,fn):
  try:fn();accepted=True
  except Exception:accepted=False
  assert not accepted,name;results.append(dict(kind=name,expected='reject',passed=True))
 for kind in['wrong-pointer','wrong-C-bank','wrong-source-byte','stale-slot']:
  coord(row,z)
  if kind=='wrong-pointer':field('R0',(z['pointer']+1)&255)
  elif kind=='wrong-C-bank':rt.globals().CB=z['C_bank']^1
  elif kind=='stale-slot':field('RgSlot',(z['slot']+1)%10);field('SsArt',0,(z['slot']+1)%10)
  else:at=z['C_bank']*8192+z['pointer']%8192+1;original=rom[at];rom[at]=original^1
  reject(kind,lambda:rt.globals().TEST_HOOK('SpecialDrawShots::Coordinates'))
  if kind=='wrong-source-byte':rom[at]=original
 coord(row,z);rt.globals().BANKA=z['A_bank']^1;rt.globals().TEST_HOOK('SpecialDrawShots::Coordinates');assert rt.globals().TEST_DRAWS(z['type'])==0;results.append(dict(kind='wrong-physical-owner-bank',expected='defer',passed=True))
 # Foreign advanced/body/HUD paths cannot inherit a nonexistent generic scope.
 coord(row,z)
 for name in['RemainingDraw::Shot','RemainingDraw::ArtPointer','MetaspriteRenderLoop']:
  rt.globals().TEST_GENERIC(address(b,name))
 assert rt.globals().TEST_DRAWS(z['type'])==0;results.append(dict(kind='advanced-HUD-body-no-generic-scope',passed=True))
 # A skipped dedicated Water return is consumed once, never on a future body.
 for rejected in compiled['water_rejections']:
  z=rejected['water'];rt.globals().TEST_CASE(case(7,1));rt.execute(f"BANKA={z['A_bank']};CB={z['C_bank']};state['cpu.sp']={z['sp']}");sp=z['sp'];ret=z['endpoint'][0]-1;mem[256+((sp+1)&255)]=ret&255;mem[256+((sp+2)&255)]=ret>>8;field('RgSlot',z['slot']);field('RgShotType',17,z['slot']);field('SsHidden',z['hidden'],z['slot']);field('CurrentOAMOffset',z['before']);rt.globals().TEST_HOOK('SpecialDrawWaterShot');returned(z['endpoint']);field('CurrentOAMOffset',(z['before']+8)%256);returned(z['endpoint']);assert rt.globals().TEST_DRAWS(17)==0;results.append(dict(kind='skipped-WATER-return-no-future-body-credit',reason=rejected['reason'],passed=True))
 assert rt.eval('#callbacks')==count
 return dict(passed=True,actual_assembled_Coordinates=52,actual_assembled_WATER_returns=66,additional_models=len(results)-118,models=results,callbacks=count,no_runtime_registration=True,emulated_writes=0,scope='Actual Lua immediate-callback bodies fed actual compiled owner/slot/pointer/return records; no PPU/native/visiblepixel verdict.')
def setup_models(LuaRuntime,script,cfg,b):
 rt=model_runtime(LuaRuntime,script,cfg,b);oldcfg=json.loads((OLD/'profiles/bass-hard/native/config.json').read_text());old=model_runtime(LuaRuntime,(OLD/'profiles/bass-hard/native/run.lua').read_text(),oldcfg,b);rows=[]
 def write_rows(runtime):return[[int(z[i])for i in[1,2,3]]for _,z in runtime.globals().writes.items()]
 for k,q in enumerate(cfg['cases'],1):
  for kind in['funded','empty','pool']:
   rt.globals().TEST_SETUP(k,kind);old.globals().TEST_SETUP(k+2,kind);current=write_rows(rt);previous=write_rows(old);oldammo=oldcfg['ram']['InvAmmo']+144+q['item'];newammo=cfg['ram']['InvAmmo']+16+q['item'];normalized=[[newammo if p==oldammo and t==1 else p,v,t]for p,v,t in previous];assert current==normalized
   rows.append(dict(item=q['item'],face=q['face'],kind=kind,write_count=len(current),all_writes_exact_except_declared_ammo_address=True,old_ammo_address=oldammo,current_ammo_address=newammo))
 return dict(passed=True,complete_declared_component_setups=42,rows=rows,actual_script_controller='Unchanged Bass policy including fresh WATER125, actual Down+A KICK, funded420/empty25/pool15/selection caps.',scope='Actual generated Lua setup writes/PPU staging models, never native acquisition or result evidence.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--lua-root',required=True,type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);source=D/'current0a-mega-common-source-v2';render=D/'current0a-mega-common-render-v3';verify_manifest(source/'manifest.json');verify_manifest(render/'manifest.json');cfg=json.loads((render/'config.json').read_text());script=(render/'run.lua').read_text();b=scoped_load(B/'candidate.nes');assert sha(B/'candidate.nes')==SHA;sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 compiled=json.loads((render/'compiled-render-controls.json').read_text());models=renderer_models(LuaRuntime,script,cfg,b,compiled);put(a.output/'immediate-art-observer-models.json',models);seeds=setup_models(LuaRuntime,script,cfg,b);put(a.output/'complete-setup-models.json',seeds)
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'+script+'\nfunction TEST_JSON()return json({[0]=true,[4]={stock=20}})end\n');count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535');rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 for frame in[1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
 assert rt.eval('#callbacks')==count;encoded=rt.globals().TEST_JSON();assert json.loads(encoded)=={'0':True,'4':{'stock':20}}
 dma=dma_mocks(LuaRuntime,(R/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=cfg['dma_protocol']));returns=core_tests(LuaRuntime,old_core((R/'tools/audit/final_item_abilities_native.lua').read_text()),(R/'tools/audit/final_item_abilities_static_return_v1.lua').read_text());put(a.output/'source-controls.json',dict(passed=True,callbacks=count,dispatcher_last=True,numeric_key_JSON_valid=True,source_owner_cells=84,source_select_sequences=4,compiled_render_components=14,immediate_art_models=118+models['additional_models'],complete_component_setups=42,actual_DMA_protocol_models=dma,static_return_models=returns))
 # Source-qualified Mega rotation genuinely reaches the inherited publication.
 if 'RosterOamReady'not in OWNER_NAMES:OWNER_NAMES.append('RosterOamReady')
 q=TraceArena(b);q.put(SelectedCharacter=1,ProtoVariant=0,PlayerStatus=1);q.set('InvOwnedLo',255,1);q.set('InvOwnedHi',0,1);q.invoke('PlayerGfxHandler');q.invoke('SamusFreezeDrawAll');assert q.get('GuestOamRotationActive')==1 and any(z['owner']=='RosterOamReady'for z in q.calls[-1]['entries']);put(a.output/'full-body-publication-owner.json',dict(passed=True,source_only=True,rotation=1,calls=q.calls,scope='Mega selected1 uses genuine rotated-tail RosterOamReady. This is not Samus legacy-tail observer reuse or native publication proof.'))
 out=a.output/'native';out.mkdir()
 for ext in['nes','dbg','lbl','map']:shutil.copy2(B/('candidate.'+ext),out/('candidate.'+ext))
 (out/'run.lua').write_text(script,encoding='utf-8');put(out/'config.json',cfg);guard=(OLD/'profiles/bass-hard/native/inherited-NMI-stack-APU-guards.lua').read_bytes();assert guard.decode().replace('\r\n','\n')in script;(out/'inherited-NMI-stack-APU-guards.lua').write_bytes(guard);assert sha(out/'inherited-NMI-stack-APU-guards.lua')=='6ab7cd71f41f441f4d4d752e2412f83c2b16da06b9e10d3cdf05180c63bf5fdf';put(a.output/'plans.json',cfg['cases'])
 env=copy.deepcopy(json.loads((OLD/'environment.json').read_text()));runtime=a.output/'emulator';runtime.mkdir()
 for q in Path(env['emulator']).parent.iterdir():
  if q.is_file():shutil.copy2(q,runtime/q.name)
 env['emulator']=str(runtime/'Mesen.exe');env['user_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(runtime/'Mesen.exe')==env['emulator_sha256']and sha(runtime/'MesenCore.dll')==env['core_sha256']and sha(runtime/'settings.json')==env['worker_settings_sha256'];settings=json.loads((runtime/'settings.json').read_text(encoding='utf-8-sig'));assert settings['Nes']['RemoveSpriteLimit']is False and settings['Nes']['AdaptiveSpriteLimit']is False and settings['Emulation']['RunAheadFrames']==0;put(a.output/'environment.json',env)
 report=R/'docs/qa/final-megaproto-common-ready-2026-10-26.txt';report.write_text('MegaHard common-special source readiness\n26 October2026. Private0a '+SHA+'. No nativegrant/run.\n\n14components:7common specials bothfacings,owner1/ProtoVariant0/numericHard1; ammoactual17..23. ExactcorrectedBassdirectPharaoh8/clamp,actual0debitwitness/nativecredits,complete-dropisolation,semanticcancelkick2,WATER125 andalloriginalcaps/sourcecontact/cleanup/art/HUD/strictE008/IRQ31/CHR/banks/5SMC/stack/fullPPU guards retained. Typedowner/index/MmSliding adaptation sourceproof73f92d6d. No defaultbuster/Rush/passives duplication; no Proto native implied.\n\n84completeUI→Proc/Specialcostcells+4selectioncycles; actualPlayerMovementSubs/MegaManMovement createsMmSliding beforeKICKpayment. Full14rendercomponents/52Coordinates+66Waterreturnobservations pass withfreshactual0aSS/nativebrick/chunkpointertables. DedicatedcommonSS ownsRgSlot; foreignBill42fullSpecialDrawShots→RemainingDraw usesAvSlot3 whileRgSlot7stale, entersZEROcommonSSCoordinates/Water. No genericMetaspriteRenderLoop/ArtPointer state canleakHUD/nonshot/familyrejectintofuturebody. ActualLua models exerciseall118compiledimmediate observations, wrongpointer/Cbank/immutablebyte/staleslot/ownerbank andskip-return controls. All42actualsetupwrite models normalizeonlyownerammoaddressvsqualifiedBass;art/framesarenotfabricated. Fixedstartupdispatcher andunchanged8return/13DMA models retained. JSONnumericobjectkeys valid. Mega selected1fullPlayerGfx→wrapper→RosterOamReady sourceproofrotates1, unliketheSamuslegacytail.\n\nRuntimefreshcopy/hardware8sprites/adaptiveoff/runahead0/AllZeros/nonrandom/doNotSave settings bindactualfiles; no userconfigwrite. Onepreparedprofile/max1launch/oneworker/noautomaticProto/no retry. Allactualmechanics/graphics/pixel/cadence proofs pendingnative; sourceequivalenceisnotcoverage. Proto0ba deadline378 andROOT9ccomposite remainoutsidehash. No production/default/Git/settings mutations.\n\nA/Bscope: everytier/inventory/ammo/completepool/scene/actor isdeclaredBnative-boundarysetup,notphysicalacquisition. ActualSelect/controlleruse/effects/exhaustion/refusal/contact/cleanup required. ARMquestionblockregressionalreadyseparate. Star/1up/Easy/rareacquisitions/allbosses/allpixel/waveform/globalFPS/flickerclosure remainopen.\n',encoding='utf-8')
 files={Path(z['path'])for p in[source,render]for z in json.loads((p/'manifest.json').read_text())['bindings']};files.update({source/'proof.json',source/'manifest.json',render/'proof.json',render/'manifest.json',Path(__file__),R/'tools/audit/final_megaproto_common_run_v1.py',Path('C:/Mesen2/settings.json'),Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__),report});pending=[Path(__file__),R/'tools/audit/final_megaproto_common_run_v1.py'];seen=set()
 while pending:
  q=pending.pop()
  if q in seen:continue
  seen.add(q);files.add(q)
  for node in ast.walk(ast.parse(q.read_text(encoding='utf-8-sig'))):
   names=[node.module]if isinstance(node,ast.ImportFrom)else[z.name for z in node.names]if isinstance(node,ast.Import)else[]
   for name in names:
    if name:
     dep=R/'tools/audit'/(name.split('.')[0]+'.py')
     if dep.is_file():pending.append(dep)
 # These Lua files are actual inputs to the source/mock controls above;
 # transitive Python-import discovery cannot find their read_text calls.
 for name in['final_item_abilities_dma731_v1.lua','final_item_abilities_native.lua','final_item_abilities_static_return_v1.lua']:files.add(R/'tools/audit'/name)
 put(a.output/'preparation-drafts.json',dict(native_launches=0,source_only_drafts=[dict(folder='current0a-mega-common-ready-v1',reason='Normal compiled WATER samples all emitted; no compiled skip record existed for requested negative model.'),dict(folder='current0a-mega-common-ready-v2',reason='Mock attempted to access localjson from a separateLua chunk; exportclosure fixes test plumbing.'),dict(folder='current0a-mega-common-ready-v3',reason='Guard CRLF file compared against LF generatedscript bytes; normalized textcomparison plus unchanged rawguardSHA preserves exactinstructions.'),dict(folder='current0a-mega-common-ready-v4',reason='Successfulsourcecontrols, but manifest omitted3Lua mock input files; held for this additive completebinding successor.')],game_or_controller_changes_in_draft_fixes=False))
 files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));bindings=verify_manifest(a.output/'manifest.json');command='python -B tools/audit/final_megaproto_common_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant';put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='mega-hard-common',mode_value=1,variant=0,maximum_cases=14,maximum_launches=1,maximum_owned_workers=1,retry=False,automatic_other_profiles=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=bindings,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,stable_command=command,source_controls_sha256=sha(a.output/'source-controls.json'),report_sha256=sha(report),lane='B',acquisition=False));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=bindings,script_sha256=sha(out/'run.lua'),stable_command=command),indent=2))
if __name__=='__main__':main()
