"""Compact authentic-SMS art/native-host prototype, source-only preparation.

The SMS frame silhouette is sampled to the existing16px native Mario canvas.
Palette and presentation are an explicit3color prototype conversion; original
SMS physics, rolling, rings, hazards and audio remain separate future work.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile

import check_remaining_roster_starts_1110 as Current
import check_manual_vertical_platform_1110 as Host
from prepare_sonic_sprite_layers_1102_v21 import decode, pair

R=Current.R
BASE=R/'build/manual-wide-floor-native-1110/candidate.nes'
PIN='74fde1dba64b17f7f9028c3da1d5948c041e9af11fb37fca4d241d834724318e'
SOURCE=R/'tools/reference/sonic_sms_native_skin_1110.s'
SMS=R/'build/sonic-sms-original-1102-v2/out/s1.sms'
SMS_PIN='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
PAGES=(224,226,228,230)
COLORS=(0,2,2,3,1,3,2,3)


def digest(raw):return sha256(raw).hexdigest()


def frame(rom,index,height=32):
    pixels=decode(rom[0x20000+index*288:0x20000+(index+1)*288])
    return [[COLORS[pixels[y*32//height][x*24//16]] for x in range(16)]
            for y in range(height)]


def atlas(rom):
    pages=[bytearray(1024) for _ in range(4)]
    rows=[]
    def put(page,tile,pixels,x,y,source):
        padded=[row+[0]*8 for row in pixels]+[[0]*24 for _ in range(32-len(pixels))]
        native=pair(padded,x,y,[1,2,3])
        at=tile*16
        assert not any(pages[page][at:at+32]) or pages[page][at:at+32]==native,(page,tile,source)
        pages[page][at:at+32]=native
        rows.append(dict(page=PAGES[page],tile=tile,source_frame=source))
    # Original native declarations in src/metasprite.s: keep every tile and
    # native left-facing reflection, with real SMS pose choices per action.
    source=(0x15,0,2,4,7,8,0x0d)
    for action,sonic in enumerate(source):
        pixels=frame(rom,sonic)
        for tile,x,y in ((action*4,0,0),(action*4+2,8,0),
                         (action*4+0x20,0,16),(action*4+0x22,8,16)):
            put(0,tile,pixels,x,y,sonic)
    for action,sonic in enumerate(source[:6]):
        pixels=frame(rom,sonic,16)
        put(2,action*4,pixels,0,0,sonic)
        put(2,action*4+2,pixels,8,0,sonic)
    # The remaining native swim/climb/growth/fire states keep their genuine
    # allocation and tile layout. Their static SMS art is provisional.
    for page in (1,3):
        pixels=frame(rom,0x15)
        for tile in range(0,64,2):
            put(page,tile,pixels,(tile&2)*4,16 if tile&0x20 else 0,0x15)
    small=frame(rom,0x15,16)
    for tile in range(0x18,0x40,2):
        if not any(pages[2][tile*16:tile*16+32]):
            put(2,tile,small,(tile&2)*4,0,0x15)
    return b''.join(pages),rows


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    assert not args.output.exists()
    args.output.mkdir()
    raw=BASE.read_bytes();assert digest(raw)==PIN
    rom=SMS.read_bytes();assert digest(rom)==SMS_PIN
    art,rows=atlas(rom)
    assert len(art)==4096
    (args.output/'sonic-native.chr').write_bytes(art)
    report=dict(passed=True,art_only=True,prototype=True,ROM_written=False,
        parent_SHA256=PIN,source_ROM_SHA256=SMS_PIN,art_SHA256=digest(art),
        physical_pages=list(PAGES),pixel_mapping=list(COLORS),source_pose_tiles=rows,
        scope='OriginalSMS source poses sampled24x32 to native16x32/16x16 canvases; '
              '3opaqueNES colors. Nativehostphysics/lifecycle prototype, not a fullSMSport. '
              'CHR ownership and menu/runtime qualification pending.',
        bindings={p.relative_to(R).as_posix():digest(p.read_bytes()) for p in
                  (Path(__file__),SOURCE,SMS,R/'src/metasprite.s')})
    (args.output/'art-proposal.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,art_only=True,bytes=len(art),pages=PAGES)))


if __name__=='__main__':main()
