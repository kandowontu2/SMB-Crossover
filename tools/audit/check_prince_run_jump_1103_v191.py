"""One earned current-source running-A trajectory for controller timing only."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
import check_prince_control_recipe_1103_v190 as V
M,N,I,O=V.M,V.N,V.I,V.O


def main():
    V.G.preflight(private_root=O,reserved_bytes=30000,reserved_files=1,fresh=True)
    base,q=M.image();e,m,lab=V.A.first8(base)
    actual=N.NesMPU;backward_writes=[]
    class Trace(actual):
        def step(self):
            mem=self.memory;old=N.get(mem,'Player_X_Position')+256*N.get(mem,'Player_PageLoc')
            pc=self.pc;bank=mem.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else None
            regs=[self.a,self.x,self.y,self.p,self.sp]
            result=super().step()
            new=N.get(mem,'Player_X_Position')+256*N.get(mem,'Player_PageLoc')
            if new<old and len(backward_writes)<16:
                s=mem.ram[2]
                backward_writes.append(dict(PC=pc,bank=bank,oldX=old,newX=new,AXYPSP=regs,
                    nativeY=N.get(mem,'Player_Y_Position'),sourceY=s[0x611],pose=s[0x617],
                    action=s[0x616],mode=s[0x618],foot=int.from_bytes(s[0x84:0x86],'little'),
                    R0_R7=list(mem[3:11])))
            return result
    prior=e['run']
    def observed(*args,**kwargs):
        N.NesMPU=Trace
        try:return prior(*args,**kwargs)
        finally:N.NesMPU=actual
    e['run']=observed
    stage='run';start=None;begun=None;rows=[];last=None;advances=controls=0
    initial=V.row(m,0)
    for epoch in range(220):
        s=m.ram[2]
        if stage=='run' and s[0x618]==1 and s[0x616]==1 and 6<=s[0x617]<14:
            stage='A';start=dict(V.row(m,epoch),advances=advances,controls=controls)
        pad=129 if stage=='A' else 1
        m.controller_pad=pad;N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
        phase=s[0xa6]&3
        e['run'](m,'GameLoop',lab)
        if phase==0:advances+=1
        if phase==2:controls+=1
        now=V.row(m,epoch)
        if stage=='A' and now['action']==4:
            begun=dict(now,advances=advances,controls=controls);stage='flight'
        if stage!='run' and (last is None or (now['action'],now['mode'],now['pose'],now['sourceY'],now['foot'],now['nativeY'],now['X'])!=last):
            rows.append(dict(now,advances=advances,controls=controls))
            last=(now['action'],now['mode'],now['pose'],now['sourceY'],now['foot'],now['nativeY'],now['X'])
        assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'NumberofLives')==2 and s[0x6cf]==5
        if stage=='flight' and epoch>begun['Main']+8 and now['mode']==1 and now['action']==1 and now['foot']>=207:
            break
    if not(start and begun and stage=='flight' and rows[-1]['action']==1):
        print(json.dumps(dict(stage=stage,start=start,begun=begun,last=V.row(m,epoch),tail=rows[-12:])),flush=True)
    assert start and begun and stage=='flight' and rows[-1]['action']==1
    source_min=min(r['sourceY'] for r in rows);footmin=min(r['foot'] for r in rows)
    out=dict(passed=True,CPU_only=True,ROM_written=False,Mesen_run=False,
             memory_SHA256=q['expected_memory_only_SHA256'],initial=initial,run_A_begin=start,
             original_action4_admitted=begun,landing=rows[-1],
             A_held_original_advances=begun['advances']-start['advances'],
             A_held_original_controls=begun['controls']-start['controls'],
             sourceY_min=source_min,physical_foot_min=footmin,
             running_initial_floor_foot=208,native_foot_lift=208-footmin,
             whole_flight_Mains=rows[-1]['Main']-begun['Main'],
             whole_flight_original_advances=rows[-1]['advances']-begun['advances'],
             native_horizontal_flight=rows[-1]['X']-begun['X'],trace=rows,
             observed_backward_native_X_writes=backward_writes,
             retained_negative='Initial191 observer logged only pose/coordinates, so omitted final action4->1 controls-only change. Currentactor was alreadyrunningaction1 atMain70; finalstoredrow stillaction4. Successor addsaction/mode to observationkey, retaining same running/landing assertions.',
             recipe='KeepRight until original action1/mode1 and pose6..13; then Right+A until genuineaction4, releaseA but keepRight through landing. Original source runningjump selector only admits during pose6..13; no source/native outcome writes.',
             limitation='Flat current-source CPU trajectory is not native enemy clearance or a stage controller. Original runningA32pipe failure remains; firstpipe requires testedUp/ledge approach.',
             bindings={p.relative_to(R).as_posix():M.sha(p) for p in [Path(__file__),Path(V.__file__),
                       M.O/'pose-manifest.json',R/'build/prince-actor-1101-v1/contact-core.s']})
    (O/'run-jump.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['trace','bindings']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        p=O/'run-jump-negative.json'
        if not p.exists():p.write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n')
        raise
