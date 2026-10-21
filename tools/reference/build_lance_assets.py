"""Pack the pinned 2.02 Lance Bean skin (Bill003), including separate limbs."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
from PIL import Image
import build_megaman_assets as assets
import build_samus_assets as packing
from build_roster_assets import NAMES,choose_groups
from build_special_art import extract
from prepare_crossover import frames

ROOT=assets.ROOT


def main():
    source_root=assets.REF.parents[1]
    items=list(ET.parse(source_root/'reference/crossover2/main.xml').getroot().iter('item'))
    sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
    source=source_root/'reference/crossover2/images/406_com.smbc.graphics.skins.BmdInfo_Bill003.png'
    sheet=Image.open(source).convert('RGBA')
    main=[extract([f],144,sheet)[0] if i<13 or i==16 else Image.new('RGBA',(96,96))
          for i,f in enumerate(frames(sprites['191']))]
    torso=extract(frames(sprites['157']),144,sheet)
    legs=extract(frames(sprites['178']),144,sheet)
    colors=[((0,0,0),(0,3)),((255,206,198),(0,2)),((255,224,168),(0,2)),
            ((0,168,168),(0,1)),((248,56,0),(2,1)),((255,255,255),(2,2))]
    def layers(im,projectile=False):
        out={p:[[0]*im.width for _ in range(im.height)] for p in (0,2)}
        for y in range(im.height):
            for x in range(im.width):
                v=im.getpixel((x,y))
                if v[3]<128:continue
                _,(p,c)=min(colors,key=lambda q:sum((v[k]-q[0][k])**2 for k in range(3)))
                out[p][y][x]=c
        return out
    assets.layers=layers;assets.SCANLINE_PRIORITY=True;packing.RAW_CACHE.clear()
    # Bill's two bullets use the first two pairs in every body bank.
    weapon_count=json.loads((ROOT/'docs/reference/roster-assets.json').read_text())['BILL']['weapon_tile_pairs']
    weapon_data=(ROOT/'chr/characters/crossover-roster-low.chr').read_bytes()[:32*weapon_count]
    reserved=[weapon_data[i:i+32] for i in range(0,len(weapon_data),32)]
    groups=[];records=[];unique={};jobs=[];keys=[]
    lines=['; Lance Bean: Crossover 2.02 Bill003 source skin.','.pushseg','.segment "BILL_GFX"']
    preview=ROOT/'build/lance-frames';preview.mkdir(exist_ok=True)
    maximum=0
    for pose in NAMES:
        if pose.startswith('JUMP'):pic=main[6+int(pose[-1])-1].copy()
        elif pose.startswith('CLIMB'):pic=main[2+int(pose[-1])-1].copy()
        elif pose.startswith('CROUCH'):pic=main[11 if 'ATTACK' in pose or 'THROW' in pose else 10].copy()
        elif pose=='HURT' or pose.startswith('DIE'):pic=main[16 if pose in ('DIE3','DIE4') else 12].copy()
        else:
            pic=Image.new('RGBA',(96,96))
            walking='WALK' in pose
            phase=int(pose[-1]) if walking else 0
            leg=2+phase-1 if walking else 0
            arm=9+phase-1 if walking else 0
            if pose.startswith('UP'):arm=2
            elif pose.startswith('DIAGUP'):arm=4
            elif pose.startswith('DIAGDOWN'):arm=6
            elif pose.startswith('ATTACK'):arm=1
            pic.alpha_composite(legs[leg],(0,-19))
            pic.alpha_composite(torso[arm],(0,-16))
        pic.save(preview/(pose+'.png'))
        pool=[];parts=packing.parts(pic,(40,16),pool)
        maximum=max(maximum,len(parts))
        key=tuple(parts),tuple(pool)
        keys.append(key)
        if key in unique:
            continue
        unique[key]=len(jobs)
        jobs.append((key,'RgLANCE_'+pose,parts,pool))
    packed_jobs=[(name,parts,pool)for key,name,parts,pool in jobs]
    groups,assignment=choose_groups(packed_jobs,[],reserved)
    for n,(key,name,parts,pool)in enumerate(jobs):
        index=assignment[n];parts=[(groups[index].index(pool[t//2])*2,p,x,y)for t,p,x,y in parts]
        packing.raw(lines,name,parts);unique[key]=(name,index)
    records=[unique[key] for key in keys]
    logical=list(range(0x74,0x78))+list(range(0x7a,0x80))
    assert len(groups)<=len(logical),('Lance CHR capacity',len(groups))
    # The port's three power states use the same 2.02 skin silhouette.
    records*=3
    for suffix,fmt in [('LeftLo','<{}Left'),('LeftHi','>{}Left'),('RightLo','<{}Right'),('RightHi','>{}Right')]:
        lines += ['RgLANCE'+suffix+':',' .byte '+','.join(fmt.format(n) for n,_ in records)]
    lines += ['RgLANCEBanks:',' .byte '+','.join(str(logical[i]) for _,i in records),'.popseg']
    (ROOT/'src/lance_metasprites.inc').write_text('\n'.join(lines)+'\n')
    (ROOT/'chr/characters/crossover-lance.chr').write_bytes(b''.join(b''.join(g)+bytes(1024-32*len(g)) for g in groups))
    (ROOT/'docs/reference/lance-assets.json').write_text(json.dumps(dict(source=str(source.relative_to(source_root)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),poses=len(NAMES),maximum_sprites=maximum,chr_banks=len(groups),logical_banks=logical[:len(groups)],palette=[28,54,15],world_palette_pants=True),indent=2)+'\n')
    print('Lance:',len(NAMES),'poses,',len(groups),'CHR banks, maximum',maximum,'sprites')


if __name__=='__main__':main()
