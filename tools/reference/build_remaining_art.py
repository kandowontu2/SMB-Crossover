"""Extract remaining 2.02 weapons and pickups from their original SWF matrices.

One stable world palette per piece keeps icons independent of player colors.
Hardware palettes are recorded rather than changing the native enemy palettes.
"""
from pathlib import Path
import sys,json,xml.etree.ElementTree as ET
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_megaman_assets as assets
import build_samus_assets as packing
from prepare_crossover import frames
ROOT=assets.ROOT
ROLES={'Bill':144,'Link':30,'Simon':80,'Ryu':36,'Samus':27,'Sophia':44}
PALS={0:[(228,0,88),(255,255,255),(0,0,0)],2:[(216,40,0),(252,252,252),(252,152,56)],3:[(0,0,0),(252,216,168),(164,80,0)]}

def extract(timeline,bitmap,sheet):
    result=[]
    for frame in timeline:
        canvas=Image.new('RGBA',(96,96))
        entries=sorted(frame['display'].items(),key=lambda p:int(p[0]))
        for index,(_,value) in enumerate(entries):
            if value.get('characterId')!=str(bitmap):continue
            mask=next((v for _,v in entries[index+1:] if v.get('characterId')=='18'),None)
            if mask is None:continue
            m=value['matrix'];mm=mask['matrix']
            tx,ty=(float(m.get(k,0))/40 for k in ('translateX','translateY'))
            a,d=(float(m.get(k,1))for k in ('scaleX','scaleY'))
            b,c=(float(m.get(k,0))for k in ('rotateSkew0','rotateSkew1'))
            det=a*d-b*c
            mx,my=(float(mm.get(k,0))/40 for k in ('translateX','translateY'))
            w,h=(float(mm.get(k,1))/2 for k in ('scaleX','scaleY'))
            left,right=sorted((mx,mx+w));top,bottom=sorted((my,my+h))
            for y in range(max(0,round(48+top)),min(96,round(48+bottom))):
                for x in range(max(0,round(48+left)),min(96,round(48+right))):
                    wx,wy=x+0.5-48-tx,y+0.5-48-ty
                    sx,sy=int((d*wx-c*wy)/det),int((-b*wx+a*wy)/det)
                    if not(0<=sx<sheet.width and 0<=sy<sheet.height):continue
                    p=sheet.getpixel((sx,sy))
                    if p[3] and p[:3]!=(111,49,152):canvas.putpixel((x,y),p)
        result.append(canvas)
    return result

def flipped(tile,flags):
    rows=[list(tile[i:i+8])for i in (0,8,16,24)]
    if flags&64:rows=[[int(f'{v:08b}'[::-1],2)for v in r]for r in rows]
    if flags&128:rows=[rows[2][::-1],rows[3][::-1],rows[0][::-1],rows[1][::-1]]
    return bytes(v for r in rows for v in r)

def main():
    items=list(ET.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item'));symbols={}
    for t in items:
        if t.get('type') in ('SymbolClassTag','ExportAssetsTag'):
            ids=t.find('tags');names=t.find('names')
            if ids is not None and names is not None:symbols.update({n.text:i.text for i,n in zip(ids,names)})
    sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
    groups=[('Bill','BillBullet',[4,5]),('Link','LinkProjectile',[5,*range(6,22),23]),
            ('Simon','SimonProjectile',list(range(5,19))),
            ('Ryu','RyuProjectile',list(range(9,17))),('Samus','SamusShot',[3,7]),
            ('Sophia','SophiaBullet',[4,5,6,7])]
    groups += [(role,role+'Pickup',list(range(1,{'Bill':10,'Link':12,'Simon':11,'Ryu':10,'Samus':11,'Sophia':13}[role]+1))) for role in ROLES]
    # Frames not obtainable in this 2.02 build are excluded, matching its upgrade arrays.
    excluded={'LinkPickup':{1,4,5,11,12},'RyuPickup':{6},'SamusPickup':{2,6,8,9},'SophiaPickup':{1,8,11,12,13},'BillPickup':{1,3,5,7,9},'SimonPickup':{9}}
    free=[0,1,13,14,15,21,25,27,28,29,30,31]
    # The final native Samus family has spare pairs. Share them without moving
    # her existing tile slots, avoiding another complete 2 KiB MMC3 window.
    native=(ROOT/'chr/characters/samus-weapons-mmc3.chr').read_bytes()[-2048:]
    native_bg=(ROOT/'chr/mmc5/bg_ground.chr').read_bytes()[2048:4096]
    occupied=[i for i,n in enumerate(free) if native[1024+n*32:1024+(n+1)*32]!=native_bg[1024+n*32:1024+(n+1)*32]]
    assert occupied==list(range(len(occupied))),occupied
    families=[[native[1024+n*32:1024+(n+1)*32]for n in free[:len(occupied)]]]
    native_mm=(ROOT/'chr/characters/special-weapons-mmc3.chr').read_bytes()[-2048:]
    mm_occupied=[i for i,n in enumerate(free)if native_mm[1024+n*32:1024+(n+1)*32]!=native_bg[1024+n*32:1024+(n+1)*32]]
    assert mm_occupied==list(range(len(mm_occupied))),mm_occupied
    families.append([native_mm[1024+n*32:1024+(n+1)*32]for n in free[:len(mm_occupied)]])
    records=[('EMPTY',0,[])];manifest={}
    original_count=None;effect_family_start=None
    groups.append(('Sophia','SophiaExplosion',list(range(8,14))))
    for role,symbol,indices in groups:
        if symbol=='SophiaExplosion':
            original_count=len(records);effect_family_start=len(families)
        sheet=Image.open(next((ROOT/'reference/crossover2/images').glob('*_'+role+'000.png'))).convert('RGBA')
        pictures=extract(frames(sprites[symbols[symbol]]),ROLES[role],sheet)
        for frame in indices:
            if frame in excluded.get(symbol,set()):continue
            im=pictures[frame-1]
            pixels=[p for p in im.getdata() if p[3]>=128]
            assert pixels or (symbol=='SophiaExplosion' and frame==9),(symbol,frame)
            palette_choices=[0] if symbol=='SophiaExplosion' else [2,3]
            pal=min(palette_choices,key=lambda p:sum(min(sum((v[k]-c[k])**2 for k in range(3)) for c in PALS[p]) for v in pixels))
            def layers(pic,projectile=False):
                out={pal:[[0]*pic.width for _ in range(pic.height)]}
                for y in range(pic.height):
                    for x in range(pic.width):
                        v=pic.getpixel((x,y))
                        if v[3]>=128:out[pal][y][x]=1+min(range(3),key=lambda c:sum((v[k]-PALS[pal][c][k])**2 for k in range(3)))
                return out
            assets.layers=layers
            raw=[];parts=packing.parts(im,(48,48),raw)
            folded=[];remap={}
            for n,tile in enumerate(raw):
                canonical,flags=min((flipped(tile,f),f)for f in(0,64,128,192))
                if canonical not in folded:folded.append(canonical)
                remap[n]=(folded.index(canonical),flags)
            parts=[(remap[t//2][0]*2,p^remap[t//2][1],x,y)for t,p,x,y in parts]
            raw=folded
            choices=[]
            for bank,pool in enumerate(families):
                if symbol=='SophiaExplosion' and bank<effect_family_start:continue
                candidate=pool+[v for v in raw if v not in pool]
                if len(candidate)<=12:choices.append((len(candidate)-len(pool),bank,candidate))
            if choices:_,bank,candidate=min(choices)
            else:bank=len(families);families.append([]);candidate=raw[:]
            assert len(candidate)<=12,(symbol,frame,len(candidate))
            families[bank][:]=candidate
            parts=[(free[candidate.index(raw[t//2])]*2,p,x,y) for t,p,x,y in parts]
            name=f'{symbol.upper()}{frame}';manifest[name]=len(records)
            records.append((name,bank,parts))
    lines=['; Source 2.02 SWF weapon/pickup frames.','.pushseg','.segment "LINK_GFX"']
    for i,(name,bank,parts) in enumerate(records):
        # Spread pointer data across the free portions of the two graphics banks.
        if i==original_count//2:lines.append('.segment "SIMON_GFX"')
        for side in ('Right','Left'):
            lines += [f'AvArt{i}{side}:',f' .byte {len(parts)*4}']
            for tile,pal,x,y in parts:
                if side=='Left':x=-x-8;pal^=64
                lines.append(f' .byte MetaspriteVramOffset{{${tile:02x}}}, {{SPRITE_BANK_4}}, ${pal:02x}, {y}, {x}')
    lines.append('.segment "SPECIAL_ROSTER"')
    for side in ('Right','Left'):
        for suffix,op in (('Lo','<'),('Hi','>')):
            lines += [f'AvArt{side}{suffix}:',' .byte '+','.join(op+f'AvArt{i}{side}' for i in range(len(records)))]
    lines += ['AvArtBanks:',' .byte '+','.join(f'.bank(AvArt{i}Right)' for i in range(len(records))),
              'AvArtFamilies:',' .byte '+','.join(str(r[1])for r in records),'.popseg']
    (ROOT/'src/remaining_art.inc').write_text('\n'.join(lines)+'\n')
    (ROOT/'src/remaining_art_ids.inc').write_text('\n'.join(f'AV_ART_{name}={i}' for i,(name,_,_) in enumerate(records))+'\n')
    for mapper in ('mmc3','mmc5'):
        bg=(ROOT/'chr/mmc5/bg_ground.chr').read_bytes()[2048:4096]
        if mapper=='mmc5':bg=bg[:1024]+(ROOT/'chr/mmc5/sprites_enemies.chr').read_bytes()[2048:3072]
        binary=bytearray()
        for index,pool in enumerate(families):
            bank=bytearray(bg)
            for index,data in enumerate(pool):bank[1024+free[index]*32:1024+(free[index]+1)*32]=data
            binary+=bank
        (ROOT/f'chr/characters/samus-remaining-shared-{mapper}.chr').write_bytes(binary[:2048])
        (ROOT/f'chr/characters/special-remaining-shared-{mapper}.chr').write_bytes(binary[2048:4096])
        (ROOT/f'chr/characters/remaining-weapons-{mapper}.chr').write_bytes(binary[4096:])
    (ROOT/'build/remaining-art.json').write_text(json.dumps({'families':len(families),'frames':manifest,'palettes':PALS},indent=2)+'\n')
    print('Remaining source artwork:',len(records),'frames,',len(families)-2,'new families + two shared families')

if __name__=='__main__':main()
