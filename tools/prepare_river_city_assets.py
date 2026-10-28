"""Repack authenticated NES RCR player pixels into the crossover's 8x16 format.

No generated art: native ED0E executes the original pose/head/attribute tables.
Native 9D3B/9E6B selects player kinds80/81 (not the enemy constructor B7FD).
Reset E306 selects pages40/42/45/41. The output preserves every winning
opaque color of the selected native poses, in both facings, for Alex and Ryan.
"""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
from prepare_river_city_reference import NATIVE,native_pixels,player_setup

ROOT=Path(__file__).resolve().parents[1]
POSES=[('Stand',0),('Walk1',1),('Walk2',2),('Run',7),('Jump',10),('Crouch',12),
       ('Hurt',13),('Down',20),('Punch1',33),('Punch2',34),('Punch3',35),
       ('Kick1',36),('Kick2',37),('Kick3',38),('RunKick',39),('Carry',40),
       ('Throw',42),('AirKick',19)]
COLORS={1:(0,0,0),2:(248,120,88),3:(255,255,255),4:(0,120,248)}

def encode(pixels):
    result=bytearray()
    for start in (0,8):
        for plane in (0,1):
            for y in range(start,start+8):
                result.append(sum(((pixels[y][x]>>plane)&1)<<(7-x) for x in range(8)))
    return bytes(result)

def decode(data):
    return [[((data[(y//8)*16+y%8]>>(7-x))&1)|(((data[(y//8)*16+y%8+8]>>(7-x))&1)<<1) for x in range(8)] for y in range(16)]

def main():
    raw=NATIVE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='276c1a1a37685717c0d808490100874a949ea79b68bdef0fcaeeab4586a72f62'
    assert raw[16+15*8192+0x306:16+15*8192+0x30a]==bytes([0x40,0x42,0x45,0x41])
    native_owners=[]
    for variant in (0,1):
        native=player_setup(raw,variant)
        native_owners.append(dict(variant=variant,player_slot=variant,
          actor_kind=native[0x48+variant],graphics_kind=native[0xcb+variant],
          CHR_pages=native[0x521:0x525],sprite_palettes=native[0x120:0x128]))
    asm=['; Generated from authenticated native RCR player renderer/patterns; see recipe.',
         '.pushseg','.segment "RIVER_CITY_ART"','RcArtStart:']
    atlas=bytearray();records=[];rows=[]
    for variant in range(2):
        pairs=[];lookup={};table={};right_parts={}
        for face in (1,2):
            for name,pose in POSES:
                source,original,cycles=native_pixels(raw,pose,variant,face)
                assert source and all(v in COLORS for v in source.values())
                left=min(x for x,y in source);top=min(y for x,y in source)
                right=max(x for x,y in source);bottom=max(y for x,y in source)
                parts=[]
                if face==2:
                    parts=[[tt,aa^0x40,yy,(14-(xx-256 if xx>=128 else xx)-7)&255] for tt,aa,yy,xx in right_parts[name]]
                for y in (range(top,bottom+1,16) if face==1 else []):
                    for x in range(left,right+1,8):
                        cell=[[source.get((x+dx,y+dy),0) for dx in range(8)] for dy in range(16)]
                        values={v for line in cell for v in line}
                        if values=={0}:continue
                        # Native pal0 and pal1 share black/white. Preserve actual
                        # colors, moving blue's hardware slot to private pal2.
                        palettes=(0,2) if {2,4}<=values else ((2,) if 4 in values else (0,))
                        for palette in palettes:
                            p=[[0 if ((v==4 and palette==0) or (v!=4 and palette==2 and len(palettes)==2)) else (2 if v==4 else v) for v in line] for line in cell]
                            direct=encode(p);mirrored=encode([line[::-1] for line in p]);canonical=min(direct,mirrored)
                            attr=palette|(0x40 if direct!=canonical else 0)
                            if canonical not in lookup:
                                lookup[canonical]=len(pairs);pairs.append(canonical)
                            parts.append([lookup[canonical]*2,attr,y&255,x&255])
                if face==1:right_parts[name]=parts
                assert len(parts)<=12,(variant,face,name,len(parts))
                # The renderer consumes records in reverse; layers are disjoint.
                rebuilt={}
                for tt,aa,yy,xx in reversed(parts):
                    pixels=decode(pairs[tt//2]);xx=xx-256 if xx>=128 else xx;yy=yy-256 if yy>=128 else yy
                    for dy in range(16):
                        for dx in range(8):
                            v=pixels[dy][7-dx if aa&64 else dx]
                            if v:rebuilt[(xx+dx,yy+dy)]=4 if (v==2 and aa&3==2) else v
                assert rebuilt==source,(variant,face,name)
                label=f'RcV{variant}{name}{"R" if face==1 else "L"}'
                table[(face,name)]=label
                asm += [label+':',' .byte '+str(len(parts)*4)]
                asm += [' .byte '+','.join(str(v) for v in p) for p in parts]
                records.append(dict(variant=variant,face=face,name=name,native_pose=pose,
                                    original_OAM=original,native_renderer_cycles=cycles,parts=parts,
                                    opaque_pixels=len(source),bounds=[left,top,right,bottom]))
                if face==1:rows.append((variant,name,source))
        assert len(pairs)<=128,(variant,len(pairs))
        atlas.extend(b''.join(pairs).ljust(4096,b'\0'))
        for face in (1,2):
            for kind,op in [('Lo','<'),('Hi','>')]:
                asm += [f'RcV{variant}Pose{"R" if face==1 else "L"}{kind}:',
                        ' .byte '+','.join(op+table[(face,n)] for n,_ in POSES)]
    asm += ['.assert *-RcArtStart<=4096,error,"River City art allocation"','.popseg']
    out=ROOT/'chr/characters/river-city.chr';out.write_bytes(atlas)
    (ROOT/'src/river_city_art.inc').write_text('\n'.join(asm)+'\n',encoding='utf-8')
    preview=Image.new('RGB',(9*128,4*112),(80,80,80));d=ImageDraw.Draw(preview)
    for i,(variant,name,pixels) in enumerate(rows):
        tile=Image.new('RGB',(48,48),(160,160,160))
        for (x,y),v in pixels.items():tile.putpixel((x+8,y+8),COLORS[v])
        x=(i%9)*128;y=(i//9)*112;preview.paste(tile.resize((96,96)),(x,y));d.text((x,y+97),f'{"Alex" if variant==0 else "Ryan"} {name}',fill='white')
    preview.save(ROOT/'chr/characters/river-city-packed-preview.png')
    metadata=dict(native_ROM=str(NATIVE),native_ROM_sha256=hashlib.sha256(raw).hexdigest(),
                  original_renderer='0F:ED0E..EF88 (complete native CPU)',
                  original_player_owner='02:9D3B..9E7F: real stage players80/81, graphics0; typed position descriptor only',
                  original_CHR_owner='0F:E2F7/E306: pages40,42,45,41',
                  original_palette_owner='0F:E3D5..E460: full-brightness sprite palettes0/1 from E9F9/E9FD',
                  original_palette_pixel_meaning={'1':'black0F','2':'white30 for native palette0; blue11 for palette1','3':'skin26'},
                  native_player_setup=native_owners,
                  output_palette0=[15,15,38,48],output_palette2=[15,15,17,48],
                  output_chr_sha256=hashlib.sha256(atlas).hexdigest(),output_bytes=len(atlas),
                  source_records=records,checks={'all72_native_pose_pixel_maps_exact':True,
                  'no_invented_art':True,'both_native_head_variants':True},
                  scope='Source art preparation; no integrated/native game claim.')
    (ROOT/'chr/characters/river-city-assets.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(dict(bytes=len(atlas),records=len(records),parts_max=max(len(q['parts'])for q in records),chr_sha256=metadata['output_chr_sha256'])))

if __name__=='__main__':main()
