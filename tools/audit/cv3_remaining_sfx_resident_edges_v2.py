"""Immutable resident-edge suite plus strict ordered source image/Dirty/high writes."""
import sys
from pathlib import Path
import cv3_remaining_sfx_resident_edges_v1 as suite
from check_tmnt_render_oa import address

original_compare=suite.compare

def ordered_compare(qs,cs):
 delta=original_compare(qs,cs);b=qs[0].b
 images=set(range(address(b,'GuestNativeApu'),address(b,'GuestNativeApu')+16))|set(range(address(b,'GuestNativeDirty'),address(b,'GuestNativeDirty')+16))|set(range(address(b,'Cv3NoiseApu'),address(b,'Cv3NoiseApu')+4))|{address(b,'Cv3FxSourceHigh')}
 writes=[[(at,v)for at,v in q.m.writes if at in images]for q in qs];assert writes[0]==writes[1],writes
 return delta

if __name__=='__main__':
 suite.compare=ordered_compare;suite.main()
 import hashlib,json
 out=Path(sys.argv[sys.argv.index('--output')+1]);p=out/'proof.json';j=json.loads(p.read_text());j['ordered_source_image_dirty_high_writes_exact']=True;j['ordering_wrapper_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p.write_text(json.dumps(j,indent=2)+'\n')
