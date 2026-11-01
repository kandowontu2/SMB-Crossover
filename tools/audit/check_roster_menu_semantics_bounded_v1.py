"""Compare actual old/new menu OAM and all displayed palette/name values."""
from pathlib import Path
import argparse,json
import check_hogan_current_bounded_v1 as C
from check_tmnt_render_oa import address
from check_roster_palette_prune_bounded_v1 import apply
COUNTS=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,4,1,2,1,6,2,4,2]


def snapshot(m):
    n=C.get(m,'VRAM_Buffer1_Offset')
    assert n<84
    packet=list(m[address(m.bundle,'VRAM_Buffer1'):address(m.bundle,'VRAM_Buffer1')+n+1])
    oam=bytes(m[address(m.bundle,'Sprite_Data'):address(m.bundle,'Sprite_Data')+256])
    used={oam[i+2]&3 for i in range(0,256,4)if oam[i]<240}
    return oam,used,apply(packet)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();parent=C.R/'build/ready76-visible'
    old,new=[C.scoped_load(p/'candidate.nes')for p in[parent,args.joint]]
    for p in[parent,args.joint]:
        stage=json.loads((p/'source-stage.json').read_text())
        for path,h in stage['bindings'].items():assert C.sha(path)==h,path
    cases=0
    for slot,count in enumerate(COUNTS):
        pair=[C.fresh(b)for b in[old,new]]
        for m in pair:C.put(m,CrossoverMenuIndex=slot);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
        for variant in range(count):
            if variant:
                for m in pair:
                    C.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);C.invoke(m,'CrossoverMenuInput')
            a,z=[snapshot(m)for m in pair]
            assert a[0]==z[0]and a[1]==z[1],('Actual preview OAM changed',slot,variant)
            assert C.get(pair[0],'SelectedCharacter')==C.get(pair[1],'SelectedCharacter')
            for at in set(a[2])|set(z[2]):
                if 0x2346<=at<0x235a:continue # static legend owns these cells
                if 0x3f19<=at<=0x3f1f and 2 not in z[1]and 3 not in z[1]:continue
                assert a[2].get(at)==z[2].get(at),('Displayed value changed',slot,variant,hex(at),a[2].get(at),z[2].get(at))
            cases+=1
    assert cases==86
    args.output.mkdir(exist_ok=True)
    result=dict(passed=True,source_CPU=True,native=False,ROM_sha256=C.sha(args.joint/'candidate.nes'),identities=cases,
                scope='Execute the actual cold menu/Select path for86 identities on both ROMs. All256 OAM bytes, selected identity, displayed sprite palettes and other VRAM values match, except the already-static legend and unused palettes2/3.',
                bindings={str(p.resolve()):C.sha(p)for p in[Path(__file__),Path(C.__file__),parent/'candidate.nes',parent/'candidate.dbg',args.joint/'candidate.nes',args.joint/'candidate.dbg',args.joint/'source-stage.json']})
    (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
