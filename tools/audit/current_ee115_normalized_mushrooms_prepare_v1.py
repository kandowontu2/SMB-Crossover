"""Darkwing/Mike raw0 -> actual prepared mature-reward components; no native."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_ee115_shared_star_life_prepare_v1 as shared
from observe_chip_committed_write import lua
sha=shared.sha;put=shared.put
OUT=R/'build/current-ee115-normalized-mushrooms-v1'
FIXTURE=R/'tests/current-ee115-normalized-mushrooms-v1.lua'

BODY=r'''
local pickups,ownerCalls,rec=0,0,{}
local function values(want)
 for _,p in ipairs(want)do assert(r(p.name,p.index)==p.value,'Actual source-normalized benefit '..p.name..'['..p.index..']')end
end
local function identity()
 assert(r('SelectedCharacter')==C.character and(not C.variant_name or r(C.variant_name)==C.variant)and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual Hard owner/alternate')
 assert(r('NumberofLives')==lives and r('InjuryTimer')==0 and r('MmDeathFlag')==0,'No injury/death/life outcome seeds')
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then if r('GameEngineSubroutine')~=8 then return end;entered=true;phase='settle';age=0;lives=r('NumberofLives')end
 updates=updates+1;age=age+1;assert(updates<500,'Finite normalized pickup updates');identity()
 if phase=='settle'and age>=30 then
  values(C.before);phase='collect';age=0
  transaction(function()
   arena();actor(46,5,0);w('Enemy_Y_Position',r('Player_Y_Position')+8,5)
   for n,v in pairs(C.prepared_actor)do w(n,v,5)end
  end)
 end
end)
hook('PhysicalPickup',function(s)
 if not entered then return end
 assert(phase=='collect'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128,'Real mature normalized pickup')
 for n,v in pairs(C.prepared_actor)do assert(r(n,5)==v,'Frozen actual Prepare output before erase')end
 pickups=pickups+1;event('physical-normalized-pickup',r('InvPickup',5))
end)
hook('CollectOwner',function(s)
 if entered and phase=='collect'then assert(pickups==1 and s['cpu.x']==5 and r('Enemy_Flag',5)==0,'Actual native erase -> genuine private collector');ownerCalls=ownerCalls+1 end
end)
hook('GameLoopFinish',function()
 if not entered or done or phase=='settle'then return end
 identity();assert(r('GuestPowerupActive')==0 and r('GameEngineSubroutine')==8,'Private item never masquerades as a power transformation')
 if phase=='collect'then
  if pickups==1 then
   assert(ownerCalls==1 and r('Enemy_Flag',5)==0,'One physical normalized reward and actual owning collector');values(C.after)
   rec.collected_update=updates;rec.publish_dma=dmas;phase='publish';age=0
  end
  assert(age<60,'Bounded actual normalized pickup')
 elseif phase=='publish'then
  values(C.after)
  if dmas>=rec.publish_dma+2 then screenshot='normalized-mushroom.png';phase='effect';age=0 end
  assert(age<60,'Bounded real benefit publication')
 elseif phase=='effect'then
  if age>=20 then values(C.final)end
  if age>=120 then rec.finished_update=updates;done=true;phase='complete' end
 end
 event('update',pickups)
end)
local function input()return C.identity=='darkwing'and phase=='effect'and age<4 and{select=true}or{}end
'''
END=r'''
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<4,'At most4 original PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<1600,'Finite normalized mature pickup')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Original actual hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,actual_mode=1,raw_source_request=0,prepared_actor=C.prepared_actor,pickups=pickups,collector_calls=ownerCalls,record=rec,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,images=images,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
'''


def fixture():
    old=R/'tests/current-shared-star-life-vic-v2.lua';text=old.read_text()
    prefix=text[:text.index("hook('GameLoopOwned'")].replace('CURRENT_SHARED_STAR_LIFE','CURRENT_NORMALIZED_MUSHROOM').replace("OUTPUT..'star-life.csv'","OUTPUT..'normalized-mushroom.csv'")
    guard=text[text.index('-- All callback registration is startup-static.'):text.index('emu.addEventCallback(function()\n if not entered')]
    result=prefix+BODY+guard+"emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput(input(),0)end end,emu.eventType.inputPolled)\n"+END
    assert result.count('emu.write(')==2
    if FIXTURE.exists():assert FIXTURE.read_text()==result
    else:FIXTURE.write_text(result,newline='\n')
    return old


def campaign(b,ns,identity):
    _,char,vname,variant=ns['BASE'][identity];q=ns['Arena'](b,char)
    q.put(CrossoverBehaviorVersion=1,OperMode_Task=3,AreaType=1,PlayerStatus=0,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_State=0,
          ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1,Player_CollisionBits=255,Player_MovingDir=1)
    if vname:q.set(vname,variant)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for page in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,page*208+row*16+col)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    fields=[('PlayerStatus',1)]+([('DwHealth',1),('DwGas',1),('DwAdaptor',1),('DwMode',1)]if identity=='darkwing'else[('JnHealth',1),('JnMaxHearts',1),('JnOwnedTier',1),('JnSelected',1),('JnAmmo',10)])
    def snapshot():return[dict(name=n,index=i,value=q.get(n,i))for n,c in fields for i in range(c)]
    calls=0
    def main(button=0):
        nonlocal calls
        q.set('SavedJoypadBits',button);q.invoke('GameLoop');calls+=1
        assert q.get('InjuryTimer')==q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8
    for _ in range(30):main()
    before=snapshot();ns['actor'](q,46,5,0,char);q.set('Enemy_Y_Position',184,5)
    q.invoke('RlPrepareDispatch',x=5)
    prepared={n:q.get(n,5)for n in ['PowerUpType','InvPickupOwner','InvPickup']}
    assert prepared==dict(PowerUpType=1,InvPickupOwner=char,InvPickup=0x26 if identity=='darkwing'else 0x81),prepared
    for age in range(20):
        main()
        if q.get('Enemy_Flag',5)==0:break
    else:raise AssertionError('Actual normalized mature collection')
    after=snapshot()
    if identity=='darkwing':assert q.get('DwAdaptor')==1 and q.get('DwHealth')==4
    else:assert q.get('JnMaxHearts')==4 and q.get('JnHealth')==8
    for age in range(120):main(4 if identity=='darkwing'and age<4 else 0)
    final=snapshot()
    if identity=='darkwing':assert q.get('DwMode')==1,'Actual Select enables the earned Arrow adaptor'
    return dict(passed=True,source_CPU_only=True,ROM_sha256=shared.EXPECTED,identity=identity,mode=1,full_GameLoop_calls=calls,
                raw_source_request=0,prepare_owner='RlPrepareDispatch',prepared_actor=prepared,before=before,after=after,final=final,
                scope='Actual whole-source Prepare on raw0, then physical mature collision and real benefit. Mike gains real maximum heart3->4/HP6->8. Darkwing gains Arrow adaptor and real Select activation. No native producer/reveal/rise or audio/render claim.')


def main():
    assert not OUT.exists()
    rom=R/'build/roster-20261028-fixes.nes';assert sha(rom)==shared.EXPECTED
    old=fixture();ns,_=shared.namespace();b=ns['scoped_load'](rom);OUT.mkdir();readies=[];held={}
    for identity in ['darkwing','mike']:
        try:
            source=campaign(b,ns,identity);out=OUT/identity;out.mkdir()
            cfg=json.loads((R/'build/current-ee115-shared-star-life-v1'/identity/'config.json').read_text())
            cfg.update(prepared_actor=source['prepared_actor'],before=source['before'],after=source['after'],final=source['final'],scope=source['scope'])
            n='DwCollectPickup'if identity=='darkwing'else'JnCollectPickup';off=ns['location'](b,n)
            cfg['hooks']['CollectOwner']=dict(pc=ns['address'](b,n),banks=[(off-16)//8192],bytes=list(b['raw'][off:off+3]),source_symbol=n,source_delta=0)
            names=set(re.findall(r"['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]",FIXTURE.read_text()))&set(b['syms'])
            names|={p['name']for key in ['before','after','final']for p in cfg[key]}
            cfg['ram'].update({n:ns['address'](b,n)for n in names})
            put(out/'config.json',cfg);put(out/'source-controls.json',source)
            preflight="local C=CURRENT_NORMALIZED_MUSHROOM;assert(C.mode==1 and C.prepared_actor.PowerUpType==1 and type(C.before[1])=='table'and type(C.final[1])=='table');for _,q in ipairs({C.before,C.after,C.final})do for _,p in ipairs(q)do assert(type(C.ram[p.name])=='number'and type(p.index)=='number'and type(p.value)=='number')end end\n"
            (out/'run.lua').write_text('CURRENT_NORMALIZED_MUSHROOM='+lua(cfg)+'\n'+preflight+'dofile([=['+FIXTURE.as_posix()+']=])\n',newline='\n')
            argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
            put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
            paths={Path(__file__),FIXTURE,old,Path(shared.__file__),shared.MATRIX,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),R/'src/mike_jones_pickups.s',R/'src/darkwing_pickups.s',R/'src/inventory.s',R/'src/roll_dispatch.s',R/'src/mike_jones_dispatch.s',R/'tools/audit/observe_chip_committed_write.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py'}
            paths|={out/n for n in ['config.json','source-controls.json','run.lua','command.json']}
            put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,ROM_sha256=shared.EXPECTED,identity=identity,mode=1,hardware_guard_literal_exact=True,
                caps=dict(wall_frames=1600,updates=500,host_seconds=1200,PNGs=4,files=64,bytes=2000000000),no_acquired_state_seeds=True,scope=source['scope'],
                limitations='Native actor metadata derives from actual current source raw0 Prepare; native producer entry/full reveal/rise is not observed. Existing whole inventory native evidence stays on original hashes.',
                bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]))
            readies.append(dict(identity=identity,path=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),command=str(out/'command.json')))
            print(json.dumps(dict(identity=identity,source_pass=True,prepared_actor=source['prepared_actor'],after=source['after'],final=source['final'])),flush=True)
        except Exception as e:
            held[identity]=repr(e);put(OUT/(identity+'-source-negative.json'),dict(source_pass=False,native_run=False,error=repr(e),ROM_sha256=shared.EXPECTED));print(json.dumps(dict(identity=identity,error=repr(e))),flush=True)
    put(OUT/'prepared-batch.json',dict(status='SOURCE_PREPARED_NOT_NATIVE',ROM_sha256=shared.EXPECTED,readies=readies,held=held))
    print(json.dumps(dict(batch=str(OUT/'prepared-batch.json'),sha256=sha(OUT/'prepared-batch.json'),prepared=len(readies),held=len(held))))


if __name__=='__main__':main()
