"""Lossless source8x8->hardware8x16 projection; allocates no host CHR page."""
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'build/arthur-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    source=json.loads((O/'art-source.json').read_text());original=(O/'arthur-original-sprites.chr').read_bytes()
    used=sorted(t['tile']for t in source['tiles']);mapping={tile:i*2 for i,tile in enumerate(used)}
    adapted=bytearray(4096)
    for tile,new in mapping.items():adapted[new*16:new*16+16]=original[tile*16:tile*16+16]
    def picture(parts,data,height):
        im=Image.new('RGBA',(160,160))
        for p in reversed(parts):
            tile,a,x,y=p['tile'],p['attribute'],p['x'],p['y']
            if tile==255:continue
            for yy in range(height):
                sy=height-1-yy if a&128 else yy
                for xx in range(8):
                    sx=7-xx if a&64 else xx;at=(tile+(sy//8))*16+sy%8
                    v=(data[at]>>(7-sx)&1)|((data[at+8]>>(7-sx)&1)<<1)
                    if v:im.putpixel((64+x+xx,65+y+yy),((a&3)*4+v,0,0,255))
        return im.tobytes()
    records=[]
    for r in source['records']:
        for key,vector in r['attribute_rows'].items():
            native=[];projected=[]
            for i,p in enumerate(r['parts']):
                if p['tile']==255:continue
                attr=p['attribute']|vector['values'][i]
                native.append(dict(tile=p['tile'],attribute=attr,x=p['x'],y=p['y']))
                projected.append(dict(tile=mapping[p['tile']],attribute=attr,x=p['x'],y=p['y']-(8 if attr&128 else 0)))
            before=picture(native,original,8);after=picture(projected,adapted,16)
            assert before==after,(r['pose'],key,'palette-index/OAM-priority/anchor mismatch')
            records.append(dict(pose=r['pose'],native_attribute_row=int(key),parts=projected,
                exact_palette_index_plane_sha256=hashlib.sha256(before).hexdigest()))
    (O/'arthur-adapted-8x16.chr').write_bytes(adapted)
    result=dict(status='PASS_LOSSLESS_8X16_SOURCE_PROJECTION_NO_HOST_ALLOCATION',
       atlas=dict(path=str((O/'arthur-adapted-8x16.chr').resolve()),sha256=sha(O/'arthur-adapted-8x16.chr'),
          bytes=4096,used_8x16_pairs=len(used),source_8x8_unique_tiles=len(used),used_bytes=len(used)*32,unused_bytes=4096-len(used)*32),
       mapping=mapping,projection='Original tile in upper8rows, transparent lower8rows. Native vertical-flip parts move OAM y-8 so hardware16row flip preserves native8row flip and original anchor.',
       exact_full_coordinate_palette_index_and_priority_cases=len(records),records=records,
       bindings={str(p.resolve()):sha(p)for p in [Path(__file__),O/'art-source.json',O/'arthur-original-sprites.chr']},
       limits='Four logical1KiB pages only; no physical host CHR lease, palette quantization/admission or OAM scanline-budget claim.')
    p=O/'art-8x16-proof.json';p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(exact_projection_cases=len(records),used_bytes=len(used)*32,atlas_bytes=4096,proof_sha256=sha(p))))
if __name__=='__main__':main()
