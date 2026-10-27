"""Bounded earned CV3 native metadata. Preparation only, ROOT owns launches."""
from pathlib import Path
import argparse,hashlib,json,re,sys
from current_cv3_powerups_prepare_v1 import VARIANTS,plans,source_campaign,EXTRA_ALLOWED
from current_link_simon_powerups_prepare_v1 import ALLOWED,BASE_SHA
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import navigation
from observe_chip_committed_write import lua
R=Path(__file__).resolve().parents[2];B=R/'build';AB='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2';FIX='9a1b68c0a26ea86ff8c4712af66b8de8cd5ed2de13c74db1bfaf15eb9e2ba333'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--family',choices=list(VARIANTS),required=True);ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();rom=a.rom.resolve();out=a.output.resolve()
 assert sha(rom)==a.expected_sha256 and a.expected_sha256 in [AB,FIX]and not out.exists()
 b=scoped_load(rom);v=VARIANTS[a.family];plan=plans(v);source=source_campaign(b,v,plan,watch_expected=180 if a.expected_sha256==FIX else 90);blocked=v==1 and a.expected_sha256==AB
 assert source['passed']==(not blocked)
 base=R/'tests/current-inventory-powerups.lua';fixture=R/'tools/audit/current_cv3_powerups_v1.lua';assert sha(base)==BASE_SHA
 text=fixture.read_text();old=base.read_text();begin='-- All callback registration is startup-static.';end="emu.addEventCallback(function()\n if not entered"
 guards=old[old.index(begin):old.index(end)];assert len(guards.encode())==4058
 token='-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS\n';assert text.count(token)==1;generated=text.replace(token,guards)
 assert generated[generated.index(begin):generated.index(end)]==guards
 assert generated.count('emu.write(')==2 and generated.count('emu.takeScreenshot(')==1 and'images<8'in generated and'removeMemoryCallback'not in generated and'dofile('not in generated
 forbidden='InvOwnedLo InvOwnedHi InvViewedLo InvViewedHi InvSelected InvAmmo PlayerStatus PlayerSize GuestPowerupActive GuestPowerupTarget GameEngineSubroutine InjuryTimer GuestHurtTicks MmDeathFlag Cv3Health Cv3Hearts Cv3Power Cv3Subweapon Cv3Ready Cv3Bat Cv3BatTransform Cv3Climb Cv3AttackAge Cv3ShotType AvStopwatch Cv3FrozenTimer AvFrozen AvFrozenHi CheatInvincible'.split();allowed=ALLOWED+EXTRA_ALLOWED
 assert not set(allowed)&set(forbidden)
 for n in forbidden:assert "w('"+n+"'"not in generated
 def raw(n,d=0):return b['raw'][location(b,n)+d]
 def hook(n,d=0,size=3):
  at=location(b,n)+d;pc=address(b,n)+d;k=(at-16)//8192;bs=list(b['raw'][at:at+size]);banks=[k]
  if k==127:assert b['raw'][16+125*8192+(at-16)%8192:16+125*8192+(at-16)%8192+size]==bytes(bs);banks=[125,127]
  return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=d)
 hooks={key:hook(n)for key,n in {'PhysicalPickup':'MarioSourcePowerupCollision','Cv3CollectEntry':'Cv3CollectPickupGate','Defeat':'ShellOrBlockDefeat','NmiEntry':'NonMaskableInterrupt','IrqEntry':'IrqScrollSplit'}.items()}
 no=location(b,'Cv3CollectPickupGate::No');assert b['raw'][no-2:no]==bytes([0x38,0x60]);delta=address(b,'Cv3CollectPickupGate::No')-1-address(b,'Cv3CollectPickupGate');hooks['Cv3CollectAccepted']=hook('Cv3CollectPickupGate',delta,1)
 start=location(b,'GameLoop');assert b['raw'][start:start+5]==bytes([0xa9,255,0x8d,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8]);hooks['GameLoopOwned']=hook('GameLoop',5)
 for key,n,opcode in [('GameLoopFinish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40)]:
  d=int(b['syms'][n]['size'],0)-1;assert raw(n,d)==opcode;hooks[key]=hook(n,d,1)
 post=location(b,'PostDmaMaskEnable');m=address(b,'Mirror_PPUMASK');load=bytes([0xa5,m])if m<256 else bytes([0xad,m&255,m>>8])
 assert b['raw'][post-3:post]==bytes([0x8d,0x14,0x40])and b['raw'][post:post+len(load)+3]==load+bytes([0x8d,1,32]);hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
 writers={}
 for case in source['cases']:
  previous=case['heart_before']
  for _,value,pc,k in case['heart_writes']:
   kind='pickup'if case['kind']=='collect'else'drop'if case['kind']=='heart'else'bat'if case['kind']=='bat'else'watch-extra'if previous-value==4 else'debit'
   at=16+k*8192+(pc&8191);bs=list(b['raw'][at:at+3]);assert bs[0]in [0x99,0xde]and bs[1]+256*bs[2]==address(b,'Cv3Hearts')
   row=dict(pc=pc,bank=k,bytes=bs,kind=kind)
   if(pc,k)in writers:assert writers[(pc,k)]==row
   writers[(pc,k)]=row;previous=value
 assert writers and any(o['kind']=='drop'for o in writers.values())
 direct=set(re.findall(r'C\.ram\.([A-Za-z_][A-Za-z_0-9]*)',generated));names=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",generated))|direct|set(allowed)|{'CurrentBank','CurrentBankC','Sprite0HitDetectFlag'}
 ram={n:address(b,n)for n in names if n in b['syms']};assert names==set(ram),sorted(names-set(ram))
 items={208:dict(id=208,health_add=16,health_max=64,authored=1)}
 for item in [209,210,211]:items[item]=dict(id=item,carried=item-208,heart_add=5,heart_max=99,cost=5 if v==1 and item==211 else 1,authored=int(v<3))
 items[212]=dict(id=212,power_add=1,power_max=2,authored=int(v==3))
 nav=navigation(b['raw'],lambda n:location(b,n),5);assert len(nav)==19
 cfg=dict(ROM_sha256=a.expected_sha256,family=a.family,character=5,variant_value=v,mode=1,slot=5,frame_limit=16000,navigation=nav,plan=plan,items=items,ram=ram,hooks=hooks,heart_writers=list(writers.values()),setup_allowed={n:True for n in allowed},powerup_sfx=address(b,'Sfx_PowerUpGrab'),dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
 emitted=lua(cfg);preflight='local C=assert(CURRENT_CV3_POWERUPS);assert(C.mode==1 and C.character==5 and C.variant_value=='+str(v)+')\n'
 for item,data in items.items():
  assert f'[{item}]='in emitted and f'["{item}"]='not in emitted
  preflight+='assert(type(C.items['+str(item)+'])=="table" and '+' and '.join(f'C.items[{item}].{k}=={n}'for k,n in data.items())+',"typedCV3 reward '+str(item)+'")\n'
 for name,at in sorted(ram.items()):preflight+=f'assert(C.ram.{name}=={at},"realRAM {name}")\n'
 out.mkdir(parents=True);put(out/'config.json',cfg);put(out/'source-controls.json',source);fp=out/'fixture.lua';fp.write_text(generated,encoding='utf-8',newline='\n');(out/'run.lua').write_text('CURRENT_CV3_POWERUPS='+emitted+'\n'+preflight+'dofile([=['+fp.as_posix()+']=])\n',encoding='utf-8',newline='\n')
 layout=dict(passed=True,ROM_sha256=a.expected_sha256,variant=v,actual_CV3_reward_stamps=items,actual_hearts_writers=list(writers.values()),actual_current_E008_completion=hooks['DmaComplete'],unchanged_4058B_hardware_guard_sha256=hashlib.sha256(guards.encode()).hexdigest(),no_tested_resource_or_outcome_seeds=True,forbidden=forbidden,setup_allowlist=allowed,literal_numeric_reward_keys_and_every_direct_RAM_preflight=True,compiled_menu_BFS=nav,known_watch_blocked=blocked,source_only_limits='Original-source finite CPU and literal generated configuration only. No LuaVM/native scheduling, full physical rendering, waveform, alternate facing, zero/maxstock saturation, actual damaged healing, full natural reveal/drop lottery, or full campaign inferred.')
 put(out/'source-layout.json',layout)
 argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1800','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 command=dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,requires_existing_ROOT_capture_gate=True)
 command['blocked_argv_NOT_AUTHORIZED'if blocked else'argv']=argv
 if blocked:command['blocked_reason']='Known originalab stopwatch double tick. Strict180 native assertion retained; no authorised command until fresh fixed-parent composition.'
 put(out/'command.json',command)
 paths=[Path(__file__),R/'tools/audit/current_cv3_powerups_prepare_v1.py',fixture,base,R/'tools/audit/current_link_simon_powerups_prepare_v1.py',R/'tools/audit/current_roster_compact_11_v1.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py',R/'tools/audit/observe_chip_committed_write.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/audit/capture_budget.py',R/'tools/run_mesen.py',rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')]
 paths +=[R/'src'/n for n in ['cv3_core.s','cv3_abilities.s','cv3_pickups.s','cv3_combat.s','cv3_drops.s','cv3_draw.s','cv3_state.inc','remaining_weapons.s','mario_source.s','game.s','object.s']]
 paths +=[out/n for n in ['config.json','run.lua','fixture.lua','source-controls.json','source-layout.json','command.json']]
 if a.expected_sha256==FIX:paths +=[B/'cv3_watch_single_owner_handoff.json',B/'cv3_watch_single_owner_combat.s']
 ready=dict(status='BLOCKED_KNOWN_STRICT180_WATCH_FALSE'if blocked else'PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=a.expected_sha256,family=a.family,variant=v,mode=1,source_controls_passed=source['passed'],complete_source_GameLoops=source['GameLoop_calls'],actual_mature_reward_stamps=[t['item']for t in plan if t['kind']=='collect'],actual_physical_heart_actors=[1,5],caps=dict(wall_frames=16000,actual_updates=6500,host_seconds=1800,bytes=2000000000,files=64,PNGs=8,containers=0),setup='Only actual GameLoop+5/NmiDisableFF with NMI/IRQ excluded: disclosed floor/wall/roof/position, mature native actor5 with source-legal variant stamp, two physical heart-pool actor types and default-health Goomba target. No hero health/hearts/power/carried/transform/projectile/damage-outcome seeds.',limits=layout['source_only_limits'],bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in paths]);put(out/'prepared-not-run.json',ready)
 print(json.dumps(dict(status=ready['status'],ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),fresh_GameLoop_calls=source['GameLoop_calls'],native_run=False)))
if __name__=='__main__':main()
