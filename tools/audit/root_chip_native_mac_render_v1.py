"""Actual Mac pose selection and whole DrawAll after moving genuine records."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, address, Memory
from verify_native_relocation import NesMPU
from root_chip_native_layout_cpu_v1 import verify_layout

ROOT=Path(__file__).resolve().parents[2]


def render(b,pose,face,mode,x,y,flags,frame):
    m=Memory(b);m.page(1,93);m.page(2,94)
    values=dict(SelectedCharacter=15,CurrentBank=221,CurrentBankC=222,
                CrossoverBehaviorVersion=mode,OperMode=1,GameEngineSubroutine=8,
                PlayerFacingDir=face,Player_X_Position=x,Player_Y_Position=y,
                Player_Y_HighPos=1,Player_Rel_XPos=x,Player_Rel_YPos=y,
                Player_SprAttrib=0,FrameCounter=frame,LmPalette=1)
    for n,v in values.items():m[address(b,n)]=v
    for i in range(256):m[0x200+i]=(i*73+29)&255
    c=NesMPU(memory=m)
    def call(entry,xv):
        c.pc=address(b,entry);c.a,c.x,c.y,c.p,c.sp=0x55,xv,0,flags,253
        m[510],m[511]=255,126;m.writes=[];start=c.processorCycles
        for _ in range(200000):
            if c.pc==0x7f00:break
            assert m[c.pc],('Unexpected BRK',entry,hex(c.pc),m.banks)
            c.step()
        else:raise AssertionError(('Graphics timeout',entry,hex(c.pc),m.banks))
        assert c.sp==255
        return (c.a,c.x,c.y,c.p&0xcf,c.sp),c.processorCycles-start,list(m.writes)
    first=call('LmSetPose',pose)
    ptr=m[address(b,'SmPosePtr')]+256*m[address(b,'SmPosePtr')+1]
    assert ptr==address(b,f'Lp{pose}{"L" if face==2 else "R"}')
    second=call('DrawAllMetasprites',0)
    return m,first,second


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
    old,new=load(ROOT/'build/smb-crossover-mmc5-expanded.nes'),load(a.rom)
    layout=verify_layout(a.rom);rows=[]
    for pose,face,mode,pos,flags,frame in itertools.product(range(10),[1,2],[0,1],
            [(8,24),(128,176),(250,240)],[0x20,0xe1],[0,1]):
        m,s,d=render(old,pose,face,mode,*pos,flags,frame)
        n,t,e=render(new,pose,face,mode,*pos,flags,frame)
        tag=pose,face,mode,pos,flags,frame
        assert s[0]==t[0] and d[0]==e[0],('Graphics registers',tag,s[0],t[0],d[0],e[0])
        assert bytes(m[0x200:0x300])==bytes(n[0x200:0x300]),('Final OAM',tag)
        assert [(at,v)for at,v in d[2]if 0x200<=at<0x300]==[(at,v)for at,v in e[2]if 0x200<=at<0x300],('Ordered OAM',tag)
        assert [(at,v)for at,v in d[2]if 0x2000<=at<0x6000]==[(at,v)for at,v in e[2]if 0x2000<=at<0x6000],('Hardware stores',tag)
        assert m.banks==n.banks,tag
        rows.append(dict(pose=pose,face=face,mode=mode,position=pos,P=flags,FrameCounter=frame,
                         SetPose_cycle_delta=t[1]-s[1],DrawAll_cycle_delta=e[1]-d[1]))
    proof=dict(passed=True,accepted=False,native_run=False,candidate_ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),
               actual_whole_draw_cases=len(rows),all20_original_pose_records=True,
               AXYP_SP_physical_banks_full256B_OAM_and_ordered_OAM_hardware_stores_exact=True,
               layout=layout,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               limits='Arranged complete compiled pose/DrawAll callers, both modes and edge positions. No PPU rendering, mapper timing, IRQ/NMI or actual Mac campaign/replay coverage; ordinary scratch pointer addresses legitimately move with the immutable records.')
    (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(rows),DrawAll_cycle_deltas=sorted({r['DrawAll_cycle_delta']for r in rows}))))


if __name__=='__main__':main()
