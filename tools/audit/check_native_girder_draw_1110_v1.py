"""Source-link native four-part girder and qualify ordered renderer writes."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_native_brick_coin_draw_1110_v1 as V
from check_mini_funded_actor_1108_v3 import install


R, P, N = V.R, V.P, V.N
ROM=R/'build/mini-lane-audio-native-1110/candidate.nes'
PIN='a226894c4f6b97f1b9df248cf1465f1a36037fcc256d8ec703e05d0f077d6746'
SOURCE=R/'tools/reference/native_girder_draw_1110_v1.s'
WITNESS=R/'build/mini-platform-draw-witness-1110/capture/instruction-sample.json'
FUNDING=0xb98e
FUNDING_END=0xba37
DISPATCH=0xbe92
DIRECT_TYPED=0xbead
INNER=0xb8d0
INNER_END=0xb8e4
GOOMBA=(0xaf2f,0xaf38,0xaf41,0xaf4a)
GIRDERS=(0xb329,0xb33a)


def compose(raw,out):
    table=bytes(5 + max(0,i-18) + max(0,i-18)//4 for i in range(169))
    V.preimage(raw,FUNDING,table)
    data=(bytes([16,90,2,0,0,90,2,0,8,90,2,0,16,90,2,0,24]),
          bytes([16,90,2,0,16,90,2,0,24,90,2,0,0,90,2,0,8]))
    for i,(pc,descriptor) in enumerate(zip(GIRDERS,data)):
        V.preimage(raw,pc,descriptor)
        for base in (0xb3de,0xb5d6):
            index=0x54+i
            V.preimage(raw,base+index,bytes([pc&255]))
            V.preimage(raw,base+0xfc+index,bytes([pc>>8]))
    old_spill=raw[V.offset(FUNDING_END):V.offset(FUNDING_END)+87]
    assert old_spill==bytes((5+max(0,i-18)*55//24)&255 for i in range(87))
    bank=raw[V.offset(0xa000):V.offset(0xa000)+8192]
    assert bank.count(bytes.fromhex('b98eb9'))==1
    V.preimage(raw,0xa0eb,bytes.fromhex('4cadbe'))
    V.preimage(raw,0xbece,bytes.fromhex('4cbaa5'))
    with tempfile.TemporaryDirectory(prefix='girder-link-',dir=out) as folder:
        tmp=Path(folder)
        cfg,obj,binary,labels=(tmp/f'girder.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { W:start=$b98e,size=$a9,file=%O,fill=yes,fillval=$ea; '
                       'D:start=$be92,size=$1b,file=%O; I:start=$b8d0,size=$14,file=%O; } '
                       'SEGMENTS { WORKER:load=W,type=ro; DISPATCH:load=D,type=ro; DEATH:load=I,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',labels],check=True)
        code=binary.read_bytes()
        symbols={cols[2][1:]:int(cols[1],16) for line in labels.read_text().splitlines()
                 if len(cols:=line.split())==3}
    assert symbols['InnerAtAge']==FUNDING and symbols['WorkerEnd']<=FUNDING_END
    cap=FUNDING_END-FUNDING
    end_dispatch=cap+DIRECT_TYPED-DISPATCH
    assert len(code)==end_dispatch+INNER_END-INNER
    other=symbols['GoombaLowDispatch']
    changes=[]
    for pc,old,new in (
        (FUNDING,table,code[:cap]),
        (DISPATCH,bytes.fromhex('a50429fdc9add0344ce0bac92ff00cc938f008c941f004c94ad021'),code[cap:end_dispatch]),
        (0xbae8,bytes.fromhex('4c9dbe'),bytes((0x4c,other&255,other>>8))),
        (INNER,bytes.fromhex('ac0960e004b016b98eb98d0f60a9008d10609009'),code[end_dispatch:]),
    ):
        at=V.preimage(raw,pc,old)
        assert len(old)==len(new)
        changes.append(dict(physical_PRG=4,start=pc,end_exclusive=pc+len(old),
                            file_offset=at,old_hex=old.hex(),new_hex=new.hex()))
    return install(raw,changes),changes,symbols,data


def renderer(seeds,data):
    histogram=Counter()

    def compare(role,entry,ptr,pos,cursor,rot,mode,attr,p):
        a,b=[V.draw(seed,entry,ptr,pos,cursor,rot,mode,attr,p) for seed in seeds]
        assert a[0]==b[0],(role,hex(entry),hex(ptr),pos,cursor,rot,mode,attr,p,a[0][:2],b[0][:2],a[0][3],b[0][3])
        saved=a[1]-b[1]
        histogram[role,saved]+=1
        return a[1],b[1],saved

    witness=json.loads(WITNESS.read_text())['renderer_entries']
    assert len(witness)==3 and all(w['pointer']==GIRDERS[0] and bytes(w['descriptor'])==data[0] for w in witness)
    observations=[]
    for w in witness:
        pos=tuple(w[n] for n in ('x_low','x_high','y_low','y_high'))
        old,new,saved=compare('witness',DISPATCH,w['pointer'],pos,w['oam_cursor'],w['rotation'],
                              w['rotation_active'],w['attribute'],0x21)
        observations.append(dict(pos=pos,old=old,new=new,saved=saved))
    assert all(x['saved']>0 for x in observations)
    positions=((0,0,0,1),(104,0,168,1),(231,0,32,1),(232,0,32,1),(248,0,128,1),
               (232,255,58,1),(255,255,0,1),(24,1,191,1),(248,127,244,1),(255,128,12,1),
               (128,0,30,0),(0,0,255,2),(24,255,128,255))
    ptrs=(*GIRDERS,0xb34b,0xb364,*GOOMBA,0xaf30,V.BRICK,V.COIN,0xada9,0xa976)
    for ptr,pos,cursor,(rot,mode),attr,p in product(
        ptrs,positions,(0,12,232,239,240,252,255),((0,0),(0,1),(204,1),(251,0x81)),
        (0,3,0x8b),(0x21,0xe5),
    ):
        compare('matrix',DISPATCH,ptr,pos,cursor,rot,mode,attr,p)
    for ptr,pos,cursor,rot in product(GOOMBA,positions,(0,239,252),(0,204)):
        compare('typed_direct',DIRECT_TYPED,ptr,pos,cursor,rot,1,0x8b,0x21)
    return dict(cases=sum(histogram.values()),witness=observations,
                witness_saved=sum(o['saved'] for o in observations),
                timing_histogram=[[role,delta,cases] for (role,delta),cases in sorted(histogram.items())])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=ROM.read_bytes()
    assert P.sha(raw)==PIN
    image,patches,symbols,data=compose(raw,args.output)
    seeds=[N.fresh(P.bundle(im)) for im in (raw,image)]
    for m in seeds:
        m.raw_page(1,132)
        N.put(m,CurrentBank=132)
    render=renderer(seeds,data)
    print('Girder exact witnesses:',render['witness'],flush=True)
    death=V.death(seeds)
    result=dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),
                patches=patches,symbols=symbols,renderer=render,death=death,
                worker_bytes=symbols['WorkerEnd']-FUNDING,
                bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),SOURCE,ROM,WITNESS)},
                scope='Exact renderer pointer witness only. Actor slot and ID from the observer ambient '
                      'ObjectOffset are not evidence. All indexed death ages, ordered OAM and native fallback.')
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','patches','renderer')}),flush=True)


if __name__=='__main__':
    main()
