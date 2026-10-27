"""Prepare one powered Mega/Proto body profile on frozenf1dd or2082+OAM; never launch.

Only one fixture, one readiness directory and source-bound metadata. No ROM,
source/runtime clone, new controller framework or resource/result seed.
"""
from pathlib import Path
import argparse,hashlib,json,re,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from robots_weapon_cpu_v1 import Arena
from current_roster_compact_11_v1 import lua,navigation

R=Path(__file__).resolve().parents[2]
EXPECTED='f1dd0c2390d4f27c373797b695e44b56b94cd12c74d47c2a14d36bc8f34f470f'
COMPOSED='3e7c53d82eb949b8527d837861d95ed6051966056ca3f336fafd66e514e055ea'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n')

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--rom',type=Path,default=R/'build/mm_body_reserve.nes')
 ap.add_argument('--expected-sha256',default=EXPECTED)
 ap.add_argument('--identity',choices=['megaman','proto'],default='megaman')
 ap.add_argument('--profile',choices=['powered','dense'],default='powered')
 ap.add_argument('--output',type=Path,required=True)
 ap.add_argument('--refresh-unrun',action='store_true')
 a=ap.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve()
 expected=a.expected_sha256;assert expected in {EXPECTED,COMPOSED}and sha(a.rom)==expected
 composition=R/'build/mm_body_current_result.json'
 if expected==COMPOSED:
  receipt=json.loads(composition.read_text());assert receipt['passed']and receipt['literal_disjoint_union']and receipt['candidate_sha256']==expected and receipt['parent_sha256']=='2082c19a7364920f828e97f70040d37f1f7059bde1ea136b5c2c4532324abf36'
 assert a.output.is_relative_to(R/'build')and a.output!=R/'build'
 if a.output.exists():
  previous=json.loads((a.output/'ready.json').read_text())
  assert a.refresh_unrun and previous['prepared']and not previous['native_run']and previous['identity']==a.identity and previous.get('profile','powered')==a.profile and previous['ROM_sha256']==expected and not(a.output/'native').exists(),'Never overwrite native/bound/different-identity evidence'
 b=scoped_load(a.rom);raw=b['raw'];variant=int(a.identity=='proto')
 if a.profile=='dense':assert expected==COMPOSED and variant==1,'One finite crowded Proto profile only'
 fixture=R/'tests/current-mega-body-components.lua';text=fixture.read_text()
 parent=R/'tests/current-inventory-powerups.lua';original=parent.read_text()
 guard_begin='-- All callback registration is startup-static.'
 guard_end='emu.addEventCallback(function()\n if not entered then emu.setInput(menu(),0);return end'
 inherited=original[original.index(guard_begin):original.index(guard_end,original.index(guard_begin))]
 assert inherited in text,'Existing full256/E008/NMI/IRQ/CHR guard code copied byte-exact, no weakening'
 def byte(n,i=0):return raw[location(b,n)+i]
 def hook(n,delta=0,count=3):
  at=location(b,n)+delta;bank=(at-16)//8192;bs=list(raw[at:at+count]);banks=[bank]
  if bank==127:
   off=(at-16)%8192
   assert raw[16+125*8192+off:16+125*8192+off+count]==bytes(bs)
   banks=[125,127]
  return dict(pc=address(b,n)+delta,banks=banks,bytes=bs,symbol=n,delta=delta)
 hooks={key:hook(n)for key,n in dict(PhysicalPickup='MarioSourcePowerupCollision',InventoryCollect='InventoryCollect',InventoryGrant='InventoryGrant',GuestPowerupUpdate='GuestPowerupUpdate',PrimarySpawn='MegaManWeapons::Spawn',RushAttack='MegaManRushAttack',RushBounce='MegaManRushBounce',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
 at=location(b,'GameLoop');nd=address(b,'NmiDisable')
 assert raw[at:at+5]==bytes([0xa9,255,0x8d,nd&255,nd>>8])
 hooks['GameLoopOwned']=hook('GameLoop',5)
 for key,n,op in [('GameLoopFinish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40)]:
  d=int(b['syms'][n]['size'],0)-1;assert byte(n,d)==op;hooks[key]=hook(n,d,1)
 post=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK')
 load=bytes([0xa5,mirror])if mirror<256 else bytes([0xad,mirror&255,mirror>>8])
 assert raw[post-3:post]==b'\x8d\x14\x40'and raw[post:post+len(load)+3]==load+b'\x8d\x01\x20'
 hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load));assert hooks['DmaComplete']['pc']==0xe008
 if a.profile=='dense':
  for key,n in dict(DenseDraw='DrawAllMetasprites',DenseShotsFinished='MmReserveFinish',DenseObject='DrawMetasprite',DenseHeader='MetaspriteHeaderValid',DenseLoopEnd='MetaspriteRenderLoop::LoopEnded',DensePublish='RosterOamReady',DenseVineEntry='MmReserveVine').items():hooks[key]=hook(n)
  pos=location(b,'MmReserveVine');size=int(b['syms']['MmReserveVine']['size'],0)
  assert raw[pos]==0x20 and raw[pos+1]+256*raw[pos+2]==address(b,'MmReservePartial')
  assert raw[pos+size-3:pos+size]==bytes([0x60,0,0x30]),'Genuine Vine return before its two-byte data table'
  hooks['DenseVineAdmitted']=hook('MmReserveVine',3);hooks['DenseVineReturn']=hook('MmReserveVine',size-3,1)
 # Exact current ownership/item data, not copied Bass indices.
 owner=address(b,'CHARACTER_MEGAMAN');assert owner==1
 at=location(b,'X5MenuCharacters');menu=list(raw[at:at+19]);assert menu.count(owner)==1;slot=menu.index(owner)
 assert byte('InvItemCount',owner)==10
 assert byte('InvAmmoIndex',owner*16+8)==24 and byte('InvSelectable',owner*16+8)==1
 assert byte('InvSelectable',owner*16+9)==0 and byte('InvSelectable',owner*16+10)==0
 assert byte('InvMushroomHi',owner)==4
 assert byte('InvInitialAmmo',24)==byte('InvMaxAmmo',24)==112 and byte('InvCosts',24)==12
 # Literal original current charge/summon/bounce contracts are bound to
 # emitted instructions. RushFly is exit, never a playable Jet assertion.
 weapon=raw[location(b,'MegaManWeapons'):location(b,'MegaManWeapons')+int(b['syms']['MegaManWeapons']['size'],0)]
 assert b'\xc9\x30'in weapon and b'\xc9\x57'in weapon and b'\xc0\x57'in weapon
 rush=raw[location(b,'MegaManRushAttack'):location(b,'MegaManRushAttack')+int(b['syms']['MegaManRushAttack']['size'],0)]
 bounce=raw[location(b,'MegaManRushBounce'):location(b,'MegaManRushBounce')+int(b['syms']['MegaManRushBounce']['size'],0)]
 assert b'\xc9\x04'in rush and b'\xe9\x0c'in bounce
 setup=['Block_Buffer_1','MmSolidTerrain','MmBrickHealth','Enemy_Flag','Enemy_CollisionBits','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum','MmVX','MmVY','MmXFraction','MmYFraction','ScrollLock','ScreenLeft_X_Pos','ScreenLeft_PageLoc','ScreenRight_X_Pos','ScreenRight_PageLoc','Player_X_Position','Player_PageLoc','MmOldX','Player_Y_Position','Player_Y_HighPos','Player_State','PlayerFacingDir','Player_MovingDir','Player_CollisionBits','Enemy_ID','Enemy_State','Enemy_BoundBoxCtrl','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_SprAttrib','PowerUpType','InvPickupOwner','InvPickup','AvPickupAmmoItem','Enemy_Y_MoveForce','Enemy_MovingDir','EnemyOffscrBitsMasked','MmFrictionYActive']
 if a.profile=='dense':setup+=['Vine_FlagOffset','Vine_ObjOffset','Vine_Start_Y_Position','Vine_Height']
 forbidden=['InvOwnedLo','InvOwnedHi','InvViewedLo','InvViewedHi','InvSelected','InvAmmo','PlayerStatus','GuestPowerupActive','MmChargeFrames','MmCharging','MmBulletType','RgShotType','SsMode','MmRushLandRequest','GameEngineSubroutine','InjuryTimer','MmDeathFlag','CheatInvincible']
 assert not set(setup)&set(forbidden)
 assert not set(re.findall(r"\bw\('([^']+)'",text))&set(forbidden)
 assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and 'dofile('not in text
 assert text.count('emu.takeScreenshot(')==1 and 'images<8'in text
 bare_ram=set(re.findall(r"\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)",text))
 names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|bare_ram|set(setup)|{'ProtoVariant','CurrentBank','CurrentBankC','Sprite0HitDetectFlag'}
 cfg=dict(identity=a.identity,profile=a.profile,ROM_sha256=expected,character=owner,slot=slot,variant_ram='ProtoVariant',variant=variant,mode=1,frame_limit=1800 if a.profile=='dense'else 16000,
  navigation=navigation(raw,lambda n:location(b,n),slot),hooks=hooks,ram={n:address(b,n)for n in names if n in b['syms']},setup_allowed={n:True for n in setup},
  charge=dict(weak=48,full=87,passive_item=10),rush=dict(item=8,ammo_index=24,initial_ammo=112,summon_gate=4,bounce_cost=12,playable_Jet=False),
  dma_store_return=address(b,'PostDmaMaskEnable'),metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},
  smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 if a.profile=='dense':cfg['dense']=dict(updates=180,frame_records=512,event_rows=6000,event_bytes=16000000,container_bytes=64*1024*1024,vine_id=address(b,'VineObject'),goomba_speed=byte('NormalXSpdData'))
 store=location(b,'MegaManWeapons::FoundSlot')+3;store_pc=address(b,'MegaManWeapons::FoundSlot')+3
 assert raw[store-3:store]==bytes([0xad,address(b,'MmTemp')&255,address(b,'MmTemp')>>8])
 assert raw[store:store+3]==bytes([0x9d,address(b,'MmBulletType')&255,address(b,'MmBulletType')>>8])
 cfg['primary_store']=dict(pc=store_pc,after=store_pc+3,bank=(store-16)//8192,bytes=list(raw[store:store+3]),source='Genuine FoundSlot LDA MmTemp then STA MmBulletType,X; distinguish native damage proxy/restoration writes.')
 for n in re.findall(r"\b[rw]\('([^']+)'",text):assert n in cfg['ram'],n
 for n in setup:assert n in cfg['ram'],n
 for n in bare_ram:assert n in cfg['ram']and isinstance(cfg['ram'][n],int)and 0<=cfg['ram'][n]<=0xffff,n
 # One finite configured-source grant sequence, not spatial/native evidence.
 q=Arena(b,owner,proto=variant);q.invoke('InventoryInit');q.put(PlayerStatus=0,OperMode_Task=3,CrossoverBehaviorVersion=1)
 source=[]
 before=q.get('InvAmmo',24)
 for item in ([0]if a.profile=='dense'else[0,8]):
  q.put(InvObject=5);q.set('InvPickupOwner',owner,5);q.set('InvPickup',item,5);c,_=q.invoke('InventoryCollect',x=5)
  assert c.p&1 and(q.get('InvOwnedLo',owner)+256*q.get('InvOwnedHi',owner))&(1<<item)
  if item==0:
   for _ in range(60):q.invoke('GuestPowerupUpdate')
   assert q.get('PlayerStatus')==1 and q.get('GuestPowerupActive')==0 and q.get('InvOwnedHi',owner)&4
  assert q.get('InvAmmo',24)==before
  source.append(dict(item=item,ownedLo=q.get('InvOwnedLo',owner),ownedHi=q.get('InvOwnedHi',owner),status=q.get('PlayerStatus'),stock=q.get('InvAmmo',24)))
 dense_controls=None
 if a.profile=='powered':
  q.invoke('InventoryCycle');assert q.get('InvSelected',owner)==8
  q.invoke('MegaManRushAttack');assert q.get('InvAmmo',24)==112 and 20 in[q.get('RgShotType',i)for i in range(10)]
  q.invoke('MegaManRushBounce');assert q.get('InvAmmo',24)==100
 else:
  q.put(PrimaryHardMode=0);q.invoke('InitGoomba',x=0)
  assert(q.get('Enemy_X_Speed',0),q.get('Enemy_BoundBoxCtrl',0),q.get('Enemy_MovingDir',0))==(cfg['dense']['goomba_speed'],9,2)
  q.put(Vine_FlagOffset=0,Vine_Height=0);q.set('Block_PageLoc',0,0);q.set('Block_X_Position',160,0);q.set('Block_Y_Position',208,0);q.invoke('Setup_Vine',x=5,y=0)
  assert(q.get('Enemy_ID',5),q.get('Enemy_Flag',5),q.get('Enemy_X_Position',5),q.get('Enemy_Y_Position',5),q.get('Vine_FlagOffset'),q.get('Vine_ObjOffset'),q.get('Vine_Start_Y_Position'))==(47,1,160,208,1,5,208)
  partial=[]
  for tag in [1,129]:
   for i in range(256):q.m[512+i]=0xaa
   q.put(CurrentOAMOffset=40,GuestOamRotationActive=tag,Enemy_Rel_XPos=160,Enemy_Rel_YPos=192,Vine_Start_Y_Position=208,ObjectOffset=5)
   q.invoke('MmReserveVine',y=0);after=q.get('CurrentOAMOffset');assert after==(68 if tag==129 else 64)
   if tag==129:assert bytes(q.m[512:556])==b'\xaa'*44
   partial.append(dict(tag=tag,before=40,after=after,reserved44_unchanged=bytes(q.m[512:556])==b'\xaa'*44))
  dense_controls=dict(actual_InitGoomba_firstquest=dict(speed=cfg['dense']['goomba_speed'],bbox=9,direction=2),actual_Setup_Vine=dict(id=47,slot=5,x=160,y=208,height=0),actual_Vine_partial=partial,native_run=False)
 observer=R/'tools/audit/mm_proto_body_reserve_passive_v1.lua';bodycfg=R/'build/mm_body_reserve_observer_config.lua';bodyjson=bodycfg.with_suffix('.json')
 body=json.loads(bodyjson.read_text());assert body['ROM_sha256']==EXPECTED
 body['ROM_sha256']=expected
 for name,h in body['hooks'].items():
  fresh=hook('PostDmaMaskEnable',len(load))if name=='dma_complete'else hook(h['name'])
  h.update(pc=fresh['pc'],bank=fresh['banks'][-1],bytes=fresh['bytes'])
 body['ram']={n:address(b,n)for n in body['ram']}
 assert body['hooks']['dma_complete']['pc']==0xe008
 for h in body['hooks'].values():
  start=16+h['bank']*8192+h['pc']%8192;assert list(raw[start:start+len(h['bytes'])])==h['bytes']
 a.output.mkdir(parents=True,exist_ok=True)
 put(a.output/'config.json',cfg)
 address_guard='for _,name in ipairs('+lua(sorted(bare_ram))+')do local a=CURRENT_MEGA_BODY_COMPONENTS.ram[name];assert(type(a)=="number"and a>=0 and a<=65535,"Missing callback RAM address: "..name)end\n'
 codec=R/'tools/audit/final_inventory_compact_capture_v1.lua'
 capture_prefix=('CURRENT_MEGA_DENSE_CAPTURE=dofile('+lua(codec.as_posix())+').install(OUTPUT,{container_bytes=67108864,records=512},function()return CURRENT_MEGA_DENSE_STAMP or{}end)\n')if a.profile=='dense'else''
 script='CURRENT_MEGA_BODY_COMPONENTS='+lua(cfg)+'\n'+address_guard+capture_prefix+'MM_BODY_OBSERVATION_CONFIG='+lua(body)+'\nMM_BODY_OBSERVATION_CONFIG.output=OUTPUT.."body-epochs.csv"\nMM_BODY_OBSERVATION_CONFIG.maximum_rows=40000\nMM_BODY_OBSERVATION_CONFIG.maximum_bytes=16000000\ndofile('+lua(observer.as_posix())+')\ndofile('+lua(fixture.as_posix())+')\n'
 (a.output/'run.lua').write_text(script)
 put(a.output/'source-controls.json',dict(passed=True,native_run=False,profile=a.profile,ROM_sha256=expected,actual_variant=variant,guard_block_byte_exact=True,guard_sha256=hashlib.sha256(inherited.encode()).hexdigest(),all_literal_RAM_bound=True,bare_callback_RAM={n:cfg['ram'][n]for n in sorted(bare_ram)},callback_addresses_checked_before_any_fixture_load=True,body_observer_metadata_fresh_from_actual_DBG=body,setup_allowlist_disjoint_from_forbidden=True,actual_compiled_grants=source,actual_dense_source_controls=dense_controls,actual_controller_cycle=8 if a.profile=='powered'else None,configured_source_summon_stock=112 if a.profile=='powered'else None,configured_source_bounce_stock=100 if a.profile=='powered'else None,syntax_execution='Not locally parsed/executed; ROOT review required before native. No unavailable archived dependency is recreated.',limits='Configured assembled leaf calls only; not physical collision/controller/NMI/pixels. No native outcome inherited. Cold menu/actual alternateSelect and first active Proto palette run are native-pending.'))
 command=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),'--emulator','C:/Mesen2/Mesen.exe',str(a.output/'run.lua'),str(a.rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_capture_lease_and_grant=True,argv=command))
 paths=[a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),fixture,parent,Path(__file__),observer,bodycfg,bodyjson,R/'tools/audit/current_roster_compact_11_v1.py',R/'tools/audit/robots_weapon_cpu_v1.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',R/'src/inventory.s',R/'src/inventory_data.inc',R/'src/megaman_weapons.s',R/'src/megaman_physics.s',R/'src/megaman_rush.s',R/'src/special_weapons.s',R/'src/protoman_cold.s',R/'src/mario_source.s']+[a.output/n for n in ['config.json','run.lua','source-controls.json','command.json']]
 if expected==COMPOSED:paths +=[composition,R/'tools/audit/mm_proto_body_current_compose_v1.py',R/'src/x5_palette.s',R/'src/proto_palette_ack.s']
 if a.profile=='dense':paths +=[codec,R/'tools/audit/final_inventory_compact_capture_v1.py',R/'src/object.s',R/'inc/constants.inc',R/'inc/common.inc']
 for p in [Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll')]:
  if p.is_file():paths.append(p)
 put(a.output/'ready.json',dict(prepared=True,native_run=False,native_grant=False,identity=a.identity,variant=variant,profile=a.profile,ROM_sha256=expected,command=command,
  bindings={str(p.resolve()):sha(p)for p in paths},human_GUI_settings=dict(path='C:/Mesen2/settings.json',role='Informational live GUI provenance, not strict watched runtime input',sha256=sha(Path('C:/Mesen2/settings.json'))),
  component_scope=('Mature mushroom0 native collision/60transform; one staged source-consistent Vine5+5Goombas,180 actual dense updates/three real basicB taps/leftslide/jump, actual native Vine entry/admission/return and fullDMA/source groups, bounded actual wholePPU. Firstquest only; no forced sample/actor/health/resource outcome.'if a.profile=='dense'else'Mature mushroom0 native collision/60transform, real48/87 charge release, realDown+A slide and A jump, mature Coil8 native grant, realSelect/free summon/floor landing/existing buster, disclosed descending-player alignment/native12debit/spring/exit/departure.'),
  seeds='Only map/complete player/typed mature actor metadata at actualGameLoop+5/NmiDisableFF; never ownership/tier/selection/ammo/charge/projectile/outcome fields.',
  caps=dict(wall_frames=cfg['frame_limit'],owned_workers=1,launches=1,screenshots=0 if a.profile=='dense'else 8,CSV_files=1,CSV_data_bytes=16000000,lossless_containers=1 if a.profile=='dense'else 0,container_bytes=67108864 if a.profile=='dense'else 0,container_frame_records=512 if a.profile=='dense'else 0,provenance_rows=6000 if a.profile=='dense'else 0,provenance_bytes=16000000 if a.profile=='dense'else 0,lossless_frame_files=0,runtime_source_clones=0,central_run_bytes=2000000000,central_run_files=64),
  remaining='No adoption/cadence proof (full3e7 Proto route has strictdeadline FALSE). No block reveal/rise/RNG, playableRushJet, othermode, zeroammo/fullpool, per-live-shot opaque fairness, lift/star/otherpartial-caller, original art/audio fidelity or campaign acceptance. Native partial/no-draw source ownership remains an observation to qualify, not assumed. Source/runtime syntax remains unexecuted; no launch until ROOT review/grant.'))
 print(json.dumps(dict(prepared=True,native_run=False,identity=a.identity,ready=str(a.output/'ready.json'),ready_sha256=sha(a.output/'ready.json'),bindings=len(paths),source_controls=sha(a.output/'source-controls.json')),indent=2))

if __name__=='__main__':main()
