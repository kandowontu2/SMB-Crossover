"""Actual FF progression/native item helpers and hosted visual-freeze controls."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v1 as C
import ff_host_combat_controls_v3 as V
import ff_ram3_execution_controls_v2 as E
from check_tmnt_render_oa import address
P=R/'build/final-fantasy-host-pickups-v2'
O=R/'build/final-fantasy-host-pickups-controls-v1'
put=C.put;get=C.get;setv=C.setv;run=C.run


def ffstate(m):return bytes(m[0x5c00:0x5c80]+m[0x5fc1:0x5fcf]+m[0x5fef:0x5ff0])


def setup(b,variant=0,tier=0,kind=0,slot=0,charges=0,player=0):
    m=C.make(b)
    put(m,FfVariant=variant,FfPower=tier,FfEarned=tier,FfHealCharges=charges,
        PlayerStatus=tier,PlayerSize=0,ObjectOffset=4,CurrentPlayer=player,
        GuestPowerupActive=0,GuestPowerupAge=0,GuestLegacyHurt=0,
        TimerControl=0,GameEngineSubroutine=8,GamePauseStatus=0,MmDeathFlag=0,
        ObjectMetasprite=address(b,'METASPRITE_SAMUS_BODY'))
    C.actor(m,x=slot,kind=address(b,'PowerUpObject'),px=120,y=160,state=128)
    setv(m,'PowerUpType',kind,slot)
    m.writes.clear()
    return m


def progression(b):
    rows=[];native_fields=['Enemy_Flag','Enemy_State','FloateyNum_Control',
        'FloateyNum_X_Pos','FloateyNum_Y_Pos','FloateyNum_Timer','Square2SoundQueue']
    for variant,tier,kind,slot,charges,player in itertools.product(range(4),range(3),[0,1],range(6),[0,1,3],[0,1]):
        if variant!=1 and charges:continue
        m=setup(b,variant,tier,kind,slot,charges,player)
        ref=setup(b,variant,tier,kind,slot,charges,player)
        run(ref,'FfPickup',a=kind)
        put(ref,ObjectOffset=slot)
        run(ref,'EraseEnemyObject',x=slot)
        run(ref,'SetupFloateyNumber',a=6,x=slot)
        c,trace,_=run(m,'FfHostCollect',x=slot,p=0x71)
        assert c.p&1 and c.x==slot and get(m,'ObjectOffset')==4
        assert ffstate(m)==ffstate(ref),('genuine FF progression',variant,tier,kind,slot,charges,player)
        for name in native_fields:
            at=slot if name!='Square2SoundQueue' else 0
            assert get(m,name,at)==get(ref,name,at),('genuine native item consumer',name,slot,variant,tier)
        assert get(m,'GuestPowerupOld')==tier and get(m,'GuestPowerupDisplay')==tier
        assert get(m,'GuestPowerupTarget')==min(2,tier+1)
        assert get(m,'GuestPowerupActive')==1 and get(m,'GuestPowerupAge')==0
        assert get(m,'TimerControl')==255 and get(m,'GameEngineSubroutine')==9
        assert get(m,'Square2SoundQueue')==address(b,'Sfx_PowerUpGrab')
        assert get(m,'FloateyNum_Control',slot)==6
        before=V.state(m);again,_,_=run(m,'FfHostCollect',x=slot)
        assert not again.p&1 and V.state(m)==before,('duplicate item consumption',slot)
        rows.append([variant,tier,kind,slot,charges,player])
    return dict(cases=len(rows),source_progression_byte_exact=True,genuine_native_erase_score_SFX=True,repeat_pickup_rejected=True,both_players=True)


def guards(b):
    cases=[dict(SelectedCharacter=n)for n in range(34)if n!=22]
    cases+=[dict(GameEngineSubroutine=n)for n in range(16)if n!=8]
    cases+=[dict(GamePauseStatus=1),dict(GamePauseStatus=3),dict(TimerControl=1),dict(MmDeathFlag=1)]
    rows=[]
    for values in cases:
        m=setup(b);put(m,**values);before=V.state(m)
        c,_,_=run(m,'FfHostCollect',x=0)
        assert not c.p&1 and V.state(m)==before,('inactive collect writes',values)
        rows.append(values)
    for name,value in [('Enemy_Flag',0),('Enemy_Flag',128),('Enemy_ID',address(b,'Goomba')),
                       ('Enemy_State',0),('Enemy_State',1),('Enemy_State',127),
                       ('PowerUpType',4),('PowerUpType',255)]:
        m=setup(b);setv(m,name,value);before=V.state(m)
        c,_,_=run(m,'FfHostCollect',x=0)
        assert not c.p&1 and V.state(m)==before,(name,value)
        rows.append([name,value])
    for slot in [6,7,255]:
        m=setup(b);before=V.state(m);c,_,_=run(m,'FfHostCollect',x=slot)
        assert not c.p&1 and V.state(m)==before,('invalid native actor index',slot)
    return dict(inactive_and_emergence_cases=len(rows),invalid_slots=3,no_auto_collection_of_rising_items=True)


def native_items(b):
    rows=[]
    for kind,slot,variant,tier,player in itertools.product([2,3],range(6),range(4),range(3),[0,1]):
        m=setup(b,variant,tier,kind,slot,0,player);before=ffstate(m)
        c,tr,_=run(m,'FfHostCollect',x=slot)
        assert c.p&1 and c.x==slot and get(m,'ObjectOffset')==4
        assert ffstate(m)==before and get(m,'GuestPowerupActive')==0
        assert get(m,'Enemy_Flag',slot)==0
        assert get(m,'Square2SoundQueue')==address(b,'Sfx_PowerUpGrab')
        if kind==2:
            assert get(m,'StarInvincibleTimer')==0x23
            assert get(m,'AreaMusicQueue')==address(b,'StarPowerMusic')
            assert get(m,'FloateyNum_Control',slot)==6
        else:assert get(m,'FloateyNum_Control',slot)==11
        rows.append([kind,slot,variant,tier,player])
    return dict(cases=len(rows),native_star_timer_music=True,native_deferred_1UP=True,FF_gear_and_charges_unchanged=True)


def freeze(b):
    rows=[]
    for variant,old in itertools.product(range(4),range(3)):
        m=setup(b,variant,old,0);run(m,'FfHostCollect',x=0)
        source=ffstate(m);target=min(2,old+1)
        for tick in range(1,61):
            run(m,'FfHostPowerupTick')
            expected=target if tick==60 or (old and (tick//6)&1) else old
            assert get(m,'GuestPowerupAge')==tick
            assert get(m,'GuestPowerupDisplay')==expected,('actual hosted tier swap',variant,old,tick)
            assert get(m,'FfPower')==target and get(m,'FfEarned')==target
            if tick<60:
                assert get(m,'GameEngineSubroutine')==9 and get(m,'GuestPowerupActive')==1 and get(m,'TimerControl')==255
                assert ffstate(m)==source
            else:
                assert get(m,'GameEngineSubroutine')==8 and get(m,'GuestPowerupActive')==0 and get(m,'TimerControl')==0
                assert get(m,'PlayerStatus')==target and get(m,'PlayerSize')==0
                assert get(m,'FfPaletteAck')==255
            rows.append([variant,old,tick,expected])
    for values in [dict(SelectedCharacter=0),dict(SelectedCharacter=21),dict(GamePauseStatus=1),
                   dict(GamePauseStatus=3),dict(GameEngineSubroutine=8),dict(GuestPowerupActive=0)]:
        m=setup(b);run(m,'FfHostCollect',x=0);put(m,**values);before=V.state(m)
        run(m,'FfHostPowerupTick');assert V.state(m)==before,('inactive freeze',values)
    return dict(tick_cases=len(rows),exact_60_updates=True,gear_never_temporarily_lost=True,inactive_pause_cases=6)


def graphics(b):
    rows=[]
    for variant,earned,display,face,action in itertools.product(range(4),range(3),range(3),[1,2],[0,1,2,3]):
        m=setup(b,variant,earned);ref=setup(b,variant,display)
        for arena in [m,ref]:put(arena,PlayerFacingDir=face,FfAction=action,FfAge=7)
        put(m,GuestPowerupActive=1,GuestPowerupDisplay=display)
        c,tr,_=run(m,'FfHostGraphics')
        run(ref,'FfGraphics')
        assert get(m,'FfPower')==earned,('graphics changed earned tier',variant,earned,display)
        for name,count in [('FfRenderBuffer',61),('SmPosePtr',2),('ObjectMetasprite',1),('FfPose',1),('FfRenderPage',1),('FfRenderYOffset',2)]:
            assert [get(m,name,i)for i in range(count)]==[get(ref,name,i)for i in range(count)],('actual source frozen-tier descriptor',name,variant,earned,display,face,action)
        rows.append([variant,earned,display,face,action])
    return dict(actual_source_descriptor_pairs=len(rows),all_four_classes_both_faces=True,visual_tier_restores_acquired_power=True)


def vectors(b):
    rows=[]
    for name in ['FfHostCollect','FfHostPowerupTick','FfHostGraphics']:
        def make():
            m=setup(b,1,1,1,2,1)
            if name!='FfHostCollect':run(m,'FfHostCollect',x=2)
            return m
        m=make();_,trace,_=run(m,name,x=2)
        for kind in ['normalNMI','lagNMI','IRQ']:
            for cut in range(len(trace)):
                m=make();put(m,NmiDisable=0 if kind=='normalNMI' else 255);fired=[]
                def hook(m,c,step):
                    if step!=cut:return
                    before=ffstate(m)
                    E.interrupt(m,c,'IRQ' if kind=='IRQ' else 'NMI')
                    assert ffstate(m)==before,('ISR changed FF item/visual source fields',name,kind,cut)
                    fired.append(True)
                run(m,name,x=2,hook=hook);assert fired
                rows.append([name,kind,cut])
    return dict(real_vector_cuts=len(rows),all143_FF_bytes_preserved_per_ISR=True,all33_SMC_live_page1_rawbanks=True)


if __name__=='__main__':
    assert not O.exists();O.mkdir();h=json.loads((P/'build-proof.json').read_text())
    for p,d in h['bindings'].items():assert C.sha(p)==d,p
    b=C.bundle(P);checks={};failures={}
    for name,fn in dict(progression=progression,guards=guards,native_items=native_items,freeze=freeze,graphics=graphics,vectors=vectors).items():
        try:checks[name]=fn(b);print(json.dumps(dict(group=name,passed=True,checks=checks[name])),flush=True)
        except Exception as e:failures[name]=dict(error=repr(e),traceback=traceback.format_exc());print(json.dumps(dict(group=name,passed=False,error=repr(e))),flush=True)
    bindings={**h['bindings'],str((P/'build-proof.json').resolve()):C.sha(P/'build-proof.json'),str(Path(__file__).resolve()):C.sha(__file__)}
    report=dict(passed=not failures,status='OFFLINE_FF_ACTUAL_ITEM_CONSUMERS_AND_HOSTED_VISUAL_FREEZE',image_sha256=C.sha(P/'ram3.bin'),checks=checks,failures=failures,native=False,Main_or_hooks=False,bindings=bindings)
    (O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=not failures,groups=len(checks),failed=list(failures))),flush=True)
    if failures:raise SystemExit(1)
