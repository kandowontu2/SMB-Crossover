"""Same-life pipe entrance chooses its native anchor before donor resumes."""
import inspect
import json
from pathlib import Path
import check_dkjr_anchored_lifetime_1103_v95 as F

A,R,O,N,W,C=F.A,F.R,F.O,F.N,F.W,F.C


def main():
    b,q=F.P.image();L=json.loads((O/'native-entrance-v89-layout.json').read_text())['labels']
    enter=inspect.getsource(F.E.run)
    assert enter.count('AltEntranceControl=0')==1
    enter=enter.replace('AltEntranceControl=0','AltEntranceControl=2')
    old="    N.invoke(m,'GameCoreRoutine',a=83,x=0,y=0,p=0x21)"
    assert enter.count(old)==1;enter=enter.replace(old,'    # Leave genuine pending pipe entry for the bounded loop below.')
    enter=enter.replace("    assert N.get(m,'GameEngineSubroutine')==8","    assert N.get(m,'GameEngineSubroutine')==7")
    env=dict(F.E.__dict__);exec(compile(enter,__file__,'exec'),env)
    m,history,_=env['run'](b)
    assert m.ram[2][0x8fe]==1 and N.get(m,'AltEntranceControl')==2
    actor=bytes(m.ram[2][:0x800]);pending=0
    for index in range(130):
        if N.get(m,'GameEngineSubroutine')==8:break
        # Actual native entrance may call native scripted motion, while its
        # DK Main guard must not consume the already constructed donor state.
        N.invoke(m,'HuMovement',a=85,x=0,y=0,p=0x31)
        assert bytes(m.ram[2][:0x800])==actor and m.ram[2][0x8fe]==1
        N.invoke(m,'PlayerEntrance',a=0,x=0,y=0,p=0x21)
        pending+=1
    else:raise AssertionError('Real native pipe entry did not complete')
    actual=dict(X=N.get(m,'Player_X_Position'),page=N.get(m,'Player_PageLoc'),Y=N.get(m,'Player_Y_Position'),high=N.get(m,'Player_Y_HighPos'),camera=N.get(m,'ScreenLeft_X_Pos'))
    assert actual['Y']==144 and actual['high']==1 and m.ram[2][0x8fe]==1
    native=N.NesMPU;snapshots=[]
    class Trace(native):
        def step(self):
            bank=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            if bank==2 and self.pc==L['DkPauseMain']:
                snapshots.append(dict(ready=self.memory.ram[2][0x8fe],X=self.memory.ram[2][0x213],Y=self.memory.ram[2][0x210],source_state=self.memory.ram[2][0x6b],source_defeat_counter=self.memory.ram[2][0x65]))
            return super().step()
    N.NesMPU=Trace
    try:N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)
    finally:N.NesMPU=native
    assert len(snapshots)==1
    first=snapshots[0]
    assert first==dict(ready=2,X=(actual['X']-actual['camera']-8)&255,Y=actual['Y']+15,source_state=1,source_defeat_counter=36),first
    assert N.get(m,'NumberofLives')==2
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(b['raw']),manual_final_native_Y_written=False,
        actual_native_pipe_entry_pending_updates=pending,actual_completed_entrance=actual,
        first_source_phase_snapshot=first,
        source_actor_unchanged_during_engine7=True,
        scope='Actual unchanged Entrance_GameTimerSetup AltEntrance2/header2 starts below viewport, PlayerEntrance moves upward toY144 and releasesengine8. PendingDK Main never advances original2048-byte actor/HP/counter/items. First realGameCore takes nativechosenX/page/Y/high/camera through existingImportAnchor, publishesReady2, and only then enters DkPauseMain/originalphase. No fixedY correction/newRAM; tablevalue144 is observed and asserted as nativebehavior. Same-life scene/Fresh rearming andpopulatedpause retire are separately97. No fullscene40/menu admission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(F.__file__),Path(F.E.__file__),O/'native-owner-proposal-v90.json',O/'native-entrance-v89-layout.json',O/'native-anchored-lifetime-v97-CPU.json',R/'src/player.s']})
    (O/'native-pipe-reanchor-v99-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','actual_native_pipe_entry_pending_updates','actual_completed_entrance','first_source_phase_snapshot']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-pipe-reanchor-v99-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
