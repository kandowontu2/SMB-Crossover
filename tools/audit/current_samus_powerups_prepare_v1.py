"""Prepare one compact current8487 Hard Samus item profile; never launch Mesen."""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
EXPECTED='8487c439ded9bc6274e1dc8f8e051494fa96ee518553d9c2f382eccf2e71d0e6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,default=ROOT/'build/bass_corner_current.nes');p.add_argument('--expected-sha256',default=EXPECTED);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.rom=a.rom.resolve();a.output=a.output.resolve();assert sha(a.rom)==a.expected_sha256 and a.rom.stat().st_size==2097168
 assert not a.output.exists(),'Never overwrite native/prepared evidence';a.output.mkdir(parents=True)
 b=scoped_load(a.rom);assert (b['raw'][6]>>4)|(b['raw'][7]&240)|((b['raw'][8]&15)<<8)==5
 fixture=ROOT/'tests/current-samus-powerups.lua';text=fixture.read_text()
 def raw(n,i=0):return b['raw'][location(b,n)+i]
 def hook(n,delta=0,size=3):
  pos=location(b,n)+delta;pc=address(b,n)+delta;bank=(pos-16)//8192;bs=list(b['raw'][pos:pos+size]);banks=[bank]
  if bank==127:
   off=pos-16-bank*8192;assert b['raw'][16+125*8192+off:16+125*8192+off+size]==bytes(bs);banks=[125,127]
  return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
 hooks={key:hook(n)for key,n in dict(PhysicalPickup='MarioSourcePowerupCollision',InventoryCollect='InventoryCollect',InventoryGrant='InventoryGrant',InventorySpend='InventorySpend',GuestPowerupUpdate='GuestPowerupUpdate',DamageEnemy='MegaManWeapons::DamageEnemy',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
 for key,n in dict(EnemyDrop='InventoryEnemyDrop',DropPhysics='InventoryEnemyDrop::Physics',RefillPickup='InventoryRefillPickup',RefillAmount='InventoryRefillAmount',RemainingRefill='RemainingRefill').items():hooks[key]=hook(n)
 delta=int(b['syms']['InventoryEnemyDrop']['size'],0)-1;assert raw('InventoryEnemyDrop',delta)==0x60;hooks['EnemyDropReturn']=hook('InventoryEnemyDrop',delta,1)
 assert raw('RemainingRefill::Done')==0x60;hooks['RemainingRefillDone']=hook('RemainingRefill::Done',0,1)
 def unique_hook(key,n,pattern,delta=0):
  start=location(b,n);data=b['raw'][start:start+int(b['syms'][n]['size'],0)];assert data.count(pattern)==1,(key,pattern.hex())
  offset=data.index(pattern)+delta;hooks[key]=hook(n,offset,len(pattern)-delta);return offset
 kind=address(b,'InvDropKind');ammo=address(b,'InvAmmo')
 unique_hook('DropCollectAccepted','InventoryUpdateDrops',bytes([0xa9,8,0xbc,kind&255,kind>>8,0xc0,2,0xd0,2,0xa9,40]))
 store_offset=unique_hook('RefillStoreBinding','RemainingRefill',bytes([0x9d,ammo&255,ammo>>8]));store_hook=hooks.pop('RefillStoreBinding')
 clear_offset=unique_hook('DropClearBinding','InventoryUpdateDrops',bytes([0xa9,0,0x9d,kind&255,kind>>8]),2);clear_hook=hooks.pop('DropClearBinding')
 assert b['raw'][location(b,'RemainingRefill::Samus'):location(b,'RemainingRefill::Samus')+4]==bytes([0xa9,2,0xa0,2]),'Actual Samus fixed +2 refill, independent of shared small/big amount'
 start=location(b,'GameLoop');assert b['raw'][start:start+5]==bytes([0xa9,255,0x8d,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8]);hooks['GameLoopOwned']=hook('GameLoop',5)
 for key,n,opcode in [('GameLoopFinish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40),('RemainingPowerDone','RemainingPower',0x60)]:
  delta=int(b['syms'][n]['size'],0)-1;assert raw(n,delta)==opcode;hooks[key]=hook(n,delta,1)
 assert raw('InventorySpend::Done')==0x60;hooks['InventorySpendDone']=hook('InventorySpend::Done',0,1)
 post=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK');load=bytes([0xa5,mirror])if mirror<256 else bytes([0xad,mirror&255,mirror>>8])
 assert b['raw'][post-3:post]==b'\x8d\x14\x40'and b['raw'][post:post+len(load)+3]==load+b'\x8d\x01\x20';hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
 setup='Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits AvFrozen AvFrozenHi RgEnemyStun LsrFrozenPose InvDropKind Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce ScrollThirtyTwo AreaParserTaskNum MmVX MmVY ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc Player_X_Position Player_PageLoc MmOldX Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_SprAttrib PowerUpType InvPickupOwner InvPickup AvPickupAmmoItem Enemy_Y_MoveForce Enemy_MovingDir EnemyOffscrBitsMasked MmEnemyHealthLo MmEnemyHealthHi MmEnemyFlash'.split()
 bare_ram=set(re.findall(r"\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)",text))
 names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|bare_ram|set(setup)|set('CurrentBank CurrentBankC Sprite0HitDetectFlag'.split())
 order=[0,1,2,7,3,4,5,6,254]
 limits='Hard1 mature physical item components only. No full block reveal/rise, natural reward lottery/drop, Easy tiers, opposite facing/aim, pool-cap/exhaustion, whole-waveform or all-graphical-fidelity claim. Long7 is mushroom-autoowned before its one explicit idempotent mature reward. Freeze expiry/AI resume and Varia firebar contact remain untested natively; later staged scene removes the frozen target. Source-only Varia branch and passive-property controls are not native hazard evidence. PNGs are2-DMA-delayed selected samples requiring separate visual review.'
 cfg=dict(ROM_sha256=a.expected_sha256,character=2,slot=2,mode=1,order=order,frame_limit=16000,dma_store_return=address(b,'PostDmaMaskEnable'),hooks=hooks,ram={n:address(b,n)for n in names if n in b['syms']},setup_allowed={n:True for n in setup},powerup_sfx=address(b,'Sfx_PowerUpGrab'),initial_missiles=raw('InvInitialAmmo',34),max_missiles=raw('InvMaxAmmo',34),missile_cost=raw('InvCosts',34),refill_amount=2,missile_sfx=address(b,'AV_SFX_SAMUSSHOOTMISSILE'),screw_sfx=address(b,'AV_SFX_SAMUSSCREWATTACK'),metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],limits=limits,items={})
 cfg['refill_store']=dict(pc=store_hook['pc'],after=store_hook['pc']+3,bank=store_hook['banks'][0],bytes=store_hook['bytes'])
 cfg['drop_clear_store']=dict(pc=clear_hook['pc'],after=clear_hook['pc']+3,bank=clear_hook['banks'][0],bytes=clear_hook['bytes'])
 assert raw('InvItemCount',2)==7 and cfg['initial_missiles']==5 and cfg['missile_cost']==1 and cfg['max_missiles']==20
 assert raw('InvMushroomLo',2)==128 and raw('InvSingleLo',35)==16 and raw('InvSingleLo',36)==8
 # Actual source projected pool/contact IDs: LongSm2->8, WaveSm3->9,
 # Bomb->10, MissileRg41->68, IceRg46->73, Screwbody->75.
 for item in range(8):
  idx=32+item;ptr=raw('InvNameLo',idx)+256*raw('InvNameHi',idx);g=b['segs'][b['syms']['InvNameLo']['seg']];off=int(g['ooffs'],0)+ptr-int(g['start'],0)
  cfg['items'][item]=dict(id=item,hud_name=list(b['raw'][off:off+7]),cost=raw('InvCosts',idx),selectable=raw('InvSelectable',idx),auto_equip=raw('InvAutoEquip',idx),sm_type={7:2,4:3}.get(item,0),rg_type={2:41,3:46}.get(item,0),damage_type={1:10,2:68,7:8,3:73,4:9,6:75}.get(item,0))
 assert raw('MegaManWeapons::RadiusX',9)>=12,'Bomb side target inside actual native blast radius'
 for n in re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text):assert n in cfg['ram'],n
 for n in bare_ram:assert n in cfg['ram']and isinstance(cfg['ram'][n],int)and 0<=cfg['ram'][n]<=0xffff,n
 assert not(set(setup)&set('InvOwnedLo InvOwnedHi InvSelected InvAmmo PlayerStatus GuestPowerupActive GameEngineSubroutine InjuryTimer GuestHurtTicks MmDeathFlag RgShotType SmShotType SmBombAge SmBall SmCrouch SmFlip CheatInvincible'.split()))
 assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and 'dofile('not in text and text.count('emu.takeScreenshot(')==1 and 'images<8'in text
 # Real assembled source leaf controls, independent of future Lua/native execution.
 q=Arena(b,2);q.invoke('InventoryInit');q.put(PlayerStatus=0,OperMode_Task=3,CrossoverBehaviorVersion=1);rows=[]
 for item in order[:-1]:
  before=q.get('InvAmmo',34);q.put(InvObject=5);q.set('InvPickupOwner',2,5);q.set('InvPickup',item,5);c,_=q.invoke('InventoryCollect',x=5);assert c.p&1
  if item==0:
   for _ in range(60):q.invoke('GuestPowerupUpdate')
   assert q.get('PlayerStatus')==1 and q.get('GuestPowerupActive')==0 and q.get('InvOwnedLo',2)==129
  else:assert q.get('InvOwnedLo',2)&(1<<item)
  assert q.get('InvAmmo',34)==before,'No fabricated upgrade refill'
  cfg['items'][item]['expected_owned']=q.get('InvOwnedLo',2)
  if item in [0,7,4]:
   cpu,_=q.invoke('SamusBeamType');assert cpu.a==(3 if item==4 else 2)
  if item==2:
   cpu,_=q.invoke('InventorySpend',a=2,y=1);assert cpu.p&1 and q.get('InvAmmo',34)==4
  if item==3:
   for i in range(10):q.set('RgShotType',0,i)
   cpu,_=q.invoke('AvSamusPrimary');assert cpu.p&1 and any(q.get('RgShotType',i)==46 for i in range(10))
   for i in range(10):q.set('RgShotType',0,i)
  if item==4:assert not(q.get('InvOwnedLo',2)&8)
  if item==5:
   cpu,_=q.invoke('RemainingPower');assert cpu.a==2
  if item==6:
   q.put(SmFlip=1,Player_State=1);cpu,_=q.invoke('RemainingContactProtection');assert cpu.p&1
  rows.append(dict(item=item,owned=q.get('InvOwnedLo',2),missiles=q.get('InvAmmo',34),property='Long auto/idempotent'if item==7 else 'source reward'))
 q.put(InvObject=5);q.set('InvPickupOwner',2,5);q.set('InvPickup',254,5);q.set('AvPickupAmmoItem',2,5);q.invoke('InventoryCollect',x=5);assert q.get('InvAmmo',34)==6
 drop_rows=[]
 for size in [0,192]:
  for before in [0,4,19,20]:
   d=Arena(b,2);d.invoke('InventoryInit');d.put(PlayerStatus=1,CrossoverBehaviorVersion=1,GameEngineSubroutine=8,Player_Y_HighPos=1,TimerControl=0,Player_X_Position=72,Player_PageLoc=0,Player_Y_Position=149)
   d.set('InvOwnedLo',5,2);d.set('InvAmmo',before,34);d.set('PseudoRandomBitReg',0,1);d.set('PseudoRandomBitReg',size,2)
   for n,value in [('Enemy_ID',6),('Enemy_State',0),('Enemy_X_Position',72),('Enemy_PageLoc',0),('Enemy_Y_Position',149)]:d.set(n,value,0)
   d.invoke('InventoryEnemyDrop',x=0);assert d.get('InvDropKind',3)==(2 if size else 1)and d.get('AvDropItem',3)==2 and d.get('InvDropX',3)==80 and d.get('InvDropY',3)==157
   d.invoke('InventoryUpdateDrops');assert d.get('InvDropKind',3)==0 and d.get('InvAmmo',34)==min(20,before+2)
   drop_rows.append(dict(kind=2 if size else 1,before=before,after=d.get('InvAmmo',34),native_clear=True))
 # A real source miss retains the pickup and cannot credit any refill.
 d.set('InvAmmo',4,34);d.invoke('InventoryEnemyDrop',x=0);d.put(Player_X_Position=180);d.invoke('InventoryUpdateDrops');assert d.get('InvAmmo',34)==4 and d.get('InvDropKind',3)==2
 frozen=ROOT/'build/current-samus-powerups-v2.lua';prior=frozen.read_text();begin='-- All callback registration is startup-static.';end="emu.addEventCallback(function()\n if not entered then emu.setInput(menu(),0);return end"
 assert text[text.index(begin):text.index(end,text.index(begin))]==prior[prior.index(begin):prior.index(end,prior.index(begin))],'Original full DMA/NMI/CHR/deadline guards remain byte-exact'
 failed_v3=ROOT/'build/current-samus-powerups-v3.lua';failed_text=failed_v3.read_text()
 for anchor in ["emu.addEventCallback(function()\n if not entered", "hook('GameLoopOwned'"]:
  finish='end,emu.eventType.inputPolled)'if anchor.startswith('emu.')else "hook('PhysicalPickup'"
  assert text[text.index(anchor):text.index(finish,text.index(anchor))]==failed_text[failed_text.index(anchor):failed_text.index(finish,failed_text.index(anchor))],'Original controller/phase setup remains exact'
 assert re.findall(r"\bw\([^\n)]+\)",text)==re.findall(r"\bw\([^\n)]+\)",failed_text),'No native game setup writes added or changed'
 put(a.output/'config.json',cfg)
 address_guard='for _,name in ipairs('+lua(sorted(bare_ram))+')do local a=CURRENT_SAMUS_POWERUPS.ram[name];assert(type(a)=="number"and a>=0 and a<=65535,"Missing callback RAM address: "..name)end\n'
 (a.output/'run.lua').write_text('CURRENT_SAMUS_POWERUPS='+lua(cfg)+'\n'+address_guard+'dofile([=['+fixture.as_posix()+']=])\n',newline='\n')
 put(a.output/'source-controls.json',dict(passed=True,source_CPU_only=True,ROM_sha256=a.expected_sha256,bare_RAM_addresses={n:cfg['ram'][n]for n in sorted(bare_ram)},callback_addresses_checked_before_fixture_load=True,fixture_change='v4 explicitly clears only Lua drop provenance alongside the unchanged staged native slot reset, since nesDebug writes bypass CPU callbacks; logs all spawn boundary fields before assertions. v3 earned-refill conservation and all mechanics/hardware assertions retained.',controller_and_setup_game_writes_unchanged=True,hardware_guard_block_byte_exact=True,actual_collect_rows=rows,real_missile_spend=1,actual_refill=2,result_missiles=6,actual_enemy_drop_refill_cases=drop_rows,actual_drop_geometry_miss_retains_ammo=True,actual_Ice_spawn=46,Wave_clears_Ice=True,Long_mushroom_auto=True,Varia_visual_tier=2,Screw_contact_protection=True,no_native_claim=True,prior_v2_natural_refill_provenance='Unlogged: CSV4-to6 alone does not prove an actual drop chain. Fresh native hooks are required.',prior_v3_failure='Actual earlier spawn wall731 survived only in Lua drops[] after subsequent staged native clear; Screw spawn wall1889 rejected. Individual failing-conjunct values were not serialized, so exact native kind/item at failure remains unlogged.',sample_metadata='One bounded JSON array at the existing at-most8 screenshot events: NT2000 HUD2x2/attributes/pattern/palette/physicalOAM256/source256/CHR latches. No new images.',limits=limits))
 argv=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),str(a.output/'run.lua'),str(a.rom),'--timeout','1800','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_authorization_and_capture_gate=True,runtime_binding='ROOT supplies its existing approved isolated runtime/settings; no runtime/source/ROM copy or launch here.',argv=argv))
 paths=[a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),fixture,Path(__file__),frozen,failed_v3,ROOT/'tests/current-inventory-powerups.lua',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/capture_budget.py']+[ROOT/'src'/n for n in ['inventory.s','inventory_data.inc','inventory_drops.s','samus.s','samus_weapons.s','remaining_weapons.s','guest_body_contact.s','samus_ice_hit.s','samus_freeze_render.s','megaman_weapons.s','reset.s','guest_powerups.s','roll_dispatch.s','darkwing_pickups.s']]+[a.output/n for n in ['config.json','run.lua','source-controls.json','command.json']]
 bindings=[dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size)for p in paths if p.is_file()]
 put(a.output/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=a.expected_sha256,actual_numeric_mode=1,physical_mature_order=order,property_scope=dict(morph='Two fresh Down presses crouch/morph, native bomb/explosion/boost, Up exits',missile='Actual Select, one ammo, real enemy damage',long='Native beam2 actual damage before Ice/Wave; explicit Long reward already autoowned',ice='NativeRg46 ordinary enemy freeze/STOP without health damage',wave='NativeSm3 through complete staged solid column then enemy damage, Ice removed',varia='ActualRemainingPower2 and powered crouch; no native firebar immunity claim',screw='Actualdiagonal jump/flip body75 real enemy damage, source cue',refill='ActualFE physical pickup adds2 missiles, capped20'),no_ownership_tier_selection_ammo_form_projectile_outcome_seeds=True,setup_boundary='ActualGameLoop+5 immediately after STA NmiDisableFF; no active NMI/IRQ, no CPU/yield inside transaction',setup_disclosure='Staged complete visible/logical map, native position/motion and mature actor/real-effect-aligned Goomba initial state. Later scenes remove prior target/drop/freeze actors; no freeze expiry claim. No result/health/ownership seeds for player.',caps=dict(frames=16000,bytes=2000000000,files=64,screenshots=8),outputs='OneCSV/resultJSON/up to8 selectedPNGs, no lossless/per-frame file forest or copied source/runtime trees.',limits=limits,bindings=bindings))
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',output=str(a.output),source_collect_cases=8,refill=2,manifest_sha256=sha(a.output/'prepared-not-run.json'))))
if __name__=='__main__':main()
