"""Independent RCR art successor: preserve world pickup palette2.

Extract original pixels; skin/white/blue share player palette0, while original
black is an optional separate mask. No shared source/config/menu mutation.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw
import prepare_river_city_assets as old

ROOT = Path(__file__).resolve().parents[1]
PHYSICAL = list(range(716, 724))+list(range(677, 680))
COLORS = {1:(0,0,0), 2:(248,120,88), 3:(255,255,255), 4:(0,120,248)}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def cell(source, x, y, ink):
    pixels = [[source.get((x+dx,y+dy),0) for dx in range(8)] for dy in range(16)]
    values = [[int(v==1) if ink else {0:0,1:0,2:2,3:1,4:3}[v]
               for v in row] for row in pixels]
    raw = old.encode(values)
    mirrored = old.encode([row[::-1] for row in values])
    return min(raw,mirrored), raw != min(raw,mirrored)


def main():
    original = old.NATIVE.read_bytes()
    assert digest(original) == '276c1a1a37685717c0d808490100874a949ea79b68bdef0fcaeeab4586a72f62'
    poses = []
    for variant in range(2):
        for pose_index,(name,pose) in enumerate(old.POSES):
            source, oam, cycles = old.native_pixels(original,pose,variant,1)
            left,top = min(x for x,y in source),min(y for x,y in source)
            chunks = [[],[]]
            for y in range(top,max(y for x,y in source)+1,16):
                for x in range(left,max(x for x,y in source)+1,8):
                    for ink in (0,1):
                        pair, flip = cell(source,x,y,ink)
                        if any(pair): chunks[ink].append((pair,flip,x,y))
            poses.append(dict(variant=variant, index=pose_index, name=name,
                              source=source, chunks=chunks, native_cycles=cycles))
    pages, assignments = [], {}
    for ink in (0,1):
        own_pages = []
        for item in sorted(poses,key=lambda q:(-len(q['chunks'][ink]),q['variant'],q['index'])):
            need = set(part[0] for part in item['chunks'][ink])
            fits = [(len(need-set(page)),i) for i,page in enumerate(own_pages)
                    if len(need|set(page)) <= 32]
            if not fits:
                own_pages.append([]); fits=[(len(need),len(own_pages)-1)]
            _,index = min(fits)
            page = own_pages[index]
            for pair in sorted(need):
                if pair not in page: page.append(pair)
            assignments[ink,item['variant'],item['index']] = len(pages)+index
        pages.extend(own_pages)
    assert len(pages) <= len(PHYSICAL), ('Additional CHR required',len(pages))
    atlas = b''.join(b''.join(page).ljust(1024,b'\0') for page in pages)
    atlas = atlas.ljust(len(PHYSICAL)*1024,b'\0')
    asm = ['; Authenticated RCR pixels; palette2 belongs to world objects.',
           '; Player palette0 visible colors=white30,skin26,blue11.',
           '; Black is optional ink: palette3 visible color1 must be native0F.',
           '.pushseg','.segment "RIVER_CITY_ART"','RcArtStart:']
    facts, tables = [], {}
    preview = Image.new('RGB',(576,36*88),(72,72,72))
    draw = ImageDraw.Draw(preview)
    for row,item in enumerate(poses):
        for face in (1,2):
            actual,*_ = old.native_pixels(original,old.POSES[item['index']][1],item['variant'],face)
            rebuilt = {}
            for ink in (0,1):
                page_index = assignments[ink,item['variant'],item['index']]
                parts = []
                for pair,flip,x,y in item['chunks'][ink]:
                    if face == 2: x=14-x-7; flip=not flip
                    tile = 2*pages[page_index].index(pair)+(64 if ink else 0)
                    attribute = (3 if ink else 0)|(64 if flip else 0)
                    parts.append([tile,attribute,y&255,x&255])
                    values = old.decode(pair)
                    for yy in range(16):
                        for xx in range(8):
                            v=values[yy][7-xx if flip else xx]
                            if v: rebuilt[x+xx,y+yy] = 1 if ink else {1:3,2:2,3:4}[v]
                label=f'RcV{item["variant"]}{"Ink" if ink else "Body"}{item["index"]}{"R" if face==1 else "L"}'
                asm += [label+':',' .byte '+str(4*len(parts))]
                asm += [' .byte '+','.join(map(str,p)) for p in parts]
                tables[ink,item['variant'],face,item['index']] = (label,PHYSICAL[page_index])
                facts.append(dict(variant=item['variant'],pose=item['index'],name=item['name'],face=face,
                                  ink=bool(ink),page=PHYSICAL[page_index],parts=parts))
            assert rebuilt == actual, ('Complete original color/position mask',item['variant'],item['name'],face)
        for column,mode in enumerate(('source','foreground','ink')):
            pixels=item['source']
            for (x,y),value in pixels.items():
                if mode=='foreground' and value==1: continue
                if mode=='ink' and value!=1: continue
                px,py=column*192+(x+14)*2,row*88+(y+3)*2
                if 0<=px<576 and row*88<=py<(row+1)*88:
                    draw.rectangle((px,py,px+1,py+1),fill=COLORS[value])
            draw.text((column*192+80,row*88+20),f'{item["variant"]} {item["name"]}',fill='white')
    for variant in range(2):
        for face in (1,2):
            for ink in (0,1):
                prefix=f'RcV{variant}{"Ink" if ink else "Pose"}{"R" if face==1 else "L"}'
                for suffix,operator in (('Lo','<'),('Hi','>')):
                    asm += [prefix+suffix+':',' .byte '+','.join(operator+tables[ink,variant,face,i][0] for i in range(18))]
        for ink in (0,1):
            asm += [f'RcV{variant}{"Ink" if ink else "Body"}Page:',
                    ' .byte '+','.join(str(tables[ink,variant,1,i][1]&255) for i in range(18))]
    asm += ['RcArtEnd:', '.assert RcArtEnd-RcArtStart<=5248,error,"RCR art capacity"','.popseg']
    files = {
        ROOT/'src/river_city_shared_palette_art.inc': ('\n'.join(asm)+'\n').encode(),
        ROOT/'chr/characters/river-city-shared-palette.chr': atlas,
    }
    for path,data in files.items():
        assert not path.exists(), 'Frozen successor must not be overwritten'
        path.write_bytes(data)
    image_path=ROOT/'chr/characters/river-city-shared-palette-preview.png'
    assert not image_path.exists();preview.save(image_path)
    metadata = dict(status='Independent art component only; not linked/playable/native',
        original_ROM_sha256=digest(original), source_frames=72,
        source_pixels_and_colors_exact_with_ink=True,
        foreground_omits_only_original_black=True,
        world_palette2_untouched=True,
        native_sprite_palette0=[15,48,38,17],
        ink_palette_contract='Only original black uses pal3 color1. Area native pal3 must be checked; castle differs. Do not overwrite a whole world palette.',
        physical_pages=PHYSICAL, page_pair_counts=list(map(len,pages)),
        extra_677_679_requires_Mac_incbin_split=True,
        publication_contract='Per-pose foreground1KB window0; optional ink1KB window1, both high2. Preserve windows2/3. Select actual matching art C70 before every consumer.',
        art_budget=5248, records=facts,
        bindings=[dict(path=str(p),sha256=digest(p.read_bytes()),bytes=p.stat().st_size)
                  for p in [Path(__file__),Path(old.__file__),ROOT/'tools/prepare_river_city_reference.py',*files,image_path]])
    report=ROOT/'chr/characters/river-city-shared-palette-v3.json'
    assert not report.exists();report.write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(dict(source_frames=72,CHR_bytes=len(atlas),pages=len(pages),
                          maximum_parts=max(len(q['parts']) for q in facts))))


if __name__ == '__main__':
    main()
