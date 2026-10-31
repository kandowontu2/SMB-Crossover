"""Qualify the exact form5 low-table factorization in the emitted cartridge."""
from pathlib import Path
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_body_host_controls_1030_v5 as G
import benj_current_menu_controls_1030_v1 as M
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

O=R/'build/smb3plus-peach-float-host-1031-v4';J=O/'joint'
P=R/'build/smb3plus-kick-host-1031-v1/joint'


def main():
    assert not (O/'graphics-controls-v1.json').exists()
    stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
    old,new=[scoped_load(p/'candidate.nes') for p in [P,J]]
    cases=[];aliases=[]
    for variant,form,frame,flags in itertools.product(range(4),range(7),range(81),[0x30,0x31,0x71,0xf1]):
        results=[];traces=[]
        for b in [old,new]:
            q=G.seed(b,variant,form,frame,1)
            c,tr,path,info=M.T.invoke(q,'M3Graphics',a=91,x=3,y=7,p=flags)
            traces.append(tr)
            results.append((M.regs(c),M.T.app(q,tr),q.m.banks[:],c.processorCycles))
        if form==5:
            # Exactly the two low-pointer stores made by M3SetFrame now
            # reference form3's identical shape. Their final high-pointer
            # stores, every other ordered write and all live outputs stay exact.
            for name in ['R0','R1']:
                at=address(new,name)
                old_w=[w for w in traces[0] if w['address']==at]
                new_w=[w for w in traces[1] if w['address']==at]
                assert len(old_w)==len(new_w)==2,(name,form,frame)
                shift=0 if name=='R0' else 8
                ov=(address(old,'M3Form5ChrLo')>>shift)&255
                nv=(address(new,'M3Form3ChrLo')>>shift)&255
                assert old_w[0]['pc']==new_w[0]['pc']
                assert old_w[0]['bank']==new_w[0]['bank']==90
                assert old_w[0]['value']==ov and new_w[0]['value']==nv
                assert old_w[1]['value']==new_w[1]['value']
                index=next(i for i,w in enumerate(results[1][1]) if w[0]==at)
                assert results[1][1][index]==(at,nv)
                results[1][1][index]=(at,ov)
            aliases.append(dict(variant=variant,form=form,frame=frame,flags=flags,
                low_pointer_old=address(old,'M3Form5ChrLo'),low_pointer_new=address(new,'M3Form3ChrLo')))
        assert results[0][:3]==results[1][:3],('Exact graphics outputs',variant,form,frame,flags,results)
        cases.append(dict(variant=variant,form=form,frame=frame,flags=flags,
            CPU_delta=results[1][3]-results[0][3]))
    # Repeat all existing exact donor-pixel/palette assertions on this hash.
    G.P=P;G.O=O;G.J=J
    G.main()
    body=O/'body-controls-v5.json'
    d=dict(passed=True,CPU_only=True,native=False,candidate=stage['candidate'],
        exact_graphics_pairs=len(cases),cases=cases,qualified_transient_aliases=aliases,
        normalization='Only the first R0/R1 stores in form5 at the identical A90 PCs; actual old/new table addresses asserted. Final high pointers/registers/maps and all other ordered application writes remain exact.',
        source_pixel_palette_receipt=str(body),limits=stage['limits'],
        bindings={str(p):B.sha(p) for p in [Path(__file__),Path(G.__file__),
            O/'source-stage.json',body,P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg']})
    B.write(O/'graphics-controls-v1.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,exact_graphics_pairs=len(cases),source_pixels=2156,source_palettes=28)))


if __name__=='__main__':main()
