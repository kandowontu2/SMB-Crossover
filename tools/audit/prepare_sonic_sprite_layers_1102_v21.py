"""Lossless source Sonic 3bpp art to private NES 2bpp layer proposal.

The three-layer form measures the cost of preserving every source color.
It is not a grant to replace shared NES palettes or a production renderer.
"""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/sonic-sms-sprite-layers-1102-v21'
GROUPS=[[1,2,7],[3,4,5],[6]]

def decode(blob):
    assert len(blob)==288
    pixels=[[0]*24 for _ in range(32)]
    for tile in range(12):
        sprite=tile//2;x0=sprite%3*8;y0=sprite//3*16+(tile&1)*8
        for y in range(8):
            for x in range(8):pixels[y0+y][x0+x]=sum(((blob[tile*24+y*3+p]>>(7-x))&1)<<p for p in range(3))
    return pixels

def pair(pixels,x0,y0,group):
    blob=bytearray(32)
    for y in range(16):
        for x in range(8):
            value=pixels[y0+y][x0+x]
            if value not in group:continue
            code=group.index(value)+1;at=(y//8)*16+y%8
            blob[at]|=(code&1)<<(7-x);blob[at+8]|=(code>>1)<<(7-x)
    return bytes(blob)

def main():
    O.mkdir(exist_ok=True)
    donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    assert rom[0x591d:0x592b]==bytes.fromhex('b4b6b8ffffffbabcbeffffffffff')
    data=R/'build/sonic-sms-original-1102-v2/src/data';inputs=[];pool=[];rows=[];original={};maximum_oam=maximum_scanline=0
    palette_path=data/'lv_ghz.pal3';palette=palette_path.read_bytes()[16:24]
    assert palette==bytes.fromhex('3820351b162a003f')
    rgb=[((v&3)*85,((v>>2)&3)*85,((v>>4)&3)*85)for v in palette]
    atlas=Image.new('RGB',(14*32,6*44),(44,49,60));draw=ImageDraw.Draw(atlas)
    for frame in range(42):
        for face in ['r','l']:
            path=data/f'sonic_{frame:02X}_{face}.sonicuncart';blob=path.read_bytes();inputs.append(path)
            at=0x20000+(0 if face=='r'else 0x3000)+frame*288
            assert rom[at:at+288]==blob,(frame,face)
            pixels=decode(blob);original[(frame,face)]=pixels;descriptors=[]
            for layer,group in enumerate(GROUPS):
                for sprite in range(6):
                    x0=sprite%3*8;y0=sprite//3*16;native=pair(pixels,x0,y0,group)
                    if not any(native):continue
                    if native not in pool:pool.append(native)
                    descriptors.append(dict(x=x0,y=y0,layer=layer,pair=pool.index(native)))
            restored=[[0]*24 for _ in range(32)]
            for d in descriptors:
                native=pool[d['pair']];group=GROUPS[d['layer']]
                for y in range(16):
                    at2=(y//8)*16+y%8
                    for x in range(8):
                        color=((native[at2]>>(7-x))&1)|(((native[at2+8]>>(7-x))&1)<<1)
                        if color:
                            assert color<=len(group)and restored[d['y']+y][d['x']+x]==0
                            restored[d['y']+y][d['x']+x]=group[color-1]
            assert restored==pixels
            scan=max(sum(d['y']<=y<d['y']+16 for d in descriptors)for y in range(32))
            maximum_oam=max(maximum_oam,len(descriptors));maximum_scanline=max(maximum_scanline,scan)
            rows.append(dict(frame=frame,face=face,sprites=descriptors,max_scanline=scan,source_SHA256=sha(path)))
            x0=(frame%7*2+(face=='l'))*32;y0=frame//7*44
            draw.text((x0,y0),f'{frame:02X}{face.upper()}',fill=(225,225,235))
            for y in range(32):
                for x in range(24):
                    value=pixels[y][x]
                    if value:atlas.putpixel((x0+x+4,y0+y+10),rgb[value])
    mirrors=[frame for frame in range(42)if original[(frame,'l')]==[list(reversed(row))for row in original[(frame,'r')]]]
    (O/'pairs.chr').write_bytes(b''.join(pool))
    (O/'sprites.json').write_text(json.dumps(dict(source_color_groups=GROUPS,rows=rows),separators=(',',':'))+'\n')
    atlas.resize((atlas.width*3,atlas.height*3),Image.Resampling.NEAREST).save(O/'source-atlas.png')
    q=dict(passed=True,private_palette_proposal=True,installed=False,ROM_written=False,frames=42,facings=2,pixel_roundtrips=84,original_pixels=84*24*32,unique_8x16_pairs=len(pool),CHR_bytes=len(pool)*32,maximum_OAM_per_body=maximum_oam,maximum_scanline_sprites=maximum_scanline,exact_mirrored_frames=mirrors,source_color_groups=GROUPS,source_SMS_palette=list(palette),original_ROM_SHA256=sha(donor),scope='All84 exact donor3bpp frames match ROM bank8 R4000/L7000 source pointers and original six8x16 spritemap. Disjoint NES2bpp layers reconstruct every original index/pixel, including all7visible colors. Source-color atlas is not native gameplay. Three distinct palettes are a resource proposal only; native palette/enemy coexistence, scanline overload handling, CHR mapping/OAM/runtime cost and renderer admission remain unqualified. Do not install or claim a playable Sonic from this packet.',bindings={str(p):sha(p)for p in [Path(__file__),palette_path,O/'pairs.chr',O/'sprites.json',O/'source-atlas.png',*inputs]})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))

if __name__=='__main__':main()
