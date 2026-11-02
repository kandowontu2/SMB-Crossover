"""Pack exact original Excitebike cells into native8x16 patterns; no ROM writes."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]
O=R/'build/excitebike-pose-1101-v3'
P=R/'build/excite-prince-component-1101-v2'


def raster(cells,patterns,height):
    pixels={}
    for cell in reversed(cells):
        data=patterns[cell['tile']]
        for y in range(height):
          for x in range(8):
            yy=height-1-y if cell['attr']&128 else y
            xx=7-x if cell['attr']&64 else x
            tile,row=divmod(yy,8)
            value=((data[tile*16+row]>>(7-xx))&1)|(((data[tile*16+row+8]>>(7-xx))&1)<<1)
            if value:pixels[cell['x']+x,cell['y']+y]=(cell['attr']&35,value)
    return pixels


def main():
    art=json.loads((P/'source-art.json').read_text())
    raw=(P/'excitebike-body-patterns.bin').read_bytes()
    original={tile:raw[index*16:index*16+16] for tile,index in
              ((int(k),v) for k,v in art['packed_tile_map'].items())}
    pairs=[];poses=[];count=0
    for pose in art['poses']:
        pending=[dict(c) for c in pose['cells']];cells=[]
        while pending:
            top=pending.pop(0)
            lower=next((c for c in pending if c['x']==top['x'] and c['y']==top['y']+8 and c['attr']==top['attr']),None)
            if lower:pending.remove(lower)
            first=original[top['tile']];second=original[lower['tile']] if lower else bytes(16)
            pair=second+first if top['attr']&128 else first+second
            if pair not in pairs:pairs.append(pair)
            cells.append(dict(x=top['x'],y=top['y'],attr=top['attr'],tile=pairs.index(pair)))
        expected=raster(pose['cells'],original,8)
        actual=raster(cells,dict(enumerate(pairs)),16)
        assert expected==actual,('Pixels/order/attributes',pose['source_pose'])
        count+=len(actual)
        poses.append(dict(source_pose=pose['source_pose'],cells=cells,palette=pose['palette']))
    payload=b''.join(pairs)
    assert len(payload)<=3072
    (O/'body-native.chr').write_bytes(payload+bytes(3072-len(payload)))
    (O/'body-native.json').write_text(json.dumps(dict(poses=poses,pair_bytes=32,
        intended_physical_pages=[736,737,738],allocation_granted=False),indent=2)+'\n')
    result=dict(passed=True,source_SHA256=art['donor_sha256'],native_emulator=False,
        poses=len(poses),exact_opaque_pixels=count,pairs=len(pairs),pattern_bytes=len(payload),
        largest_sprite_count=max(len(p['cells']) for p in poses),
        CHR_SHA256=hashlib.sha256((O/'body-native.chr').read_bytes()).hexdigest(),
        source_art_SHA256=hashlib.sha256((P/'source-art.json').read_bytes()).hexdigest(),
        scope='All23 original source poses retain opaque pixels, palette indices, priority and per-pixel overlap ordering. No invented pixels; no hardware/OAM capacity/ROM integration claim.')
    (O/'art-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
