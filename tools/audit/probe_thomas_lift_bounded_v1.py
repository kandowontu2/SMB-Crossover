"""Controller-byte first-platform boarding/carry probe; no gameplay state edits."""
from pathlib import Path
import argparse,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_thomas_camera_bounded_v1 as Q
C=Q.C;T=Q.T
J=R/'build/thomas-pipe-lifts';O=J/'boarding'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    global J,O
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint',type=Path,default=J)
    ap.add_argument('--output',type=Path,default=O)
    ap.add_argument('--runup',action='store_true')
    args=ap.parse_args();J=args.joint.resolve();O=args.output.resolve()
    assert not O.exists();O.mkdir();q=dict(passed=False,source_CPU=True,native=False)
    rows=[];minimum_sp=255
    try:
        b=C.scoped_load(J/'candidate.nes');syms=T.labels(J/'candidate.lbl')
        def factory(bundle):
            m=Q.ns['HostMemory'](bundle);m.observe(syms)
            m.frame_entry=syms['ThomasC2AcceptedFrame'];m.pending=None;m.actor_frames=0
            return m
        C.Bus=factory;C.NesMPU=Q.CPU
        m=C.fresh(b);C.put(m,CrossoverMenuIndex=10,FmAlts=64,FmGroups=0)
        for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
        C.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
        C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
        def step(keys):
            nonlocal minimum_sp
            C.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
            z=C.invoke(m,'GameLoop');minimum_sp=min(minimum_sp,z['minimum_SP']);C.consume(m)
            assert C.get(m,'GameEngineSubroutine')!=11,'Natural death'
            return z
        for setup in range(600):
            if C.get(m,'OperMode_Task')==3 and C.get(m,'GameEngineSubroutine')==8:break
            step(0)
        else:raise AssertionError('Native parser bound')
        state='approach';hop=0;previous_lift=None;defeats=0;runup=0
        for age in range(1500):
            x=C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc')
            slots=[i for i in range(6)if C.get(m,'Enemy_Flag',i)==1 and C.get(m,'Enemy_ID',i)==37 and C.get(m,'Enemy_X_Position',i)+256*C.get(m,'Enemy_PageLoc',i)==400]
            slot=slots[0]if slots else None
            ly=C.get(m,'Enemy_Y_Position',slot)if slot is not None else None
            near=any(0<C.get(m,'Enemy_Flag',i)<128 and C.get(m,'Enemy_ID',i)==6 and not C.get(m,'Enemy_State',i)&32 and
                     0<C.get(m,'Enemy_X_Position',i)+256*C.get(m,'Enemy_PageLoc',i)-x<=38 for i in range(6))
            if near:keys=68 if age%24<6 else 4
            elif state=='approach':
                keys=1
                if x>=(376 if args.runup else 368):state='wait';keys=0
            elif state=='wait':
                keys=0
                if ly and ly>=188 and(previous_lift is None or ly>=previous_lift):state='runup'if args.runup else'hop';hop=0
            elif state=='runup':
                keys=1;runup+=1
                if runup>=6:state='hop';hop=0
            elif state=='hop':
                keys=1|(8 if hop<3 else 0);hop+=1
                if x>=414:state='ride'
            elif state=='ride':
                keys=0
                if C.get(m,'Player_Y_Position')+32<=160:state='cross';hop=0
            else:keys=1|(8 if hop<3 else 0);hop+=1
            z=step(keys);defeats+=z['counts'].get('ShellOrBlockDefeat',0)
            x=C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc')
            rows.append(dict(age=age,state=state,input=keys,X=x,Y=C.get(m,'Player_Y_Position'),
                             original_B6=m.ram[2][0xb6],ground=int.from_bytes(m.ram[2][0x820:0x822],'little'),
                             lift_slot=slot,lift_Y=ly,platform_contact=C.get(m,'PlatformCollisionFlag',slot)if slot is not None else None,
                             player_state=C.get(m,'Player_State'),native_defeats=defeats,minimum_SP=z['minimum_SP']))
            previous_lift=ly
            if x>=496:break
        q.update(Main=len(rows),original_actor_frame_pairs=m.actor_frames,maximum_X=max(z['X']for z in rows),
                 minimum_Y=min(z['Y']for z in rows),minimum_Main_SP=minimum_sp,native_defeats=defeats,rows=rows)
        assert x>=496,('First pipe/carry bound',rows[-1]);q['passed']=True
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        q.update(candidate=sha(J/'candidate.nes'),running_start=args.runup,scope='Finite controller-byte source CPU route and exact donor actor oracle; no native emulator or full1-1 claim.',
                 bindings={str(p):sha(p)for p in [Path(__file__),Path(Q.__file__),Path(C.__file__),Q.observer,Q.oracle,J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg']})
        (O/'probe.json').write_text(json.dumps(q,indent=2)+'\n')
        print(json.dumps({k:v for k,v in q.items()if k not in ['rows','bindings','traceback']}))


if __name__=='__main__':main()
