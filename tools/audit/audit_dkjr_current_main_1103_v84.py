"""Bounded first-writer diagnostic for actual cold/Main idle displacement."""
import inspect
import json
from pathlib import Path
import check_dkjr_current_main_1103_v83 as P


def main():
    text=inspect.getsource(P.main)
    text=text[:text.index('    L=json.loads')]+"    return b,q,seed\n"
    env=dict(P.__dict__);exec(compile(text,__file__,'exec'),env)
    b,q,m=env['main']();N,W=P.N,P.W
    addresses={n:W.address(b,n)for n in ['Player_X_Position','ScreenLeft_X_Pos','Player_Rel_XPos']}
    writes=[];history=[];CPU=N.NesMPU
    def snap():
        return dict(nativeX=N.get(m,'Player_X_Position'),nativePage=N.get(m,'Player_PageLoc'),
            camera=N.get(m,'ScreenLeft_X_Pos'),sourceX=m.ram[2][0x213],sourceY=m.ram[2][0x210],
            source_scratch_X=m.ram[2][0],source_state=m.ram[2][0x6b],ready=m.ram[2][0x8fe])
    class Trace(CPU):
        def step(self):
            before={n:self.memory[at]for n,at in addresses.items()};pc=self.pc;maps=list(self.memory.rawtags)
            out=super().step()
            for n,at in addresses.items():
                if before[n]!=self.memory[at]and len(writes)<32:
                    writes.append(dict(field=n,old=before[n],new=self.memory[at],PC=pc,maps=maps,snapshot=snap()))
            return out
    N.NesMPU=Trace
    try:
        history.append(dict(epoch=-1,**snap()))
        for epoch in range(4):
            N.put(m,FrameCounter=epoch,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0)
            N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)
            history.append(dict(epoch=epoch,**snap()))
    finally:N.NesMPU=CPU
    out=dict(passed=True,qualification_complete=False,ROM_written=False,native_owner_admitted=False,
        retained_negative='native-current-main-v83-negative.json',history=history,first_writers=writes,
        scope='Exact current physically cold-loaded source. First native position writers and source/camera snapshots only; no code/state outcome repair or relaxed acceptance.',
        bindings={p.relative_to(P.R).as_posix():P.A.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),P.O/'native-current-main-v83-negative.json',P.O/'native-owner-proposal-v79.json']})
    (P.O/'native-current-main-v84-diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))


if __name__=='__main__':main()
