"""Qualify added body/impulse services and genuine deferred item score/lives."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_pickups_controls_v2 as T
import ff_host_pickups_vectors_v2 as ISR
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/final-fantasy-host-pickups-v3'
O=R/'build/final-fantasy-host-pickups-edges-v3'
C=T.C;put=T.put;get=T.get;setv=T.setv;run=T.run


def unchanged_prefix(b):
    old=T.P/'ram3.bin';new=P/'ram3.bin';before=old.read_bytes();after=new.read_bytes()
    changes=[i for i,(a,z)in enumerate(zip(before,after))if a!=z]
    assert changes and all(0x1cce<=i<0x1cef for i in changes)
    original=C.bundle(T.P)
    for n in ['FfHostCollect','FfHostPowerupTick','FfHostGraphics','FfHostBeginFreeze',
              'FfHostWeapons','FfHostFresh','FfHostMovement','FfHostHead','FfHostBox',
              'FfMovement','FfPickup','FfGraphics','FfPublishChunk']:
        assert address(original,n)==address(b,n),n
    checks=json.loads((T.O/'controls.json').read_text());assert checks['passed']
    return dict(exact_prior_code_data_except_new_helpers=True,new_span='BCCE..<BCEF',
                reused_exact_prior_image_controls=checks['checks'],
                immutable_previous_image_sha256=C.sha(old))


def body(b):
    rows=[]
    for rules,wet,p in itertools.product([0,1],[0,1],C.flags()):
        m=T.setup(b);put(m,CrossoverBehaviorVersion=rules,MmUnderwater=wet)
        c,tr= T.V.direct(m,'FfHostBody',a=0xd7,x=5,y=0xa7,p=p,bank=3)
        allowed=rules==0 and wet==0
        assert get(m,'GuestBodyStompAllowed')==int(allowed)
        assert get(m,'GuestBodyNoStomp')==int(not allowed)
        assert (c.a,c.x,c.y)==(0xd7,5,0xa7)and not c.p&1
        assert c.p&(4|8|64)==p&(4|8|64)
        rows.append([rules,wet,p])
    return dict(policy_cases=len(rows),genuine_source_Easy_water_policy=True,original_enemy_ID_AXY_VDI_retained=True)


def impulses(b):
    native=qualified(C.E.P/'candidate.nes');rows=[]
    for name,p,keys in itertools.product(['X5StompDispatch','X5SpringDispatch'],C.flags(),[0,128]):
        m=T.setup(b,variant=2,tier=2)
        put(m,SavedJoypadBits=keys,CrossoverBehaviorVersion=0,Player_State=2,
            FfJump=0,FfGPhase=31,Player_Y_Speed=252,Player_Y_Position=176)
        # Real existing raw22 profile and genuine MarioSource impulse first.
        physical=(location(native,name)-16)//8192
        c,tr=T.V.direct(m,name,a=0xd7,x=2,y=0xa7,p=p,bank=physical|128)
        actual=[get(m,'MmVY',i)for i in range(3)]
        assert actual[2]&128,('real native upward impulse',name,p,keys,actual)
        before=(c.a,c.x,c.y,c.p)
        m.raw_page(1,3);setv(m,'CurrentBank',3)
        c,tr=T.V.direct(m,'FfHostImpulseAccepted',a=c.a,x=c.x,y=c.y,p=c.p)
        assert (c.a,c.x,c.y,c.p)==before
        assert [get(m,'MmVY',i)for i in range(3)]==actual
        assert get(m,'FfJump')==1 and get(m,'FfGPhase')==0
        # The actual source air integrator must retain the imported fractional
        # impulse, rather than silently replacing it with an integer bounce.
        put(m,Player_State=1,SavedJoypadBits=0)
        run(m,'FfMovement')
        assert get(m,'FfJump')==1
        rows.append([name,p,keys,actual])
    return dict(actual_native_stomp_spring_pairs=len(rows),all64_APXY_flags=True,
                native_MmVY_fraction_retained=True,source_jump_pose_and_gravity_reset=True,
                adaptation='Existing shared MarioSource stump/spring impulses; not invented FF original-game values.')


def score_and_life(b):
    native=qualified(C.E.P/'candidate.nes')
    physical=(location(native,'FloateyNumbersCore')-16)//8192;rows=[]
    for kind,slot,player,wx,camera in itertools.product([0,1,2,3],range(6),range(2),[260,384],[252]):
        m=T.setup(b,variant=1,tier=2,kind=kind,slot=slot,charges=1,player=player)
        setv(m,'Enemy_X_Position',wx&255,slot);setv(m,'Enemy_PageLoc',wx>>8,slot)
        put(m,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,VRAM_Buffer1_Offset=0)
        for n in ['DigitModifier','Player1ScoreDisplay','Player2ScoreDisplay']:
            for i in range(6):setv(m,n,0,i)
        run(m,'FfHostCollect',x=slot)
        assert get(m,'FloateyNum_X_Pos',slot)==(wx-camera)&255
        assert get(m,'FloateyNum_Y_Pos',slot)==160
        # Invoke the real deferred native digit/life consumer, with its genuine
        # actor-loop ObjectOffset contract, until the one actual award occurs.
        for tick in range(8):
            setv(m,'ObjectOffset',slot)
            T.V.direct(m,'FloateyNumbersCore',x=slot,bank=physical|128)
        expected=[0]*6
        if kind!=3:expected[3]=1
        own='Player1ScoreDisplay'if player==0 else'Player2ScoreDisplay'
        other='Player2ScoreDisplay'if player==0 else'Player1ScoreDisplay'
        assert [get(m,own,i)for i in range(6)]==expected
        assert [get(m,other,i)for i in range(6)]==[0]*6
        assert get(m,'NumberofLives')==(3 if kind==3 else 2)
        if kind==3:
            run(m,'FfEnsure')
            assert get(m,'FfPower')==2 and get(m,'FfEarned')==2
            assert get(m,'FfHealCharges')==1 and get(m,'FfLife')==3
        rows.append([kind,slot,player,wx,camera])
    return dict(actual_deferred_cases=len(rows),all6actor_slots_both_players=True,
                popup_actual_world_projection=True,score_and_life_awarded_once=True,
                real_1UP_keeps_earned_FF_gear=True)


def vectors(b):
    rows=[]
    for name in ['FfHostBody','FfHostImpulseAccepted']:
        m=T.setup(b);_,trace,_=run(m,name)
        for kind in ['normalNMI','lagNMI','IRQ']:
            for cut in range(len(trace)):
                m=T.setup(b);put(m,NmiDisable=0 if kind=='normalNMI' else 255);fired=[]
                def hook(m,c,step):
                    if step!=cut:return
                    before=T.ffstate(m);ISR.interrupt(m,c,'IRQ'if kind=='IRQ'else'NMI')
                    assert T.ffstate(m)==before;fired.append(True)
                run(m,name,hook=hook);assert fired;rows.append([name,kind,cut])
    return dict(real_vector_cuts=len(rows),all143_FF_bytes_and_33_SMC_live_page1=True)


if __name__=='__main__':
    assert not O.exists();O.mkdir();h=json.loads((P/'build-proof.json').read_text())
    for p,d in h['bindings'].items():assert C.sha(p)==d,p
    b=C.bundle(P);checks={};failures={}
    for name,fn in dict(exact_prefix_reuse=unchanged_prefix,body_policy=body,real_impulses=impulses,deferred_item_consumers=score_and_life,real_vectors=vectors).items():
        try:checks[name]=fn(b);print(json.dumps(dict(group=name,passed=True,checks=checks[name])),flush=True)
        except Exception as e:failures[name]=dict(error=repr(e),traceback=traceback.format_exc());print(json.dumps(dict(group=name,passed=False,error=repr(e))),flush=True)
    extras=[Path(__file__).resolve(),Path(T.__file__).resolve(),Path(ISR.__file__).resolve(),T.O/'controls.json']
    bindings={**h['bindings'],str((P/'build-proof.json').resolve()):C.sha(P/'build-proof.json')}
    for p in extras:bindings[str(p)]=C.sha(p)
    report=dict(passed=not failures,image_sha256=C.sha(P/'ram3.bin'),checks=checks,failures=failures,native=False,cart_hooks=False,bindings=bindings)
    (O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=not failures,groups=len(checks),failed=list(failures))))
    if failures:raise SystemExit(1)
