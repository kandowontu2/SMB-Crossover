"""Decode real pipe geometry and try finite controller-only first-pipe approaches."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_thomas_camera_bounded_v1 as Q
C=Q.C;T=Q.T
J=Q.J;O=J/'pipe-analysis'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir()
    b=C.scoped_load(J/'candidate.nes');syms=T.labels(J/'candidate.lbl')
    def factory(bundle):
        m=Q.ns['HostMemory'](bundle);m.observe(syms)
        m.frame_entry=syms['ThomasC2AcceptedFrame'];m.pending=None;m.actor_frames=0
        return m
    C.Bus=factory;C.NesMPU=Q.CPU
    # Explicit static-map fixture, not a gameplay replay. Execute the existing
    # native parser; never infer geometry from a screenshot or guessed tiles.
    static=C.fresh(b);C.put(static,AreaPointer=37,WorldNumber=0,Hidden1UpFlag=1)
    C.invoke(static,'GetAreaDataAddrs')
    for i in range(3):static[C.address(b,'AreaObjectLength')+i]=255
    columns=[]
    for x in range(72):
        C.invoke(static,'AreaParserCore')
        columns.append(list(static[C.address(b,'MetatileBuffer'):C.address(b,'MetatileBuffer')+13]))
        C.invoke(static,'IncrementColumnPos')
    at=C.location(b,'VerticalPipeData');pipe_tiles=list(b['raw'][at:at+8])
    pipes=[]
    # Pipe cap left/right are the exact native VerticalPipeData[1]/[0].
    for x,col in enumerate(columns[:-1]):
        for y,tile in enumerate(col):
            if tile==pipe_tiles[1]and columns[x+1][y]==pipe_tiles[0]:
                pipes.append(dict(X=x*16,top=(y+2)*16,width=32,height=208-(y+2)*16))
    assert pipes,'Actual pipe caps were decoded'
    m=C.fresh(b);C.put(m,CrossoverMenuIndex=10,FmAlts=64,FmGroups=0)
    for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
    C.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
    C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
    for setup in range(600):
        if C.get(m,'OperMode_Task')==3 and C.get(m,'GameEngineSubroutine')==8:break
        step(m,0)
    else:raise AssertionError('Native parser bound')
    defeats=0
    for age in range(650):
        x=world(m)
        near=any(0<C.get(m,'Enemy_Flag',i)<128 and C.get(m,'Enemy_ID',i)==6 and not C.get(m,'Enemy_State',i)&32 and
                 0<C.get(m,'Enemy_X_Position',i)+256*C.get(m,'Enemy_PageLoc',i)-x<=38 for i in range(6))
        execution=step(m,(68 if age%24<6 else 4)if near else 1)
        defeats+=execution['counts'].get('ShellOrBlockDefeat',0)
        if world(m)>=369 and defeats:break
    else:raise AssertionError('Natural opening approach')
    cases=[]
    for start in [405,420,432]:
        for policy in ['up-pulse','up-held','up-kick']:
            z=C.fork(m);jump_age=None;minimum_y=255;maximum_x=world(z);frames=z.actor_frames
            for age in range(150):
                x=world(z)
                if jump_age is None and x>=start:jump_age=age
                j=age-jump_age if jump_age is not None else -1
                up=0<=j<(40 if policy=='up-held'else 3)
                keys=1|(8 if up else 0)|(128 if policy=='up-kick'and 3<=j<9 else 0)
                step(z,keys);minimum_y=min(minimum_y,C.get(z,'Player_Y_Position'));maximum_x=max(maximum_x,world(z))
            cases.append(dict(start_X=start,policy=policy,Main=150,original_actor_pairs=z.actor_frames-frames,maximum_X=maximum_x,minimum_Y=minimum_y,cleared_first_pipe=maximum_x>=480,health=z.ram[2][0x4a6]))
    q=dict(completed=True,source_CPU=True,native=False,product_changed=False,candidate=sha(J/'candidate.nes'),
           pipes=pipes,pipe_tile_bytes=pipe_tiles,source_jump_rise=27,cases=cases,
           scope='One static native-parser map fixture plus legal cold/controller-byte approach and in-memory branches. No coordinate/HP/tile edits in gameplay. Nine policies are finite evidence, not exhaustive TAS impossibility.',
           proposed_changes_before_implementation=[dict(character='Thomas only',stage='1-1',pipe=p,proposed_native_vertical_platform_X=p['X']-48,proposed_initial_Y=192,reason='Original27px jump; reuse SMB native vertical platform25 and its support/carry/render code.')for p in pipes if p['X']<1000],
           changes_applied=False,
           bindings={str(p):sha(p)for p in [Path(__file__),Path(Q.__file__),Path(C.__file__),Q.observer,Q.oracle,J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg']})
    (O/'analysis.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['completed','pipes','cases','changes_applied']}))


def world(m):return C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc')


def step(m,keys):
    C.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
    q=C.invoke(m,'GameLoop');C.consume(m)
    assert C.get(m,'GameEngineSubroutine')!=11,'Natural death'
    return q


if __name__=='__main__':main()
