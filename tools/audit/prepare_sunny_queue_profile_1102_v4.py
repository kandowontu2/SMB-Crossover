"""Save only the current late NMI's compact native command buffer."""
from pathlib import Path
import prepare_sunny_nmi_profile_1102_v3 as P
from check_tmnt_render_oa import address
O=P.R/'build/sunny-queue-profile-1102-v4'

def main():
    original=P.prepare
    def prepare(output,rom,text,refs,**kw):
        at=address(P.A.bundle(),'VRAM_Buffer1')
        anchor="   q.profile=timing;q.elapsed=s['cpu.cycleCount']-timing.start"
        assert text.count(anchor)==1
        text=text.replace(anchor,anchor+"\n   q.commands={};for i=0,timing.buffer do q.commands[i+1]=emu.read("+str(at)+"+i,emu.memType.nesDebug)end")
        return original(output,rom,text,[*refs,Path(__file__),Path(P.__file__)],**kw)
    P.O=O;P.prepare=prepare;P.main()
if __name__=='__main__':main()
