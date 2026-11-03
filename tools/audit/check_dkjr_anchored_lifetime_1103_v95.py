"""Current private cold90 entrance, earned pause, scene and retire lifetime."""
import json
from pathlib import Path
import prepare_dkjr_anchored_owner_1103_v90 as P
import check_dkjr_entrance_order_1103_v88 as E
import check_dkjr_native_score_tail_1102_v55 as S
import check_dkjr_native_service_ff_1102_v51 as F

A,R,O=P.A,P.R,P.O
C=P.P.C;N,W=C.N,A.W


def private(m,entry,**args):
    maps=m.rawtags[:];shadow=(N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'))
    m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2)
    try:return S.direct(m,entry,**args)
    finally:
        for i,tag in enumerate(maps):m.raw_page(i,tag)
        N.put(m,CurrentBank=shadow[0],CurrentBankC=shadow[1])


def fixture():
    b,q=P.image();m,history,good=E.run(b)
    assert good and m.ram[2][0x8fe]==2
    L=json.loads((O/'native-entrance-v89-layout.json').read_text())['labels']
    # Same relative legal geometry as the proven earned-fruit fixture: the
    # genuine native entrance selectedX40, fruit/victim lie12px to its right.
    for i,value in enumerate([52,0,191,0]):m[W.address(b,'R0')+i]=value
    z=private(m,L['DkjrNativeFruitSet'],x=0);assert z[3]&1
    for slot,x in [(0,52),(5,180)]:
        for name,value in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),('Enemy_X_Position',x),('Enemy_PageLoc',0),('Enemy_Y_Position',184),('Enemy_Y_HighPos',1)]:
            m[W.address(b,name)+slot]=value
        N.put(m,ObjectOffset=slot);N.invoke(m,'InitGoomba',x=slot)
    N.put(m,PlayerFacingDir=1,NmiDisable=255)
    for i,value in enumerate([4,0,0]):m[W.address(b,'GameTimerDisplay')+i]=value
    return b,m,L,q


def epoch(m,index):
    N.put(m,FrameCounter=index,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
    F.timers(m)
    return N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)


def main():
    b,m,L,q=fixture();rows=[];cohorts={}
    for i in range(1,63):
        seed=N.fork(m);z=epoch(m,i)
        assert m.ram[2][0x8fe]==2 and N.get(m,'NumberofLives')==2
        if i in [1,2,61,62]:
            rows.append(dict(epoch=i,source_hit=m.ram[2][0x68],pause_active=m.ram[2][0x440],TimerControl=N.get(m,'TimerControl'),source_counter=m.ram[2][0x65]))
            cohorts[i]=(seed,N.fork(m))
    assert rows[0]['source_hit'] and not rows[0]['pause_active']
    assert rows[1]['pause_active'] and rows[1]['TimerControl']==255
    assert not rows[2]['source_hit'] and rows[2]['pause_active']
    assert not rows[3]['source_hit'] and not rows[3]['pause_active'] and rows[3]['TimerControl']==0
    paused=cohorts[2][1];scene=[]
    for service in ['Fresh15','Scene36','Reset19','ResidentRetire']:
        for context in ['same','nested-native-powerup','different-area']:
            z=N.fork(paused)
            if context=='nested-native-powerup':N.put(z,GameEngineSubroutine=9,TimerControl=48)
            elif context=='different-area':N.put(z,AreaPointer=N.get(z,'AreaPointer')^1,TimerControl=37)
            before_lives=N.get(z,'NumberofLives')
            if service=='ResidentRetire':
                call=C.I.invoke(z,193,0xae0b,(83,71,109,0x21))
                for bank in [2,3]:assert z.ram[bank][0x1fe0]==0
            else:
                N.put(z,DisableScreenFlag=1,Mirror_PPUMASK=0)
                entry={'Fresh15':0xb0b9,'Scene36':0xb0f8,'Reset19':0xb0c5}[service]
                # Resolve real published entry PCs from native globals where
                # available; scene36 has no invented HuGenericFresh alias.
                if service=='Fresh15':call=N.invoke(z,'HuFresh',a=83,x=71,y=109,p=0x21)
                elif service=='Reset19':call=N.invoke(z,'HuReset',a=83,x=71,y=109,p=0x21)
                else:call=C.I.invoke(z,193,entry,(83,71,109,0x21))
                assert z.ram[2][0x8fe]==(1 if service in ['Fresh15','Scene36']else 0)
            assert not z.ram[2][0x440] and N.get(z,'NumberofLives')==before_lives
            assert N.get(z,'TimerControl')==({'same':0,'nested-native-powerup':48,'different-area':37}[context])
            for slot in range(1,5):assert N.get(z,'Enemy_Flag',slot)==0
            # Second retirement/thaw has no old token to restore again. New
            # positive births must remain owned by the native engine.
            at=W.address(b,'Enemy_Flag')+2;z[at]=1
            saved=[bytes(z.ram[k])for k in [2,3]]
            if service=='ResidentRetire':C.I.invoke(z,193,0xae0b,(83,71,109,0x21))
            else:private(z,L['DkPauseThaw'])
            assert z[at]==1 and saved==[bytes(z.ram[k])for k in [2,3]]
            scene.append(dict(actual_service=service,context=context,pause_unwound_once=True,native_timer_preserved=True,positive_spawn_not_restored=True))
    # Public source-audio/effects/draw policies may act during construction,
    # but they cannot advance original actor HP/items/phase before anchoring.
    pending,_=C.cold(b,40)
    N.put(pending,Player_X_Position=0,Player_Y_Position=0,Player_Y_HighPos=0,GameEngineSubroutine=0)
    N.invoke(pending,'HuFresh',a=83,x=0,y=109,p=0x21)
    original=bytes(pending.ram[2][:0x800]);passive=[]
    for row in [1,2,3,4,6,9,12,13,20,26,29,30,31,32,34,35,37]:
        z=N.fork(pending);N.put(z,CurrentOAMOffset=24,VRAM_Buffer1_Offset=0)
        C.I.invoke(z,193,0xb08c+3*row,(0,0,0,0x21))
        assert bytes(z.ram[2][:0x800])==original and z.ram[2][0x8fe]==1,(row,'pending actor advanced')
        passive.append(row)
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(b['raw']),genuine_native_entrance_before_source=True,
        earned_original_hitstop_cohorts=rows,populated_pause_reset_retire_cases=scene,
        pending_passive_public_rows=passive,source_ready_value_after_first_engine8=2,
        scope='Realcold90→unchanged table-driven nativeentrance→Ready2; earnedfruit/victim geometry then original capture, following60D1AE updates andthaw. Actual publicFresh15/scene36/reset19 andresidentRetire unwind populated nativepause once, preserve nestedEngine9/different-area timer, and do not restore a newpositivebirth. Seventeen pending graphics/effect/profile/status rows do not advance original2048-byte actor. Header-invalid secondretire is harmless. CurrentPrince130 model only; full native scene40 gate/finalPrince successor/IRQ proof remain separate.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(E.__file__),O/'native-owner-proposal-v90.json',O/'native-entrance-v89-layout.json',O/'native-ready-domains-v94-CPU.json']})
    (O/'native-anchored-lifetime-v95-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','earned_original_hitstop_cohorts','pending_passive_public_rows']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-anchored-lifetime-v95-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
