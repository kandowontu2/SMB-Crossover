"""Interrupt each instruction of each facing/pose with the actual linked IRQ."""
from pathlib import Path
import argparse
import hashlib
import json
import check_tmnt_primary_od as renderer
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU

INJECT=None
LAST=None


class InterruptProbe(NesMPU):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.path=[];self.interrupted=False
        global LAST
        LAST=self

    def step(self):
        self.path.append(self.pc)
        if len(self.path)-1==INJECT:
            assert not self.p&self.INTERRUPT, 'Fixture must admit a maskable IRQ'
            state=(self.pc,self.a,self.x,self.y,self.p&0xcf,self.sp)
            stack=bytes(self.memory[0x101+self.sp:0x200])
            super().irq()
            for _ in range(1000):
                if self.pc==state[0] and self.sp==state[-1]:break
                super().step()
            else:raise AssertionError(('actual IRQ did not return',state,hex(self.pc),self.sp))
            assert (self.pc,self.a,self.x,self.y,self.p&0xcf,self.sp)==state
            assert bytes(self.memory[0x101+self.sp:0x200])==stack, 'Live synthetic/caller return bytes changed'
            self.interrupted=True
        return super().step()


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    assert address(new,'IrqScrollSplit')==int.from_bytes(new['raw'][16+128*8192-2:16+128*8192],'little')
    renderer.NesMPU=InterruptProbe
    global INJECT
    cases=0;poses=[];return_windows=0
    for face,suffix in [(1,'R'),(2,'L')]:
        lo,hi=location(old,'TnWeapon'+suffix+'Lo'),location(old,'TnWeapon'+suffix+'Hi')
        for pose in range(31):
            ptr=old['raw'][lo+pose]|old['raw'][hi+pose]<<8
            for rotation in [(0,0),(1,128)]:
                args=(ptr,pose,face,(128,176,0),112,rotation,0x30)
                INJECT=0
                expected=renderer.execute(old,qualified(a.baseline)[('TnDraw','Draw')],*args)
                INJECT=None
                plain=renderer.execute(new,address(new,'TnPrimaryRender'),*args)
                count=len(LAST.path)
                assert plain[0]==expected[0] and plain[2:4]==expected[2:4]
                for instruction in range(count):
                    INJECT=instruction
                    actual=renderer.execute(new,address(new,'TnPrimaryRender'),*args)
                    assert LAST.interrupted
                    assert actual[:4]==expected[:4],(face,pose,rotation,instruction,expected[0],actual[0])
                    # A return target is temporarily on the live stack while
                    # code dispatch pushes its high/low bytes and executes RTS.
                    if 0xa000<=LAST.path[instruction]<0xc000:
                        pos=16+89*8192+LAST.path[instruction]-0xa000
                        if new['raw'][pos] in [0x48,0x60]:return_windows+=1
                    cases+=1
                poses.append(dict(face=face,pose=pose,rotation=rotation,instruction_boundaries=count))
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=cases,facing_pose_ring_cases=len(poses),PHA_or_RTS_boundaries=return_windows,
           scope='Every actual instruction boundary for all62 weapon entries in two OAM ring configurations, interrupted with the actual linked MMC5 IrqScrollSplit handler through its hardware vector. Each interrupt must restore registers/meaningful flags/SP/PC and live stack including partial synthetic return bytes. Completed draw matches the original interrupted Draw in all application RAM outside discarded stack/SMC/safecall scratch, ordered OAM and final banks. This is a CPU interruption test, not a timed PPU/NMI proof.')
    (a.output/'cases.json').write_text(json.dumps(poses,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
