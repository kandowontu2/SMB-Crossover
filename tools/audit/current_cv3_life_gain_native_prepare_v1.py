"""One earned Grant D1 -> physical1Up -> retained dagger native preparation only."""
from pathlib import Path
import argparse,hashlib,json,re,sys
from cv3_life_gain_controls_v1 import NEW,earned_life
from current_cv3_powerups_prepare_v1 import plans
from current_shared_star_life_prepare_v1 import hooks_for
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import navigation
from observe_chip_committed_write import lua
R=Path(__file__).resolve().parents[2];B=R/'build';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
def fixture():
 base=R/'tools/audit/current_cv3_powerups_watch_phase_v2.lua';text=base.read_text();changes=[]
 def replace(old,new):
  nonlocal text
  assert text.count(old)==1,old;text=text.replace(old,new);changes.append(dict(old=old,new=new))
 replace("rec={case_index=index", "rec={lives_before=r('NumberofLives'),life_collision=0,life_increment=0,life_writes=0,case_index=index")
 replace("if task.kind=='collect'then mature(task.item)","if task.kind=='collect'then mature(task.item)\n  elseif task.kind=='life'then mature(252);w('PowerUpType',3,5);w('Cv3PickupVariant',0,5)")
 replace("elseif phase=='wall'or phase=='ceiling'then",'''elseif phase=='life'then
  assert(age<120,'Bounded real1-Up popup cleanup')
  assert(r('Cv3Health',h)==rec.health_before and owned()==rec.power_before and coldHearts()==rec.heart_before and r('Cv3Subweapon',h)==rec.sub_before,'Earned CV3 fields preserved on every complete update through physical1-Up')
  assert(rec.sub_before==1 and rec.heart_before==15 and rec.health_before==64,'Genuinely earned nondefault D1/+5hearts before1-Up')
  assert(r('NumberofLives')==((rec.lives_before+rec.life_writes)&255),'Actual one source INC, no hidden life changes')
  if rec.life_writes==1 then
   assert(rec.life_collision==1 and rec.life_increment==1 and r('Cv3LastLife')==r('NumberofLives') and rec.life_sound,'Real physical collision, popupINC, acknowledgment and SFX')
   if r('FloateyNum_Control',5)==0 and dmas>=rec.life_dma+2 then screenshot='physical-1up-earned-D1-retained.png';finishCase()end
  end
 elseif phase=='wall'or phase=='ceiling'then''')
 at="-- Additional read-only witness: actual source birth/decrement stores and NPC"
 added='''-- New life-only witnesses are registered at startup, with exact source owners.
hook('PhysicalPickup',function(s)
 if entered and phase=='life'then
  assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128 and r('PowerUpType',5)==3 and r('InvPickupOwner',5)==5 and r('InvPickup',5)==252,'Actual mature native1-Up collision, no equipment/outcome seed')
  rec.life_collision=rec.life_collision+1;event('physical-1up-collision')
 end
end)
hook('LifeIncrement',function(s)
 if entered and phase=='life'then
  assert(s['cpu.x']==5 and rec.life_collision==1 and rec.life_increment==0 and r('NumberofLives')==rec.lives_before and r('FloateyNum_Control',5)==11 and r('FloateyNum_Timer',5)==42,'Genuine delayed native popupINC entry')
  rec.life_increment=rec.life_increment+1;rec.life_dma=dmas;event('actual-popup-inc-entry')
 end
end)
emu.addMemoryCallback(function(_,v)
 if not entered or phase~='life'or writing then return end
 local h=C.hooks.LifeIncrement;local s=emu.getState();assert(s['cpu.pc']==h.pc+3 and bank(h.pc)==h.banks[1] and rec.life_increment==1,'Actual native life INC bus owner')
 if v==rec.lives_before then event('actual-life-rmw-old',v);return end
 assert(v==((rec.lives_before+1)&255)and rec.life_writes==0,'Exactly one actual increment, including rollover');rec.life_writes=1;event('actual-life-gain',v)
end,emu.callbackType.write,C.ram.NumberofLives)
emu.addMemoryCallback(function(_,v)if entered and phase=='life'and v&C.extra_life_sfx~=0 then rec.life_sound=true;event('actual-extra-life-sfx',v)end end,emu.callbackType.write,C.ram.Square2SoundQueue)
'''
 replace(at,added+at)
 hardware=(R/'tests/current-inventory-powerups.lua').read_text();begin='-- All callback registration is startup-static.';end="emu.addEventCallback(function()\n if not entered";guards=hardware[hardware.index(begin):hardware.index(end)];assert len(guards.encode())==4058
 assert text.count('-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS\n')==1;text=text.replace('-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS\n',guards)
 assert text[text.index(begin):text.index(end)]==guards and text.count('emu.write(')==2 and text.count('emu.takeScreenshot(')==1 and'removeMemoryCallback'not in text
 return text,changes,hashlib.sha256(guards.encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();assert not out.exists()
 rom=B/'cv3_life_gain_watch.nes';assert sha(rom)==NEW;b=scoped_load(rom)
 controls=B/'cv3_life_gain_watch_controls.json';z=json.loads(controls.read_text());assert z['passed']and z['candidate_sha256']==NEW
 source=next(x for x in z['actual_earned_source_campaigns']if x['variant']==1 and x['mode']==1)
 old= B/'current-9a1b-grant-earned-hard-v2/config.json';cfg=json.loads(old.read_text());cfg['ROM_sha256']=NEW;cfg['family']='grant';cfg['plan']=[plans(1)[2],dict(kind='life',item=3,name='physical-1up-preserves-earned-D1',limit=120),plans(1)[3]]
 assert cfg['plan'][0]['item']==209 and cfg['plan'][2]['name']=='use-dagger'
 generated,changes,guardsha=fixture();cfg['items']={int(k):v for k,v in cfg['items'].items()}
 def hook(name,delta=0,size=3):
  at=location(b,name)+delta;k=(at-16)//8192;bs=list(b['raw'][at:at+size]);banks=[k]
  if k==127:assert b['raw'][16+125*8192+(at-16)%8192:16+125*8192+(at-16)%8192+size]==bytes(bs);banks=[125,127]
  return dict(pc=address(b,name)+delta,banks=banks,bytes=bs,source_symbol=name,source_delta=delta)
 for name,h in list(cfg['hooks'].items()):
  actual=hook(h['source_symbol'],h.get('source_delta',0),len(h['bytes']));assert actual==h,(name,h,actual);cfg['hooks'][name]=actual
 hs,extra=hooks_for(b);cfg['hooks']['LifeIncrement']=hs['LifeIncrement'];cfg['extra_life_sfx']=extra
 for name,h in [('watch_birth_store',cfg['watch_birth_store']),('watch_tick_store',cfg['watch_tick_store'])]:assert hook(h['source_symbol'],h['source_delta'],len(h['bytes']))==h
 allowed=list(cfg['setup_allowed']);forbidden='Cv3Health Cv3Hearts Cv3Power Cv3Subweapon Cv3Ready Cv3LastLife NumberofLives FloateyNum_Control FloateyNum_Timer CheatInvincible InjuryTimer GuestPowerupActive'.split();assert not set(allowed)&set(forbidden)
 for n in forbidden:assert "w('"+n+"'"not in generated
 names=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",generated))|set(re.findall(r'C\.ram\.([A-Za-z_][A-Za-z_0-9]*)',generated))|set(cfg['ram'])|set(allowed)
 cfg['ram']={n:address(b,n)for n in sorted(names)}
 cfg['navigation']=navigation(b['raw'],lambda n:location(b,n),5);assert len(cfg['navigation'])==19
 for n,o in cfg['metatiles'].items():assert o==dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)
 for o in cfg['heart_writers']:
  at=16+o['bank']*8192+(o['pc']&8191);assert list(b['raw'][at:at+len(o['bytes'])])==o['bytes']
 emitted=lua(cfg);pre='local C=assert(CURRENT_CV3_POWERUPS);assert(C.mode==1 and C.character==5 and C.variant_value==1 and #C.plan==3)\n'
 for item,data in cfg['items'].items():
  assert f'[{item}]='in emitted and f'["{item}"]='not in emitted
  pre+='assert(type(C.items['+str(item)+'])=="table" and '+' and '.join(f'C.items[{item}].{k}=={v}'for k,v in data.items())+')\n'
 for n,at in sorted(cfg['ram'].items()):pre+=f'assert(C.ram.{n}=={at},"actual RAM {n}")\n'
 out.mkdir(parents=True);put(out/'config.json',cfg);put(out/'source-controls.json',dict(source,exact_candidate_SHA=NEW,shared_watch_180_source_proof=str(controls),native_run=False));fp=out/'fixture.lua';fp.write_text(generated,encoding='utf-8',newline='\n');(out/'run.lua').write_text('CURRENT_CV3_POWERUPS='+emitted+'\n'+pre+'dofile([=['+fp.as_posix()+']=])\n',encoding='utf-8',newline='\n')
 put(out/'source-layout.json',dict(passed=True,native_run=False,unchanged_original_hardware_guard_bytes=4058,guard_sha256=guardsha,changes=changes,new_RAM=0,old_fixture_sha256=sha(R/'tools/audit/current_cv3_powerups_watch_phase_v2.lua'),old_fixture_unchanged=True,config_all_numeric_reward_keys_and_literal_RAM_preflight=True,actual_popup_INC_hook=cfg['hooks']['LifeIncrement'],setup='Only actual GameLoop+5/NmiDisableFF, NMI/IRQ excluded, disclosed flat logical/visible map and mature actor, source-legal D1 stamp then native1Up type3/FC. No life/earned health/hearts/power/carried/popup timer/outcome seeds.',caps=dict(wall_frames=16000,updates=6500,PNGs=8,files=64,bytes=2000000000),limits='One Grant Hard component, facing right. Earn D1/+5hearts, physical1Up native delayed INC/cleanup/retained fields, then real retained dagger/1heart debit/contact/cleanup. Does not retag old9a watch/health native, test death/life rollover natively, natural reveal/drop lottery, all variants, or waveform/blanket graphics.'))
 argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1800','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,requires_existing_ROOT_capture_gate=True,argv=argv))
 paths=[Path(__file__),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),controls,B/'cv3_life_gain_watch_build.json',B/'cv3_life_gain_watch_flagoff.json',B/'cv3_life_gain_watch_implementation.patch',B/'cv3_life_gain_watch_core.s',B/'cv3_life_gain_watch_helper.s',B/'cv3_watch_single_owner_combat.s',old,R/'tools/audit/current_cv3_powerups_watch_phase_v2.lua',R/'tests/current-inventory-powerups.lua',R/'tools/audit/cv3_life_gain_controls_v1.py',R/'tools/audit/cv3_life_gain_build_v1.py',R/'tools/audit/current_shared_star_life_prepare_v1.py',R/'tools/audit/current_cv3_powerups_prepare_v1.py',R/'tools/audit/current_link_simon_powerups_prepare_v1.py',R/'tools/audit/observe_chip_committed_write.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/audit/capture_budget.py',R/'tools/run_mesen.py']
 paths +=[R/'src'/n for n in['cv3_core.s','cv3_pickups.s','cv3_combat.s','cv3_state.inc','game.s','player.s','screen_render.s','mario_source.s','remaining_weapons.s']]
 paths +=[out/n for n in['config.json','fixture.lua','run.lua','source-controls.json','source-layout.json','command.json']]
 ready=dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,ROM_sha256=NEW,identity='grant',mode=1,source_campaign_passed=True,cases=['Actual D1 equipment+5hearts collection','Physical native1Up+delayed INC and popup cleanup retaining earned fields','Actual retained dagger allocation/cost1/contact/cleanup'],caps=dict(wall_frames=16000,updates=6500,host_seconds=1800,files=64,bytes=2000000000,PNGs=8,containers=0),bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in paths]);put(out/'prepared-not-run.json',ready)
 print(json.dumps(dict(prepared=True,native_run=False,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths))))
if __name__=='__main__':main()
