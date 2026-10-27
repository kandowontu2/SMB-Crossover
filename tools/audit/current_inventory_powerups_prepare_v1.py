"""Prepare one small current Bass collection/use profile. Never launches Mesen.
No ROM/debug/source/runtime copying; no deleted Archive dependencies.
"""
from pathlib import Path
import argparse,csv,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
from final_item_matrix import FAMILIES
EXPECTED='fb2a608e4670788c0a170d6a17e7802b226e9e6933cd44103cb1b9212db54eed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,default=ROOT/'build/smb-crossover-mmc5-expanded.nes');p.add_argument('--expected-sha256',default=EXPECTED);p.add_argument('--mode',choices=['easy','hard'],default='easy');p.add_argument('--output',type=Path,required=True);p.add_argument('--refresh-unrun',action='store_true');a=p.parse_args()
 expected=a.expected_sha256
 a.rom=a.rom.resolve();a.output=a.output.resolve()
 assert re.fullmatch('[0-9a-f]{64}',expected)
 assert sha(a.rom)==expected,'Explicit current ROM hash binding'
 assert a.rom.stat().st_size==2097168,'Expanded MMC5 target'
 b=scoped_load(a.rom);fixture=ROOT/'tests/current-inventory-powerups.lua';text=fixture.read_text()
 assert(b['raw'][6]>>4)|(b['raw'][7]&240)|((b['raw'][8]&15)<<8)==5,'MMC5 mapper'
 if a.output.exists():
  old=a.output/'prepared-not-run.json';z=json.loads(old.read_text())
  assert a.refresh_unrun and z['status']=='PREPARED_DO_NOT_RUN'and not z['native_run']and z['ROM_sha256']==expected and not(a.output/'native').exists(),'Never overwrite native evidence or retag a different ROM'
 else:a.output.mkdir(parents=True)
 def raw(n,i=0):return b['raw'][location(b,n)+i]
 def hook(n,delta=0,size=3):
  pos=location(b,n)+delta;pc=address(b,n)+delta;bank=(pos-16)//8192;bs=list(b['raw'][pos:pos+size]);banks=[bank]
  if bank==127:
   off=pos-16-bank*8192;assert b['raw'][16+125*8192+off:16+125*8192+off+size]==bytes(bs);banks=[125,127]
  return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
 hooks={key:hook(n)for key,n in dict(PhysicalPickup='MarioSourcePowerupCollision',InventoryCollect='InventoryCollect',InventoryGrant='InventoryGrant',InventorySpend='InventorySpend',GuestPowerupUpdate='GuestPowerupUpdate',DamageEnemy='MegaManWeapons::DamageEnemy',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
 start=location(b,'GameLoop');assert b['raw'][start:start+5]==bytes([0xa9,255,0x8d,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8])
 hooks['GameLoopOwned']=hook('GameLoop',5)
 for key,n,opcode in[('GameLoopFinish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40)]:
  delta=int(b['syms'][n]['size'],0)-1;assert raw(n,delta)==opcode;hooks[key]=hook(n,delta,1)
 assert raw('InventorySpend::Done')==0x60;hooks['InventorySpendDone']=hook('InventorySpend::Done',0,1)
 size=int(b['syms']['OAMandReadJoypad']['size'],0);data=b['raw'][location(b,'OAMandReadJoypad'):location(b,'OAMandReadJoypad')+size];assert data.count(b'\x8d\x14\x40')==1
 hooks['DmaComplete']=hook('OAMandReadJoypad',data.index(b'\x8d\x14\x40')+3)
 names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))
 setup_allowed=['Block_Buffer_1','MmSolidTerrain','MmBrickHealth','Enemy_Flag','Enemy_CollisionBits','InvDropKind','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum','MmVX','MmVY','ScrollLock','ScreenLeft_X_Pos','ScreenLeft_PageLoc','ScreenRight_X_Pos','ScreenRight_PageLoc','Player_X_Position','Player_PageLoc','MmOldX','Player_Y_Position','Player_Y_HighPos','Player_State','PlayerFacingDir','Player_MovingDir','Player_CollisionBits','Enemy_ID','Enemy_State','Enemy_BoundBoxCtrl','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_SprAttrib','PowerUpType','InvPickupOwner','InvPickup','AvPickupAmmoItem','Enemy_Y_MoveForce','Enemy_MovingDir','EnemyOffscrBitsMasked','MmEnemyHealthLo','MmEnemyHealthHi','MmEnemyFlash','RgEnemyStun']
 names.update(setup_allowed);names.update(['CurrentBank','CurrentBankC','SsAudioRequest','Square2SoundQueue','Sprite0HitDetectFlag'])
 cfg=dict(ROM_sha256=expected,character=9,slot=9,mode=int(a.mode=='hard'),frame_limit=16000,hooks=hooks,ram={n:address(b,n)for n in names if n in b['syms']},setup_allowed={n:True for n in setup_allowed},powerup_sfx=address(b,'Sfx_PowerUpGrab'),metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},smc=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],items={})
 # Source-derived IDs/costs; ARM lift/throw, short PHARAOH, paid KICK,
 # FLAME's actual ignited phase and WATER's native orbit/second-B expansion.
 contact=[0,9,10,11,12,19,16,17,0];sfx=[0,0,64,22,61,65,22,67,0]
 assert raw('InvItemCount',9)==8 and FAMILIES['bass']['inventory']=='ARM, METAL, KNUCKLE, PHARAOH, KICK, FLAME, WATER, BALANCE'
 for item in range(9):
  idx=144+item;ptr=raw('InvNameLo',idx)+256*raw('InvNameHi',idx);g=b['segs'][b['syms']['InvNameLo']['seg']];off=int(g['ooffs'],0)+ptr-int(g['start'],0)
  cfg['items'][item]=dict(id=item,hud_name=list(b['raw'][off:off+7]),cost=raw('InvCosts',idx),initial_ammo=raw('InvInitialAmmo',idx),max_ammo=raw('InvMaxAmmo',idx),selectable=raw('InvSelectable',idx),auto_equip=raw('InvAutoEquip',idx),contact_type=contact[item],damage_type=raw('SpecialWeapons::DamageTypes',contact[item]-9)if contact[item]else 0,sfx=sfx[item])
 for n in re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text):assert n in cfg['ram'],n
 for n in setup_allowed:assert n in cfg['ram'],n
 # Complete genuine leaf-owner expectations, independently of the Lua native
 # observer/controller. These CPU arenas are not physical/native receipts.
 q=Arena(b,9);q.invoke('InventoryInit');q.put(PlayerStatus=0,OperMode_Task=3,CrossoverBehaviorVersion=cfg['mode'])
 source_rows=[]
 for item in range(9):
  assert not(q.get('InvOwnedLo',9)+256*q.get('InvOwnedHi',9))&(1<<item)
  before=[q.get('InvAmmo',144+i)for i in range(9)]
  q.put(InvObject=5);q.set('InvPickupOwner',9,5);q.set('InvPickup',item,5);c,_=q.invoke('InventoryCollect',x=5)
  assert c.p&1 and(q.get('InvOwnedLo',9)+256*q.get('InvOwnedHi',9))&(1<<item)
  assert before==[q.get('InvAmmo',144+i)for i in range(9)],'Grant must not fabricate a refill'
  if item==0:
   for _ in range(60):q.invoke('GuestPowerupUpdate')
   assert q.get('GuestPowerupActive')==0 and q.get('PlayerStatus')==1
  elif item<8:
   cost=cfg['items'][item]['cost'];before=q.get('InvAmmo',144+item);q.invoke('InventorySpend',a=item,y=cost);assert q.get('InvAmmo',144+item)==before-cost
  source_rows.append(dict(item=item,ownedLo=q.get('InvOwnedLo',9),ownedHi=q.get('InvOwnedHi',9),status=q.get('PlayerStatus'),ammo=[q.get('InvAmmo',144+i)for i in range(9)]))
 q.set('InvSelected',0,9);q.invoke('InventoryRefillAmount',a=40);assert q.get('InvRefill')==151,'Actual least pool is naturally spent WATER'
 for _ in range(90):q.invoke('InventoryUiTick')
 assert q.get('InvRefill')==0 and q.get('InvAmmo',151)==112
 # Static safety contracts: only w()/tile() perform game writes; callbacks
 # are all registered at load, no old endFrame seed/bootstrap and no copies.
 assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and 'dofile('not in text
 forbidden=['InvOwnedLo','InvOwnedHi','InvViewedLo','InvViewedHi','InvSelected','InvAmmo','PlayerStatus','GuestPowerupActive','GameEngineSubroutine','InjuryTimer','MmDeathFlag','RgShotType','CheatInvincible']
 assert not(set(setup_allowed)&set(forbidden))
 assert 'w(\'PlayerStatus\''not in text and 'w(\'InvAmmo\''not in text and 'w(\'RgShotType\''not in text
 assert text.count('emu.takeScreenshot(')==1 and 'images<8'in text and cfg['frame_limit']<20000
 put(a.output/'config.json',cfg)
 (a.output/'run.lua').write_text('CURRENT_INVENTORY_POWERUPS='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
 put(a.output/'source-controls.json',dict(passed=True,source_CPU_only=True,ROM_sha256=expected,actual_InventoryCollect_cases=source_rows,actual_balancer_refill=dict(source_amount=40,chosen_index=151,result=112),no_item_ammo_grant_seed=True,static_setup_allowlist=True,source_preerase_order='MarioSourcePowerupCollision -> EraseEnemyObject -> queue pickup SFX -> actual InventoryCollect; observer scopes both real boundaries.',limits='Leaf CPU calls do not establish Lua execution, spatial collisions, native cadence/PPU/SFX/audio fidelity.'))
 with(a.output/'requirements.csv').open('w',newline='')as f:
  w=csv.writer(f);w.writerow(['family','item_id','name','prepared_native_scope','remaining'])
  for item,name in enumerate(['MUSHROOM','ARM','METAL','KNUCKLE','PHARAOH','KICK','FLAME','WATER','BALANCE']):w.writerow(['bass',item,name,'Mature physical collision + real collection; acquired effect/contact/spend/cleanup or Balancer refill','Full block reveal/rise and natural lottery; facing2; empty/full-pool; charged Pharaoh; drop acquisition/caps; star/1up; other mode'])
  for family,ch in[('mm',1),('samus',2),('bill',3),('link',4),('simon',5),('ryu',10),('sophia',11)]:
   for item in range(1,raw('InvItemCount',ch)+1):w.writerow([family,item,'source inventory ID','NOT PREPARED in this first Bass profile','Source-specific passive/ability/gallery adaptation required; no inherited pass from old matrices'])
 command=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),str(a.output/'run.lua'),str(a.rom),'--timeout','1800','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_authorization_and_capture_gate=True,runtime_binding='ROOT must supply its existing approved isolated emulator/settings/CLI binding; this task did not launch, copy or choose a new runtime.',argv=command))
 bindings=[]
 for p in[a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),fixture,Path(__file__),ROOT/'tests/remaining-inventory.lua',ROOT/'tools/audit/final_item_matrix.py',ROOT/'tools/audit/current731_powerup_ledger_v1.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/capture_budget.py',ROOT/'src/inventory.s',ROOT/'src/inventory_data.inc',ROOT/'src/inventory_drops.s',ROOT/'src/special_weapons.s',ROOT/'src/megaman_super_arm.s',ROOT/'src/guest_body_contact.s',ROOT/'src/megaman_weapons.s',ROOT/'src/game.s',ROOT/'src/common.s',ROOT/'src/mario_source.s']+[a.output/n for n in['config.json','run.lua','source-controls.json','requirements.csv','command.json']]:
  if p.is_file():bindings.append(dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size))
 put(a.output/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,goal_complete=False,ROM_sha256=expected,family='bass',actual_numeric_mode=cfg['mode'],mature_collection_ids=list(range(9)),refill_id=254,use_ids=list(range(1,8)),passive_use_ids=[8],no_ownership_tier_selection_ammo_projectile_outcome_seeds=True,setup_boundary='GameLoop+5 after actual STA NmiDisable=$FF; one synchronous callback, no active NMI/IRQ; no CPU steps/yields inside fixture transaction',setup_disclosure='Logical+visible map, complete player position/motion setup, mature item5 actor metadata, complete live-effect-aligned target enemy initialized before real native HP/damage. No natural encounter or head-bump/reveal/rise/RNG claim.',caps=dict(frames=16000,bytes=2000000000,files=64,screenshots=8,lossless_frame_files=0),output_files='One CSV, one compact JSON result, up to8 full-frame PNGs; no per-frame dumps, private runtime or source tree copies.',historical_warning='final_item_matrix CURRENT55 and ledger CURRENT731 are requirements/context only; never executed or retagged as current evidence.',remaining='Other mode; opposite facing; per-weapon zero-ammo/full-pool/charge/property/cap cases; full block reveal/rise; natural drops/RNG; star/1up; remaining character inventories. No native run until ROOT authorization.',bindings=bindings))
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ROM=expected,source_collect_cases=9,output=str(a.output),manifest_sha256=sha(a.output/'prepared-not-run.json'))))
if __name__=='__main__':main()
