"""Decode original NES Parodius sprite records/CHR without redrawing pixels.

The sprite program is PRG bank 4 and its group-zero record table lives in
bank 5 at $ACC2. Entry zero is unused, not a valid sprite pointer. Native
animation/weapon state chooses frames 1..240 and the skin CHR page.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('pn_native',ROOT/'tools/reference/build_parodius_native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
RGB={0x0f:(0,0,0),0x30:(252,252,252),0x21:(60,188,252),0x03:(68,40,188),
     0x28:(248,216,120),0x06:(108,6,0),0x15:(228,0,88),0x08:(80,48,0),
     0x38:(248,248,120),0x17:(228,92,16)}
PALETTES=[[0x0f,0x30,0x21,0x03],[0x0f,0x30,0x28,0x06],
          [0x0f,0x30,0x15,0x08],[0x0f,0x38,0x17,0x0f]]


def records(raw, group=0):
    prg=raw[16:131088]
    both=prg[4*8192:6*8192]
    read=lambda address:both[address-0x8000]
    word=lambda address:read(address)+256*read(address+1)
    sign=lambda value:value if value<128 else value-256
    assert word(0x882e)==0xacc2 and word(0xacc4)==0xaea4
    assert group in (0,1),group
    table,count=(0xacc2,240)if group==0 else(0x8836,209)
    assert word(0x882e+group*2)==table
    result={}
    for frame in range(1,count+1):
        pointer=word(table+frame*2)
        assert 0x8000<=pointer<0xc000,(frame,hex(pointer))
        count=read(pointer)
        cursor=pointer+1
        parts=[]
        if count==255:
            # Original $86B0: a two-sprite 16x16 object at (X-8,Y-8).
            for dx in (-8,0):
                attr,tile=read(cursor),read(cursor+1);cursor+=2
                parts.append(dict(dx=dx,dy=-8,attr=attr&0xc3,tile=tile))
        else:
            assert count<=32,(frame,count)
            for _ in range(count):
                dx,attr,tile=[read(cursor+i) for i in range(3)];cursor+=3
                if attr&0x3c:
                    dy=read(0x8748+((attr&0x3c)>>2))
                else:
                    dy=read(cursor);cursor+=1
                parts.append(dict(dx=sign(dx),dy=sign(dy),attr=attr&0xc3,tile=tile))
        result[frame]=dict(pointer=pointer,source_bytes=list(both[pointer-0x8000:cursor-0x8000]),
                           compressed_pair=count==255,parts=parts)
    return result


def pixels(chr_data,tile,pages):
    address=(tile&1)*4096+(tile&254)*16
    page=pages[address//1024]
    offset=page*1024+address%1024
    data=chr_data[offset:offset+32]
    assert len(data)==32
    return [[((data[(y//8)*16+y%8]>>(7-x))&1)|
             (((data[(y//8)*16+y%8+8]>>(7-x))&1)<<1)
             for x in range(8)] for y in range(16)]


def draw_pose(image,origin,record,chr_data,skin,palette_override=0):
    for part in reversed(record['parts']):
        attr=part['attr']
        palette=PALETTES[palette_override if palette_override else attr&3]
        px=pixels(chr_data,part['tile'],[skin,4,11,5,0,0,0,0])
        for y in range(16):
            for x in range(8):
                color=px[15-y if attr&128 else y][7-x if attr&64 else x]
                if color:
                    dx,dy=origin[0]+part['dx']+x,origin[1]+part['dy']+y
                    if 0<=dx<image.width and 0<=dy<image.height:
                        image.putpixel((dx,dy),(*RGB[palette[color]],255))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'reference/parodius-nes/art')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    raw,cpu=native.source_cpu();decoded=records(raw)
    chr_data=raw[131088:]
    animations=native.native_animations(cpu)
    animation_frames=set()
    for animation in animations:
        data=animation['data']
        animation_frames.update(value for value in (data[2:-1] if data[0]==253 else data[:-1:2]) if value)
    assert animation_frames<=set(decoded),sorted(animation_frames-set(decoded))
    # Separate atlases preserve each character's skin bank. Weapon records
    # often share pixels, and Big uses its original dedicated skin bank.
    for variant,name in enumerate(('vic-viper','octopus','twinbee','pentarou')):
        image=Image.new('RGBA',(12*80,20*72),(40,40,48,255))
        draw=ImageDraw.Draw(image)
        for frame,record in decoded.items():
            index=frame-1;ox=index%12*80;oy=index//12*72
            draw.text((ox+2,oy+2),str(frame),fill='white')
            draw_pose(image,(ox+34,oy+38),record,chr_data,variant)
        image.save(out/(name+'-records.png'))
    report=dict(source_sha256=native.SHA,player_record_prg_banks=[4,5],
                group_pointer=0x882e,record_table=0xacc2,frame_zero_unused=True,
                first_sprite_chr_pages=[0,1,2,3],big_chr_pages=list(cpu.memory[0x9326:0x932a]),
                other_sprite_chr_pages=[4,11,5],original_sprite_palettes=PALETTES,
                records=decoded,animation_frames=sorted(animation_frames),
                preserves_original_pixels=True,playable=False,
                scope='Source record extraction; no packed-ROM renderer or SMB gameplay certification.')
    (out/'source-art.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(records=len(decoded),animation_frames=len(animation_frames),output=str(out))))


if __name__=='__main__':main()
