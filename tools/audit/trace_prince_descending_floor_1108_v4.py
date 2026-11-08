"""Trace current source speed and native floor writers; no candidate changes."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import rebase_prince_deep_foot_1108_v1 as Q
N,I,A=Q.N,Q.I,Q.A
O=R/'build/prince-easy-descending-1108-v4'
NATIVE=R/'build/prince-deep-gap130-1108/capture/prince-diagnostic.json'


def fixture():
    _,base,_,_=Q.image();e,m,lab=A.first8(base)
    Q.N.put(m,CrossoverBehaviorVersion=0)
    return base,e,m,lab


def main():
    Q.M.STORAGE.preflight(private_root=O,reserved_bytes=30000,reserved_files=2,fresh=True);O.mkdir(exist_ok=True)
    native=json.loads(NATIVE.read_text());p=native['first_pipe_route'];bad=p['precontacts'][0]
    before=next(r for r in p['pose_boxes'] if r['source_frame']==42)
    assert native['ROM_sha256']=='61d09e24ab3cd32ca0ad96ac7383111d24e99a793bb2094c26c7116da1cc6a9d'
    assert (before['physical_foot'],bad['physical_foot'],bad['native_enemy_world'][1],bad['native_DY'],bad['native_state'])==(193,211,198,0,0)
    base,e,m,lab=fixture()
    addr=lambda n:I.address(base,n)
    points={(((I.location(base,n)-16)//8192)|128,addr(n)):n for n in ['X5EasyFootBox','X5EasyBodyContact','X5BounceProfile','LmBodyGate','GuestBodyContactBridge','LandPlyr','EnemyStomped','HandlePECollisions']}
    points[3,lab['PpNativeVerticalExport']]='PpNativeVerticalExport'
    points[2,lab['PpNativeMotionExport']]='PpNativeMotionExport'
    fields=['Player_Y_Speed','Player_State','X5FootDescending','Player_Y_Position']
    addrs={n:addr(n) for n in fields}
    events=[];calls={};actual=N.NesMPU;epoch=0
    def state(c):
        s=c.memory.ram[2]
        return dict(source_pose=s[0x617],source_action=s[0x616],source_mode=s[0x618],source_phase=s[0xa6],
            foot=int.from_bytes(s[0x84:0x86],'little'),oldfoot=int.from_bytes(s[0x86:0x88],'little'),
            **{n:c.memory[a] for n,a in addrs.items()})
    class Trace(actual):
        def step(self):
            mem=self.memory;pc=self.pc;bank=mem.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else None
            point=points.get((bank,pc));watch=54<=epoch<=63
            if point:
                calls[point]=calls.get(point,0)+1
                if watch:events.append(dict(Main=epoch,PC=pc,bank=bank,entry=point,A=self.a,X=self.x,Y=self.y,P=self.p,**state(self)))
            snapshot=[mem[a] for a in addrs.values()] if watch else None
            result=super().step()
            if watch:
                after=[mem[a] for a in addrs.values()]
                if snapshot!=after:
                    events.append(dict(Main=epoch,PC=pc,bank=bank,changed={n:[x,y] for n,x,y in zip(addrs,snapshot,after) if x!=y},**state(self)))
            return result
    stage='run'
    for epoch in range(65):
        s=m.ram[2]
        if stage=='run' and s[0x616]==1 and s[0x618]==1 and 6<=s[0x617]<14:stage='A'
        pad=129 if stage=='A' else 1;m.controller_pad=pad;N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
        N.NesMPU=Trace
        try:e['run'](m,'GameLoop',lab)
        finally:N.NesMPU=actual
        if stage=='A' and s[0x616]==4:stage='flight'
        assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'NumberofLives')==2 and s[0x6cf]==5
    at43=[r for r in events if r['source_pose']==43]
    assert at43 and any(r['foot']==211 and r['oldfoot']==193 for r in at43)
    writes=[r for r in at43 if 'Player_Y_Speed' in r.get('changed',{})]
    assert any(r['changed']['Player_Y_Speed'][1]==18 for r in writes)
    assert any(r['changed']['Player_Y_Speed']==[18,0] for r in writes)
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,Mesen_run=False,
        exact_native_negative=dict(sha256=native['ROM_sha256'],pose42=before,precontact_pose43=bad),
        actual_current_CPU_pose43_writes=writes,calls=calls,pose43_trace=at43,
        addresses={n:f'{a:04X}' for n,a in addrs.items()},
        bindings={p.relative_to(R).as_posix():Q.M.sha(p) for p in [Path(__file__),NATIVE,Q.O/'landing-contract.json',R/'src/collision.s',R/'src/x5_bounce.s']})
    (O/'descending-floor-trace.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(calls=calls,pose43_speed_writes=writes,first_native=dict(foot=[193,211],enemy_top=198,DY=0)),indent=2),flush=True)


if __name__=='__main__':main()
