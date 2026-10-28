"""Seven actual differing Easy classic pickup/tier/primary components; no native."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_ee115_shared_star_life_prepare_v1 as shared
from observe_chip_committed_write import lua
sha=shared.sha;put=shared.put
IDS=('megaman','proto','samus','bill','lance','link','simon')
FIXTURE=R/'tests/current-ee115-classic-tiers-v1.lua'
OUT=R/'build/current-ee115-classic-tiers-v1'

BODY=r'''
local tier,index,rec,records=0,0,nil,{}
local function primary()
 local t={};local field,count
 if C.character==1 then field,count='MmBulletType',4 elseif C.character==2 then field,count='SmShotType',3 else field,count='RgShotType',10 end
 for i=0,count-1 do local v=r(field,i);if v~=0 then t[#t+1]=v end end
 return t
end
local function identity()
 assert(r('SelectedCharacter')==C.character and(not C.variant_name or r(C.variant_name)==C.variant)and r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0,'Actual Easy classic identity')
 assert(r('InvOwnedLo',C.character)==0 and r('InvOwnedHi',C.character)==0 and r('InvSelected',C.character)==0 and r('InvHudActive')==0,'Classic owns no modern inventory/HUD')
 assert(r('NumberofLives')==lives and r('InjuryTimer')==0 and r('MmDeathFlag')==0 and r('GuestHurtTicks')==0,'No injury/death/life outcome seeds')
end
local function beginUse()
 phase='use';age=0;rec={kind='primary',tier=tier,types={},max_pool=0,max_attack=0,sampled=false};records[#records+1]=rec
 event('real-primary-start',tier)
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==C.character and(not C.variant_name or r(C.variant_name)==C.variant)and r('CrossoverBehaviorVersion')==0,'Cold menu actual Easy classic')
  entered=true;phase='settle';age=0;lives=r('NumberofLives')
 end
 updates=updates+1;age=age+1;assert(updates<800,'Finite classic component updates');identity()
 if phase=='settle'and age>=30 then
  assert(r('PlayerStatus')==0 and r('GuestPowerupActive')==0,'Genuine cold small tier')
  transaction(arena);beginUse()
 elseif phase=='pickup-setup'then
  index=tier;phase='collect';age=0;rec={kind='pickup',raw_type=index,tier_before=tier,collisions=0,growth=0,begin=false,fallback=false};records[#records+1]=rec
  transaction(function()arena();actor(0x2e,5,index)end)
 elseif phase=='use-setup'then transaction(arena);beginUse()end
end)
hook('PhysicalPickup',function(s)
 if not entered then return end
 assert(phase=='collect'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128,'Genuine mature classic pickup')
 assert(r('PowerUpType',5)==index and r('InvPickup',5)==252,'No modern equipment grant masquerading as classic tier')
 rec.collisions=rec.collisions+1;rec.collision_update=updates;event('actual-classic-pickup',index)
end)
hook('InventoryCollect',function(s)
 if entered and phase=='collect'then assert(s['cpu.x']==5 and rec.collision_update==updates and r('Enemy_Flag',5)==0,'Native erase then actual inventory fallback');rec.fallback=true end
end)
hook('InventoryGrant',function()if entered then error('No modern equipment grant in classic Easy')end end)
hook('GuestBeginPowerup',function()
 if entered and phase=='collect'then assert(rec.fallback and r('PlayerStatus')==tier,'Genuine classic transformation entry');rec.begin=true end
end)
hook('GuestPowerupUpdate',function()if entered and phase=='collect'and r('GuestPowerupActive')~=0 then rec.growth=rec.growth+1 end end)
hook('GameLoopFinish',function()
 if not entered or done or phase=='settle'then return end
 identity();assert(r('GameEngineSubroutine')==8 or phase=='collect'and r('GameEngineSubroutine')==9,'Only actual native transformation may freeze engine')
 if phase=='collect'then
  if rec.begin and r('GuestPowerupActive')==0 then
   assert(rec.collisions==1 and rec.growth==60 and r('PlayerStatus')==tier+1 and r('TimerControl')==0 and r('Enemy_Flag',5)==0,'Actual collection and full60-update native growth')
   tier=tier+1;rec.tier_after=tier;rec.finished=updates;rec.publish_dma=dmas;phase='publish';age=0
  end
  assert(age<120,'Bounded classic transformation')
 elseif phase=='publish'then
  if dmas>=rec.publish_dma+2 then screenshot='classic-tier-'..tier..'.png';phase='use-setup';age=0 end
  assert(age<60,'Bounded post-transform publication')
 elseif phase=='use'then
  assert(r('PlayerStatus')==tier and r('GuestPowerupActive')==0,'Earned tier remains real during primary use')
  local p=primary();rec.max_pool=math.max(rec.max_pool,#p);rec.max_attack=math.max(rec.max_attack,r('RgAttack'));for _,v in ipairs(p)do rec.types[tostring(v)]=true end
  if(#p>0 or r('RgAttack')>0)and not rec.active_dma then rec.active_dma=dmas end
  if rec.active_dma and not rec.sampled and dmas>=rec.active_dma+2 and(#p>0 or r('RgAttack')>0)then screenshot='classic-primary-'..tier..'.png';rec.sampled=true end
  if age>=100 then
   local expected=C.primary[tier+1]
   assert(rec.max_pool==expected.max_pool and rec.max_attack==expected.max_attack,'Exact current compiled classic primary pool/melee behavior')
   for _,v in ipairs(expected.types)do assert(rec.types[tostring(v)],'Actual earned-tier primary type')end
   local n=0;for _ in pairs(rec.types)do n=n+1 end;assert(n==#expected.types,'No foreign primary type')
   assert(#p==0 and r('RgAttack')==0,'Actual primary/melee cleanup after released B')
   rec.finished=updates;if not rec.sampled then rec.sample_limit='No live two-DMA sample window; mechanics still required' end
   if tier==2 then done=true;phase='complete'else phase='pickup-setup';age=0 end
  end
  assert(age<=120,'Finite primary action/cleanup')
 end
 event('update',r('PlayerStatus'))
end)
local function input()return phase=='use'and age<4 and{b=true}or{}end
'''

END=r'''
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<8,'At most8 whole-frame PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<2200,'Finite2200 physical frame classic profile')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'All original actual hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,actual_mode=0,records=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,images=images,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
'''


def fixture():
    old=R/'tests/current-shared-star-life-vic-v2.lua';text=old.read_text()
    prefix=text[:text.index("hook('GameLoopOwned'")]
    prefix=prefix.replace('CURRENT_SHARED_STAR_LIFE','CURRENT_CLASSIC_TIERS').replace("OUTPUT..'star-life.csv'","OUTPUT..'classic-tiers.csv'")
    guard=text[text.index('-- All callback registration is startup-static.'):text.index('emu.addEventCallback(function()\n if not entered')]
    text=prefix+BODY+guard+"emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput(input(),0)end end,emu.eventType.inputPolled)\n"+END
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text
    if FIXTURE.exists():assert FIXTURE.read_text()==text,'Never alter frozen fixture'
    else:FIXTURE.write_text(text,newline='\n')
    return old


def campaign(b,ns,identity):
    _,char,vname,variant=ns['BASE'][identity];q=ns['Arena'](b,char)
    q.put(CrossoverBehaviorVersion=0,OperMode_Task=3,AreaType=1,PlayerStatus=0,Player_X_Position=112,Player_PageLoc=0,
          Player_Y_Position=176,Player_State=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1,Player_CollisionBits=255,Player_MovingDir=1)
    if vname:q.set(vname,variant)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for page in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,page*208+row*16+col)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    calls=0;out=[]
    def main(button=0):
        nonlocal calls
        q.set('SavedJoypadBits',button);calls+=1;q.invoke('GameLoop')
        assert q.get('InjuryTimer')==q.get('MmDeathFlag')==0
        assert q.get('InvOwnedLo',char)==q.get('InvOwnedHi',char)==q.get('InvSelected',char)==q.get('InvHudActive')==0
    for _ in range(30):main()
    for tier in range(3):
        assert q.get('PlayerStatus')==tier
        types=set();mp=ma=0
        name,count=('MmBulletType',4)if char==1 else('SmShotType',3)if char==2 else('RgShotType',10)
        for age in range(100):
            main(64 if age<4 else 0);p=[q.get(name,i)for i in range(count)if q.get(name,i)]
            types.update(p);mp=max(mp,len(p));ma=max(ma,q.get('RgAttack'))
        assert not any(q.get(name,i)for i in range(count))and q.get('RgAttack')==0,'Released real primary drains'
        out.append(dict(tier=tier,types=sorted(types),max_pool=mp,max_attack=ma))
        if tier<2:
            ns['actor'](q,46,5,tier,char);growth=0;pickup=False
            for age in range(120):
                if q.get('GuestPowerupActive'):growth+=1
                main()
                pickup|=q.get('Enemy_Flag',5)==0
                if q.get('PlayerStatus')==tier+1 and q.get('GuestPowerupActive')==0:break
            assert pickup and growth==60 and q.get('TimerControl')==0,(identity,tier,growth)
            for _ in range(4):main()
    assert out[0]['max_pool']or out[0]['max_attack'],'Real classic primary action required'
    return dict(passed=True,source_CPU_only=True,ROM_sha256=shared.EXPECTED,identity=identity,mode=0,full_GameLoop_calls=calls,
                pickups=[dict(raw_type=0,before=0,after=1,growth=60),dict(raw_type=1,before=1,after=2,growth=60)],primary=out,
                scope='Actual full GameLoop cold source context, real mature actor collision/transformation then actual B-input primary and cleanup at all3 tiers; no native/menu/PPU/interrupt claim.')


def main():
    assert not OUT.exists(),'No preparation/evidence overwrite'
    rom=R/'build/roster-20261028-fixes.nes';assert sha(rom)==shared.EXPECTED
    old=fixture();ns,_=shared.namespace();b=ns['scoped_load'](rom);OUT.mkdir();readies=[];held={}
    for identity in IDS:
        try:
            source=campaign(b,ns,identity);out=OUT/identity;out.mkdir()
            cfg=json.loads((R/'build/current-ee115-shared-star-life-v1'/identity/'config.json').read_text())
            cfg.update(mode=0,primary=source['primary'],scope='Two physical mature classic pickups, actual60-update growth each and primary use/cleanup at all3 earned tiers; no modern inventory. No native block reveal/rise, charge thresholds, damage/terrain contact or audio-waveform claim.')
            def hook(n):
                off=ns['location'](b,n);return dict(pc=ns['address'](b,n),banks=[(off-16)//8192],bytes=list(b['raw'][off:off+3]),source_symbol=n,source_delta=0)
            cfg['hooks'].update({n:hook(n)for n in ['InventoryCollect','InventoryGrant','GuestBeginPowerup','GuestPowerupUpdate']})
            names=set(re.findall(r"['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]",FIXTURE.read_text()))&set(b['syms'])
            cfg['ram'].update({n:ns['address'](b,n)for n in names})
            put(out/'config.json',cfg);put(out/'source-controls.json',source)
            preflight="local C=CURRENT_CLASSIC_TIERS;assert(C.mode==0 and type(C.primary[1])=='table'and type(C.primary[3])=='table');for i,p in ipairs(C.primary)do assert(type(p.tier)=='number'and p.tier==i-1 and type(p.types)=='table')end\n"
            (out/'run.lua').write_text('CURRENT_CLASSIC_TIERS='+lua(cfg)+'\n'+preflight+'dofile([=['+FIXTURE.as_posix()+']=])\n',newline='\n')
            argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
            put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
            paths={Path(__file__),FIXTURE,old,Path(shared.__file__),shared.MATRIX,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),R/'src/guest_powerups.s',R/'src/inventory_legacy_leaf.s',R/'src/roster_weapons.s',R/'src/samus_weapons.s',R/'src/megaman_weapons.s',R/'src/remaining_weapons.s',R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',R/'tools/audit/observe_chip_committed_write.py'}
            paths|={out/n for n in ['config.json','source-controls.json','run.lua','command.json']}
            put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,ROM_sha256=shared.EXPECTED,identity=identity,mode=0,
                source_calls=source['full_GameLoop_calls'],hardware_guard_literal_exact=True,no_acquired_state_seeds=True,caps=dict(wall_frames=2200,updates=800,host_seconds=1200,PNGs=8,files=64,bytes=2000000000),scope=cfg['scope'],bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]))
            readies.append(dict(identity=identity,path=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),command=str(out/'command.json')))
            print(json.dumps(dict(identity=identity,source_pass=True,primary=source['primary'])),flush=True)
        except Exception as e:
            held[identity]=repr(e);put(OUT/(identity+'-source-negative.json'),dict(native_run=False,source_pass=False,error=repr(e),ROM_sha256=shared.EXPECTED));print(json.dumps(dict(identity=identity,error=repr(e))),flush=True)
    put(OUT/'prepared-batch.json',dict(status='SOURCE_PREPARED_NOT_NATIVE',ROM_sha256=shared.EXPECTED,readies=readies,held=held,no_native_launch=True))
    print(json.dumps(dict(batch=str(OUT/'prepared-batch.json'),sha256=sha(OUT/'prepared-batch.json'),prepared=len(readies),held=len(held))))


if __name__=='__main__':main()
