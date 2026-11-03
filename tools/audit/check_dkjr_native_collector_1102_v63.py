"""Exact genuine native collector behind private DK Jr policy24.

These are explicitly isolated legal item fixtures, not proof that the still
ungranted shared raw40 rare gate reaches this callback in native gameplay.
"""
import itertools,json
from pathlib import Path
import check_dkjr_native_item_status_1102_v61 as P
A,R,O,W,N=P.A,P.R,P.O,P.W,P.N


def main():
    b,seed,L,q=P.fixture();cases=[]
    for kind,player,status in itertools.product(range(4),[0,1],[0,1,2]):
        m=N.fork(seed)
        N.put(m,CurrentPlayer=player,PlayerStatus=status,PlayerSize=int(status==0),ObjectOffset=5,TimerControl=0,VRAM_Buffer1_Offset=0)
        for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,Enemy_X_Position=48,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1).items():m[W.address(b,field)+5]=value
        P.P.direct(m,L['DkNativePrepare'],x=5)
        ref=N.fork(m);before=[bytes(z)for z in m.ram]
        a=N.invoke(ref,'MarioSourcePowerupCollision',x=5,y=91,p=0x31)
        out=P.P.direct(m,L['DkNativePickup'],x=5,y=91,p=0x31)
        assert out==(a['A'],a['X'],a['Y'],a['P']&0xef,224),(kind,player,status,'collectorAXYP',out,a)
        assert not P.differences(P.native(ref),P.native(m)),(kind,player,status,'nativecollectorstate')
        assert m.ram==ref.ram and before==[bytes(z)for z in m.ram],(kind,player,status,'source/private mutation')
        assert m.rawtags==ref.rawtags
        assert N.get(m,'Enemy_Flag',5)==0
        if kind==2:assert N.get(m,'StarInvincibleTimer')==35
        elif kind==3:assert N.get(m,'FloateyNum_Control',5)==11
        cases.append(dict(kind=kind,native_player=player,initial_status=status,resulting_status=N.get(m,'PlayerStatus'),
            native_engine=N.get(m,'GameEngineSubroutine'),native_timer=N.get(m,'TimerControl'),native_star=N.get(m,'StarInvincibleTimer'),
            native_float=N.get(m,'FloateyNum_Control',5),source_actor_unchanged=True,native_reference_minimum_SP=a['minimum_SP']))
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        isolated_legal_fixture=True,historical_v65_matching_header_fixture=True,cases=cases,
        scope='All4 native item types×both native score/life owners×three native power states execute the genuine unchanged MarioSourcePowerupCollision, preserve exact architecturalAXYP/all nondeadstack nativeRAM/maps/private arrays versus that native service, and leave original donor actor unchanged. Full real PowerUpObjHandler raw40 gate is not patched/admitted; cold/life/fullIRQ and nativegameplay remain pending.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'native-items-v60.s',O/'native-items-v60.bin',O/'native-items-v60-layout.json',R/'src/mario_source.s',R/'src/new_roster_dispatch.s']})
    (O/'native-collector-v63-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(cases),resulting_native_states=sorted({(z['kind'],z['initial_status'],z['resulting_status'],z['native_engine'],z['native_timer'])for z in cases}))))


if __name__=='__main__':main()
