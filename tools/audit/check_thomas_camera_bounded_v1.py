"""Natural Main/camera route with each accepted actor frame replayed in donor code."""
from pathlib import Path
import argparse,ast,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_hogan_current_bounded_v1 as C
import thomas_original_cpu_1031_v1 as T
from verify_native_relocation import NesMPU
J=R/'build/thomas-adapter';O=J/'checks'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
observer=R/'tools/audit/check_thomas_actual_host_vectors_1031_v1.py'
oracle=R/'tools/audit/check_thomas_natural_original_1031_v1.py'
ns={'OverlayMemory':C.Bus,'NesMPU':NesMPU}
nodes=[n for n in ast.parse(observer.read_text()).body if isinstance(n,ast.ClassDef)and n.name in ['HostMemory','CPU']]
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(observer),'exec'),ns)
refns={'T':T}
nodes=[n for n in ast.parse(oracle.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in ['original_hunk','original_frame']]
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(oracle),'exec'),refns)


class CPU(ns['CPU']):
    def step(self):
        m=self.memory
        if m.rawtags[1]==3 and self.pc==m.frame_entry:
            assert m.pending is None
            ref=T.machine();state=bytearray(m.ram[2][:2048]);state[:16]=m.logical
            ref.memory[:2048]=state
            attack=refns['original_frame'](ref,self.a)
            ret=m[0x101+self.sp]|(m[0x102+self.sp]<<8)
            m.pending=(ret+1,self.sp+2,ref,attack)
        if m.pending and self.pc==m.pending[0]and self.sp==m.pending[1]:
            _,_,ref,attack=m.pending
            state=bytearray(m.ram[2][:2048]);state[:16]=m.logical
            actual=bytes(state[:256]+state[512:])
            expected=bytes(ref.memory[:256]+ref.memory[512:2048])
            assert actual==expected,('Original actor first difference',m.actor_frames,[(hex(i),a,z)for i,(a,z)in enumerate(zip(actual,expected))if a!=z][:12])
            assert (m.ram[2][0x808],m.ram[2][0x809],bytes(m.ram[2][0x80a:0x80e]))==attack
            m.actor_frames+=1;m.pending=None
        return super().step()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--crouch',action='store_true')
    args=ap.parse_args()
    if O.exists():
        assert args.crouch and (O/'negative/standing-kick-attempt.zip').is_file()
        output=O/'controls-crouch.json';assert not output.exists()
    else:O.mkdir();output=O/'controls.json'
    q=dict(passed=False,native=False,source_CPU=True,contact_policy='crouch-punch'if args.crouch else'standing-kick')
    try:
        stage=json.loads((J/'source-stage.json').read_text())
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=C.scoped_load(J/'candidate.nes');syms=T.labels(J/'candidate.lbl')
        def factory(bundle):
            m=ns['HostMemory'](bundle);m.observe(syms)
            m.frame_entry=syms['ThomasC2AcceptedFrame'];m.pending=None;m.actor_frames=0
            return m
        C.Bus=factory;C.NesMPU=CPU
        m=C.fresh(b);C.put(m,CrossoverMenuIndex=10,FmAlts=64,FmGroups=0)
        for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
        C.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
        C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
        for setup in range(600):
            if C.get(m,'OperMode_Task')==3 and C.get(m,'GameEngineSubroutine')==8:break
            C.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
            C.invoke(m,'GameLoop');C.consume(m)
        else:raise AssertionError('Actual parser bound')
        rows=[];defeats=0
        for age in range(650):
            x=C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc')
            near=any(0<C.get(m,'Enemy_Flag',i)<128 and C.get(m,'Enemy_ID',i)==6 and not C.get(m,'Enemy_State',i)&32 and
                     0<C.get(m,'Enemy_X_Position',i)+256*C.get(m,'Enemy_PageLoc',i)-x<=38 for i in range(6))
            if age<20:keys=0
            elif age<135:keys=1|(8 if 90<=age<94 else 0)
            elif age<155:keys=2
            elif near:keys=(68 if age%24<6 else 4)if args.crouch else(128 if age%24<6 else 0)
            else:keys=1
            C.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
            execution=C.invoke(m,'GameLoop');assert m.pending is None
            defeats+=execution['counts'].get('ShellOrBlockDefeat',0)
            x=C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc')
            camera=C.get(m,'ScreenLeft_X_Pos')+256*C.get(m,'ScreenLeft_PageLoc')
            rows.append(dict(age=age,input=keys,X=x,Y=C.get(m,'Player_Y_Position'),camera=camera,
                             original_B6=m.ram[2][0xb6],original_health=m.ram[2][0x4a6],
                             engine=C.get(m,'GameEngineSubroutine'),native_defeats=defeats,CPU=execution['CPU'],
                             attack_enabled=m[C.address(b,'ThAttackEnabled')],
                             attack_rectangle=list(m[C.address(b,'ThHostAttackRect'):C.address(b,'ThHostAttackRect')+4])if near else None))
            assert C.get(m,'GameEngineSubroutine')!=11,('Natural death',rows[-1])
            C.consume(m)
            if x>=369 and camera>=257 and defeats:break
        q.update(parser_Main=setup,Main_updates=len(rows),original_actor_frame_pairs=m.actor_frames,
                 maximum_X=max(z['X']for z in rows),maximum_camera=max(z['camera']for z in rows),
                 minimum_original_B6=min(z['original_B6']for z in rows),native_defeats=defeats,rows=rows)
        assert q['maximum_X']>=369 and q['maximum_camera']>=257 and defeats,('Bounded route/contact',rows[-1])
        assert q['minimum_original_B6']==108,'Original27px jump must remain intact'
        assert rows[154]['X']<rows[134]['X'],'Actual reversal'
        q['passed']=True
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        q.update(candidate=sha(J/'candidate.nes'),scope='Native parser/Main/NMI CPU model and exact original actor-frame oracle, with explicit host stage-distance projection. No native emulator, full1-1, pipe-clearance or audio claim.',
                 bindings={str(p):sha(p)for p in [Path(__file__),observer,oracle,Path(T.__file__),Path(C.__file__),C.model,T.DONOR,J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg']})
        output.write_text(json.dumps(q,indent=2)+'\n')
        print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','rows','traceback']}))


if __name__=='__main__':main()
