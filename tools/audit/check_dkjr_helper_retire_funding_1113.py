"""Owned compaction proposals only; no ROM/RAM lease or output artifacts."""
from hashlib import sha256
from itertools import product
import json

import check_dkjr_head_bridge_1113 as H
import check_dkjr_powerups_current_1113 as B
import compose_dkjr_head_bridge_1113 as T

N,W,L=H.N,H.W,H.L


def predicate(seed):
    source,*_=T.old_source()
    start=source.index('D_ebe3:');end=source.index('D_f1af:',start)
    old=T.assemble('.segment "PREDICATE"\n'+source[start:end],dict(PREDICATE=(0xaeef,62)))
    assert old['used']['PREDICATE']==62
    raw=seed.bundle['raw'];body=T.payload(raw)
    assert body[0xeef:0xeef+62]==old['images']['PREDICATE']
    new=T.assemble((B.R/'tools/reference/dkjr_helper_retire_funding_1113.s').read_text(),dict(PREDICATE=(0xaeef,62)))
    assert new['used']['PREDICATE']==42
    models=[]
    for image in(old['images']['PREDICATE'],new['images']['PREDICATE']):
        m=L.clone(seed);m.ram[3][0xeef:0xeef+len(image)]=image
        class ReadTrace(type(m)):
            def __getitem__(self,at):
                if isinstance(at,int)and 0xc03e<=at<0xc046:self.field_reads.append(at)
                return super().__getitem__(at)
        m.__class__=ReadTrace;m.field_reads=[];models.append(m)
    count=0
    def pair(rectangles,flags,x=71,y=203):
        results=[]
        for m in models:
            W.clear_logs(m)
            m.ram[2][0x3e:0x46]=rectangles;m.field_reads=[]
            c=H.call(m,0xaeef,a=83,x=x,y=y,p=flags)
            results.append(((c.a,c.x,c.y,c.p,c.sp),tuple(m.field_reads),bytes(m.ram[2])))
        assert results[0]==results[1],(list(rectangles),flags,x,y,results[0][:2],results[1][:2])
    # Exhaust both coordinate starts, with points, inclusive edges, long and
    # byte-wrapped widths. Exercise each axis while the other really overlaps.
    for axis,a,b in product(range(2),range(256),range(256)):
        r=[20,20,40,40,25,25,35,35]
        r[axis]=a;r[2+axis]=(a+(0,1,15,255)[(a+b)&3])&255
        r[4+axis]=b;r[6+axis]=(b+(0,1,16,255)[(a^b)&3])&255
        pair(bytes(r),(a+b)&255,x=a,y=b);count+=1
    edges=(0,1,15,16,127,128,254,255)
    for flags,choice in product(range(256),range(16)):
        a,b=edges[choice&7],edges[(choice*3+1)&7]
        r=bytes((a,b,(a+15)&255,(b+16)&255,b,a,(b+31)&255,(a+32)&255))
        pair(r,flags,x=flags,y=255-flags);count+=1
    return dict(paired_cases=count,old_bytes=62,new_bytes=42,freed_bytes=20,
        original_field_read_order=True,AXYP_SP_and_all_source_RAM_equal=True,
        fixture_only=True,allocated=False)


def main():
    raw=B.C.ROM.read_bytes();assert sha256(raw).hexdigest()==B.STEVE_SUCCESSOR
    _,seed=H.cold(raw,B.COOKIE)
    print('DKJR_RETIRE_PREDICATE_FUNDING '+json.dumps(predicate(seed),separators=(',',':')),flush=True)


if __name__=='__main__':main()
