"""Bound OJ to two existing query operands and a newly appended PRG segment."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
from check_tmnt_render_oa import load,location
from check_tmnt_audio_fallback_oc import qualified


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    before,after=load(a.baseline),load(a.rom);old,new=before['raw'],after['raw']
    qb,qa=qualified(a.baseline),qualified(a.rom)
    ignored={('_FARCALL_COUNT',)}
    moved={str(k):[v,qa.get(k)]for k,v in qb.items()if k not in ignored and qa.get(k)!=v}
    assert not moved,moved
    counter_delta=qa[('_FARCALL_COUNT',)]-qb[('_FARCALL_COUNT',)]
    assert counter_delta==16,counter_delta
    dbg=a.rom.with_suffix('.dbg')
    debug=dbg.read_text()if dbg.exists()else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    segments=[]
    for line in debug.splitlines():
        if not line.startswith('seg\t'):continue
        q=dict(s.split('=',1)for s in line.split('\t',1)[1].split(',')if '='in s)
        if q.get('name')=='"HOT_COLLISION_GATE"':segments.append(q)
    assert len(segments)==1
    segment=segments[0];start,size=int(segment['ooffs'],0),int(segment['size'],0)
    assert (start-16)//8192==66 and (start+size-17)//8192==66
    allowed=set(range(start,start+size));spans={}
    for name in ['ExpandedCollisionAdder','ExpandedCollisionBox']:
        pos=location(before,name)
        assert location(after,name)==pos and (pos-16)//8192==127
        allowed.update(range(pos,pos+18));spans[name]=dict(offset=pos,bytes=18)
    changes={i for i,(x,y)in enumerate(zip(old,new))if x!=y}
    assert len(old)==len(new) and changes<=allowed
    assert old[:16]==new[:16] and old[16+1048576:]==new[16+1048576:]
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old).hexdigest(),
        changed_bytes=len(changes),allowed_query_spans=spans,new_segment=dict(offset=start,bytes=size,bank=66),
        all_preexisting_qualified_symbols_exact=True,farcall_counter_delta=counter_delta,header_and_CHR_exact=True,
        scope='Every changed ROM byte is confined to two existing18-byte fixed-bank query calls and the new appended bank66 segment. Full named scope/symbol addresses remain exact except the compile-time farcall count. No existing RAM, CHR, native collision leaf or other PRG byte changes.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
