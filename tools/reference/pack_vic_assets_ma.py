"""Pack original Vic Viper pixels for the expanded MMC5 sprite window.

The shared world palettes stay untouched. White uses the existing world2 white;
the player's three colors hold original navy/red/cyan. The original exhaust's
dark red and bullets' sky blue map to the player's red/cyan respectively.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/vic-viper-lq/art/packed-mh2'
BODY=(1,2,3,45,46,47,48)
SHOTS=(6,7,8,10,0x24,4,5,16,17,18)
COLORS={0x0c:(0,64,88),0x26:(248,120,88),0x30:(252,252,252),0x2c:(0,232,216)}


def decode(raw):
    return [[((raw[(y//8)*16+y%8]>>(7-x))&1)|
             (((raw[(y//8)*16+y%8+8]>>(7-x))&1)<<1)
             for x in range(8)] for y in range(16)]


def encode(px):
    return bytes(sum(((px[y+b*8][x]>>p)&1)<<(7-x) for x in range(8))
                 for b in range(2) for p in range(2) for y in range(8))


def main():
    assert not O.exists(), 'Preserve earlier art evidence'
    O.mkdir(parents=True)
    record=json.loads((O.parent/'source-records.json').read_text())
    rom=Path('C:/NES/Gradius (USA).nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==record['rom_sha256']
    source=rom[16+32768:]
    native=(R/'chr/mmc5/sprites_mario.chr').read_bytes()
    # Native enemy art occupies the second1KB of this window; never replace it.
    original_upper=native[1024:2048]
    assert len(original_upper)==1024
    palette=record['palette']
    mappings={0x0c:(0,1),0x26:(0,2),0x2c:(0,3),0x30:(2,2),
              0x06:(0,2),0x21:(0,3)}
    pool=[]
    def pack_pose(key):
        result=[]
        for y,t,attr,x in record['records'][str(key)]:
            base=(t&1)*4096+(t&0xfe)*16
            pixels=decode(source[base:base+32])
            for pal in (0,2):
                layer=[[0]*8 for _ in range(16)]
                for yy in range(16):
                    for xx in range(8):
                        c=pixels[yy][xx]
                        if c:
                            target,value=mappings[palette[(attr&3)*4+c]]
                            if pal==target:layer[yy][xx]=value
                if not any(any(row) for row in layer):continue
                raw=encode(layer)
                if raw not in pool:pool.append(raw)
                index=pool.index(raw)*2
                result.append((index,(attr&0xc0)|pal,((y+128)%256-128+8)&255,
                               ((x+128)%256-128+8)&255))
        return result
    common={key:pack_pose(key) for key in SHOTS}
    prefix=pool.copy()
    body={};banks=[]
    for number,key in enumerate(BODY):
        pool[:]=prefix if key in (1,2,3) else []
        body[key]=pack_pose(key)
        assert len(pool)*32<=1024,(key,len(pool))
        banks.append(b''.join(pool).ljust(1024,b'\0')+original_upper)
    lines=['; Original Gradius USA records; two explicit NES palette approximations.',
           '.pushseg','.segment "VIC_GFX"','VicArtBegin:']
    for key,parts in {**common,**body}.items():
        lines += [f'VvPose{key}:',f'  .byte {len(parts)*4}']
        lines += [f'  .byte ${t:02x},${a:02x},${y:02x},${x:02x}' for t,a,y,x in parts]
    lines += ['.popseg']
    (O/'vic_art.inc').write_text('\n'.join(lines)+'\n')
    (O/'vic.chr').write_bytes(b''.join(banks))
    report=dict(status='PACKED_ORIGINAL_ART_COMPONENT_NOT_YET_PLAYABLE',
        source_sha256=record['rom_sha256'],chr_first=380,chr_kilobytes=len(banks)*2,
        pose_banks={str(k):380+n*2 for n,k in enumerate(BODY)},
        common_shot_poses=list(SHOTS),common_pair_count=len(prefix),common_only_in_ship_banks=True,
        body_records={str(k):v for k,v in body.items()},
        shot_records={str(k):v for k,v in common.items()},
        native_upper_1k_preserved=True,world_palette_writes=0,
        player_palette=[0x0c,0x26,0x2c],white_world2_color=2,
        approximations={'original06_exhaust':'26','original21_bullets':'2C'})
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    canvas=Image.new('RGBA',(128*3,56*3))
    for n,key in enumerate(BODY):
        for t,a,y,x in body[key]:
            dx=x if x<128 else x-256;dy=y if y<128 else y-256
            pixels=decode(banks[n][t*16:t*16+32])
            for yy in range(16):
                for xx in range(8):
                    c=pixels[15-yy if a&128 else yy][7-xx if a&64 else xx]
                    if c:
                        color=0x30 if a&3==2 else [0,0x0c,0x26,0x2c][c]
                        canvas.putpixel((n%3*128+40+dx+xx,n//3*56+16+dy+yy),(*COLORS[color],255))
    canvas.save(O/'packed-poses.png')
    print(json.dumps(report))


if __name__=='__main__':main()
