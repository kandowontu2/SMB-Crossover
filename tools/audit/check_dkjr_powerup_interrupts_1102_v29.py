"""Real IRQ/lagNMI cuts through the final nested native powerup callback.

Consumes frozen v27 unchanged. Historical private shared model only; no ROM.
"""
import argparse,contextlib,io,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0);args=ap.parse_args()
    path=R/'tools/audit/check_dkjr_native_powerup_1102_v27.py';source=path.read_text()
    source=source.replace("N.invoke(m,'PlayerChangeSize')","PROBE['active']=epoch==60;N.invoke(m,'PlayerChangeSize');PROBE['active']=False")
    source=source.replace("O/'native-powerup-v27-CPU.json'","O/'native-powerup-v29-trace.json'")
    native=N.NesMPU;allcuts=set();minimum=255;stress_counts={}
    def run(kind=None,cut=None):
        probe=dict(active=False);injected=False;injected_shapes=set()
        class Interrupt(native):
            def step(self):
                nonlocal injected,minimum
                m=self.memory
                if probe['active']:
                    here=(self.pc,self.sp,m.rawtags[1],m.rawtags[2]);allcuts.add(here)
                    if(cut=='ALL'and here not in injected_shapes)or(cut==here and not injected):
                        injected_shapes.add(here)
                        injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(m.rawtags);private=[bytes(v)for v in m.ram];scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);writes=len(m.ram_writes)
                        assert not self.p&4,('masked fixture interrupt',kind,cut)
                        self.irq()if kind=='IRQ'else self.nmi()
                        for _ in range(200000):
                            minimum=min(minimum,self.sp)
                            if(self.pc,self.sp)==(regs[5],regs[4]):break
                            assert m[self.pc]!=0,('actual native ISR BRK',kind,cut,hex(self.pc));native.step(self)
                        else:raise AssertionError(('actual native ISR bound',kind,cut))
                        assert regs[:3]==(self.a,self.x,self.y)and regs[3]&0xef==self.p&0xef and regs[4:]==(self.sp,self.pc),(kind,cut,'ISR AXYP/SP/PC')
                        if maps!=m.rawtags:
                            op=bytes(m[self.pc:self.pc+3]);assert op in [bytes.fromhex('8d1551'),bytes.fromhex('8e1651'),bytes.fromhex('8d1651')]
                            win=1 if op[1]==0x15 else 2;shadow=N.get(m,'CurrentBank'if win==1 else'CurrentBankC');assert m.rawtags[win]==shadow and all(maps[i]==m.rawtags[i]for i in range(4)if i!=win)
                        assert private==[bytes(v)for v in m.ram]and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b]),(kind,cut,'ISR private/scratch/SMC')
                        assert not m.ram_writes[writes:],(kind,cut,'ISR overlay writes')
                return native.step(self)
        N.NesMPU=Interrupt;env={'__name__':'dk_irq_probe','__file__':__file__,'PROBE':probe}
        try:
            with contextlib.redirect_stdout(io.StringIO()):exec(compile(source,str(path),'exec'),env);env['main']()
        finally:N.NesMPU=native
        assert cut is None or injected,(kind,cut,'cut not reached')
        if cut=='ALL':stress_counts[kind]=len(injected_shapes)
        return json.loads((O/'native-powerup-v29-trace.json').read_text())
    base=run();cuts=sorted(allcuts);assert cuts
    chosen=cuts[:args.limit]if args.limit else cuts;cases=0
    for kind in ['IRQ','lagNMI']:
        if not args.limit:
            result=run(kind,'ALL');assert result['checks']==base['checks']and result['actual_calls']==base['actual_calls'],(kind,'all shapes sequential stress','full foreground continuation')
            cases+=stress_counts[kind]
        else:
            for cut in chosen:
                result=run(kind,cut);assert result['checks']==base['checks']and result['actual_calls']==base['actual_calls'],(kind,cut,'full foreground native continuation')
                cases+=1
    independent_deep=0
    if not args.limit:
        for kind in ['IRQ','lagNMI']:
            for cut in sorted(cuts,key=lambda x:(x[1],x[0]))[:4]:
                result=run(kind,cut);assert result['checks']==base['checks']and result['actual_calls']==base['actual_calls'],(kind,cut,'independent deepest-stack control')
                independent_deep+=1
    out=dict(passed=True,ROM_written=False,native_owner_admitted=False,historical_private_CPU_model_only=True,unique_final_powerup_instruction_cut_shapes=len(cuts),tested_cut_shapes=len(chosen),actual_IRQ_and_lagNMI_returns=cases,independent_deepest_stack_controls=independent_deep,minimum_ISR_SP=minimum,sample_limited=bool(args.limit),sequential_stress_per_kind=stress_counts,
        cut_identity='PC/SP/A-window/C-window; final real native powerup epoch includes nested GuestFinish/GetPlayerColors/own26 and full authenticated frame/header transport. Loop iterations sharing this state shape are one cut, consistent with earlier shared-frame proofs.',
        proven='Actual native IRQ/lagNMI handlers return exact AXYP/SP/PC, permitted pending mapper-store relation, full R0..7/SMC/private arrays unchanged and zero overlay writes. Default mode injects one interrupt at every distinct foreground shape sequentially in one final powerup epoch per interrupt kind, then verifies the full60update/sourcepause/foreignretire continuation. It is not independent fresh-native-bookkeeping replay per shape; --limit provides independent individual-cut controls.',
        remaining=['All final latest-Prince four-owner cold/retire/scene/service cuts and foreign parity; current model is v65 only.','Unfinished29DKrows, full art/cookie/real native candidate and Mesen1-1.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,O/'native-powerup-v27-CPU.json',O/'native-powerup-v26.bin',O/'native-powerup-ports-v26.bin',O/'retire-owner-v18.bin',O/'retire-selector-v18.bin']})
    (O/'native-powerup-v29-IRQ.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','unique_final_powerup_instruction_cut_shapes','tested_cut_shapes','actual_IRQ_and_lagNMI_returns','minimum_ISR_SP','sample_limited']}))


if __name__=='__main__':main()
