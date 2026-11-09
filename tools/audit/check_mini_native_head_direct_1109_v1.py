"""Check Mini's direct authenticated head vector at the actual native ingress."""

import argparse
from collections import defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path
import subprocess

from check_mini_native_side_single_map_1109_v1 import BASE, PIN, N, R, locations, offset, sha
from prepare_mini_mario_native_power_1103_v56 import address, bundle
from prepare_mini_side_alias_1108 import compare_memory
from profile_mini_busy_1108_v1 import fixture


SOURCE=R/'tools/reference/mini_native_head_direct_1109_v1.s'
SITE=offset(89,0xbfb0)
OLD=bytes.fromhex('08488d6a01a9b08d6c01a9bf8d6d01a99c205a01901568288d6a01a9fe8d6c01a9b68d6d01a902205a0160'
                  '68288d6a01a9f18d6c01a9b68d6d01a9c2205a0160'+'ff'*16)


def assemble(out,old):
    assert locations(old,'4c13f1')==[offset(126,0x9899)] and not locations(old,'2013f1')
    assert old[offset(126,0x988f):offset(126,0x9899)]==bytes.fromhex('ad0260c903d0034cb094')
    assert locations(old,'a9b08d6c01a9bf8d6d01a9d9')==[offset(bank,0xf116) for bank in (119,120,125,127)]
    assert old[offset(84,0xb43e):offset(84,0xb441)]==old[offset(84,0xb420):offset(84,0xb423)]
    assert len(OLD)==80 and old[SITE:SITE+80]==OLD
    obj,cfg,binary=(out/f'head.{ext}' for ext in ('o','cfg','bin'))
    cfg.write_text('MEMORY { HEAD:start=$bfb0,size=80,file=%O; } SEGMENTS { HEAD:load=HEAD,type=ro; }\n')
    cc=R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
    obj.unlink()
    new=binary.read_bytes()
    assert len(new)==len(OLD)
    return old[:SITE]+new+old[SITE+80:],dict(bank=89,pc=0xbfb0,file_offset=SITE,old_hex=OLD.hex(),new_hex=new.hex())


def bind(raw):
    b=bundle(raw)
    b['segs']['head_fixed']=dict(start=str(0x8000),ooffs=str(offset(126,0x8000)))
    b['syms']['HeadIngress']=dict(val=str(0x988f),seg='head_fixed')
    return b


def setup(m,owner,engine,x,y,tile,pending,ready):
    N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,Player_X_Position=x,Player_PageLoc=5,
          Player_Y_Position=y,Player_Y_HighPos=1,Player_Y_Speed=0xff,PlayerSize=1)
    N.invoke(m,'BlockBufferColli_Head',y=14)
    cell=m[9]+256*m[10]+m[5]
    m[cell]=tile
    if owner==41:
        s=m.ram[2]
        assert s[0x300]==2
        if not ready:
            s[0x300]=1
        s[0x25c:0x264]=bytes((int(pending),x+8&255,0,y+18,1,tile,cell&255,cell>>8))


def compare(old,new):
    bundles=[bind(raw) for raw in (old,new)]
    seeds=[fixture(b,0,False,False) for b in bundles]
    foreign=[N.fresh(b) for b in bundles]
    cases=[]
    for engine,x,y,pending,ready in product((4,8),(60,249),(32,135),(False,True),(False,True)):
        for tile in (0,0x12,0x26,0x54,0xc0,0xc1,0xc2,0xc3):
            cases.append((41,engine,x,y,tile,pending,ready))
    cases.extend((owner,8,x,135,tile,False,False) for owner,x,tile in product(
        (0,1,2,3,4,6,9,10,11,13,15,19,25,26,28,38,42),(60,249),(0,0xc1,0xc2)))
    stats=defaultdict(list)
    for case in cases:
        owner,engine,x,y,tile,pending,ready=case
        pair=[N.fork(m) for m in (seeds if owner==41 else foreign)]
        returns=[]
        maps=[]
        for m in pair:
            setup(m,*case)
            n=len(m.writes)
            returns.append(N.invoke(m,'HeadIngress',a=0xe7,x=1,y=14,p=0x21))
            maps.append(sum(at==0x5115 for at,_ in m.writes[n:]))
        assert all(returns[0][k]==returns[1][k] for k in ('A','X','Y','P')),(case,returns)
        compare_memory(*pair)
        assert pair[0][0x170:0x17b]==pair[1][0x170:0x17b]
        if owner==41:
            assert maps[0]>maps[1],(case,maps)
            if engine==8 and ready and pending:
                assert pair[1].ram[2][0x25c]==0 and returns[1]['A']==tile,(case,returns)
        stats[(owner,engine,pending,ready)].append((returns[0]['CPU']-returns[1]['CPU'],maps[0]-maps[1]))
    return [dict(owner=k[0],engine=k[1],pending=k[2],ready=k[3],cases=len(v),
                 cycles_saved=[min(c for c,_ in v),max(c for c,_ in v)],
                 A_mapper_stores_removed=[min(m for _,m in v),max(m for _,m in v)])
            for k,v in sorted(stats.items())]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    assert out.is_dir()
    raw=BASE.read_bytes()
    assert sha(BASE)==PIN
    image,patch=assemble(out,raw)
    cases=compare(raw,image)
    proof=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
               expected_memory_only_SHA256=hashlib.sha256(image).hexdigest(),patches=[patch],cases=cases,
               funding='Source pool BASS_HEAD_GATE covers bank89 BF70..C000. Existing BFB0..BFF0 dispatch plus its 16-byte terminal fill.',
               scope='Authentic fixed 988F ingress. Exact vector 10, live and cold ABI, pending metatile consumed once, foreign effects retained. Actual asynchronous cuts separate.')
    (out/'head-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ('passed','expected_memory_only_SHA256','cases')}))


if __name__=='__main__':
    main()
