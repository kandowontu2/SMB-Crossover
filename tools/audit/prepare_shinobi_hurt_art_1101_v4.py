"""Recover original injury/death OAM and exact native 8x16 append-only art."""
import hashlib,json
from pathlib import Path
import check_shinobi_component_1101_v2 as C
import prepare_shinobi_owning_graft_1101_v1 as P

O=P.R/'build/shinobi-hurt-art-1101-v4'


def main():
    assert P.sha(C.S.ROM)==C.S.EXPECTED
    e=C.Engine(P.V,False)
    original=(P.V/'source-body.chr').read_bytes()
    packed=(P.O/'native-art.chr').read_bytes()
    assert len(packed)==3072
    pairs=[packed[i:i+32] for i in range(0,len(packed),32)]
    packets=[]
    def raster(rows,art,height):
        pixels={}
        for x,y,t,attr in rows:
            for dy in range(height):
                sy=height-1-dy if attr&128 else dy
                tile=t*16+(sy//8)*16
                for dx in range(8):
                    sx=7-dx if attr&64 else dx
                    v=((art[tile+sy%8]>>(7-sx))&1)|(((art[tile+sy%8+8]>>(7-sx))&1)<<1)
                    if v and 0<=x+dx<256 and 0<=y+1+dy<240:
                        pixels.setdefault((x+dx,y+1+dy),(attr&3,v))
        return pixels
    for pose in [6,7]:
        for face in [0,4]:
            e.fixture();e.put(0x300,pose);e.put(0x363,face);e.run(0x83ab,x=0)
            for frame in range(e.get(0x321)):
                e.put(0x30b,frame);e.put(0x541,4);e.run(0x83fc,x=0)
                oam=e.state()[0x204:e.get(0x541)+0x200]
                sprites=[oam[i:i+4] for i in range(0,len(oam),4)]
                used=set();rows=[]
                for i,s in enumerate(sprites):
                    if i in used:continue
                    used.add(i);low=None
                    for j,z in enumerate(sprites):
                        if j not in used and s[3]==z[3] and z[0]==s[0]+8 and s[2]==z[2]:
                            low=z;used.add(j);break
                    tiles=[original[s[1]*16:s[1]*16+16],original[low[1]*16:low[1]*16+16] if low else bytes(16)]
                    if s[2]&128:tiles.reverse()
                    key=b''.join(tiles)
                    if key not in pairs:pairs.append(key)
                    rows.append([s[3],s[0],pairs.index(key)*2,s[2]])
                a=raster([[s[3],s[0],s[1],s[2]] for s in sprites],original,8)
                b=raster(rows,b''.join(pairs),16)
                assert a==b,(pose,face,frame)
                packets.append(dict(pose=pose,frame=frame,facing=face,source_OAM=oam,native_rows=rows,
                                    opaque_pixels=len(a),raster_sha256=hashlib.sha256(repr(sorted(a.items())).encode()).hexdigest()))
    assert len(pairs)==107
    O.mkdir(parents=True,exist_ok=True)
    (O/'additional-art.chr').write_bytes(b''.join(pairs[96:]))
    (O/'packets.json').write_text(json.dumps(packets,indent=2)+'\n')
    result=dict(passed=True,donor_sha256=C.S.EXPECTED,original_art_sha256=hashlib.sha256(original).hexdigest(),
                existing_native_art_sha256=hashlib.sha256(packed).hexdigest(),packets=len(packets),
                additional_pairs=11,additional_bytes=352,exact_raster_and_priority=True,
                installed=False,scope='Original CPU animator/emitter output; exact 8x16 raster conversion, both facings. No native hardware publication.',
                next='Allocate fourth sprite window/tail and extend metadata; wire injury/death and native damage.')
    (O/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
