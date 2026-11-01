"""Verify original pose raster mirroring before sharing facing descriptors."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/shinobi-component-1101-v2'
O=R/'build/shinobi-original-mirrors-1101-v1'
def main():
    cp=V/'source-body.chr';pp=V/'pose-packets.json';art=cp.read_bytes()
    poses=json.loads(pp.read_text())['poses'];images={}
    for pose in poses:
        pixels={};oam=pose['OAM']
        for i in range(0,len(oam),4):
            y,t,a,x=oam[i:i+4]
            for yy in range(8):
                for xx in range(8):
                    sx=7-xx if a&64 else xx;sy=7-yy if a&128 else yy
                    v=((art[t*16+sy]>>(7-sx))&1)|(((art[t*16+sy+8]>>(7-sx))&1)<<1)
                    if v and x+xx<256 and y+1+yy<240:pixels.setdefault((x+xx,y+1+yy),(a&3,v))
        images[pose['pose'],pose['frame'],pose['facing']]=pixels
    pairs=[]
    for (pose,frame,face),pixels in images.items():
        if face:continue
        assert {(255-x,y):v for (x,y),v in pixels.items()}==images[pose,frame,4],(pose,frame)
        pairs.append([pose,frame])
    assert len(pairs)==26
    O.mkdir(exist_ok=True)
    result=dict(passed=True,original_frame_pairs=pairs,all_original_priority_pixels_exact=True,
        descriptor_mirror='x_offset becomes -x_offset-8; attribute XOR40',
        scope='Original raster equivalence only; runtime staging, buffer bounds and cycle cost remain to be verified.',
        bindings={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),cp,pp]})
    (O/'mirrors.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,original_frame_pairs=len(pairs))))
if __name__=='__main__':main()
