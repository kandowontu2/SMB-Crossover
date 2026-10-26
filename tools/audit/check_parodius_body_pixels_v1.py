"""Compare exact palette/index pixels after body-only record permutations."""
from pathlib import Path
import argparse
import hashlib
import json

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
signed=lambda x:x if x<128 else x-256


def pixels(chrdata,pool,parts):
    result={}
    windows=[pool['body_chr'],16,17,18,19,20,pool['special_chr'],pool['pickup_chr']]
    for tile,attr,y,x in parts:
        for dy in range(16):
            sy=15-dy if attr&128 else dy
            at=(tile&1)*4096+(tile&254)*16+(sy//8)*16+sy%8
            get=lambda k:chrdata[windows[k//1024]*1024+k%1024]
            lo,hi=get(at),get(at+8)
            for dx in range(8):
                sx=dx if attr&64 else 7-dx
                value=((lo>>sx)&1)|(((hi>>sx)&1)<<1)
                if value:
                    point=(signed(x)+dx,signed(y)+dy)
                    assert point not in result,('overlapping opaque body planes',pool['index'],point)
                    result[point]=(attr&3,value)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--old-manifest',type=Path,required=True)
    p.add_argument('--new-manifest',type=Path,required=True)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); old=json.loads(a.old_manifest.read_text()); new=json.loads(a.new_manifest.read_text())
    chrdata=a.rom.read_bytes()[1048592:];count=0;crops=0
    for left,right in zip(old['pools'],new['pools'],strict=True):
        for frame in left['body_frames']:
            before=pixels(chrdata,left,left['records'][str(frame)])
            after=pixels(chrdata,right,right['records'][str(frame)])
            assert before==after;count+=1
            for ox,oy in [(-16,120),(0,0),(4,24),(96,120),(247,232),(255,255),(256,120),(96,-8)]:
                for flip in (False,True):
                    def transform(data):
                        return {((ox-px if flip else ox+px),oy+py):value
                                for (px,py),value in data.items()
                                if 0<=(ox-px if flip else ox+px)<256 and 0<=oy+py<240}
                    assert transform(before)==transform(after);crops+=1
    assert count==131
    proof=dict(passed=True,native_run=False,production_changes=False,body_poses=count,
               screen_edge_and_facing_cases=crops,candidate_ROM_sha256=sha(a.rom),
               old_manifest_sha256=sha(a.old_manifest),new_manifest_sha256=sha(a.new_manifest),
               tool_sha256=sha(Path(__file__)),exact_pixel_palette_and_pattern_index=True,
               all_body_opaque_planes_disjoint=True,
               scope='Direct actual CHR decoding of old/new records, unlimited sprite composition '
                     'and clipping. No NES eight-sprite visibility or cadence claim.')
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
