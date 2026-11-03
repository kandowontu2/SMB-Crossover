"""Real native entrance-after-constructor ordering, without seeded final Y."""
import json
from pathlib import Path
import prepare_dkjr_current_owner_1103_v79 as P

A,R,O,C=P.A,P.R,P.O,P.C
N,W=C.N,A.W


def snapshot(m):
    return dict(nativeX=N.get(m,'Player_X_Position'),nativeY=N.get(m,'Player_Y_Position'),
        nativeHighY=N.get(m,'Player_Y_HighPos'),engine=N.get(m,'GameEngineSubroutine'),
        sourceX=m.ram[2][0x213],sourceY=m.ram[2][0x210],sourceState=m.ram[2][0x6b],ready=m.ram[2][0x8fe])


def run(base):
    m,_=C.cold(base,40)
    N.put(m,Player_X_Position=0,Player_PageLoc=0,Player_Y_Position=0,Player_Y_HighPos=0,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,
        GameEngineSubroutine=0,PlayerEntranceCtrl=2,AltEntranceControl=0,JoypadOverride=0,
        AreaType=1,AreaParserTaskNum=7,GameTimerSetting=1,FetchNewGameTimerFlag=1,
        GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,DisableIntermediate=1,
        PlayerSize=1,Player_BoundBoxCtrl=1,VRAM_Buffer1_Offset=0)
    N.invoke(m,'HuFresh',a=83,x=0,y=109,p=0x21)
    history=[dict(stage='real_ctor_before_entrance',**snapshot(m))]
    # Actual unchanged native table-driven entrance, not a fixed host-Y repair.
    N.invoke(m,'Entrance_GameTimerSetup',a=83,x=0,y=0,p=0x21)
    history.append(dict(stage='after_real_entrance_setup',**snapshot(m)))
    N.invoke(m,'PlayerEntrance',a=0,x=0,y=0,p=0x21)
    history.append(dict(stage='after_real_PlayerEntrance',**snapshot(m)))
    assert N.get(m,'GameEngineSubroutine')==8
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        at=W.address(base,name);m[at:at+208]=bytes(208)
        for row in [11,12]:m[at+row*16:at+row*16+16]=bytes([0x54])*16
    for slot in range(6):m[W.address(base,'Enemy_Flag')+slot]=0
    N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,TimerControl=0,FrameCounter=1,
        SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0)
    N.invoke(m,'GameCoreRoutine',a=83,x=0,y=0,p=0x21)
    history.append(dict(stage='after_first_real_engine8_Main',**snapshot(m)))
    last=history[-1]
    good=(last['nativeX'],last['nativeY'],last['nativeHighY'],last['sourceX'],last['sourceY'])==(40,176,1,32,191)
    return m,history,good


def main():
    base,q=P.image();m,history,good=run(base)
    out=dict(passed=good,qualification_complete=False,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(base['raw']),actual_entrance_control=2,
        manual_final_native_Y_written=False,history=history,
        scope='Cold/Fresh source constructor sees genuine pre-entry native0/high0; unchanged native Entrance_GameTimerSetup and PlayerEntrance choose X40/Y176/high1/engine8, followed by complete native GameCore. Explicit legal flat BlockBuffer floor only. No source actor or final native-Y correction seeded.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),O/'native-owner-proposal-v79.json',R/'src/player.s']})
    path=O/('native-entrance-v88-CPU.json'if good else'native-entrance-v88-negative.json')
    path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
    assert good,'Original constructor origin survives genuine native entrance; first source Main is stale.'


if __name__=='__main__':main()
