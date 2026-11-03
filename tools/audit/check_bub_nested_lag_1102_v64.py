"""Focused worst-stack real lag-NMI plus nested native IRQ; no image emitted."""
from collections import Counter
import json
from pathlib import Path
import check_bub_collecting_interrupts_1102_v59 as I
import compose_bub_powerup_update_1102_v62 as G
from prepare_selected_native_packet_v1 import R,sha
Q,N,address=I.Q,I.N,I.address
O=R/'build/bub-upgrades-root-nested-1102-v64'

def main():
    O.mkdir(exist_ok=True);_,b,route,q=G.bundles();actual=N.NesMPU;winners={};context=None;mode='gather';wanted=None;minimum=224;counts=Counter()
    class Trace(actual):
        def nmi(self):self.lag_return=(self.pc,self.sp);return super().nmi()
        def step(self):
            nonlocal minimum
            ret=getattr(self,'lag_return',None)
            if ret is not None and (self.pc,self.sp)==ret:self.lag_return=None;ret=None
            if ret is not None and not self.p&4:
                m=self.memory;cut=(self.pc,self.sp,m.rawtags[1],m.rawtags[2]);key=(cut[0],cut[2],cut[3])
                if mode=='gather':
                    if key not in winners or self.sp<winners[key][0][1]:winners[key]=(cut,context)
                elif cut==wanted and not getattr(self,'nested_done',False):
                    self.nested_done=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);before=I.state(m);audio=m[0x7da]
                    self.irq()
                    for _ in range(20000):
                        minimum=min(minimum,self.sp)
                        if (self.pc,self.sp)==(regs[5],regs[4]):break
                        assert m[self.pc]!=0,('nested IRQ BRK',context,cut,hex(self.pc),self.sp);super().step()
                    else:raise AssertionError(('nested IRQ bound',context,cut))
                    assert (self.a,self.x,self.y,self.p&0xef,self.sp,self.pc)==(*regs[:3],regs[3]&0xef,*regs[4:])
                    assert I.state(m)==before and m[0x7da]==audio,('nested IRQ state',context,cut,minimum)
                    counts['nested_IRQ']+=1
            return super().step()
    N.NesMPU=Trace;scenarios=[]
    try:
        for identity in [0,1]:
            seed=Q.Q.fresh(b,route,identity);Q.L.E.main_fields(seed);N.put(seed,NmiDisable=255,TimerControl=1,Player_Rel_XPos=64,Player_Rel_YPos=176)
            N.invoke(seed,'HuFullBox',a=83,x=0,y=0,p=0x21)
            for kind in [0,1]:
                m=N.fork(seed);N.put(m,ObjectOffset=5)
                for field,v in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=191,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():m[address(b,field)+5]=v
                z=N.fork(m);ref=I.run(z);want=I.state(z);deep=min(ref['cuts'],key=lambda c:c[1]);index=len(scenarios);scenarios.append((m,ref,want))
                context=(index,deep);z=N.fork(m);I.run(z,('lagNMI',deep));assert I.state(z)==want;counts['deep_foreground_lag']+=1
        mode='replay';print('Focused deepest nested domain',len(winners),flush=True)
        # Deepest first makes an unsafe stack fail before broad replay.
        for cut,(index,fore) in sorted(winners.values(),key=lambda row:row[0][1]):
            context=(index,fore);wanted=cut;seed,ref,want=scenarios[index];before=counts['nested_IRQ'];z=N.fork(seed);out=I.run(z,('lagNMI',fore))
            assert counts['nested_IRQ']==before+1 and out['regs']==ref['regs'] and I.state(z)==want
    finally:N.NesMPU=actual
    out=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,ROM_memory_SHA256=q['expected_memory_only_ROM_SHA256'],counts=dict(counts),minimum_nested_IRQ_SP=minimum,scope='Focused worst foreground stack for both actors/mushroom+flower: all I0 native lag-handler PC/A-bank/C-bank pairs at deepest reached SP across those4 lag cuts receive genuine nested HUD IRQ. Full private/scratch/SMC/maps/AXYP/SP exact, outer state exact except tracked native async07DA. Not all foreground lag cut contexts, transformation ISR or emulator qualification.',bindings={str(f.relative_to(R)):sha(f) for f in [Path(__file__),Path(I.__file__),G.O/'proposal.json']})
    (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':
    try:main()
    except Exception as e:
        O.mkdir(exist_ok=True);(O/'negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
