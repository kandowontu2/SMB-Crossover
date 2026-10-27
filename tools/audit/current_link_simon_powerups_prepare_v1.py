"""Prepare bounded earned Link/Simon Hard inventory components; never run Mesen."""
from pathlib import Path
import argparse, hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from observe_chip_committed_write import lua
from verify_native_relocation import NesMPU

EXPECTED = '9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
BASE_SHA = 'bcc2419a25ecc0d465dddd3f08b96a212d57c38703c61bbd2c2fddbdd5f24fa2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
put = lambda p,z: p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def plans(char):
    def collect(item, **kw): return dict(name=f'collect-{item:02d}',kind='collect',item=item,**kw)
    def use(item, shot, proxy, **kw): return dict(name=f'use-{item:02d}',kind='use',item=item,shot=shot,proxy=proxy,limit=300,**kw)
    if char == 4:
        return [collect(0),collect(6),use(6,5,18,stop=True),collect(1),collect(4),collect(5),
                use(1,34,61,initial=33),collect(2),use(2,32,59),collect(3),
                use(3,5,18,stop=True),dict(name='bomb-refill',kind='refill',item=254,ammo_item=1,amount=2)]
    return [collect(0),collect(9),collect(1),collect(2),use(2,35,62),collect(3),
            use(3,37,64,initial=36),dict(name='large-heart',kind='refill',item=254,ammo_item=0,amount=5),
            collect(4),dict(name='use-watch',kind='use',item=4,shot=0,proxy=0,watch=True,limit=300),
            collect(5),use(5,38,65),collect(6),use(6,6,22),
            dict(name='second-large-heart',kind='refill',item=254,ammo_item=0,amount=5),
            collect(7),collect(2)|dict(name='reacquire-dagger'),use(2,35,62)|dict(expected_limit=2,name='double-dagger'),
            collect(8),use(2,35,62)|dict(expected_limit=3,name='triple-dagger')]

ALLOWED = '''Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits InvDropKind Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce ScrollThirtyTwo AreaParserTaskNum MmVX MmVY MmXFraction MmYFraction ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc Player_X_Position Player_PageLoc MmOldX Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_SprAttrib PowerUpType InvPickupOwner InvPickup AvPickupAmmoItem Enemy_Y_MoveForce Enemy_MovingDir EnemyOffscrBitsMasked MmEnemyHealthLo MmEnemyHealthHi MmEnemyFlash RgEnemyStun'''.split()

def setup(q, char, task):
    assert all(q.get('RgShotType',s)==0 for s in range(10))
    assert q.get('RgAttack')==q.get('RgShootPose')==q.get('AvStopwatch')==0
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']: q.array(n,[0]*416)
    for page in (0,1):
        for row in (11,12):
            for col in range(16): q.set('Block_Buffer_1',0x54,page*208+row*16+col)
    for i in range(6): q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    for i in range(4): q.set('InvDropKind',0,i)
    q.put(Player_X_Position=64,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,
          Player_State=0,PlayerFacingDir=1,Player_MovingDir=1,Player_CollisionBits=255,
          MmOldX=64,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,
          ScreenRight_X_Pos=255,ScrollLock=1,ScrollThirtyTwo=0,AreaParserTaskNum=0,
          Player_X_Speed=0,Player_Y_Speed=0,Player_X_MoveForce=0,Player_Y_MoveForce=0)
    for n,size in [('MmVX',3),('MmVY',3),('MmXFraction',2),('MmYFraction',2)]:q.array(n,[0]*size)
    if task['kind'] in ('collect','refill'):
        for n,v in dict(Enemy_Flag=1,Enemy_ID=0x2e,Enemy_State=128,Enemy_BoundBoxCtrl=3,
                        Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,
                        Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_SprAttrib=0,
                        PowerUpType=0 if task['item']==0 else 1,InvPickupOwner=char,InvPickup=task['item']).items():q.set(n,v,5)
        if task['kind']=='refill':q.set('AvPickupAmmoItem',task['ammo_item'],5)

def target(q, x, y):
    for n,v in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=x,
                    Enemy_PageLoc=0,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,
                    Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=1,Enemy_BoundBoxCtrl=9,
                    EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,MmEnemyHealthLo=0,MmEnemyHealthHi=0,
                    MmEnemyFlash=0,RgEnemyStun=0).items():q.set(n,v,0)

def source_campaign(b,char,plan):
    q=Arena(b,char);q.invoke('InventoryInit');q.put(PlayerStatus=0,OperMode_Task=3,AreaType=1)
    q.array('GameTimerDisplay',[3,9,9]);q.put(CrossoverBehaviorVersion=1)
    if char==4:q.set('Z2Variant',0)
    else:q.set('Cv3Variant',0)
    out=[];original=NesMPU.step;trace=None;age=0
    owners={}
    for n in ['MarioSourcePowerupCollision','InventoryCollect','InventoryGrant','InventorySpend',
              'GuestPowerupUpdate','MegaManWeapons::DamageEnemy','LsrEffectsBoomerang',
              'AvRosterSpecial','AvSimonRelease','RemainingPower','GameLoop']:
        owners[(address(b,n),(location(b,n)-16)//8192)]=n
    def step(c):
        k=q.m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        n=owners.get((c.pc,k))
        if n and trace is not None:
            if n=='GameLoop':trace['GameLoop_calls']=trace.get('GameLoop_calls',0)+1
            if n not in trace['owners']:trace['owners'].append(n)
            if n=='MarioSourcePowerupCollision':assert c.x==5;trace['collections']+=1
            if n=='GuestPowerupUpdate' and q.get('GuestPowerupActive'):trace['growth']+=1
            if n=='InventorySpend':trace['spends'].append([age,c.a,c.y])
            if n in ('MegaManWeapons::DamageEnemy','LsrEffectsBoomerang') and c.x==0:
                trace['contacts'].append([age,n,q.get('MmBulletType')])
        original(c)
    NesMPU.step=step
    try:
        for task in plan:
            setup(q,char,task)
            item=task['item'];idx=char*16+(0 if char==5 else item)
            trace=dict(name=task['name'],owners=[],collections=0,growth=0,spends=[],contacts=[],
                       types=[],stock_before=q.get('InvAmmo',idx if item<16 else char*16+task['ammo_item']))
            before_owned=q.get('InvOwnedLo',char)+256*q.get('InvOwnedHi',char)
            if task['kind']=='use':
                # Real paused UI cycles only; never seed selected weapon.
                selection=[]
                if q.get('InvSelected',char)!=item:
                    for t in range(180):
                        bits=16 if t%12==1 else 0;q.set('SavedJoypadBits',bits);q.invoke('GameLoop')
                        if q.get('GamePauseStatus')&1:break
                    assert q.get('GamePauseStatus')&1
                    for t in range(240):
                        bits=1 if t%8==1 else 0;q.set('SavedJoypadBits',bits);q.invoke('GameLoop')
                        selection.append([bits,q.get('InvSelected',char),q.get('GamePauseStatus'),q.get('GamePauseTimer')])
                        if q.get('InvSelected',char)==item:break
                    assert q.get('InvSelected',char)==item,(char,item,'selection',selection)
                    for t in range(180):
                        bits=16 if t%12==1 else 0;q.set('SavedJoypadBits',bits);q.invoke('GameLoop')
                        if q.get('GamePauseStatus')&1==0:break
                    assert q.get('GamePauseStatus')&1==0
                    q.set('SavedJoypadBits',0);q.invoke('GameLoop')
                    trace['paused_selection']=selection
                trace['spends']=[];trace['contacts']=[]
                if task.get('watch'):target(q,192,184);q.set('Enemy_X_Speed',248,0)
            placed=False;watch_seen=False;watch_zero=False;effect_first=None
            for age in range(task.get('limit',150)+1):
                bits=32 if task['kind']=='use' and age==6 else 0
                q.set('SavedJoypadBits',bits)
                if task['kind']=='use' and not task.get('watch') and not placed:
                    for s in range(10):
                        if q.get('RgShotType',s)==task['shot'] and q.get('RgShotPage',s)==0 and (16 if task['shot']==34 else 100)<=q.get('RgShotX',s)<=220 and 48<=q.get('RgShotY',s)<=208:
                            if effect_first is None:effect_first=age
                            if age<effect_first+8:continue
                            target(q,q.get('RgShotX',s)+12 if task['shot']==34 else q.get('RgShotX',s)-6,min(184,q.get('RgShotY',s)-8));placed=True;break
                _,writes=q.invoke('GameLoop')
                assert q.get('MmDeathFlag')==q.get('InjuryTimer')==q.get('GuestHurtTicks')==0,(char,task['name'],age,'injury')
                for s in range(10):
                    v=q.get('RgShotType',s)
                    if v and v not in trace['types']:
                        trace['types'].append(v)
                        trace.setdefault('first_positions',[]).append([v,q.get('RgShotX',s),q.get('RgShotY',s),q.get('RgShotPage',s),q.get('RgShotYHigh',s)])
                if q.get('AvStopwatch'):
                    watch_seen=True
                    xy=[q.get('Enemy_X_Position'),q.get('Enemy_Y_Position')]
                    assert 'watch_xy' not in trace or xy==trace['watch_xy'],(task,'freeze movement',trace,xy)
                    trace['watch_xy']=xy;trace['watch_ticks']=trace.get('watch_ticks',0)+1
                if watch_seen and q.get('AvStopwatch')==0:watch_zero=True
                if task.get('stop') and trace['contacts'] and not trace.get('stopped'):
                    assert q.get('RgEnemyStun')>0;trace['stopped']=q.get('RgEnemyStun')
                if task.get('shot')==34:
                    for s in range(10):
                        if q.get('RgShotType',s)==34 and abs(q.get('RgShotX',s)-72)<19 and abs(q.get('RgShotY',s)-194)<25:
                            assert q.get('AvBombHurt')==0 and q.get('InvOwnedLo',4)&32
                            trace['blue_ring_actual_self_overlap']=True
                if task['kind'] in ('collect','refill'):
                    if trace['collections'] and q.get('GuestPowerupActive')==q.get('TimerControl')==0:
                        assert trace['collections']==1
                        if item==0:assert trace['growth']==60 and q.get('PlayerStatus')==1
                        elif item<16:assert(q.get('InvOwnedLo',char)+256*q.get('InvOwnedHi',char))&(1<<item)
                        else:assert q.get('InvAmmo',char*16+task['ammo_item'])==trace['stock_before']+task['amount']
                        break
                elif age>=task['limit']:
                    assert all(q.get('RgShotType',s)==0 for s in range(10)) and q.get('RgAttack')==q.get('RgShootPose')==0,(char,item,'cleanup',trace)
                    if task.get('watch'):assert watch_seen and watch_zero
                    else:
                        assert task['shot'] in trace['types'] and placed and trace['contacts'],(char,item,'effect/contact',trace)
                        assert any(z[2]==task['proxy'] for z in trace['contacts']),trace
                    cost=b['raw'][location(b,'InvCosts')+char*16+item]
                    assert trace['spends']==([[6,item,cost]] if cost else []),(char,item,trace['spends'])
                    assert q.get('InvAmmo',idx)==trace['stock_before']-cost
                    if task.get('expected_limit'):assert q.get('AvLimit')==task['expected_limit']
                    if task.get('watch'):assert q.get('Enemy_X_Position')!=trace['watch_xy'][0] and trace['watch_ticks']==180
                    if task.get('shot')==34:assert trace.get('blue_ring_actual_self_overlap')
                    break
            else:raise AssertionError((char,task,'case timeout',trace))
            trace.update(GameLoop_age=age,owned_before=before_owned,owned_after=q.get('InvOwnedLo',char)+256*q.get('InvOwnedHi',char),stock_after=q.get('InvAmmo',idx if item<16 else char*16+task['ammo_item']),watch_seen=watch_seen,watch_expired=watch_zero)
            c,_=q.invoke('RemainingPower');trace['source_power']=c.a
            if char==4 and item==4 or char==5 and item==1:assert c.a==2
            out.append(trace)
    finally:NesMPU.step=original
    return dict(passed=True,source_CPU_only=True,actual_complete_GameLoop=True,no_tested_resource_seed=True,
                cases=out,GameLoop_calls=sum(t['GameLoop_calls'] for t in out),limits='No native interrupts, physical PPU/APU, Lua-VM or actual capture inference. Scene and aligned default-health target are disclosed staging.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',default=EXPECTED);p.add_argument('--family',choices=['link','simon'],required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--source-only',action='store_true')
    a=p.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve()
    assert sha(a.rom)==a.expected_sha256 and not a.output.exists()
    b=scoped_load(a.rom);char={'link':4,'simon':5}[a.family];plan=plans(char)
    source=source_campaign(b,char,plan)
    a.output.mkdir(parents=True);put(a.output/'source-controls.json',source)
    if a.source_only:print(json.dumps(dict(passed=True,output=str(a.output),cases=len(plan))));return
    base=ROOT/'tests/current-inventory-powerups.lua';fixture=ROOT/'tools/audit/current_link_simon_powerups_v1.lua'
    assert sha(base)==BASE_SHA
    text=fixture.read_text();old=base.read_text();begin='-- All callback registration is startup-static.'
    end="emu.addEventCallback(function()\n if not entered"
    guards=old[old.index(begin):old.index(end)]
    assert text.count('-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS')==1
    generated=text.replace('-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS\n',guards)
    assert generated[generated.index(begin):generated.index(end)]==guards
    assert generated.count('emu.write(')==2 and 'removeMemoryCallback'not in generated and 'dofile('not in generated
    forbidden='InvOwnedLo InvOwnedHi InvViewedLo InvViewedHi InvSelected InvAmmo PlayerStatus PlayerSize GuestPowerupActive GameEngineSubroutine InjuryTimer GuestHurtTicks MmDeathFlag RgShotType RgAttack RgShootPose AvStopwatch AvLimit CheatInvincible'.split()
    assert not set(ALLOWED)&set(forbidden)
    for n in forbidden:assert "w('"+n+"'"not in generated
    assert generated.count('emu.takeScreenshot(')==1 and 'images<8'in generated
    def raw(n,i=0):return b['raw'][location(b,n)+i]
    def hook(n,delta=0,size=3):
        pos=location(b,n)+delta;pc=address(b,n)+delta;k=(pos-16)//8192;bs=list(b['raw'][pos:pos+size]);banks=[k]
        if k==127:
            off=(pos-16)%8192;assert b['raw'][16+125*8192+off:16+125*8192+off+size]==bytes(bs);banks=[125,127]
        return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
    hooks={key:hook(n)for key,n in dict(PhysicalPickup='MarioSourcePowerupCollision',InventoryCollect='InventoryCollect',InventoryGrant='InventoryGrant',InventorySpend='InventorySpend',GuestPowerupUpdate='GuestPowerupUpdate',DamageEnemy='MegaManWeapons::DamageEnemy',BoomerangStop='LsrEffectsBoomerang',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
    start=location(b,'GameLoop');assert b['raw'][start:start+5]==bytes([0xa9,255,0x8d,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8]);hooks['GameLoopOwned']=hook('GameLoop',5)
    for key,n,opcode in [('GameLoopFinish','GameLoop',0x60),('PowerReturn','RemainingPower',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40)]:
        delta=int(b['syms'][n]['size'],0)-1;assert raw(n,delta)==opcode;hooks[key]=hook(n,delta,1)
    assert raw('InventorySpend::Done')==0x60;hooks['InventorySpendDone']=hook('InventorySpend::Done',0,1)
    post=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK');load=bytes([0xa5,mirror])if mirror<256 else bytes([0xad,mirror&255,mirror>>8])
    assert b['raw'][post-3:post]==b'\x8d\x14\x40' and b['raw'][post:post+len(load)+3]==load+b'\x8d\x01\x20'
    hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
    count=raw('InvItemCount',char);assert count=={4:6,5:9}[char]
    items={}
    for item in range(count+1):
        idx=char*16+item;ptr=raw('InvNameLo',idx)+256*raw('InvNameHi',idx);g=b['segs'][b['syms']['InvNameLo']['seg']];off=int(g['ooffs'],0)+ptr-int(g['start'],0)
        items[item]=dict(id=item,hud_name=list(b['raw'][off:off+7]),cost=raw('InvCosts',idx),initial_ammo=raw('InvInitialAmmo',idx),max_ammo=raw('InvMaxAmmo',idx),selectable=raw('InvSelectable',idx),auto_equip=raw('InvAutoEquip',idx),availability=raw('InvAvailability',idx),single_mask=raw('InvSingleLo',idx)+256*raw('InvSingleHi',idx))
    direct=set(re.findall(r'C\.ram\.([A-Za-z_][A-Za-z_0-9]*)',generated))
    names=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",generated))|direct|set(ALLOWED)|set('CurrentBank CurrentBankC Sprite0HitDetectFlag'.split())
    variant='Z2Variant'if char==4 else'Cv3Variant';names.add(variant)
    ram={n:address(b,n)for n in names if n in b['syms']}
    for n in names:assert n in ram,n
    cfg=dict(ROM_sha256=a.expected_sha256,character=char,slot=char,variant=variant,mode=1,frame_limit=16000,item_count=count,auto_mask=raw('InvMushroomLo',char)+256*raw('InvMushroomHi',char),plan=plan,items=items,ram=ram,hooks=hooks,setup_allowed={n:True for n in ALLOWED},powerup_sfx=address(b,'Sfx_PowerUpGrab'),dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    for task in plan:
        if task['kind']=='use':assert cfg['items'][task['item']]['selectable']==1
    # Typed configuration is emitted from integer keys; verify literal numeric
    # table fields and install native preflight BEFORE loading the fixture.
    emitted=lua(cfg)
    for item in range(count+1):assert f'[{item}]='in emitted and f'["{item}"]='not in emitted
    preflight="local C=assert(CURRENT_LINK_SIMON_POWERUPS);assert(C.mode==1 and C.character=="+str(char)+")\n"
    for item,info in items.items():
        terms=[f'type(C.items[{item}])==\'table\'']+[f'C.items[{item}].{k}=={v}' for k,v in info.items() if isinstance(v,int)]
        preflight+='assert('+ ' and '.join(terms)+f",'typed item {item}')\n"
    put(a.output/'config.json',cfg)
    generated_path=a.output/'fixture.lua';generated_path.write_text(generated,newline='\n')
    (a.output/'run.lua').write_text('CURRENT_LINK_SIMON_POWERUPS='+emitted+'\n'+preflight+'dofile([=['+generated_path.as_posix()+']=])\n',newline='\n')
    put(a.output/'source-layout.json',dict(passed=True,ROM_sha256=a.expected_sha256,item_tables=items,plan=plan,unchanged_complete_hardware_guard_sha256=hashlib.sha256(guards.encode()).hexdigest(),hardware_guard_source_sha256=sha(base),setup_allowlist=ALLOWED,forbidden=forbidden,actual_E008_DMA_completion=hooks['DmaComplete'],typed_numeric_items_preflight=True,source_model_limits=source['limits'],legacy_remaining_inventory='IDs/attack context only; no old endFrame setup, resource refill, direct selection or ownership/outcome writes reused.'))
    argv=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),str(a.output/'run.lua'),str(a.rom),'--timeout','1800','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,requires_existing_ROOT_isolated_runtime_and_capture_gate=True,argv=argv))
    paths=[a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),Path(__file__),fixture,base,ROOT/'tests/remaining-inventory.lua',ROOT/'docs/qa/current37-powerup-reuse-index-2026-10-27.json',ROOT/'docs/qa/link-simon-earned-source-draft-negatives-2026-10-27.json']
    paths += [ROOT/'tools/audit'/n for n in ['link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py','observe_chip_committed_write.py','run_mesen_isolated.py','capture_budget.py']]+[ROOT/'tools/run_mesen.py']
    paths += [ROOT/'src'/n for n in ['inventory.s','inventory_data.inc','inventory_drops.s','roster_weapons.s','remaining_weapons.s','easy_link_order.s','lsr_effects.s','guest_powerups.s','game.s','mario_source.s','megaman_weapons.s']]
    paths += [a.output/n for n in ['config.json','fixture.lua','run.lua','source-controls.json','source-layout.json','command.json']]
    put(a.output/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=a.expected_sha256,family=a.family,character=char,mode=1,mature_collection_ids=sorted({t['item']for t in plan if t['kind']=='collect'}),actual_refill_actors=[t for t in plan if t['kind']=='refill'],actual_use_ids=sorted({t['item']for t in plan if t['kind']=='use'}),source_controls_passed=True,source_GameLoop_calls=source['GameLoop_calls'],caps=dict(wall_frames=16000,actual_updates=6000,host_seconds=1800,bytes=2000000000,files=64,PNGs=8,containers=0),setup='Actual GameLoop+5 after STA NmiDisable=$FF, no NMI/IRQ; disclosed logical+visible arena, player position/motion, mature actor5, default-health Goomba0 placed only from real active effect. No owned/tier/stock/selection/projectile/outcome seeds.',limits='Not run. Hard only, facing right, mature actor not full reveal/rise/RNG/drop. No natural item lottery, damage/armor generalization, zero/full-stock caps, concurrent multiplier saturation, primary melee/air/thrust/campaign, original waveform or blanket visual/cadence claim. Source CPU is finite instruction execution, not native timing/Lua/PPU proof.',bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in paths]))
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',output=str(a.output),readiness_sha256=sha(a.output/'prepared-not-run.json'),bindings=len(paths),source_GameLoop_calls=source['GameLoop_calls'],native_run=False)))

if __name__=='__main__':main()
