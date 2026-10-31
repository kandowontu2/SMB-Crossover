"""Foreign movement and menu ABI plus exact unchanged graphics on05b1."""
from pathlib import Path
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_kick_host_controls_1031_v1 as K
import smb3plus_body_host_controls_1030_v5 as G
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

O=R/'build/smb3plus-peach-gravity-consumer-1031-v1';J=O/'joint'
P=R/'build/smb3plus-menu-host-1031-v4/joint'
M,B=K.M,K.B


def main():
    out=O/'regressions-v1.json';assert not out.exists()
    stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
    old,new=[scoped_load(p/'candidate.nes') for p in [P,J]]
    movement=[]
    for variant,form,held,water,air,flags in itertools.product([0,1,2],range(7),[0,64,128,68],
        [0,1],[0,2],[0x30,0x31,0x71,0xf1]):
        results=[]
        for b in [old,new]:
            q=K.seed(b,variant,form,held,water,air)
            c,tr,path,info=M.T.invoke(q,'M3Movement',a=91,x=3,y=7,p=flags)
            # The extra leaf farcall writes only actual SFC code/stack/map
            # protocol. The existing provenance-aware protocol classifier
            # keeps every application write and all returned registers/maps.
            results.append((M.regs(c),M.T.app(q,tr),q.m.banks[:],c.processorCycles))
        assert results[0][:3]==results[1][:3],('Foreign movement',variant,form,held,water,air,flags,results)
        movement.append(dict(variant=variant,form=form,held=held,water=water,air=air,flags=flags,
            CPU_delta=results[1][3]-results[0][3]))
    graphics=[]
    for variant,form,frame,flags in itertools.product(range(4),range(7),range(81),[0x30,0x31,0x71,0xf1]):
        results=[]
        for b in [old,new]:
            q=G.seed(b,variant,form,frame,1)
            c,tr,path,info=M.T.invoke(q,'M3Graphics',a=91,x=3,y=7,p=flags)
            results.append((M.regs(c),M.T.app(q,tr),q.m.banks[:]))
        assert results[0]==results[1],('Graphics',variant,form,frame,flags)
        graphics.append(dict(variant=variant,form=form,frame=frame,flags=flags))
    d=dict(passed=True,CPU_only=True,native=False,candidate=stage['candidate'],
        foreign_movement_pairs=len(movement),exact_graphics_pairs=len(graphics),movement=movement,
        graphics=graphics,scope=__doc__,
        limits='This checks existing0/1/2 outputs and every graphics ABI. Native screenshots/interrupts and original donor movement are qualified separately.',
        bindings={str(p):B.sha(p) for p in [Path(__file__),Path(K.__file__),Path(G.__file__),
            O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']})
    B.write(out,json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,movement=len(movement),graphics=len(graphics),candidate=stage['candidate'])))


if __name__=='__main__':main()
