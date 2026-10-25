"""Repack authenticated body pixels without the native tile-boundary padding.

The native palette split can turn one original sprite into three overlapping
sprites. Regrid each exact palette plane to reduce full16-row hardware overlap.
This preserves every visible pixel and its palette/index, not just silhouette.
"""
from pathlib import Path
import hashlib, json
from roll_sprite_packing import pack_layers

ROOT=Path(__file__).resolve().parents[2]


def layers_from_parts(parts, pixels):
    composed={}
    signed=lambda n:n if n<128 else n-256
    # Earlier NES sprites have pixel priority over later ones.
    for tile,attr,dy,dx in reversed(parts):
        px=pixels(tile)
        for y in range(16):
            for x in range(8):
                v=px[15-y if attr&128 else y][7-x if attr&64 else x]
                if v:composed[signed(dx)+x,signed(dy)+y]=(attr&3,v)
    layers={}
    for point,(palette,value)in composed.items():layers.setdefault(palette,{})[point]=value
    return layers


def compose_packed(parts):
    result={}
    for px,palette,top,left in parts:
        for y in range(16):
            for x in range(8):
                if px[y][x]:
                    assert(left+x,top+y)not in result,'Repacked planes may not overlap opaque pixels'
                    result[left+x,top+y]=palette,px[y][x]
    return result


def peak(parts):
    return max((sum(top<=y<top+16 for _,_,top,_ in parts)for y in range(-64,96)),default=0)


def trial():
    manifest=json.loads((ROOT/'reference/parodius-nes/art/packed/manifest.json').read_text())
    raw=(ROOT/'chr/characters/parodius.chr').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==manifest['CHR_sha256']
    output=ROOT/'build/verification/parodius-render-nq'
    output.mkdir(parents=True,exist_ok=False)
    cases=[]
    for pool in manifest['pools']:
        def pixels(tile):
            at=(pool['body_chr']-manifest['first_chr'])*1024
            at+=(2048 if tile&1 else 0)+(tile&62)*16
            b=raw[at:at+32];assert len(b)==32
            return [[((b[y//8*16+y%8]>>(7-x))&1)|(((b[y//8*16+y%8+8]>>(7-x))&1)<<1)for x in range(8)]for y in range(16)]
        for frame in pool['body_frames']:
            original=pool['records'][str(frame)]
            layers=layers_from_parts(original,pixels)
            packed=pack_layers(layers)
            expected={point:(palette,v)for palette,plane in layers.items()for point,v in plane.items()}
            assert compose_packed(packed)==expected
            old=[(None,attr&3,dy if dy<128 else dy-256,dx if dx<128 else dx-256)for _,attr,dy,dx in original]
            cases.append(dict(pool=pool['index'],variant=pool['variant'],phase=pool['phase'],frame=frame,
                pixels=len(expected),before_parts=len(original),before_peak=peak(old),
                after_parts=len(packed),after_peak=peak(packed)))
    report=dict(passed=True,CHR_sha256=manifest['CHR_sha256'],cases=cases,
        scope='Read-only packing trial over exact installed body pixels; not installed, no runtime/weapon visibility claim.')
    (output/'packing-trial.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),max_before=max(c['before_peak']for c in cases),
        max_after=max(c['after_peak']for c in cases),pentarou=[c for c in cases if c['frame']==164])))


if __name__=='__main__':trial()
