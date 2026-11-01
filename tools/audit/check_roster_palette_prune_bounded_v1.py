"""Replay actual NMI packets through the linked OAM-dependent palette pruner."""
from pathlib import Path
import argparse,json,sys
import check_hogan_current_bounded_v1 as C
from check_tmnt_render_oa import address
R=C.R


def commands(packet):
    i=0
    while packet[i]:
        high,low,n=packet[i:i+3];assert 0<n<64
        yield high*256+low,packet[i+3:i+3+n]
        i+=3+n
    assert i==len(packet)-1


def apply(packet):
    values={0x3f0c:15}
    for a,data in commands(packet):
        for i,v in enumerate(data):
            at=a+i
            if 0x3f00<=at<0x4000:
                at=0x3f00+(at&31)
                if at&0x13==0x10:at-=16
            values[at]=v
    return values


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();q=json.loads((args.joint/'source-stage.json').read_text())
    for p,h in q['bindings'].items():assert C.sha(p)==h,p
    trace=R/'build/ready76-visible/menu-nmi-timing/capture/result.json'
    packets=[e['NMI_packet']for e in json.loads(trace.read_text())['ppu_events']if'NMI_packet'in e]
    assert len(packets)==117
    b=C.scoped_load(args.joint/'candidate.nes');base=C.fresh(b)
    layouts=[(0,160),(1,160),(2,160),(3,160),(2,240),(3,255)]
    cases=removed=0
    for packet in packets:
        for palette,y in layouts:
            m=C.fork(base);C.put(m,VRAM_Buffer1_Offset=len(packet)-1)
            for i,v in enumerate(packet):m[address(b,'VRAM_Buffer1')+i]=v
            for i in range(0,256,4):m[address(b,'Sprite_Data')+i]=240
            m[address(b,'Sprite_Data')]=y;m[address(b,'Sprite_Data')+2]=palette|192
            valid=C.invoke(m,'MenuQueueValidate');assert valid['P']&1,('Every actual packet shape must be accepted',packet)
            C.invoke(m,'MenuPruneUnusedPalette2')
            out=list(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+C.get(m,'VRAM_Buffer1_Offset')+1])
            if palette>=2 and y<240:assert out==packet
            else:
                before,after=apply(packet),apply(out)
                for at in set(before)|set(after):
                    if 0x3f19<=at<=0x3f1f:continue
                    assert before.get(at)==after.get(at),(hex(at),palette,y)
                removed+=len(packet)-len(out)
            assert out[-1]==0;cases+=1
    args.output.mkdir(exist_ok=True)
    result=dict(passed=True,source_CPU=True,native=False,ROM_sha256=C.sha(args.joint/'candidate.nes'),actual_NMI_packets=len(packets),OAM_layouts=layouts,cases=cases,removed_unused_bytes=removed,
                scope='Actual linked validator/pruner on117 observed packets with six visible/hidden OAM palette cases. Preserve every nametable/background/used sprite palette value; visible palettes2/3 retain exact input bytes.',
                bindings={str(p.resolve()):C.sha(p)for p in[Path(__file__),Path(C.__file__),trace,args.joint/'candidate.nes',args.joint/'candidate.dbg',args.joint/'source-stage.json']})
    (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
