"""Compare the complete current Rogue scheduler before and after Giant PRG funding."""

import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter

import check_mega_giant_compound_1110 as C
from check_mega_giant_resident_1110 import DRIVER
import rogue_dawn_scheduler_controls_v3 as V


def current_images(proof):
    for p,expected in proof['bindings'].items():
        assert C.sha(Path(p))==expected,p
    old=C.HOST.read_bytes()
    assert proof['parent_SHA256']==C.PIN==hashlib.sha256(old).hexdigest()
    new=bytearray(old)
    for row in proof['patches']:
        at=row['file_offset']
        pre,post=(bytes.fromhex(row[key]) for key in ('old_hex','new_hex'))
        assert len(pre)==len(post) and new[at:at+len(pre)]==pre
        new[at:at+len(pre)]=post
    assert hashlib.sha256(new).hexdigest()==proof['expected_memory_only_SHA256']
    return C.bundle(old),C.bundle(new)


def campaign(images,labels):
    rows=[]
    theme_requests=(16,1,8,64,16,128)
    for area,theme in enumerate(theme_requests):
        pair=[V.prepared(b,area) for b in images]
        totals=Counter()
        min_sp=[255,255]
        for tick in range(48):
            completed=tick%3
            nmi_disable=0 if tick%2==0 else 255
            for m in pair:
                m[0x5fb6]=completed*2
                V.put(m,NmiDisable=nmi_disable,GamePauseStatus=int(32<=tick<36))
                if tick==1:
                    m[0x5c25]=theme
                if tick%6==4:
                    m[0x5c21]|=1<<((tick//6)%8)
            old,new=[V.nmi(m) for m in pair]
            assert old['requests']==new['requests'] and old['writes']==new['writes'],(area,tick)
            x,z=pair
            assert x[:0x100]==z[:0x100] and x[0x200:0x8000]==z[0x200:0x8000] and x.banks==z.banks
            direct=sum(pc==DRIVER and bank==97 for pc,bank,_ in old['trace'])
            virtual=sum(pc==labels['GiantRogueMux'] and bank==97 for pc,bank,_ in new['trace'])
            assert direct==sum(pc==DRIVER and bank==97 for pc,bank,_ in new['trace'])
            assert 0<=virtual<=direct
            cost=new['CPU']-old['CPU']
            assert cost>=0,(area,tick,cost)
            assert cost==0 if direct==0 else cost<=2*direct+60*virtual,(area,tick,cost,direct,virtual)
            totals.update(ticks=1,actual_source_requests=len(old['requests']),reader_calls=direct,
                          virtual_calls=virtual,old_CPU=old['CPU'],new_CPU=new['CPU'])
            totals['old_max']=max(totals['old_max'],old['CPU'])
            totals['new_max']=max(totals['new_max'],new['CPU'])
            totals['largest_delta']=max(totals['largest_delta'],cost)
            min_sp=[min(a,z['minimum_SP']) for a,z in zip(min_sp,(old,new),strict=True)]
        assert totals['reader_calls']>0,(area,totals)
        rows.append(dict(area=area,theme_request=theme,minimum_SP=min_sp,**totals))
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    proof_path=args.output/'proof-v2.json'
    proof=json.loads(proof_path.read_text())
    assert proof['passed'] and proof['resident_PRG']
    rows=campaign(current_images(proof),proof['storage']['symbols'])
    report=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=C.PIN,
                memory_SHA256=proof['expected_memory_only_SHA256'],areas=rows,
                full_NMIs=sum(q['ticks'] for q in rows),largest_delta=max(q['largest_delta'] for q in rows),
                scope='Exact parent and memory-only patch, the six authored scene projections, genuine NMI and retained ordered APU/mapped writes. CPU model omits hardware DMA stalls and full-video cadence.',
                bindings={str(p):C.sha(p) for p in (proof_path,Path(__file__),Path(V.__file__))})
    (args.output/'rogue-nmi-v2.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':
    main()
