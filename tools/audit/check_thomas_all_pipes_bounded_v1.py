"""Cold controller-byte four-pipe route and genuine deepest-combat vector cuts."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_thomas_camera_bounded_v1 as Q
from verify_native_relocation import NesMPU
C=Q.C;T=Q.T
J=R/'build/thomas-native-carry';O=J/'all-pipes'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BEST=None


class CPU(Q.CPU):
    def step(self):
        global BEST
        m=self.memory
        if self.pc==m.defeat_pc and m.rawtags[0]==254:m.defeat_phase=True
        if m.defeat_phase and(BEST is None or self.sp<BEST[1]['sp']):
            BEST=(C.fork(m),{k:v for k,v in self.__dict__.items()if k!='memory'})
        return super().step()


def vectors():
    assert BEST is not None
    results=[]
    for nested in [False,True]:
        m=C.fork(BEST[0]);c=NesMPU(memory=m);c.__dict__.update(BEST[1])
        real=lambda:(c.pc,c.sp,c.a,c.x,c.y,c.p&~0x30)
        before=real();maps=m.rawtags[:];smc=bytes(m[0x15a:0x17b]);borrowed=bytes(m[3:11]);detached=bytes(m.ram[2][0x850:0x85e])
        low=c.sp;injected=False;c.nmi()
        for _ in range(200000):
            low=min(low,c.sp)
            if real()==before:break
            if nested and not injected and not c.p&4:
                c.irq();injected=True
            assert m[c.pc]!=0,('Actual vector BRK',hex(c.pc),low)
            c.step()
        else:raise AssertionError('Actual vector return bound')
        assert not nested or injected,'Only legally unmasked nested IRQ counts'
        result=dict(nested_IRQ=nested,entry_SP=before[1],minimum_SP=low,returned_exact=real()==before,
                    SMC33_exact=bytes(m[0x15a:0x17b])==smc,borrowed_R0_R7_exact=bytes(m[3:11])==borrowed,
                    maps_exact=m.rawtags==maps,own_detached_gap_exact=bytes(m.ram[2][0x850:0x85e])==detached)
        result['passed']=low>0x7a and all(result[n]for n in ['returned_exact','SMC33_exact','borrowed_R0_R7_exact','maps_exact','own_detached_gap_exact'])
        results.append(result)
    return results


def main():
    assert not O.exists();O.mkdir();q=dict(passed=False,source_CPU=True,native=False);rows=[]
    try:
        stage=json.loads((J/'source-stage.json').read_text())
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=C.scoped_load(J/'candidate.nes');syms=T.labels(J/'candidate.lbl')
        def factory(bundle):
            m=Q.ns['HostMemory'](bundle);m.observe(syms)
            m.frame_entry=syms['ThomasC2AcceptedFrame'];m.pending=None;m.actor_frames=0
            m.defeat_pc=syms['ShellOrBlockDefeat'];m.defeat_phase=False
            return m
        C.Bus=factory;C.NesMPU=CPU
        m=C.fresh(b);C.put(m,CrossoverMenuIndex=10,FmAlts=64,FmGroups=0)
        for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
        C.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
        C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
        def step(keys):
            m.defeat_phase=False
            C.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
            z=C.invoke(m,'GameLoop');C.consume(m)
            assert C.get(m,'GameEngineSubroutine')!=11,'Natural death'
            return z
        for setup in range(600):
            if C.get(m,'OperMode_Task')==3 and C.get(m,'GameEngineSubroutine')==8:break
            step(0)
        else:raise AssertionError('Native parser bound')
        targets=[(400,176),(560,160),(688,144),(864,144)]
        target=0;state='approach';hop=runup=0;previous=None;defeats=0;clears=[]
        for age in range(6000):
            lift,pipe_top=targets[target]
            x=C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc');py=C.get(m,'Player_Y_Position')
            slots=[i for i in range(6)if C.get(m,'Enemy_Flag',i)==1 and C.get(m,'Enemy_ID',i)==37 and C.get(m,'Enemy_X_Position',i)+256*C.get(m,'Enemy_PageLoc',i)==lift]
            slot=slots[0]if slots else None;ly=C.get(m,'Enemy_Y_Position',slot)if slot is not None else None
            near=any(0<C.get(m,'Enemy_Flag',i)<128 and C.get(m,'Enemy_ID',i)==6 and not C.get(m,'Enemy_State',i)&32 and
                     0<C.get(m,'Enemy_X_Position',i)+256*C.get(m,'Enemy_PageLoc',i)-x<=38 and abs(C.get(m,'Enemy_Y_Position',i)-py)<=24 for i in range(6))
            if near:keys=68 if age%24<6 else 4
            elif state=='approach':
                keys=1
                if x>=lift-24:state='wait';keys=0
            elif state=='wait':
                keys=0
                if ly and ly>=188 and(previous is None or ly>=previous):state='runup';runup=0
            elif state=='runup':
                keys=1;runup+=1
                if runup>=6:state='hop';hop=0
            elif state=='hop':
                keys=1|(8 if hop<3 else 0);hop+=1
                if x>=lift+14:state='ride'
            elif state=='ride':
                keys=0
                if py+32<=pipe_top-16:state='cross';hop=0
            else:
                keys=1|(8 if 6<=hop<9 else 0);hop+=1
            z=step(keys);defeats+=z['counts'].get('ShellOrBlockDefeat',0)
            x=C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc')
            rows.append(dict(age=age,target=target,state=state,input=keys,X=x,Y=C.get(m,'Player_Y_Position'),lift_Y=ly,
                             contact=C.get(m,'PlatformCollisionFlag',slot)if slot is not None else None,
                             source_health=m.ram[2][0x4a6],native_defeats=defeats,minimum_SP=z['minimum_SP']))
            previous=ly
            if x>=lift+96:
                clears.append(dict(pipe_X=lift+48,Main=age+1,X=x));print('Thomas native-source pipe clear',clears[-1],flush=True)
                target+=1
                if target==4:break
                state='approach';previous=None
        q.update(parser_Main=setup,Main=len(rows),original_actor_frame_pairs=m.actor_frames,pipe_clears=clears,
                 native_defeats=defeats,maximum_X=max(z['X']for z in rows),rows=rows,combat_vectors=vectors())
        assert len(clears)==4,('Four-pipe controller bound',rows[-1])
        assert all(v['passed']for v in q['combat_vectors']),q['combat_vectors']
        q['passed']=True
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        q.update(candidate=sha(J/'candidate.nes'),scope='Real native parser/AI/support/carry/combat executed in CPU/peripheral model; exact original actor-frame pairs. Finite source interrupt cuts. No Mesen/raster, full1-1, audio or all-powerup qualification.',
                 bindings={str(p):sha(p)for p in [Path(__file__),Path(Q.__file__),Path(C.__file__),Q.observer,Q.oracle,J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg']})
        (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['rows','bindings','traceback']}))


if __name__=='__main__':main()
