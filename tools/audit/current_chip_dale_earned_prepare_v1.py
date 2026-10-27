"""Prepare Chip/Dale Hard earned components on adopted bdf9; ROOT launches only."""
from pathlib import Path
import argparse,hashlib,json,re,sys
from current_chip_dale_earned_cpu_v1 import SHA,PLAN,ALLOWED,FORBIDDEN,campaign
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import navigation
from current_shared_star_life_prepare_v1 import hooks_for
from observe_chip_committed_write import lua
R=Path(__file__).resolve().parents[2];B=R/'build';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--identity',choices=['chip','dale'],required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();assert not out.exists();variant=int(a.identity=='dale');rom=B/'cv3_life_gain_watch.nes';assert sha(rom)==SHA;b=scoped_load(rom)
 source_path=B/'current-bdf9-chip-dale-earned-source-v1.json';sources=json.loads(source_path.read_text());assert sources['passed']and len(sources['campaigns'])==4
 source=next(x for x in sources['campaigns']if x['variant']==variant and x['mode']==1);assert source['ROM_sha256']==SHA and source['passed']and source['plan']==PLAN
 base=R/'tests/current-inventory-powerups.lua';fixture=R/'tools/audit/current_chip_dale_earned_v1.lua';text=fixture.read_text();old=base.read_text();begin='-- All callback registration is startup-static.';end="emu.addEventCallback(function()\n if not entered";guards=old[old.index(begin):old.index(end)];assert len(guards.encode())==4058
 assert text.count('-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS\n')==1;text=text.replace('-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS\n',guards);assert text[text.index(begin):text.index(end)]==guards
 assert text.count('emu.write(')==2 and text.count('emu.takeScreenshot(')==1 and'images<8'in text and'removeMemoryCallback'not in text and'dofile('not in text
 assert not set(ALLOWED)&set(FORBIDDEN)
 for name in FORBIDDEN:assert "w('"+name+"'"not in text
 def hook(name,d=0,size=3):
  at=location(b,name)+d;k=(at-16)//8192;bs=list(b['raw'][at:at+size]);banks=[k]
  if k==127:assert b['raw'][16+125*8192+(at-16)%8192:16+125*8192+(at-16)%8192+size]==bytes(bs);banks=[125,127]
  return dict(pc=address(b,name)+d,banks=banks,bytes=bs,source_symbol=name,source_delta=d)
 hooks={key:hook(n)for key,n in{'PhysicalPickup':'HandlePowerUpCollision','FoodEntry':'CdCollectPickup','Defeat':'CdDefeatEnemy','Injury':'CdInjury','Release':'CdRelease','NmiEntry':'NonMaskableInterrupt','IrqEntry':'IrqScrollSplit'}.items()}
 at=location(b,'CdCollectPickup::No');assert b['raw'][at-2:at]==b'\x38\x60';hooks['FoodAccepted']=hook('CdCollectPickup',address(b,'CdCollectPickup::No')-address(b,'CdCollectPickup')-1,1)
 at=location(b,'GameLoop');nd=address(b,'NmiDisable');assert b['raw'][at:at+5]==bytes([169,255,141,nd&255,nd>>8]);hooks['GameLoopOwned']=hook('GameLoop',5)
 for key,name,op in[('GameLoopFinish','GameLoop',96),('NmiReturn','NonMaskableInterrupt',64),('IrqReturn','IrqScrollSplit',64)]:
  d=int(b['syms'][name]['size'],0)-1;assert b['raw'][location(b,name)+d]==op;hooks[key]=hook(name,d,1)
 hs,extra=hooks_for(b);hooks['LifeIncrement']=hs['LifeIncrement'];hooks['DmaComplete']=hs['DmaComplete']
 # Real source metadata preparation deliberately uses FF, never raw family14.
 q=Arena(b,14)
 for p in[0,1,3]:
  q.set('PowerUpType',p,5);q.invoke('CdPreparePickup',x=5);assert q.get('InvPickup',5)==252 and q.get('InvPickupOwner',5)==255 and q.get('PowerUpType',5)==p
 names=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'C\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))|set(ALLOWED)|set(FORBIDDEN)|set('CurrentBank CurrentBankC Sprite0HitDetectFlag'.split())
 ram={name:address(b,name)for name in sorted(names)}
 writers=source['health_writers'];assert{w['kind']for w in writers}=={'injury','small-food','full-food'}
 for w in writers:
  at=16+w['bank']*8192+(w['pc']&8191);assert list(b['raw'][at:at+3])==w['bytes']and w['bytes'][1:]==[ram['CdHealth']&255,ram['CdHealth']>>8]
 cfg=dict(ROM_sha256=SHA,family=a.identity,character=14,variant=variant,mode=1,frame_limit=16000,plan=PLAN,ram=ram,hooks=hooks,health_writers=writers,setup_allowed={n:True for n in ALLOWED},forbidden={n:True for n in FORBIDDEN},powerup_sfx=address(b,'Sfx_PowerUpGrab'),extra_life_sfx=extra,navigation=navigation(b['raw'],lambda n:location(b,n),14),dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
 assert len(cfg['navigation'])==19 and sum(bool(t.get('image'))for t in PLAN)==8
 # Literal numeric source-discriminant table and direct label preflight.
 cfg['foods']={0:dict(add=1,cap=3,next_status=1),1:dict(add=3,cap=3,next_status=0),3:dict(native_extra_life=1)}
 emitted=lua(cfg);pre=f'local C=assert(CURRENT_CHIP_DALE);assert(C.character==14 and C.variant=={variant} and C.mode==1 and #C.plan==12)\n'
 for key,data in cfg['foods'].items():
  assert f'[{key}]='in emitted and f'["{key}"]='not in emitted
  pre+='assert(type(C.foods['+str(key)+'])=="table" and '+' and '.join(f'C.foods[{key}].{n}=={v}'for n,v in data.items())+')\n'
 for n,value in ram.items():pre+=f'assert(C.ram.{n}=={value},"actual RAM {n}")\n'
 out.mkdir(parents=True);put(out/'config.json',cfg);put(out/'source-controls.json',source);fp=out/'fixture.lua';fp.write_text(text,encoding='utf-8',newline='\n');(out/'run.lua').write_text('CURRENT_CHIP_DALE='+emitted+'\n'+pre+'dofile([=['+fp.as_posix()+']=])\n',encoding='utf-8',newline='\n')
 layout=dict(passed=True,source_CPU_only=True,native_run=False,ROM_sha256=SHA,all_RAM_and_source_hook_bytes_verified=True,source_food_metadata_owner=255,actual_HP_writers=writers,exact_original_hardware_guard_bytes=4058,hardware_guard_sha256=hashlib.sha256(guards.encode()).hexdigest(),startup_static_callbacks_only=True,only_two_write_sites_guarded_to_actual_GameLoop_plus5_and_NmiDisableFF=True,no_acquired_HP_ammo_held_object_life_outcome_seeds=True,typed_numeric_food_keys_and_all_literal_RAM_preflight=True,images_max=8,real_capabilities='Mushroom+1HP/cap3; flowerfull3HP; actual source entrance crate pickup, hiding defense, authored brick lift, horizontal/upward release/real enemy defeat/cleanup. Native1Up after mushroom while carrying a real brick preserves HP/food-status/held object. No ammo/permanent weapon upgrade system exists for Chip/Dale; unusedFlowers/Stars counters asserted unchanged.',source_setup='Source campaigns stage initial cold PlayerStatus0/lives2/timer399, then only actor/map/position scenes. Native uses actual menu/cold initialization and never seeds those scalar outcomes.',limits='Prepared only, no native/LuaVM/audio/render/cadence result. Hard/native one identity per profile; both modes source-only. Mature actors not full reveal/rise/drop lottery. No Star2, generalized climb/jump/death/wrap or all-roster/all-art claim.')
 put(out/'source-layout.json',layout)
 argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1800','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,requires_existing_ROOT_capture_gate=True,argv=argv))
 paths=[Path(__file__),fixture,base,R/'tools/audit/current_chip_dale_earned_cpu_v1.py',R/'tools/audit/current_rygar_powerups_prepare_v1.py',R/'tools/audit/current_shared_star_life_prepare_v1.py',R/'tools/audit/current_roster_compact_11_v1.py',R/'tools/audit/observe_chip_committed_write.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/audit/capture_budget.py',R/'tools/run_mesen.py',rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),source_path,B/'current_chip_dale_earned_draft_negatives_v1.json',R/'docs/qa/cv3-life-watch-adoption-2026-10-27.json']
 paths +=[R/'src'/n for n in['chip_dale_core.s','chip_dale_health.s','chip_dale_boxes.s','chip_dale_motion.s','chip_dale_dispatch.s','chip_dale_render.s','chip_dale_state.inc','chip_dale_native_motion.inc','collision.s','mario_source.s','game.s']]
 paths +=[out/n for n in['config.json','source-controls.json','source-layout.json','run.lua','fixture.lua','command.json']]
 ready=dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=SHA,identity=a.identity,variant=variant,mode=1,source_campaign_passed=True,source_GameLoops=source['GameLoop_calls'],source_both_modes_also_in_combined_receipt=True,cases=12,real_collectibles=[dict(type=0,benefit='+1HP from actual2HP deficit'),dict(type=1,benefit='full3HP from actual1HP'),dict(type=3,benefit='native delayed1Up; earnedHP/status/held preserved')],caps=dict(wall_frames=16000,updates=6500,host_seconds=1800,bytes=2000000000,files=64,PNGs=8,containers=0),scope=layout['real_capabilities'],limits=layout['limits'],bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in paths]);put(out/'prepared-not-run.json',ready)
 print(json.dumps(dict(prepared=True,identity=a.identity,native_run=False,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),source_calls=source['GameLoop_calls'])))
if __name__=='__main__':main()
