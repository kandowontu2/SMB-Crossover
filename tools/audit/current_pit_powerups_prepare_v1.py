"""Prepare two small Pit component modes on frozen6be; no emulator or clones."""
from pathlib import Path
import argparse,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from observe_chip_committed_write import lua
EXPECTED='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
PLAN=[dict(name='cold-bow',kind='bow',tier=0,limit=110),dict(name='cold-jump-gate',kind='gate',tier=0,limit=190),dict(name='mushroom-transform',kind='collect',tier=0,pickup=0,limit=120),dict(name='tier1-bow',kind='bow',tier=1,limit=110),dict(name='tier1-hammer',kind='hammer',tier=1,limit=100),dict(name='tier1-jump-gate',kind='gate',tier=1,limit=190),dict(name='flower-transform',kind='collect',tier=1,pickup=1,limit=120),dict(name='tier2-flutter-exhaust',kind='fullflight',tier=2,limit=350),dict(name='tier2-flutter-release',kind='releaseflight',tier=2,limit=240),dict(name='tier2-hammer',kind='hammer',tier=2,limit=100)]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,default=R/'build/samus_fixed_hud_current4a.nes');p.add_argument('--expected-sha256',default=EXPECTED);p.add_argument('--mode',choices=['easy','hard'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve()
 assert sha(a.rom)==a.expected_sha256 and len(a.rom.read_bytes())==2097168
 assert not a.output.exists();b=scoped_load(a.rom);fixture=R/'tools/audit/current_pit_powerups_v1.lua';text=fixture.read_text();mode=int(a.mode=='hard')
 def hook(n,delta=0,size=3):
  pos=location(b,n)+delta;pc=address(b,n)+delta;k=(pos-16)//8192;bs=list(b['raw'][pos:pos+size]);banks=[k]
  if k==127:
   off=(pos-16)%8192;assert b['raw'][16+125*8192+off:16+125*8192+off+size]==bytes(bs);banks=[125,127]
  return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
 hooks={key:hook(n)for key,n in dict(PhysicalPickup='MarioSourcePowerupCollision',GuestBeginPowerup='GuestBeginPowerup',GuestPowerupUpdate='GuestPowerupUpdate',DamageEnemy='MegaManWeapons::DamageEnemy',PitFlightEntry='PitFlightUpdate',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
 start=location(b,'GameLoop');assert b['raw'][start:start+5]==bytes([0xa9,255,0x8d,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8]);hooks['GameLoopOwned']=hook('GameLoop',5)
 for key,n,op in [('GameLoopFinish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40)]:
  delta=int(b['syms'][n]['size'],0)-1;assert b['raw'][location(b,n)+delta]==op;hooks[key]=hook(n,delta,1)
 for key,n,delta in [('PitFlightStopReturn','PitFlightUpdate::Stop',8),('PitFlightDoneReturn','PitFlightUpdate::Done',0)]:
  assert b['raw'][location(b,n)+delta]==0x60;hooks[key]=hook(n,delta,1)
 post=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK');load=bytes([0xa5,mirror])if mirror<256 else bytes([0xad,mirror&255,mirror>>8]);assert b['raw'][post-3:post]==b'\x8d\x14\x40'and b['raw'][post:post+len(load)+3]==load+b'\x8d\x01\x20';hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
 # Literal unchanged hardware module, no inherited old E005 completion.
 baseline=(R/'tests/current-inventory-powerups.lua').read_text();begin='-- All callback registration is startup-static.';end="emu.addEventCallback(function()\n if not entered"
 assert text[text.index(begin):text.index(end)]==baseline[baseline.index(begin):baseline.index(end)]
 allowed='Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits InvDropKind Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce ScrollThirtyTwo AreaParserTaskNum MmVX MmVY MmXFraction MmYFraction ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc Player_X_Position Player_PageLoc MmOldX Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_SprAttrib PowerUpType InvPickupOwner InvPickup Enemy_Y_MoveForce Enemy_MovingDir EnemyOffscrBitsMasked MmEnemyHealthLo MmEnemyHealthHi MmEnemyFlash RgEnemyStun'.split()
 names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|set(allowed)|set('CurrentBank CurrentBankC Sprite0HitDetectFlag MmEnemyHealthLo MmEnemyHealthHi RgShotType Square1SoundQueue'.split())
 ram={n:address(b,n)for n in names if n in b['syms']}
 for n in re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text)+allowed:assert n in ram,n
 assert not(set(allowed)&set('PlayerStatus PlayerSize XgPitFuel XgPitFlight XgPitBlocked InvOwnedLo InvOwnedHi InvAmmo InvSelected RgShotType InjuryTimer GuestHurtTicks CheatInvincible MmDeathFlag'.split()))
 assert text.count('emu.write(')==2 and'removeMemoryCallback'not in text and'dofile('not in text and text.count('emu.takeScreenshot(')==1
 # Full physical native owner calls, not InventoryCollect alone: Pit is not a
 # modern inventory profile; genuine source fallthrough starts GuestPowerup.
 collects=[];q=Arena(b,6);q.put(PlayerStatus=0,ObjectOffset=5,CrossoverBehaviorVersion=mode)
 for pickup,tier in [(0,1),(1,2)]:
  q.set('PowerUpType',pickup,5);q.set('InvPickupOwner',6,5);q.set('InvPickup',0xfc,5);q.set('Enemy_Flag',1,5);q.set('Enemy_State',128,5)
  q.invoke('MarioSourcePowerupCollision',x=5);assert q.get('GuestPowerupActive')==1 and q.get('GuestPowerupTarget')==tier and q.get('Enemy_Flag',5)==0
  for _ in range(60):q.invoke('GuestPowerupUpdate')
  assert q.get('PlayerStatus')==tier and q.get('GuestPowerupActive')==0 and q.get('TimerControl')==0 and q.get('GameEngineSubroutine')==8
  collects.append(dict(pickup=pickup,actual_tier=tier,full_physical_owner=True,real_transform_calls=60))
 calls=[];returns=set();exitpcs=set()
 for tier in [0,1,2]:
  q=Arena(b,6);q.put(PlayerStatus=tier,CrossoverBehaviorVersion=mode,Player_State=0,A_B_Buttons=0,SavedJoypadBits=0);q.invoke('ExpandedMovement');assert q.get('XgPitFuel')==60 and q.get('XgPitFlight')==0
  q.put(Player_State=1,A_B_Buttons=128,SavedJoypadBits=128)
  orig=NesMPU.step;seen={}
  def step(cpu):
   pc=cpu.pc;k=q.m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
   if pc==address(b,'PitFlightUpdate')and k==hooks['PitFlightEntry']['banks'][0]:
    sp=cpu.sp;ret=(q.m[256+(sp+1)%256]+256*q.m[256+(sp+2)%256]+1)%65536
    assert q.m[ret-3]==0x20 and q.m[ret-2]+256*q.m[ret-1]==pc
    seen.update(entry_pc=pc,bank=k,sp=sp,return_pc=ret,JSR_bytes=list(q.m[ret-3:ret]));returns.add(ret)
   if pc in [hooks['PitFlightStopReturn']['pc'],hooks['PitFlightDoneReturn']['pc']]and k==hooks['PitFlightEntry']['banks'][0]:
    assert seen and cpu.sp==seen['sp'];exitpcs.add(pc);seen['actual_exit']=pc
   orig(cpu)
  NesMPU.step=step
  try:q.invoke('ExpandedMovement')
  finally:NesMPU.step=orig
  assert seen and q.get('XgPitFuel')==(59 if tier==2 else 60)and q.get('XgPitFlight')==int(tier==2)
  if tier==2:
   for _ in range(59):q.invoke('PitFlightUpdate')
   assert q.get('XgPitFuel')==0;q.invoke('PitFlightUpdate');assert q.get('XgPitFlight')==0
   q.put(Player_State=0,A_B_Buttons=0,SavedJoypadBits=0);q.invoke('ExpandedMovement');assert q.get('XgPitFuel')==60
  calls.append(dict(tier=tier,actual_full_movement_call=seen,airborne_fuel_after_first=59 if tier==2 else 60,source_ground_recharge=60,no_CPU_fuel_seed=True))
 assert len(returns)==1 and exitpcs=={hooks['PitFlightStopReturn']['pc'],hooks['PitFlightDoneReturn']['pc']}
 cfg=dict(ROM_sha256=a.expected_sha256,character=6,slot=6,mode=mode,hooks=hooks,ram=ram,setup_allowed={n:True for n in allowed},flight_return_PC=next(iter(returns)),dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},poses={key:address(b,n)for key,n in dict(flap1='XG_POSE_FLAP1',flap2='XG_POSE_FLAP2',shot1='XG_POSE_FLAPSHOT1',shot2='XG_POSE_FLAPSHOT2').items()},plan=PLAN)
 a.output.mkdir(parents=True);put(a.output/'config.json',cfg);(a.output/'run.lua').write_text('CURRENT_PIT_POWERUPS='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
 put(a.output/'source-controls.json',dict(passed=True,source_CPU_only=True,mode=mode,physical_owner_collects=collects,complete_ExpandedMovement_call_controls=calls,real_leaf_RTS_PCs=sorted(exitpcs),static_callbacks_only=True,hardware_guard_block_byte_exact=True,limits='CPU source controls, not Lua/native reachability or PPU/audio/collision proof. Native fixture has no tier/fuel/form/ownership/health/outcome writes.'))
 argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),str(a.output/'run.lua'),str(a.rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
 paths=[a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),fixture,Path(__file__),R/'tests/current-inventory-powerups.lua',R/'tools/audit/final_item_abilities_native.lua',R/'tools/audit/final_item_abilities_static_return_v1.lua',R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py']+[R/'src'/n for n in ['expanded.s','expanded_weapons.s','guest_powerups.s','mario_source.s','inventory.s','roster.s']]+[a.output/n for n in ['config.json','run.lua','source-controls.json','command.json']]
 put(a.output/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=a.expected_sha256,actual_numeric_mode=mode,plan=PLAN,caps=dict(updates=3000,wall_frames=8000,host_seconds=1200,bytes=2000000000,files=64,PNGs=8,perframe_lossless_files=0),setup='GameLoop+5 private boundary: disclosed map/position/motion/mature pickup/complete target only. No player tier/fuel/form/owned/ammo/health/outcome writes.',limits='Mature mushroom+flower components, no emergence/RNG/star/1up/roof/water/oppositefacing/fullcampaign/allpixel/audio fidelity claim. Same source wing contract in both explicit modes; this is no native EasyHard equivalence claim. Lua execution/source-art visual review remains native work for ROOT.',bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in paths]))
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',output=str(a.output),manifest_sha256=sha(a.output/'prepared-not-run.json'),plan_records=len(PLAN),CPU_collects=2,CPU_movement_calls=3)))
if __name__=='__main__':main()
