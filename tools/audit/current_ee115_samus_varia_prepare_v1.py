"""Earned Varia versus actual firebar, with real unprotected injury comparison.

Source CPU and native preparation only. No native launch or gameplay edits.
"""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_ee115_shared_star_life_prepare_v1 as shared
from observe_chip_committed_write import lua
from verify_native_relocation import NesMPU
sha=shared.sha;put=shared.put
OUT=R/'build/current-ee115-samus-varia-firebar-v1'
FIXTURE=R/'tests/current-ee115-samus-varia-firebar-v1.lua'
EXTRA='MmVX MmVY MmXFraction MmYFraction MmOldX FirebarSpinSpeed FirebarSpinDirection'.split()

BODY=r'''
local item,stage,rec=0,0,nil
local records,contacts={},{}
local injuryCalls,variaCalls,injuryStarts=0,0,0
local function identity()
 assert(r('SelectedCharacter')==2 and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0 and r('StarInvincibleTimer')==0,'Actual uncheated SamusHard without Star protection')
 assert(r('NumberofLives')==lives and r('MmDeathFlag')==0,'No death or life changes')
end
local function scene()
 arena()
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('MmOldX',r('Player_X_Position'))
end
local function pickup(i)
 item=i;rec={item=i,stage=stage,collisions=0,growth=0,grants=0};records[#records+1]=rec
 transaction(function()scene();actor(46,5,i==0 and 0 or 1);w('Enemy_Y_Position',184,5);w('InvPickup',i,5)end)
 phase='collect';age=0
end
local function firebar()
 scene()
 for n,v in pairs(C.firebar)do w(n,v,0)end
 w('Enemy_X_Position',r('Player_X_Position')+4,0);w('Enemy_PageLoc',r('Player_PageLoc'),0)
 w('Enemy_Y_Position',r('Player_Y_Position')+12,0)
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then if r('GameEngineSubroutine')~=8 then return end;entered=true;phase='settle';age=0;lives=r('NumberofLives')end
 updates=updates+1;age=age+1;assert(updates<900,'Finite actual Varia component');identity()
 if phase=='settle'and age>=30 then
  assert(r('PlayerStatus')==0 and r('InvOwnedLo',2)==0 and r('InvOwnedHi',2)==0,'Unpowered actual cold Samus')
  stage=1;pickup(0)
 elseif phase=='unprotected-setup'then
  assert(r('PlayerStatus')==1 and r('InvOwnedLo',2)==129 and r('InjuryTimer')==0,'Earned Long/mushroom, no Varia or protection')
  transaction(firebar);phase='unprotected';age=0
 elseif phase=='remove-hazard'then
  transaction(function()w('Enemy_Flag',0,0)end);phase='recovery';age=0
 elseif phase=='second-mushroom'then stage=2;pickup(0)
 elseif phase=='varia-setup'then stage=3;pickup(5)
 elseif phase=='protected-setup'then
  assert(r('PlayerStatus')==1 and r('InvOwnedLo',2)==161 and r('InvOwnedHi',2)==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0 and r('GuestInvulTicks')==0 and r('SmFlip')==0,'Only earned Varia can protect this contact')
  transaction(firebar);phase='protected';age=0;rec={kind='Varia-firebar',before_injury_calls=injuryCalls,before_starts=injuryStarts,branch_calls=0};records[#records+1]=rec
 elseif phase=='protected-remove'then transaction(function()w('Enemy_Flag',0,0)end);phase='drain';age=0 end
end)
hook('PhysicalPickup',function(s)
 if not entered then return end
 assert(phase=='collect'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128 and r('InvPickupOwner',5)==2 and r('InvPickup',5)==item,'Actual earned mature Samus pickup')
 rec.collisions=rec.collisions+1;event('actual-pickup',item)
end)
hook('InventoryGrant',function(s)if entered and phase=='collect'then assert(item==5 and s['cpu.a']==5,'Only actual Varia grant');rec.grants=rec.grants+1 end end)
hook('GuestPowerupUpdate',function()if entered and phase=='collect'and r('GuestPowerupActive')~=0 then rec.growth=rec.growth+1 end end)
hook('FirebarBranch',function(s)
 if not entered then return end
 assert(phase=='unprotected'or phase=='protected','Firebar only in disclosed comparison scenes')
 assert(r('ObjectOffset')==0 and r('Enemy_ID',0)==27 and r('Enemy_Flag',0)~=0,'Actual native firebar owner')
 local carry=assert(s['cpu.ps'],'Actual CPU flags')&1
 assert(carry==(phase=='protected'and 1 or 0),'Real InventoryHasVaria return controls actual native firebar branch')
 contacts[#contacts+1]={phase=phase,update=updates,carry=carry,x=r('R6'),y=r('R7'),playerX=r('Player_Rel_XPos'),playerY=r('Player_Y_Position'),pc=s['cpu.pc'],bank=bank(s['cpu.pc'])}
 if phase=='protected'then variaCalls=variaCalls+1;rec.branch_calls=rec.branch_calls+1 end
 event('actual-firebar-distance-admitted',carry)
end)
hook('FirebarInjure',function()if entered then assert(phase=='unprotected','Earned Varia must bypass actual InjurePlayer call');injuryCalls=injuryCalls+1;event('actual-unprotected-firebar-injury-call')end end)
hook('InjuryStarted',function()if entered then assert(phase=='unprotected','Only actual unprotected comparison can start injury');injuryStarts=injuryStarts+1;event('real-injury-start')end end)
hook('GameLoopFinish',function()
 if not entered or done or phase=='settle'then return end
 identity()
 if phase=='collect'then
  if rec.collisions==1 and r('GuestPowerupActive')==0 then
   assert(r('Enemy_Flag',5)==0 and r('PlayerStatus')==1 and r('InvOwnedLo',2)==(item==5 and 161 or 129),'Actual acquired state comes only from collision')
   assert(rec.growth==(item==0 and 60 or 0)and rec.grants==(item==5 and 1 or 0),'Exact real growth/grant counts')
   rec.publish_dma=dmas;rec.complete_update=updates;phase='publish';age=0
  end
  assert(age<120,'Bounded real pickup/transform')
 elseif phase=='publish'then
  if dmas>=rec.publish_dma+2 then screenshot=stage==1 and'01-earned-before-hazard.png'or stage==2 and'03-reacquired-mushroom.png'or'04-earned-varia.png';phase=stage==1 and'unprotected-setup'or stage==2 and'varia-setup'or'protected-setup';age=0 end
  assert(age<60,'Bounded actual publication')
 elseif phase=='unprotected'then
  if injuryStarts>0 then
   assert(injuryStarts==1 and injuryCalls>0 and r('PlayerStatus')==0 and r('InvOwnedLo',2)==0 and r('InjuryTimer')~=0,'Same real firebar damages unprotected earned Samus')
   phase='remove-hazard';age=0
  end
  assert(age<40,'Actual unprotected contact required')
 elseif phase=='recovery'then
  if age>=90 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0 and r('GuestInvulTicks')==0 and r('Player_State')==0 then
   screenshot='02-real-injury-recovered.png';phase='second-mushroom';age=0
  end
  assert(age<300,'Natural recoil/protection expiry and landing')
 elseif phase=='protected'then
  assert(r('PlayerStatus')==1 and r('InvOwnedLo',2)==161 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0 and r('GuestInvulTicks')==0 and r('SmFlip')==0 and r('Player_State')==0,'Actual Varia retains power through unprotected body contact')
  assert(injuryCalls==rec.before_injury_calls and injuryStarts==rec.before_starts and r('FirebarPartCount',0)==6,'Actual six-part native firebar without injury')
  if age>=4 and variaCalls>0 and not rec.sample_dma then rec.sample_dma=dmas end
  if rec.sample_dma and dmas>=rec.sample_dma+2 and not rec.sampled then screenshot='05-varia-real-firebar-contact.png';rec.sampled=true end
  if age>=24 then assert(rec.branch_calls>=24 and rec.sampled,'Repeated real distance-admitted contacts and actual live sample');phase='protected-remove';age=0 end
 elseif phase=='drain'then
  assert(r('PlayerStatus')==1 and r('InvOwnedLo',2)==161 and r('InjuryTimer')==0,'Protection does not hide delayed damage')
  if age>=45 then done=true;phase='complete' end
 end
 event('update',r('PlayerStatus'))
end)
'''

END=r'''
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<8,'At most8 original PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<2600,'Finite Varia comparison physical frames')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Original actual hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity='samus',actual_mode=1,records=records,contacts=contacts,unprotected_injury_calls=injuryCalls,real_injury_starts=injuryStarts,protected_Varia_branches=variaCalls,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,images=images,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
'''


def fixture():
    old=R/'tests/current-shared-star-life-vic-v2.lua';text=old.read_text()
    prefix=text[:text.index("hook('GameLoopOwned'")].replace('CURRENT_SHARED_STAR_LIFE','CURRENT_SAMUS_VARIA').replace("OUTPUT..'star-life.csv'","OUTPUT..'varia-firebar.csv'")
    guard=text[text.index('-- All callback registration is startup-static.'):text.index('emu.addEventCallback(function()\n if not entered')]
    result=prefix+BODY+guard+"emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput({},0)end end,emu.eventType.inputPolled)\n"+END
    assert result.count('emu.write(')==2 and not re.search(r'\b(?:and|or|else)\d',result),'Valid Lua keyword token boundaries'
    if FIXTURE.exists():assert FIXTURE.read_text()==result
    else:FIXTURE.write_text(result,newline='\n')
    return old


def firebar(b,ns):
    raw=b['raw'];at=ns['location']
    return dict(Enemy_Flag=1,Enemy_ID=27,Enemy_State=0,Enemy_BoundBoxCtrl=9,Enemy_Y_HighPos=1,EnemyOffscrBitsMasked=0,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_SprAttrib=0,Enemy_CollisionBits=0,
                FirebarSpinSpeed=raw[at(b,'FirebarSpinSpdData')],FirebarSpinDirection=raw[at(b,'FirebarSpinDirData')])


def hooks(b,ns):
    out,_=ns['hooks_for'](b)
    def add(key,n,delta=0,size=3):
        p=ns['location'](b,n)+delta;out[key]=dict(pc=ns['address'](b,n)+delta,banks=[(p-16)//8192],bytes=list(b['raw'][p:p+size]),source_symbol=n,source_delta=delta)
    for n in ['InventoryGrant','GuestPowerupUpdate']:add(n,n)
    add('InjuryStarted','GuestInjuryStarted')
    safe=ns['location'](b,'VariaFirebarSafe');inj=ns['address'](b,'InjurePlayer')
    assert b['raw'][safe-5:safe]==bytes([176,3,32,inj&255,inj>>8]),'Actual BCS VariaSafe then JSR InjurePlayer'
    add('FirebarBranch','VariaFirebarSafe',-5,2);add('FirebarInjure','VariaFirebarSafe',-3)
    return out


def campaign(b,ns,h):
    q=ns['Arena'](b,2);q.put(CrossoverBehaviorVersion=1,OperMode_Task=3,AreaType=1,PlayerStatus=0)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
    phase='settle';calls=0;injures=starts=0;contacts=[];trace=[];original=NesMPU.step
    lookup={(a['pc'],k):n for n,a in h.items()for k in a['banks']if n in ['FirebarBranch','FirebarInjure','InjuryStarted']}
    def step(c):
        nonlocal injures,starts
        k=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1;n=lookup.get((c.pc,k))
        if n=='FirebarBranch':
            assert phase in ['unprotected','protected'];want=int(phase=='protected');assert c.p&1==want
            contacts.append(dict(phase=phase,call=calls,carry=c.p&1,x=q.get('R6'),y=q.get('R7'),playerY=q.get('Player_Y_Position')))
        elif n=='FirebarInjure':assert phase=='unprotected';injures+=1
        elif n=='InjuryStarted':assert phase=='unprotected';starts+=1
        original(c)
    def tick():
        nonlocal calls
        q.set('SavedJoypadBits',0);calls+=1;q.invoke('GameLoop');assert q.get('MmDeathFlag')==0
        # Actual consumer plus only InitBuffer's two clear stores: no fake
        # never-consumed queue and no native timing/PPU claim from source CPU.
        p=ns['address'](b,'VRAM_Buffer1');q.put(NmiR0=p&255,NmiR1=p>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1_Offset=0,VRAM_Buffer1=0)
    def scene():
        for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
        for page in range(2):
            for row in [11,12]:
                for col in range(16):q.set('Block_Buffer_1',84,page*208+row*16+col)
        for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
        q.put(Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=1,Player_MovingDir=1,Player_CollisionBits=255,
              ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1,MmOldX=112,Player_X_Speed=0,Player_Y_Speed=0,Player_X_MoveForce=0,Player_Y_MoveForce=0)
        for n,z in [('MmVX',3),('MmVY',3),('MmXFraction',2),('MmYFraction',2)]:q.array(n,[0]*z)
    def collect(item):
        nonlocal phase
        scene();phase='collect';ns['actor'](q,46,5,0 if item==0 else 1,2);q.set('Enemy_Y_Position',184,5);q.set('InvPickup',item,5);growth=0
        for age in range(120):
            if q.get('GuestPowerupActive'):growth+=1
            tick()
            if q.get('Enemy_Flag',5)==0 and q.get('GuestPowerupActive')==0:break
        assert q.get('PlayerStatus')==1 and growth==(60 if item==0 else 0),(item,growth,q.get('PlayerStatus'))
        trace.append(dict(event='actual-mature-pickup',item=item,growth=growth,call=calls,owned=q.get('InvOwnedLo',2)))
        for _ in range(4):tick()
    def hazard():
        scene()
        for n,v in firebar(b,ns).items():q.set(n,v,0)
        q.set('Enemy_X_Position',116,0);q.set('Enemy_PageLoc',0,0);q.set('Enemy_Y_Position',188,0);q.set('Enemy_Y_HighPos',1,0)
    NesMPU.step=step
    try:
        scene()
        for _ in range(30):tick()
        collect(0);assert q.get('InvOwnedLo',2)==129
        hazard();phase='unprotected'
        for age in range(40):
            tick()
            if starts:break
        assert starts==1 and injures>0 and q.get('PlayerStatus')==0 and q.get('InvOwnedLo',2)==0 and q.get('InjuryTimer')>0
        trace.append(dict(event='real-unprotected-firebar-injury',call=calls,status=0,owned=0))
        q.set('Enemy_Flag',0,0);phase='recovery'
        for age in range(300):
            tick()
            if age>=90 and q.get('InjuryTimer')==q.get('GuestHurtTicks')==q.get('GuestInvulTicks')==0 and q.get('Player_State')==0:break
        else:raise AssertionError('Natural Samus recovery')
        trace.append(dict(event='natural-protection-expiry',call=calls,updates=age+1))
        collect(0);collect(5);assert q.get('InvOwnedLo',2)==161
        hazard();phase='protected';before=injures
        for age in range(24):
            tick();assert q.get('PlayerStatus')==1 and q.get('InvOwnedLo',2)==161 and q.get('InjuryTimer')==q.get('GuestHurtTicks')==q.get('GuestInvulTicks')==q.get('SmFlip')==q.get('Player_State')==0
            assert q.get('FirebarPartCount',0)==6
        assert injures==before and starts==1 and len([a for a in contacts if a['phase']=='protected'])>=24
        q.set('Enemy_Flag',0,0);phase='drain'
        for _ in range(45):tick()
    finally:NesMPU.step=original
    return dict(passed=True,source_CPU_only=True,ROM_sha256=shared.EXPECTED,full_GameLoop_calls=calls,events=trace,contacts=contacts,injury_calls=injures,injury_starts=starts,
                source_consumer='Actual SamusFreezeUpdateScreen between Main calls, then two native InitBuffer zero stores. No actual NMI/timing/audio claim.',
                scope='Real acquired mushroom then native firebar distance branch/InjurePlayer/resource loss, natural recoil/protection expiry, real mushroom reacquisition and Varia5 collection, same six-part firebar protected24updates,45neutral cleanup. No acquired state/HP/invulnerability/outcome seeds.')


def main():
    assert not OUT.exists();rom=R/'build/roster-20261028-fixes.nes';assert sha(rom)==shared.EXPECTED
    ns,_=shared.namespace();b=ns['scoped_load'](rom);h=hooks(b,ns);OUT.mkdir()
    try:source=campaign(b,ns,h)
    except Exception as e:
        put(OUT/'source-negative.json',dict(source_pass=False,native_run=False,error=repr(e),ROM_sha256=shared.EXPECTED));raise
    old=fixture();cfg=json.loads((R/'build/current-ee115-shared-star-life-v1/samus/config.json').read_text())
    cfg.update(hooks=h,firebar=firebar(b,ns),scope=source['scope'])
    cfg['setup_allowed'].update({n:True for n in EXTRA})
    names=(set(re.findall(r"['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]",FIXTURE.read_text()))&set(b['syms']))|set(EXTRA)|set(cfg['firebar'])
    cfg['ram'].update({n:ns['address'](b,n)for n in names})
    for n in re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",FIXTURE.read_text()):assert n in cfg['ram'],n
    assert not set(cfg['setup_allowed'])&set(cfg['resource_bans'])
    put(OUT/'config.json',cfg);put(OUT/'source-controls.json',source)
    preflight="local C=CURRENT_SAMUS_VARIA;assert(C.mode==1 and C.character==2 and C.firebar.Enemy_ID==27);for n,v in pairs(C.firebar)do assert(type(v)=='number'and type(C.ram[n])=='number'and C.setup_allowed[n]and not C.resource_bans[n])end\n"
    (OUT/'run.lua').write_text('CURRENT_SAMUS_VARIA='+lua(cfg)+'\n'+preflight+'dofile([=['+FIXTURE.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(OUT/'native'),str(OUT/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(OUT/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths={Path(__file__),FIXTURE,old,Path(shared.__file__),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),R/'src/object.s',R/'src/collision.s',R/'src/guest_injury.s',R/'src/remaining_weapons.s',R/'src/inventory.s',R/'src/inventory_data.inc',R/'src/guest_powerups.s',R/'src/samus.s',R/'tests/current-samus-powerups.lua',R/'tools/audit/current_samus_powerups_prepare_v1.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',R/'tools/audit/observe_chip_committed_write.py'}
    paths|={OUT/n for n in ['config.json','source-controls.json','run.lua','command.json']}
    put(OUT/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,ROM_sha256=shared.EXPECTED,identity='samus',mode=1,source_calls=source['full_GameLoop_calls'],scope=source['scope'],hardware_guard_literal_exact=True,
        no_acquired_state_seeds=True,caps=dict(wall_frames=2600,updates=900,host_seconds=1200,PNGs=8,files=64,bytes=2000000000),
        setup='Actual GameLoop+5 NmiDisableFF, no NMI/IRQ; logical/visible map and complete scene/player position/motion, mature earned item metadata, initialized native short firebar with actual table speed/direction. Hazard removed only after actual injury, never protection/reset seeded.',
        limits='Hard only, actual physical mature actors and staged firebar origin. Natural reveal/rise/lottery or original attack art/audio fidelity not inferred. PNGs delayed by2real completeDMAs; ROOT native/whole-image review still required.',
        bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]))
    print(json.dumps(dict(ready=str(OUT/'prepared-not-run.json'),sha256=sha(OUT/'prepared-not-run.json'),source_calls=source['full_GameLoop_calls'],native_run=False)))


if __name__=='__main__':main()
