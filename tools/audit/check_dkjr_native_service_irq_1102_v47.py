"""Actual IRQ/lagNMI at deepest earned Main service cut, full continuation."""
import contextlib,io,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O


def main():
    path=R/'tools/audit/check_dkjr_native_defeat_leaf_1102_v46.py';source=path.read_text();base=N.NesMPU
    minsp=255;deepest=None;minimum_ISR=255;results=[]
    def run(kind=None,cut=None):
        nonlocal minsp,deepest,minimum_ISR
        injected=False
        class Interrupt(base):
            def step(self):
                nonlocal injected,minsp,deepest,minimum_ISR
                m=self.memory;here=(self.pc,self.sp,m.rawtags[1],m.rawtags[2])
                if self.sp<minsp:minsp=self.sp;deepest=here
                if cut==here and not injected:
                    injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(m.rawtags);private=[bytes(v)for v in m.ram];scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);writes=len(m.ram_writes)
                    assert not self.p&4
                    self.irq()if kind=='IRQ'else self.nmi()
                    for _ in range(200000):
                        minimum_ISR=min(minimum_ISR,self.sp)
                        if(self.pc,self.sp)==(regs[5],regs[4]):break
                        assert m[self.pc]!=0,('native service ISR BRK',kind,cut,hex(self.pc));base.step(self)
                    else:raise AssertionError(('native service ISR bound',kind,cut))
                    assert regs[:3]==(self.a,self.x,self.y)and regs[3]&0xef==self.p&0xef and regs[4:]==(self.sp,self.pc)
                    assert maps==m.rawtags and private==[bytes(v)for v in m.ram]and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b]),('native service ISR preservation',kind,cut,minimum_ISR)
                    assert not m.ram_writes[writes:]
                return super().step()
        N.NesMPU=Interrupt;env={'__name__':'dk_deep_service_irq','__file__':str(path)}
        try:
            with contextlib.redirect_stdout(io.StringIO()):exec(compile(source,str(path),'exec'),env);env['main']()
        finally:N.NesMPU=base
        assert cut is None or injected
        return json.loads((O/'native-defeat-v46-qualified.json').read_text())
    baseline=run();cut=deepest
    for kind in ['IRQ','lagNMI']:
        try:
            receipt=run(kind,cut);assert receipt['full_native_Main']==baseline['full_native_Main'];results.append(dict(kind=kind,passed=True))
        except AssertionError as error:
            out=dict(passed=False,ROM_written=False,native_owner_admitted=False,minimum_foreground_SP=minsp,deepest_PC_SP_maps=cut,minimum_ISR_SP=minimum_ISR,error=str(error),completed=results)
            (O/'native-service-v47-IRQ-negative.json').write_text(json.dumps(out,indent=2)+'\n');raise
    out=dict(passed=True,ROM_written=False,native_owner_admitted=False,minimum_foreground_SP=minsp,deepest_PC_SP_maps=cut,minimum_ISR_SP=minimum_ISR,checks=results,
        scope='Independent actual IRQ and lagNMI at the measured deepest native earned-Main service cut, with complete62epoch/192native-defeat continuations unchanged. Not every changed service instruction or final latest-owner ISR closure.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,O/'native-defeat-v45.bin',O/'native-defeat-v46-qualified.json']})
    (O/'native-service-v47-IRQ.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':main()
