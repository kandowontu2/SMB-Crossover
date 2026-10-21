"""Extract 2.02 weapon frames through SWF bitmap/mask matrices.

Every composite CHR bank preserves all native background and actor tiles.
Only unreferenced 8x16 pairs in the spare sprite window are allocated.
"""
from pathlib import Path
import sys,json,xml.etree.ElementTree as ET
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_megaman_assets as assets
import build_samus_assets as packing
from prepare_crossover import frames

ROOT=assets.ROOT
PAL=[(0x0f,0x30,0x17),(0x0f,0x37,0x18),(0x0f,0x10,0x01),
     (0x0f,0x14,0x34),(0x0f,0x30,0x26),(0x0f,0x27,0x16),
     (0x0f,0x31,0x11)]
from build_expanded_assets import RGB
RGB={**RGB,0x11:(0,112,236),0x34:(252,196,252),0x19:(0,148,0),
     0x29:(88,216,84),0x2c:(0,232,216),0x18:(172,124,0),
     0x10:(188,188,188),0x01:(0,0,187),0x14:(168,0,200),0x31:(184,224,248)}


def extract(timeline,bitmap,sheet):
    result=[]
    for frame in timeline:
        canvas=Image.new('RGBA',(96,96))
        entries=sorted(frame['display'].items(),key=lambda p:int(p[0]))
        for index,(depth,value) in enumerate(entries):
            if value.get('characterId')!=str(bitmap):continue
            mask=next((v for _,v in entries[index+1:] if v.get('characterId')=='18'),None)
            if mask is None:continue
            m=value['matrix']; mm=mask['matrix']
            x,y=(float(mm[k])/40 for k in ('translateX','translateY'))
            w,h=(float(mm[k])/2 for k in ('scaleX','scaleY'))
            left=x-float(m['translateX'])/40;top=y-float(m['translateY'])/40
            pic=sheet.crop(tuple(round(v) for v in (left,top,left+w,top+h)))
            pic.putdata([(0,0,0,0) if p[:3]==(111,49,152) else p for p in pic.getdata()])
            canvas.alpha_composite(pic,(round(48+x),round(48+y)))
        result.append(canvas)
    return result


def main():
    tree=ET.parse(ROOT/'reference/crossover2/main.xml')
    items=list(tree.getroot().iter('item'));symbols={}
    for tag in items:
        if tag.get('type') in ('SymbolClassTag','ExportAssetsTag'):
            ids=tag.find('tags');names=tag.find('names')
            if ids is not None and names is not None:symbols.update({n.text:i.text for i,n in zip(ids,names)})
    sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
    sheet=Image.open(ROOT/'reference/crossover2/images/412_com.smbc.graphics.skins.BmdInfo_Bass000.png').convert('RGBA')
    source={name:extract(frames(sprites[symbols[name]]),24,sheet)
            for name in ('MegaManProjectile','MegaManSimpleGraphics','MegaManPickup','Rush')}
    groups=[('METAL','MegaManProjectile',[15,16],1),
            ('KNUCKLE','MegaManProjectile',list(range(17,24)),2),
            ('PHARAOH','MegaManProjectile',list(range(42,54)),3),
            ('FLAME','MegaManProjectile',list(range(24,40)),5),
            ('WATER','MegaManProjectile',[40,41],6),
            ('KICK','MegaManSimpleGraphics',[10,11,12],4),
            ('RUSH','Rush',list(range(1,14)),0),
            ('PICKUP','MegaManPickup',[i for i in range(1,18) if i not in (9,11,12)],0),
            ('FLAME90','MegaManProjectile',list(range(25,40)),5),
            ('FLAME180','MegaManProjectile',list(range(25,40)),5),
            ('FLAME270','MegaManProjectile',list(range(25,40)),5)]
    # Native SPRITE_BANK_4 users, plus the background axe/chain metatiles.
    reserved={2,3,4,5,6,7,8,9,10,11,12,16,17,18,19,20,22,23,24,26}
    free=[i for i in range(32) if i not in reserved]
    families=[];records=[('EMPTY',0,[])];lookup={}
    assets.SCANLINE_PRIORITY=True
    for group,symbol,indices,palette in groups:
        colors=[(RGB[n],(0,i+1)) for i,n in enumerate(PAL[palette])]
        colors += [(RGB[0x16],(2,1)),(RGB[0x30],(2,2)),(RGB[0x27],(2,3))]
        palettes=(0,2)
        if group=='PICKUP':
            # Pickups coexist with every suit. Never put their pixels in the
            # player's changing palette, or alter mushrooms/enemies to fit.
            colors=[(RGB[n],(p,i+1)) for p,ns in
                    ((2,(0x16,0x30,0x27)),(3,(0x0f,0x37,0x17)))
                    for i,n in enumerate(ns)]
            palettes=(2,3)
        def layers(image,projectile=False):
            output={p:[[0]*image.width for _ in range(image.height)] for p in palettes}
            for y in range(image.height):
                for x in range(image.width):
                    v=image.getpixel((x,y))
                    if v[3]<128:continue
                    rgb,(p,c)=min(colors,key=lambda z:sum((v[k]-z[0][k])**2 for k in range(3)))
                    output[p][y][x]=c
            return output
        assets.layers=layers
        for frame in indices:
            im=source[symbol][frame-1]
            if group.startswith('FLAME') and group!='FLAME':
                im=im.rotate(-int(group[5:]),center=(48,48),resample=Image.Resampling.NEAREST)
            raw=[];rawparts=packing.parts(im,(48,48),raw)
            choices=[]
            for family,pool in enumerate(families):
                candidate=pool+[v for v in raw if v not in pool]
                if len(candidate)<=len(free):choices.append((len(candidate)-len(pool),family,candidate))
            if choices:
                _,family,candidate=min(choices,key=lambda c:(c[0],c[1]))
            else:
                family=len(families);families.append([])
                candidate=raw[:]
            parts=[(candidate.index(raw[t//2])*2,p,x,y) for t,p,x,y in rawparts]
            pool=families[family]
            assert len(candidate)<=len(free),(group,frame,len(candidate),len(free))
            pool[:]=candidate
            parts=[(free[t//2]*2,p,x,y) for t,p,x,y in parts]
            name=f'{group}{frame}'
            lookup[name]=len(records);records.append((name,family,parts))
    # Flame pixels are outside GraphicsManager's suit-recolor rectangles.
    # Keep them on the fixed world red/orange palette; the seed's black
    # outline uses palette3. Preserve every non-Flame tile, pose and family,
    # especially the fixed Water renderer's source family/slot contract.
    original_records=list(records)
    original_families=len(families);shared_family=original_families-1
    occupied=[set() for _ in families]
    protected={}
    for name,family,parts in records:
        if name.startswith('FLAME'):continue
        for tile,_,_,_ in parts:
            slot=free.index(tile//2);occupied[family].add(slot)
            protected[family,slot]=families[family][slot]
    # Remaining weapons share spare pairs in the final special family.
    # Those pairs stay reserved, and their exact old bytes are retained in
    # the shared overlays when this generator updates the Flame tiles.
    overlay_pairs={}
    for mapper in ('mmc3','mmc5'):
        base=ROOT/f'chr/characters/special-weapons-{mapper}.chr'
        shared=ROOT/f'chr/characters/special-remaining-shared-{mapper}.chr'
        if base.exists() and shared.exists():
            old,over=base.read_bytes()[-2048:],shared.read_bytes()
            overlay_pairs[mapper]={i:over[1024+n*32:1024+(n+1)*32] for i,n in enumerate(free)
                                   if old[1024+n*32:1024+(n+1)*32]!=over[1024+n*32:1024+(n+1)*32]}
    locked=set().union(*(set(p) for p in overlay_pairs.values()))
    occupied[shared_family]|=locked
    for pool in families:pool += [None]*(len(free)-len(pool))
    def fixed_flame_layers(image,projectile=False):
        output={p:[[0]*image.width for _ in range(image.height)]for p in (2,3)}
        choices=[(RGB[0x16],2,1),(RGB[0x27],2,3),(RGB[0x0f],3,1)]
        for y in range(image.height):
            for x in range(image.width):
                v=image.getpixel((x,y))
                if v[3]<128:continue
                _,pal,color=min(choices,key=lambda z:sum((v[k]-z[0][k])**2 for k in range(3)))
                output[pal][y][x]=color
        return output
    assets.layers=fixed_flame_layers
    for i,(name,old_family,old_parts) in enumerate(original_records):
        if not name.startswith('FLAME'):continue
        match=__import__('re').fullmatch(r'FLAME(?:(90|180|270))?(\d{2})',name)
        angle=int(match[1] or 0);frame=int(match[2])
        im=source['MegaManProjectile'][frame-1]
        if angle:im=im.rotate(-angle,center=(48,48),resample=Image.Resampling.NEAREST)
        raw=[];rawparts=packing.parts(im,(48,48),raw);candidates=[]
        for family,pool in enumerate(families):
            used=set(occupied[family]);assign=[];writes={}
            for tile in raw:
                same=next((s for s,v in enumerate(pool) if v==tile and not(family==shared_family and s in locked)),None)
                if same is not None:slot=same
                else:
                    slot=next((s for s in range(len(free)) if s not in used),None)
                    if slot is None:break
                    writes[slot]=tile
                used.add(slot);assign.append(slot)
            else:candidates.append((len(writes),family!=old_family,family,assign,writes,used))
        if not candidates:
            assert len(families)<original_families+3,('Fixed Flame palette exceeds CHR budget',name)
            family=len(families);families.append([None]*len(free));occupied.append(set())
            assert len(raw)<=len(free)
            candidates=[(len(raw),True,family,list(range(len(raw))),dict(enumerate(raw)),set(range(len(raw))))]
        _,_,family,assign,writes,used=min(candidates,key=lambda c:c[:3])
        for slot,tile in writes.items():families[family][slot]=tile
        occupied[family]=used
        records[i]=(name,family,[(free[assign[t//2]]*2,p,x,y)for t,p,x,y in rawparts])
    if len(families)>original_families:
        # pack_chr maps Remaining's shared window to the final special bank.
        # Keep that original final family last; it contains only Flame art.
        assert not any(f==shared_family and not n.startswith('FLAME') for n,f,_ in original_records)
        order=[*range(shared_family),*range(original_families,len(families)),shared_family]
        remap={old:new for new,old in enumerate(order)}
        families=[families[old] for old in order]
        records=[(n,remap[f],p)for n,f,p in records]
        protected={(remap[f],s):v for (f,s),v in protected.items()}
    for i,record in enumerate(original_records):
        if not record[0].startswith('FLAME'):assert records[i]==record
    for (family,slot),tile in protected.items():assert families[family][slot]==tile
    lines=['; Generated from 2.02 SWF matrices.','.pushseg','.segment "SAMUS_GFX"']
    for i,(name,family,parts) in enumerate(records):
        segment='LINK_GFX' if name.startswith(('FLAME90','FLAME180','FLAME270')) else 'SAMUS_GFX'
        lines.append(f'.segment "{segment}"')
        for facing in ('Left','Right'):
            lines += [f'SsArt{i}{facing}:',f' .byte {len(parts)*4}']
            for tile,pal,x,y in parts:
                if facing=='Left':x=-x-8;pal^=0x40
                lines.append(f' .byte MetaspriteVramOffset{{${tile:02x}}}, {{SPRITE_BANK_4}}, ${pal:02x}, {y}, {x}')
    lines.append('.segment "SAMUS_GFX"')
    for side in ('Left','Right'):
        for suffix,operator in [('Lo','<'),('Hi','>')]:
            lines += [f'SsArt{side}{suffix}:',' .byte '+','.join(operator+f'SsArt{i}{side}' for i in range(len(records)))]
    lines += ['SsArtFamilies:',' .byte '+','.join(str(r[1]) for r in records),
              'SsArtBanks:',' .byte '+','.join(f'.bank(SsArt{i}Right)' for i in range(len(records))),
              'SsNativeBrick: .byte 8',
              ' .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_1}, 0,-8,-8',
              ' .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_1}, 0,-8,0',
              'SsNativeChunk: .byte 4',
              ' .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_1}, 0,-4,-4','.popseg']
    constants=[f'SS_ART_{name} = {i}' for i,(name,_,_) in enumerate(records)]
    (ROOT/'src/special_art.inc').write_text('\n'.join(lines)+'\n')
    (ROOT/'src/special_art_ids.inc').write_text('\n'.join(constants)+'\n')
    # Active-play HUD only: these tiles are unused by level metatiles and
    # the native score. Area transitions restore the unmodified font bank.
    hud=bytearray()
    for frame in (3,4,5,6,7,8,13,10):
        bank=bytearray((ROOT/'chr/mmc5/bg_ground.chr').read_bytes()[:2048])
        im=source['MegaManPickup'][frame-1].crop((40,32,56,48))
        pixels=[]
        for y in range(16):
            row=[]
            for x in range(16):
                p=im.getpixel((x,y))
                row.append(0 if p[3]<128 else min((1,2,3),key=lambda c:sum((p[k]-((252,252,252),(60,188,252),(0,0,0))[c-1][k])**2 for k in range(3))))
            pixels.append(row)
        for tile,dx,dy in ((0x2a,0,0),(0x2b,8,0),(0x2c,0,8),(0x2d,8,8)):
            bank[tile*16:(tile+1)*16]=bytes(sum(((pixels[y+dy][x+dx]>>plane)&1)<<(7-x) for x in range(8)) for plane in range(2) for y in range(8))
        # Two visible bars per cell, with black outlines on the HUD palette.
        meter=[[3 if y in (1,6) or x in (0,3,4,7) else 1 if 1<y<6 else 0 for x in range(8)] for y in range(8)]
        bank[0x2f*16:0x30*16]=bytes(sum(((meter[y][x]>>plane)&1)<<(7-x) for x in range(8)) for plane in range(2) for y in range(8))
        for row in meter:row[4:]=[0]*4
        bank[0x2e*16:0x2f*16]=bytes(sum(((meter[y][x]>>plane)&1)<<(7-x) for x in range(8)) for plane in range(2) for y in range(8))
        hud+=bank
    (ROOT/'chr/characters/inventory-hud.chr').write_bytes(hud)
    for mapper in ('mmc3','mmc5'):
        bg=(ROOT/'chr/mmc5/bg_ground.chr').read_bytes()[2048:4096]
        if mapper=='mmc5':bg=bg[:1024]+(ROOT/'chr/mmc5/sprites_enemies.chr').read_bytes()[2048:3072]
        binary=bytearray()
        for pool in families:
            bank=bytearray(bg)
            for index,data in enumerate(pool):
                if data is not None:bank[1024+free[index]*32:1024+(free[index]+1)*32]=data
            binary+=bank
        (ROOT/f'chr/characters/special-weapons-{mapper}.chr').write_bytes(binary)
        if mapper in overlay_pairs:
            shared=bytearray(binary[-2048:])
            for slot,tile in overlay_pairs[mapper].items():shared[1024+free[slot]*32:1024+(free[slot]+1)*32]=tile
            (ROOT/f'chr/characters/special-remaining-shared-{mapper}.chr').write_bytes(shared)
    path=ROOT/'build/special-weapons';path.mkdir(exist_ok=True)
    (path/'art.json').write_text(json.dumps(dict(families=len(families),frames=lookup),indent=2))
    print('Source weapon art:',len(records),'frames,',len(families),'composite CHR banks')


if __name__=='__main__':main()
