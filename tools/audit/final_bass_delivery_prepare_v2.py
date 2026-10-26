"""Prepare ONE current3b BassEasy four-reward physical profile. Never runs Mesen."""
from pathlib import Path
import argparse,ast,hashlib,json,re,shutil,sys
from final_item_abilities_static_prepare_v2 import ROOT,D
from final_item_abilities_run import lua
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_current731_prepare_v1 import protocol,dma_mocks
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
from parodius_visibility_hud_static_startup_v1 import MOCK

SHA='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def cpu_controls(b):
 rows=[]
 # Actual reveal owner, no synthetic random substitution inside native tests.
 # These CPU cases explicitly control PRNG/history to exercise the source rules.
 for mode in [0,1]:
  for power,lo,hi,view,viewhi,tag in [(0,0,0,0,0,'mushroom'),(1,1,0,0,0,'initial-seven'),(1,9,0,0,0,'owned-knuckle-excluded'),(1,247,1,255,1,'missed-knuckle-next-pass'),(1,255,1,255,1,'complete-refill')]:
   for roll in range(16):
    q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=power)
    for n,v in [('InvOwnedLo',lo),('InvOwnedHi',hi),('InvViewedLo',view),('InvViewedHi',viewhi)]:q.set(n,v,9)
    q.set('PowerUpType',0,5);q.set('PseudoRandomBitReg',roll,1)
    q.invoke('InventoryPreparePickup',x=5);item=q.get('InvPickup',5)
    if tag=='mushroom':assert item==0
    elif tag=='missed-knuckle-next-pass':assert item==3
    elif tag=='complete-refill':assert item==254
    else:
     assert 1<=item<=8 and not((lo+hi*256)&(1<<item))
     if tag=='initial-seven':assert item!=8
    assert q.get('InvOwnedLo',9)==lo and q.get('InvOwnedHi',9)==hi
    rows.append(dict(mode=mode,kind=tag,roll=roll,item=item,source='complete InventoryPreparePickup; isolated CPU controlled PRNG/history'))
  # Passive is selectable in neither mode. Tie goes to lower local ID.
  for balance,selected,stocks,amount in [(0,0,[40,4],8),(1,0,[40,4],8),(1,1,[40,4],8),(1,1,[112,4],40),(1,0,[4,4],8),(1,0,[112,112],40),(1,0,[108,112],40)]:
   q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode)
   q.set('InvOwnedLo',7,9);q.set('InvOwnedHi',balance,9);q.set('InvSelected',selected,9)
   q.set('InvAmmo',stocks[0],145);q.set('InvAmmo',stocks[1],146)
   q.invoke('InventoryRefillAmount',a=amount)
   target=145 if selected==1 and stocks[0]<112 else (145 if stocks[0]<=stocks[1] else 146) if balance and min(stocks)<112 else 0
   assert q.get('InvRefill')==target
   ticks=[]
   for i in range(3*(amount//4)+1):
    before=[q.get('InvAmmo',145),q.get('InvAmmo',146)];q.invoke('InventoryUiTick');after=[q.get('InvAmmo',145),q.get('InvAmmo',146)]
    if before!=after:
     assert target and after[target-145]==min(112,before[target-145]+4)
     ticks.append(dict(call=i+1,before=before,after=after))
   expected=list(stocks)
   if target:expected[target-145]=min(112,expected[target-145]+amount)
   assert [q.get('InvAmmo',145),q.get('InvAmmo',146)]==expected and q.get('InvRefill')==0
   rows.append(dict(mode=mode,kind='BALANCE-route-and-full-UiTick',passive_owned=balance,selected=selected,before=stocks,amount=amount,target=target,after=expected,ticks=ticks))
  q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode);q.set('InvOwnedLo',7,9);q.set('InvOwnedHi',1,9)
  got=[]
  for want in [1,2,0,1]:q.invoke('InventoryCycle');got.append(q.get('InvSelected',9));assert got[-1]==want
  rows.append(dict(mode=mode,kind='passive-selection-skip',actual=got))
 # Exact rise/freeze and the exposed top clipping, rather than a universal
 # claim that pickups cannot be collected before maturation from above.
 for timer in [0,2]:
  q=Arena(b,9);q.set('InvPickupOwner',9,5);q.set('InvPickup',2,5);q.set('Enemy_State',1,5);q.set('Enemy_Y_Position',152,5);q.put(TimerControl=timer)
  for _ in range(48):q.invoke('InventoryRisePickup',x=5)
  assert(q.get('Enemy_Y_Position',5),q.get('Enemy_State',5))==((136,128)if not timer else(152,1))
  rows.append(dict(kind='private-native-rise',timer=timer,y=q.get('Enemy_Y_Position',5),state=q.get('Enemy_State',5),calls=48))
 for state in [1,2,8,16,128]:
  q=Arena(b,9);q.set('InvPickupOwner',9,5);q.set('InvPickup',2,5);q.set('Enemy_State',state,5);q.set('Enemy_Y_Position',152,5)
  c,_=q.invoke('InventoryPickupCollision',x=5);assert bool(c.p&1)==(state!=1)
  if 2<=state<128:assert q.get('EnemyBoundingBoxCoord',21)==160 and q.get('EnemyBoundingBoxCoord',23)==(152+state+6)%256
  rows.append(dict(kind='exposed-rise-collision',state=state,admitted=bool(c.p&1),scope='State1 hidden, later top only clipped; mature native box unchanged.'))
 # All actual grants retain old inventory and do not auto-equip Bass.
 for mode in [0,1]:
  for item in range(1,9):
   q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode);q.set('InvOwnedLo',1,9);q.invoke('InventoryGrant',a=item)
   assert q.get('InvOwnedLo',9)+256*q.get('InvOwnedHi',9)==1|(1<<item) and q.get('InvSelected',9)==0
   rows.append(dict(mode=mode,kind='actual-passive-or-weapon-grant',item=item,after=q.get('InvOwnedLo',9)+256*q.get('InvOwnedHi',9),selected=0))
  q=Arena(b,9);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=0);q.set('InvPickupOwner',9,5);q.set('InvPickup',0,5);q.invoke('InventoryCollect',x=5)
  assert q.get('InvOwnedLo',9)==1 and q.get('GuestPowerupActive')==1 and q.get('PlayerStatus')==0
  for i in range(60):
   assert q.get('GuestPowerupAge')==i;q.invoke('GuestPowerupUpdate')
  assert q.get('GuestPowerupActive')==0 and q.get('PlayerStatus')==1
  rows.append(dict(mode=mode,kind='actual-mushroom-collect-and-sixty-updates',status=1,owned=1))
 for item in range(1,9):
  mapped=9 if item==8 else item;art=b['raw'][location(b,'InventoryDrawPickups::UpgradeArt')+mapped]
  for actualart in [art,art+1]if item==8 else[art]:
   q=Arena(b,9);q.put(SsDrawFamily=255);c,_=q.invoke('SpecialPickupArt',a=actualart)
   ptr=b['raw'][location(b,'SsArtRightLo')+actualart]+256*b['raw'][location(b,'SsArtRightHi')+actualart];bn=b['raw'][location(b,'SsArtBanks')+actualart]&127
   assert c.p&1 and q.get('R0')+256*q.get('R1')==ptr and q.m.banks[2]==bn
   off=16+bn*8192+ptr%8192;n=b['raw'][off];record=b['raw'][off:off+1+n]
   rows.append(dict(kind='actual-unique-pickup-pointer',item=item,art=actualart,address=ptr,bank=bn,record_sha256=hashlib.sha256(record).hexdigest()))
 return rows

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--lua-root',required=True,type=Path);a=p.parse_args();assert not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True,exist_ok=False)
 old=D/'current3b112-bass-semantic-cleanup-ready-v1';verify_manifest(old/'manifest.json');op=json.loads((old/'proof.json').read_text());assert op['ROM_sha256']==SHA
 source=D/'root-current-roster-composition-v1';assert sha(source/'candidate.nes')==SHA;b=scoped_load(source/'candidate.nes')
 oldout=old/'profiles/bass-easy/native';cfg=json.loads((oldout/'config.json').read_text());oldscript=(oldout/'run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n';assert oldscript.startswith(prefix);body=oldscript[len(prefix):]
 start=body.index('-- Controlled B-only gallery.');end=body.index('local saved=nil',start);module=ROOT/'tools/audit/final_bass_delivery_native_v2.lua';newmodule=module.read_text()
 pre=body[:start];tail=body[end:]
 # Retain the exact E008, physical OAM, CHR, NMI, IRQ and five-SMC layer.
 assert (oldout/'inherited-NMI-stack-APU-guards.lua').read_text()in tail
 forbidden="assert(not(n=='PlayerStatus' or n:match('^Inv') or n:match('^AvPickup') or n=='PowerUpType' or n=='PseudoRandomBitReg' or n:match('^GuestPowerup')),'No acquisition/result/resource/RNG seed');"
 before="assert(writeBoundary,'Fixture writes only at native GameLoop entry');"
 assert pre.count(before)==1;pre=pre.replace(before,before+forbidden)
 # Fix the inherited legacy serializer for future files only. Old raw outputs
 # remain unchanged; this avoids malformed integer object keys in new reports.
 before="string.format('%q',k)..':'..json(x)";assert pre.count(before)==1;pre=pre.replace(before,"string.format('%q',tostring(k))..':'..json(x)")
 before='emu.setInput(galleryInput(),0)';assert tail.count(before)==1;tail=tail.replace(before,'emu.setInput(deliveryInput(),0)')
 tail=tail.replace("OUTPUT..'native-bass-gallery.json'","OUTPUT..'native-bass-delivery.json'").replace("lane='B controlled use only',acquisition=false","lane='A physical-delivery component; post-rise contact alignment disclosed',acquisition=true").replace("wall<22000,'Bounded controlled Bass gallery '","wall<6000,'Bounded four-reward Bass delivery '")
 assert "native-bass-delivery.json"in tail and 'wall<6000'in tail
 cfg.update(cases=[dict(reward=1,expected='native mushroom'),dict(reward=2,expected='native eligible upgrade'),dict(reward=3,expected='native new eligible upgrade'),dict(reward=4,expected='native new eligible upgrade')],family='bass',hard=False,mode_value=0,ROM_sha256=SHA,use_types=[4,9,10,11,12,19,16,17])
 for n in ['InventoryPreparePickup','InventoryRisePickup','InventoryCollect','InventoryGrant','GuestBeginPowerup','GuestPowerupUpdate','SpecialPickupArt']:
  off=location(b,n);cfg['hooks'][n]=dict(address=address(b,n),physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]))
 cfg['pickup_art']={};cfg['pickup_records']=[]
 for item in range(1,9):
  mapped=9 if item==8 else item;art=b['raw'][location(b,'InventoryDrawPickups::UpgradeArt')+mapped];cfg['pickup_art'][item]=[art,art+1 if item==8 else art]
 size=address(b,'SsArtRightHi')-address(b,'SsArtRightLo')
 for i in range(size):
  ptr=b['raw'][location(b,'SsArtRightLo')+i]+256*b['raw'][location(b,'SsArtRightHi')+i];bn=b['raw'][location(b,'SsArtBanks')+i]&127;off=16+bn*8192+ptr%8192;n=b['raw'][off];assert n%4==0 and n<=252
  cfg['pickup_records'].append(dict(address=ptr,bank=bn,bytes=list(b['raw'][off:off+n+1])))
 scriptbody=pre+newmodule+'\n'+tail
 names=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",scriptbody));cfg['ram'].update({n:address(b,n)for n in names});cfg['ram']['PseudoRandomBitReg']=address(b,'PseudoRandomBitReg')
 script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+scriptbody;out=a.output/'native';out.mkdir()
 for ext in['.nes','.dbg','.lbl','.map']:shutil.copy2(source/('candidate'+ext),out/('candidate'+ext))
 put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');shutil.copy2(oldout/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua')
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end')
 negative="\nwriteBoundary=true;for _,n in ipairs({'PlayerStatus','InvOwnedLo','InvAmmo','InvPickup','PowerUpType','PseudoRandomBitReg','GuestPowerupActive'})do local ok,err=pcall(function()w(n,1)end);assert(not ok and tostring(err):find('No acquisition/result/resource/RNG seed',1,true),'Exact forbidden-write guard owns rejection')end;writeBoundary=false"
 rt.execute(script+negative)
 count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')and rt.eval('#events[emu.eventType.endFrame]')==3
 rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 # Negative calls above share the script's actual lexical write guard. They
 # reject its exact message, rather than accidentally passing on a nil global.
 rows=cpu_controls(b);put(a.output/'compiled-controls.json',dict(passed=True,native_run=False,ROM_sha256=SHA,cases=len(rows),rows=rows))
 dma=dma_mocks(LuaRuntime,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=protocol(b)))
 controls=dict(passed=True,native_run=False,static_callbacks=count,dispatcher_last=True,endFrame_callbacks=3,original_strict_module_sha256=sha(out/'inherited-NMI-stack-APU-guards.lua'),all_nonmechanics_tail_changes=['galleryInput->deliveryInput','output filename/acquisition scope','finite6000wall cap'],cold_menu_input_policy_literal=True,hardware_protocol=cfg['dma_protocol'],DMA_models=dma,compiled_cases=len(rows),forbidden_outcome_write_negatives=7,legacy_newfile_json_key_fix=True)
 put(a.output/'source-controls.json',controls)
 policy=dict(profile='bass-easy-four-rewards',maximum_rewards=4,actual_mode_required=0,acquisition='Cold inventory/tier with native mushroom then3actual PRNG-chosen upgrades; no inventory/ammo/pickup/result/RNG seeds.',staging='Existing qualified logical/visible world floor/question-block+playerposition/velocity/collision/scroll/protection/oldactor reset at native GameLoop entry. No tier/result writes. Native A head hit owns reward creation.',contact='Exactly the existing actual actor is aligned to player only after full native emergence+110updates, at GameLoop boundary; not an unassisted route. No spawned/mature-actor shortcut.',under_block='No premature grant in this under-block jump geometry. Source top-exposed rise contact can legitimately collect from above; not a universal before-maturity refusal claim.',transform='Mushroom60committed GuestPowerup updates0to1, upgrades grant ownership without invented tier2; controls through actual acquired Select/B or Down+A plus cost/effect/naturalcleanup.',BALANCE='May be chosen by unchanged native PRNG after first acquired weapon, never forced or guaranteed. Passive availability/selection/refill are CPU-qualified separately; native physical BALANCE/refill remain pending if not actually encountered.',not_in_first_four=['full eight-item pool/fallback/recovery flower','missed world duplicate/copy lifetimes','all unique icon pixels/bothmodes/allfacing use','native BALANCE least-energy refill/8and40/caps/ties unless separately tested','star/1up/injury/death/campaign/sourceaudiofidelity'])
 put(a.output/'seed-policy.json',policy)
 # Reuse the already isolated portable worker without modifying any settings.
 env=json.loads((old/'environment.json').read_text());assert sha(Path(env['emulator']))==env['emulator_sha256'];assert sha(Path(env['emulator']).parent/'settings.json')==env['worker_settings_sha256'];env['user_context_sha256']=sha(Path('C:/Mesen2/settings.json'));put(a.output/'environment.json',env)
 report=ROOT/'docs/qa/final-bass-delivery-source-2026-10-26.txt'
 report.write_text('Current3b Bass physical-delivery first profile - SOURCE ONLY\n\nOne Easy0 cold profile: actual mushroom then three native eligible unique upgrades, max4rewards. No RNG/tier/inventory/ammo/pickup/result seed. Explicit staged visible/logical block and scene; actual A reveal, native full rise, existing post-rise contact alignment, mushroom60update transform, source ownership/Select/use/cost/effect/cleanup. This is a bounded physical delivery component, not an unassisted route or all-item certificate.\n\nBALANCE8 is a passive replacement eligible only after a weapon, excluded from Select and zero-ammo. Source refills selected nonfull first, else least owned energy when BALANCE present; lower index wins ties, +4every3UI calls,112cap,8/40amounts. It cannot be guaranteed within four untouched-RNG deliveries. Native BALANCE physical/refill remains a separate gap unless actually encountered; CPU state controls are not acquisition evidence.\n\nPinned2.02 Bass/StatManager/MegaManBase establish seven obtainable weapons, mushroom no weapon, passive replacement, owned/viewed distinction and full-pool big-energy fallback. Two uncollected identical actors can coexist across reveal passes; already-owned new rolls must exclude duplicates. Early emerging pickup top may be legitimately exposed; only the under-block fixture asserts no premature grant. World source icons/bottom pivot/animated BALANCE are bound to compiled records; actual whole PPU pixel review remains native-pending. Current art includes NES palette adaptation, no new art/sourceword changes.\n\nExactROM '+SHA+'\nPrepared '+str(a.output)+'\nCompiled CPU cases '+str(len(rows))+'; startup callbacks '+str(count)+' /static dispatcher last; old strict NMI/CHR/APU/IRQ/5SMC/stack module exact. Draftv1 is retained; v2 corrects the passive controller to exercise a full real Select cycle before calling BALANCE skipped. No native granted/run. No production/default/settings/Git edits.\n',encoding='utf-8')
 files={Path(__file__),module,report,old/'proof.json',old/'manifest.json',source/'ROOT-source-readiness.json',source/'source-manifest.json',source/'ROOT-bindings.json',Path('C:/Mesen2/settings.json')}
 files.update(source/'source'/r for r in json.loads((source/'source-manifest.json').read_text()))
 files.update(f for f in Path(env['emulator']).parent.iterdir()if f.is_file())
 refs=['characters/Bass.as','characters/base/MegaManBase.as','managers/StatManager.as','pickups/Pickup.as','pickups/MegaManPickup.as']
 files.update(ROOT/'reference/crossover2/extracted/scripts/com/smbc'/r for r in refs)
 files.update(ROOT/'tests'/n for n in['bass-inventory.lua','bass-pickup-contact.lua','bass-pickup-rise.lua','bass-upgrade-random.lua','bass-energy-drops.lua','bass-pickup-art.lua'])
 pending=[Path(__file__),ROOT/'tools/audit/final_bass_delivery_run_v1.py'];seen=set()
 while pending:
  f=pending.pop()
  if f in seen:continue
  seen.add(f);files.add(f)
  for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   mods=[node.module]if isinstance(node,ast.ImportFrom)else[q.name for q in node.names]if isinstance(node,ast.Import)else[]
   for n in mods:
    if n:
     dep=ROOT/'tools/audit'/(n.split('.')[0]+'.py')
     if dep.is_file():pending.append(dep)
 files.update([Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__),ROOT/'tools/audit/final_item_abilities_dma731_v1.lua'])
 files.update(f for f in a.output.rglob('*')if f.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]))
 command='python -B tools/audit/final_bass_delivery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant'
 put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='bass-easy-four-rewards',mode_value=0,maximum_rewards=4,maximum_launches=1,maximum_owned_workers=1,retry=False,source_controls_sha256=sha(a.output/'source-controls.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),output=str(out),script_sha256=sha(out/'run.lua'),source_freeze_sha256=sha(source/'ROOT-source-readiness.json'),stable_command=command,environment=env,scope=policy))
 verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),script_sha256=sha(out/'run.lua'),compiled_cases=len(rows),stable_command=command),indent=2))

if __name__=='__main__':main()
