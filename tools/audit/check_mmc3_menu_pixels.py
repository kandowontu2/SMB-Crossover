"""Compare every stable and transition portrait to original captured pixels."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]


def render(oam,chr_data,palette, *, body_only=False):
    image=bytearray(256*240*2)
    for slot in reversed(range(64)):
        y,tile,attr,x=oam[slot*4:slot*4+4]
        if y>=240:continue
        address=(tile&1)*4096+(tile&254)*16
        if body_only:
            assert tile&1 and tile<64,('Menu sprite outside resident portrait page',slot,tile)
            address-=4096
        data=chr_data[address:address+32]
        assert len(data)==32,(slot,tile,address)
        for yy in range(16):
            sy=15-yy if attr&128 else yy
            offset=(sy//8)*16+sy%8
            py=y+1+yy
            if py>=240:continue
            for xx in range(8):
                sx=xx if attr&64 else 7-xx
                color=((data[offset]>>sx)&1)|(((data[offset+8]>>sx)&1)<<1)
                px=x+xx
                if color and px<256:
                    dest=(py*256+px)*2
                    image[dest]=1
                    image[dest+1]=palette[16+(attr&3)*4+color]&63
    return bytes(image)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path,required=True)
    parser.add_argument('--source',type=Path,required=True)
    args=parser.parse_args();out=args.capture.resolve();source=args.source.resolve()
    manifest=json.loads((out/'manifest.json').read_text())
    reference=json.loads((source/'manifest.json').read_text())
    assert manifest['exit']==reference['exit']==0
    actual_folder=out/'build/verification';source_folder=source/'build/verification'
    setting='on'if manifest['outlines']else'off'
    expected=[];stable=[]
    for number,case in enumerate(manifest['identities'],1):
        key=f'{number:02d}-{setting}-{case[0].lower().replace(" ","-")}'
        pixels=render((source_folder/(key+'-oam.bin')).read_bytes(),
                      (source_folder/(key+'-chr.bin')).read_bytes(),
                      (source_folder/(key+'-palette.bin')).read_bytes())
        expected.append(pixels)
        actual=render((actual_folder/(key+'-oam.bin')).read_bytes(),
                      (actual_folder/(key+'-chr.bin')).read_bytes(),
                      (actual_folder/(key+'-palette.bin')).read_bytes())
        assert pixels==actual,('Stable portrait differs from source pixels',case[0],setting)
        reference_image=Image.open(source_folder/(key+'.png')).convert('RGB')
        actual_image=Image.open(actual_folder/(key+'.png')).convert('RGB')
        assert reference_image.size==actual_image.size and reference_image.tobytes()==actual_image.tobytes(),('Actual rendered screenshot differs from MMC5 source',case[0],setting)
        assert (source_folder/(key+'-nametable.bin')).read_bytes()==(actual_folder/(key+'-nametable.bin')).read_bytes(),('Background grid or labels differ',case[0])
        stable.append(case[0])
    valid={hashlib.sha256(pixels).digest()for pixels in expected}
    trace=(actual_folder/'browsing.bin').read_bytes()
    size=1320
    assert len(trace)%size==0
    failures=[];frames=0
    # A menu can briefly display the previous complete portrait while the new
    # input/label is queued. Both complete portraits are legitimate; combining
    # a new CHR page with old OAM/palette is never accepted.
    for offset in range(0,len(trace),size):
        record=trace[offset:offset+size]
        frame,slot,mask,profile=struct.unpack_from('<IHBB',record)
        if mask&0x18!=0x18:
            failures.append(dict(frame=frame,slot=slot,mask=mask,reason='forced blank'))
            continue
        try:
            pixels=render(record[8:264],record[264:1288],record[1288:1320],body_only=True)
            if hashlib.sha256(pixels).digest()not in valid:
                failures.append(dict(frame=frame,slot=slot,profile=profile,reason='mixed or corrupted portrait'))
        except AssertionError as error:
            failures.append(dict(frame=frame,slot=slot,profile=profile,reason=str(error)))
        frames+=1
    report=dict(ROM_sha256=manifest['ROM_sha256'],source_ROM_sha256=reference['ROM_sha256'],
                outline_setting=setting,stable_identity_pixels=stable,transition_frames=frames,
                rendered_screenshots_exact=len(stable),
                bad_frames=failures,trace_sha256=hashlib.sha256(trace).hexdigest(),
                passed=not failures)
    (out/'pixel-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not failures,failures[:12]
    print('PASS',len(stable),'exact source portraits and',frames,'browsing frames;',setting)


if __name__=='__main__':main()
