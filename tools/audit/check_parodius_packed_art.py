"""Verify every packed native pose's opaque pixels and declared NES colors."""
from pathlib import Path
import argparse
import importlib.util
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('native_art',ROOT/'tools/reference/export_parodius_art.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def compose(parts,read,colors):
    result={}
    for dx,dy,tile,attr in reversed(parts):
        px=read(tile)
        for y in range(16):
            for x in range(8):
                value=px[15-y if attr&128 else y][7-x if attr&64 else x]
                if value:result[(dx+x,dy+y)]=colors(attr&3,value)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build/verification/parodius-render-nq/packed-art-proof.json')
    args=parser.parse_args()
    raw,_=native.native.source_cpu();poses=native.records(raw);pickups=native.records(raw,1);source=raw[131088:]
    manifest=json.loads((ROOT/'reference/parodius-nes/art/packed/manifest.json').read_text())
    packed=(ROOT/'chr/characters/parodius.chr').read_bytes()
    assert hashlib.sha256(packed).hexdigest()==manifest['CHR_sha256']
    cases=[]
    for pool in manifest['pools']:
        variant=pool['variant'];skin=pool['skin']
        main=pool['private_palette']
        # These are declared palette constraints, not a promise of source RGB
        # parity. Native world palettes are preserved, including white/ink.
        palette=[main,[0x1a,0x30,0x27],[0x16,0x30,0x27],[0x0f,0x37,0x17]]
        expected_map={0x30:0x30,0x0f:0x0f,0x38:0x30,0x17:0x17,
                      0x06:0x06 if variant==3 else 0x17,0x08:main[1],
                      0x15:main[0]if variant==1 else 0x17,
                      0x21:main[2]if variant==1 else main[0],
                      0x03:0x0f if variant!=2 else main[1],
                      0x28:0x27 if variant==1 else main[2]}
        if variant in(2,3):
            expected_map.update({0x30:0x30,0x38:0x30,0x21:0x21,0x03:0x03,
                                 0x06:0x16,0x28:0x27,0x08:0x17})
        def read(tile):
            offset=(pool['body_chr']-manifest['first_chr'])*1024
            offset+=(3072 if tile&1 and tile>=0xc0 else 2048 if tile&1 else 0)+(tile&62)*16
            data=packed[offset:offset+32]
            assert len(data)==32
            return [[((data[y//8*16+y%8]>>(7-x))&1)|(((data[y//8*16+y%8+8]>>(7-x))&1)<<1)
                     for x in range(8)]for y in range(16)]
        for frame,records in pool['records'].items():
            frame=int(frame)
            colors=expected_map
            if frame>240:
                info=pool['pickup_sources'][str(frame)]
                original=pickups[info['frame']]['parts']
                override=info['palette_override']
                original=[dict(p,attr=(p['attr']&0xc0)|override)if override is not None else p for p in original]
                colors={0x30:0x30,0x28:0x27,0x06:0x16,0x15:0x16,0x08:0x17,
                        0x21:0x21,0x03:0x03 if variant in(2,3)else 0x0f,
                        0x38:0x30,0x17:0x17,0x0f:0x0f}
            else:original=poses[frame]['parts']
            expected=compose([(p['dx']+8,p['dy']+8,p['tile'],p['attr'])for p in original],
                             lambda tile:native.pixels(source,tile,[skin,4,11,5,0,0,0,0]),
                             lambda p,v:colors[native.PALETTES[p][v]])
            signed=lambda n:n if n<128 else n-256
            actual=compose([(signed(x),signed(y),t,a)for t,a,y,x in records],
                           read,lambda p,v:palette[p][v-1])
            assert expected==actual,(variant,pool['phase'],pool['index'],frame,'packed pixels differ')
            cases.append(dict(pool=pool['index'],frame=frame,group=1 if frame>240 else 0,pixels=len(expected)))
    output=args.output.resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    report=dict(source_sha256=native.native.SHA,CHR_sha256=manifest['CHR_sha256'],
                cases=cases,native_pose_pixels_equal=True,
                scope='Original silhouette/overlap/flip pixels and explicit NES color quantization. No full RGB parity, dynamic animation or runtime bank certification.')
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(cases),'packed native Parodius poses')


if __name__=='__main__':main()
