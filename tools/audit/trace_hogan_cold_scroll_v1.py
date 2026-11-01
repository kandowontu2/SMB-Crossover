"""Record exact executed PPU-register writers through Hogan's cold scene."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
from verify_native_relocation import NesMPU

O=R/'build/hogan-current/scroll-cpu'
original_step=NesMPU.step
original_bus=C.Bus


class TraceBus(original_bus):
    def __init__(self,b):self.reg_writes=[];self.trace_pc=0;super().__init__(b)
    def __setitem__(self,a,v):
        if isinstance(a,int)and a in[0x2000,0x2001,0x2005,0x2006]:
            self.reg_writes.append(dict(address=a,value=v,PC=self.trace_pc,maps=self.rawtags[:],
                                       horizontal=C.get(self,'HorizontalScroll'),vertical=C.get(self,'VerticalScroll')))
        super().__setitem__(a,v)


def step(c):c.memory.trace_pc=c.pc;return original_step(c)


def main():
    assert not O.exists();O.mkdir()
    C.Bus=TraceBus;NesMPU.step=step
    b=C.scoped_load(C.J/'candidate.nes');m=C.fresh(b);C.put(m,CrossoverMenuIndex=28)
    for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
    C.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
    start=C.invoke(m,'CrossoverMenuInput')
    C.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    C.invoke(m,'PauseRoutine',a=0)
    scenes=[]
    for age in range(180):
        before=len(m.reg_writes)
        C.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
        C.invoke(m,'GameLoop');C.consume(m)
        scenes.append(dict(age=age,task=C.get(m,'OperMode_Task'),screen=C.get(m,'ScreenRoutineTask'),engine=C.get(m,'GameEngineSubroutine'),writes=m.reg_writes[before:]))
        if C.get(m,'OperMode_Task')==3 and C.get(m,'GameEngineSubroutine')==8:break
    q=dict(source_CPU=True,native=False,candidate=hashlib.sha256((C.J/'candidate.nes').read_bytes()).hexdigest(),
           first_nonzero_2005=[e for e in m.reg_writes if e['address']==0x2005 and e['value']!=0][:20],scenes=scenes,
           scope='Actual PPU writer PCs and declared peripheral model; no raster timing assertion.')
    (O/'trace.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(source_CPU=True,frames=len(scenes),nonzero_scroll=q['first_nonzero_2005'])))


if __name__=='__main__':main()
