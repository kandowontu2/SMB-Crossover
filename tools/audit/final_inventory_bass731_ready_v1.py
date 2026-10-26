"""Prepare two controlled Bass galleries on exact731. NO native execution option."""
from pathlib import Path
import argparse,ast,hashlib,json,re,shutil,sys
from final_item_abilities_run import lua
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT,core_tests,old_core
from final_item_abilities_current731_prepare_v1 import protocol,dma_mocks,OLD_DMA
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def compiled_cpu(b):
 rows=[]
 for mode in [0,1]:
  for face in [1,2]:
   for item,cost,typ in [(1,8,9),(2,4,10),(3,8,11),(4,4,12),(5,4,19),(6,4,15),(7,16,17)]:
    for kind in ['funded','underfunded','fullpool']:
     q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,InvFresh=64,SavedJoypadBits=64)
     q.set('InvOwnedLo',255,9);q.set('InvSelected',item,9)
     before=cost if kind=='funded'else cost-1 if kind=='underfunded'else 112;q.set('InvAmmo',before,144+item)
     if kind=='fullpool':
      for i in range(10):q.set('RgShotType',10,i);q.set('RgShotX',96+i*3,i);q.set('RgShotPage',1,i);q.set('RgShotY',72,i);q.set('RgShotYHigh',1,i);q.set('RgShotDir',face,i)
     if item==5:q.put(XgDash=1,SsKick=0)
     if item==1 and kind!='fullpool':
      q.put(SsHeld=10);q.set('RgShotType',9,9);q.set('RgShotDir',face,9);q.set('SsMode',1,9)
      c,t=q.invoke('MegaManSuperArmThrow')
     else:c,t=q.invoke('SpecialWeapons')
     spent=cost if kind=='funded'or kind=='fullpool'and item in [5,7]else 0
     assert q.get('InvAmmo',144+item)==before-spent,(mode,face,item,kind,before,q.get('InvAmmo',144+item))
     types=[q.get('RgShotType',i)for i in range(10)]
     if kind=='funded':assert typ in types,(item,types)
     if kind=='funded':assert all(q.get('RgShotDir',i)==face for i,t in enumerate(types)if t)
     if kind=='underfunded'and item!=1:assert all(t==0 for t in types),(item,types)
     if kind=='fullpool':assert types==[10]*10,(item,types)
     rows.append(dict(mode=mode,face=face,item=item,kind=kind,before=before,after=q.get('InvAmmo',144+item),types=types,cycles=c.processorCycles,source='complete actual routine, isolated CPU'))
   # Genuine big Pharaoh release: source spends/clamps8, type14, full return.
   for stock in [0,4,8,112]:
    q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,SsSelected=4,RgSlot=9);q.set('InvSelected',4,9);q.set('InvAmmo',stock,148)
    for n,v in [('RgShotType',18),('RgShotAge',63),('RgShotDir',face)]:q.set(n,v,9)
    c,t=q.invoke('SpecialWeapons::ReleaseBalloon',x=9);assert q.get('RgShotType',9)==14 and q.get('InvAmmo',148)==max(0,stock-8)
    rows.append(dict(mode=mode,face=face,item=4,kind='charged-release',before=stock,after=q.get('InvAmmo',148),cycles=c.processorCycles))
   q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode);q.set('InvOwnedLo',255,9)
   for expected in [1,2,3,4,5,6,7,0]:
    for i in range(10):q.set('RgShotType',10,i)
    c,t=q.invoke('InventoryCycle');assert q.get('InvSelected',9)==expected and all(q.get('RgShotType',i)==0 for i in range(10))
    rows.append(dict(mode=mode,face=face,kind='compiled-selection-cleanup',expected=expected,cycles=c.processorCycles))
   for count in [0,3,4,10]:
    q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face)
    for i in range(count):q.set('RgShotType',4,i)
    c,t=q.invoke('ExpandedWeapons::FireShot');types=[q.get('RgShotType',i)for i in range(10)]
    assert sum(v!=0 for v in types)==(count+1 if count<4 else count)
    if count<4:assert q.get('RgShotDir',9)==face
    assert q.get('RgCooldown')in[4,5]
    rows.append(dict(mode=mode,face=face,kind='compiled-default-buster-pool',before=count,after=sum(v!=0 for v in types),cycles=c.processorCycles))
   for damage_type in [31,42,43,44,47,52,49,50]:
    q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,MmSlot=0,MmBulletType=damage_type)
    q.set('Enemy_Flag',1);q.set('Enemy_ID',6);q.set('Enemy_Y_HighPos',1);q.set('Enemy_Y_Position',184);q.set('Enemy_X_Position',150);q.set('Enemy_PageLoc',1)
    q.set('MmEnemyHealthLo',232);q.set('MmEnemyHealthHi',3)
    expected=b['raw'][location(b,'MegaManWeapons::DamageTable')+damage_type-1]
    c,t=q.invoke('MegaManWeapons::DamageEnemy',x=0);after=q.get('MmEnemyHealthLo')+256*q.get('MmEnemyHealthHi');assert after==1000-expected,(damage_type,after,expected)
    rows.append(dict(mode=mode,face=face,kind='compiled-native-damage-consumer',damage_type=damage_type,before=1000,after=after,source_damage=expected,cycles=c.processorCycles,scope='Isolated accepted consumer, not spatial contact/native acquisition'))
 return rows

def compose(cfg):
 base=(ROOT/'tools/audit/final_item_matrix_progressive.lua').read_text()
 prefix=base[:base.index('local function seed()')]
 prefix=prefix.replace("assert(n~='PlayerStatus','Power tiers must be acquired');",'')
 prefix=prefix.replace("if C.family=='scrooge'and r('DarkwingVariant')~=0 then return{select=true}end","if r('RlVariant')~=0 then return{select=true}end")
 prefix=prefix.replace(OLD_DMA,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text()+'\n')
 assert OLD_DMA not in prefix
 core=(ROOT/'tools/audit/final_item_abilities_static_return_v1.lua').read_text()
 mechanics=(ROOT/'tools/audit/final_inventory_bass731_native_v1.lua').read_text()
 guards=base[base.index('local saved=nil'):base.index('emu.addEventCallback(function()\n if not entered then emu.setInput')]
 event_tail=base[base.index('emu.addEventCallback(function()\n wall=wall+1'):]
 old="local f=assert(io.open(OUTPUT..'native-progressive.json','w'));f:write(json({passed=true,goal_complete=false,family=C.family,hard=C.hard,cases=records,updates=updates,nmis=nmis,minSP=minSP,apuWrites=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,scope='Actual head-bump/reveal/native full rise; explicit post-rise collision placement; cold selection and source-owned transformation/use. No campaign claim'}));f:close();emu.stop(0)"
 new="local f=assert(io.open(OUTPUT..'native-bass-gallery.json','w'));f:write(json({passed=true,goal_complete=false,lane='B controlled use only',acquisition=false,actual_mode_readback=r('CrossoverBehaviorVersion'),family=C.family,hard=C.hard,cases=records,updates=updates,nmis=nmis,minSP=minSP,apuWrites_includingDMAController=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,source_owners=C.hooks}));f:close();emu.stop(0)"
 assert event_tail.count(old)==1;event_tail=event_tail.replace(old,new).replace("wall<9000,'Bounded progressive fixture '","wall<22000,'Bounded controlled Bass gallery '")
 capture=(ROOT/'tools/audit/final_item_abilities_pit731_ppu_v1.lua').read_text()
 inputs="emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput(galleryInput(),0)end end,emu.eventType.inputPolled)\n"
 return 'FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+(ROOT/'tools/audit/final_item_abilities_failure.lua').read_text()+'\n'+prefix+core+'\n'+mechanics+'\n'+guards+inputs+capture+'\n'+event_tail+'\nFINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS()\n',guards

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args()
 assert not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True,exist_ok=False)
 parent=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq';rom=parent/'candidate.nes';assert sha(rom)==CURRENT;b=scoped_load(rom)
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 files=set();source=parent/'source'
 for rel,h in json.loads((parent/'source-manifest.json').read_text()).items():f=source/rel;assert sha(f)==h;files.add(f)
 files.update([parent/'source-manifest.json',D/'mm-proto-clean-menu-candidates-v1/freeze-v1/receipt.json'])
 for file in ['inventory.s','inventory_data.inc','special_weapons.s','expanded_weapons.s','expanded.s','entrypoint.s','guest_body_contact.s','megaman_super_arm.s']:
  assert (source/'src'/file).is_file()
 hooks={}
 names=['GameLoop','NonMaskableInterrupt','IrqScrollSplit','RosterOamReady','InventorySelectionCommit','InventorySpend','InventoryCycle','SpecialWeapons','SpecialWeapons::Spawn','SpecialWeapons::MegaAttack','ExpandedWeapons::FireShot','MegaManWeapons::DamageEnemy','MegaKickBodyDamage','SpecialDrawShots::Coordinates','SpecialDrawWaterShot','ExpandedWeaponPointer']
 for n in names:
  pos=location(b,n);hooks[n]=dict(address=address(b,n),physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+3]))
 for key,n in [('finish','GameLoop'),('NmiReturn','NonMaskableInterrupt')]:
  delta=int(b['syms'][n]['size'],0)-1;pos=location(b,n)+delta;assert b['raw'][pos]in[0x60,0x40];hooks[key]=dict(address=address(b,n)+delta,physical_bank=(pos-16)//8192,bytes=[b['raw'][pos]])
 pos=location(b,'IrqScrollSplit');irq=[address(b,'IrqScrollSplit')+i for i in range(int(b['syms']['IrqScrollSplit']['size'],0)-2)if b['raw'][pos+i:pos+i+3]==b'\x8d\x05\x20']
 specs=[('BUSTER',0,4,31,0),('ARM',1,9,42,8),('METAL',2,10,43,4),('KNUCKLE',3,11,44,8),('PHARAOH',4,14,47,12),('KICK',5,19,52,4),('FLAME',6,16,49,4),('WATER',7,17,50,16)]
 plans=[]
 for word,item,t,damage,initial in specs:
  idx=144+item;ptr=b['raw'][location(b,'InvNameLo')+idx]+256*b['raw'][location(b,'InvNameHi')+idx];g=b['segs'][b['syms']['InvNameLo']['seg']];off=int(g['ooffs'],0)+ptr-int(g['start'],0)
  for face in [1,2]:
   plans.append(dict(name=f'{word.lower()}-face{face}',word=word,item=item,face=face,contact_type=t,damage_type=damage,initial_stock=initial,source_cost=b['raw'][location(b,'InvCosts')+idx],hud_name=list(b['raw'][off:off+7]),icon_bank=b['raw'][location(b,'InvHudPhysicalBanks')+item-1]if item else None,subphases=['actual Select cycle and committed HUD/icon','funded actual native input/effect/contact','natural cleanup and exact seeded-stock exhaustion','exhausted source refusal (default remains free)','controlled complete10-record pool policy','actual Select-owned cleanup'],acquisition=False))
 assert len(plans)==16 and b['raw'][location(b,'InvItemCount')+9]==8
 def record(ptr,bank):
  off=16+bank*8192+ptr%8192;n=b['raw'][off];assert n%4==0 and n<=252
  return dict(address=ptr,bank=bank,bytes=list(b['raw'][off:off+1+n]))
 def named_record(n):return record(address(b,n),(location(b,n)-16)//8192)
 effects=[]
 for i in range(address(b,'SsArtRightHi')-address(b,'SsArtRightLo')):
  row=[]
  for side in ['Right','Left']:
   ptr=b['raw'][location(b,'SsArt'+side+'Lo')+i]+256*b['raw'][location(b,'SsArt'+side+'Hi')+i]
   row.append(record(ptr,b['raw'][location(b,'SsArtBanks')+i]&127))
  effects.append(row)
 put(a.output/'plans.json',plans)
 cpu=compiled_cpu(b);put(a.output/'assembled-cpu-controls.json',dict(passed=True,cases=len(cpu),rows=cpu,scope='Actual assembled finite isolated routine returns; not controller/native timing/contact/visibility evidence.'))
 oldmodule=(ROOT/'tools/audit/final_item_abilities_native.lua').read_text();core=(ROOT/'tools/audit/final_item_abilities_static_return_v1.lua').read_text()
 return_controls=core_tests(LuaRuntime,old_core(oldmodule),core);dma_controls=dma_mocks(LuaRuntime,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=protocol(b)))
 profiles=[]
 for mode in [0,1]:
  name='bass-'+('hard'if mode else'easy');out=a.output/'profiles'/name/'native';out.mkdir(parents=True)
  for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(rom.with_suffix(ext),out/('candidate'+ext))
  arrays=['RgShotType','RgShotX','RgShotPage','RgShotY','RgShotYHigh','RgShotDir','RgShotAge','RgShotFracX','RgShotFracY','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotHits','RgShotImpact','XgShotAim']
  cfg=dict(family='bass',character=9,slot=9,hard=mode==1,mode_value=mode,cases=plans,ram={},hooks=hooks,shot_arrays=arrays,effect_records=effects,native_brick=named_record('SsNativeBrick'),native_chunk=named_record('SsNativeChunk'),buster_record=named_record('XgBASSWeapon0Right'),irq_scroll_stores=irq,special_ram_bytes=address(b,'SpecialRamEnd')-address(b,'SpecialRamStart'),dma_protocol=protocol(b),art={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
  probe,_=compose(cfg);used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",probe));used.update(arrays+['Sprite_Data','SpecialRamStart'])
  cfg['ram']={n:address(b,n)for n in used if n in b['syms']};script,guards=compose(cfg)
  direct=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",script));assert not direct-set(cfg['ram']),direct-set(cfg['ram'])
  assert "w('InvSelected'"not in script and "w('CrossoverBehaviorVersion'"not in script
  put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');(out/'inherited-NMI-stack-APU-guards.lua').write_text(guards,encoding='utf-8')
  from parodius_visibility_hud_static_startup_v1 import MOCK
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end');rt.execute(script)
  n=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')and rt.eval('#events[emu.eventType.endFrame]')==2
  rt.execute('emu.addMemoryCallback=function()error("Runtime registration forbidden")end;emu.removeMemoryCallback=function()error("Runtime removal forbidden")end')
  for frame in [1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
  assert rt.eval('#callbacks')==n
  profiles.append(dict(profile=name,mode_value=mode,plans=16,output=str(out),script_sha256=sha(out/'run.lua'),callbacks=n,maximum_launches=1,compiled_hook_count=len(hooks),original_NMI_stack_bank_5SMC_APU_guards_sha256=sha(out/'inherited-NMI-stack-APU-guards.lua')))
 runtime=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator';isolated=a.output/'emulator';isolated.mkdir()
 for f in runtime.iterdir():
  if f.is_file():shutil.copy2(f,isolated/f.name);files.add(f)
 worker=runtime/'settings.json';user=Path('C:/Mesen2/settings.json');s=json.loads(worker.read_bytes().decode('utf-8-sig'))
 for k,v in dict(RemoveSpriteLimit=False,AdaptiveSpriteLimit=False,RandomizeCpuPpuAlignment=False,RandomizeMapperPowerOnState=False,PpuExtraScanlinesBeforeNmi=0,PpuExtraScanlinesAfterNmi=0,DisableSprites=False,DisableBackground=False).items():assert s['Nes'][k]==v
 assert s['Emulation']['RunAheadFrames']==0 and s['Emulation']['EmulationSpeed']==100
 env=dict(emulator=str(isolated/'Mesen.exe'),emulator_sha256=sha(isolated/'Mesen.exe'),core_sha256=sha(isolated/'MesenCore.dll'),worker_settings_sha256=sha(worker),user_context_sha256=sha(user),Nes=s['Nes'],Emulation=s['Emulation'],actual_command_overrides=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
 put(a.output/'environment.json',env);files.add(user)
 limits=['B-only; tier1/allsevenowned255 and per-componentammo are explicit seeds, not pickup/reveal/rise/transform/acquisition.','Actual controller selection required percase, no InvSelected/mode/outcome writes. Complete controlled pool actors/relative fallingGoomba contacts are seeded at native GameLoop boundaries.','BALANCE8 passive, other items/refills/star/1up/otherforms/othercharacters not in16plans.','FullPPU/actual256DMA/rawactual2004/startFrame/casecaptures retained. Pixel/fairness/audio/native results not proven by source preparation.','Full-pool sourcepolicy: WATER pays16 even withzero free slots; KICK pays4 for bodyattack withnoeffectslot. ARM checks slot before free lift. No invented universal refund rule.','No native launches/grant from preparation. Runtime accuracy flags retained; no physical-console fidelity/60Hz/campaign claim.']
 seed=dict(lane='B',acquisition=False,boundary='Real GameLoop entry after cold selection, OperMode1/task3/engine8',initial=['PlayerStatus1','InvOwnedLo[9]255 / Hi0 (default+seven specials, BALANCE absent)'],per_component=['Complete logical/visible arena, floor, player motion/fractions/facing, protection/empty prior pools/SpecialRam reset','Stock exact sourcecost (Pharaoh12=4initial+8release),112 forfullpoolstress; exhaustedstock is earned in funded stage and NOT refilled inempty stage','ARM51realfrontblock; complete10METALrecords forfullpool; one controlled fallingGoomba aligned to actual emitted effect (KICK body), no defender result write'],native_required=['all selection changes','actual input dispatch/spawn/effect/art','actual costs/refusals/charge/slide/orbit/expansion','actual damage/cleanup'],forbidden=['raw selection/mode writes','damage/outcome writes','claiming seeded acquisition'])
 put(a.output/'seed-policy.json',seed);put(a.output/'source-controls.json',dict(passed=True,native_run=False,Lua='5.4',assembled_CPU_cases=len(cpu),return_controls=return_controls,DMA_controls=dma_controls,profiles=profiles,limits=limits))
 commands={q['profile']:'python -B tools/audit/final_inventory_bass731_run_v1.py --ready "'+a.output.as_posix()+'" --profile '+q['profile']+' --native-grant'for q in profiles};put(a.output/'commands.json',commands)
 files.update(p for p in a.output.rglob('*')if p.is_file())
 roots=[Path(__file__),ROOT/'tools/audit/final_inventory_bass731_run_v1.py'];seen=set()
 while roots:
  f=roots.pop()
  if f in seen:continue
  seen.add(f);files.add(f)
  for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   mods=[node.module]if isinstance(node,ast.ImportFrom)else[q.name for q in node.names]if isinstance(node,ast.Import)else[]
   for n in mods:
    if n:
     dep=ROOT/'tools/audit'/(n.split('.')[0]+'.py')
     if dep.is_file():roots.append(dep)
 for n in ['final_inventory_bass731_native_v1.lua','final_item_matrix_progressive.lua','final_item_abilities_native.lua','final_item_abilities_static_return_v1.lua','final_item_abilities_dma731_v1.lua','final_item_abilities_pit731_ppu_v1.lua','final_item_abilities_failure.lua']:files.add(ROOT/'tools/audit'/n)
 old=D/'native-probes-qa-v2/legacy-native-items-batch-v2/bass';files.update([old/'run.lua',old/'build/verification/native-legacy-items.json',D/'native-probes-qa-v2/legacy-physical-summary-v1/proof.json',Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__)])
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]))
 z=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=CURRENT,profiles=profiles,plans=32,maximum_owned_workers=1,maximum_launches_per_profile=1,automatic_next_profile=False,retries=False,source_controls_sha256=sha(a.output/'source-controls.json'),manifest_sha256=sha(a.output/'manifest.json'),manifest_bindings=len(files),environment=env,commands=commands,limits=limits)
 put(a.output/'proof.json',z)
 for q in json.loads((a.output/'manifest.json').read_text())['bindings']:assert sha(q['path'])==q['sha256']
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),CPU_cases=len(cpu),commands=commands),indent=2))

if __name__=='__main__':main()
