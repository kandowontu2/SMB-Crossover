"""Compose Bass's separate source arm clips and Pharaoh palette layers."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image
import build_megaman_assets as assets
import build_samus_assets as packing
import build_expanded_assets as expanded
from build_special_art import extract
from prepare_crossover import frames

ROOT=assets.ROOT


def main():
    items=list(ET.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item'));symbols={}
    for tag in items:
        if tag.get('type') in ('SymbolClassTag','ExportAssetsTag') and tag.find('tags') is not None:
            symbols.update({n.text:i.text for i,n in zip(tag.find('tags'),tag.find('names'))})
    sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
    sheet=expanded.sheet('BASS')
    mainframes=frames(sprites[symbols['MegaMan']])
    bodies=extract(mainframes[:17],24,sheet)
    arms=extract(frames(sprites[symbols['MegaManArm']]),24,sheet)
    expanded.ROLE='BASS';expanded.COLORS=expanded.targets('BASS')
    records=[]
    for pose in expanded.POSES:
        records.append(('PHARAOH_'+pose,expanded.body('BASS',pose,0),(32,32),True))
    for name,frame,arm in [('THROW',3,2),('AIR_THROW',17,5),('FIST',3,6),('AIR_FIST',16,6),
                           ('CARRY',2,3),('CARRY_STEP',5,3),('CARRY_WALK1',6,3),
                           ('CARRY_WALK2',7,3),('CARRY_WALK3',8,3),('CARRY_JUMP',15,3)]:
        pic=bodies[frame-1].copy()
        placement=next(v for v in mainframes[frame-1]['display'].values() if v.get('characterId')==symbols['MegaManArm'])['matrix']
        pic.alpha_composite(arms[arm-1],tuple(round(float(placement[k])/40) for k in ('translateX','translateY')))
        records.append(('ARM_'+name,pic,(40,16),False))
        records.append(('PHARAOH_ARM_'+name,pic,(40,16),True))
    groups=[];entries=[];lines=['; Source-composed Bass arms and Pharaoh body layers.','.pushseg','.segment "XG_BASS_GFX"']
    packing.RAW_CACHE.clear();assets.SCANLINE_PRIORITY=True
    shared_body_pool=[]
    for name,pic,origin,pharaoh in records:
        def layers(im,projectile=False):
            if not pharaoh:return expanded.layers(im)
            out={p:[[0]*im.width for _ in range(im.height)] for p in (2,3)}
            targets=[((5,5,5),(3,1)),((112,112,112),(2,3)),((248,152,56),(2,2)),
                     ((248,224,160),(3,2)),((255,255,255),(2,2))]
            for y in range(im.height):
                for x in range(im.width):
                    v=im.getpixel((x,y))
                    if v[3]<128:continue
                    _,(p,c)=min(targets,key=lambda q:sum((v[k]-q[0][k])**2 for k in range(3)))
                    out[p][y][x]=c
            return out
        assets.layers=layers
        pool=shared_body_pool[:];parts=packing.parts(pic,origin,pool)
        shared_body_pool=pool[:]
        compact=[]
        for t,p,x,y in parts:
            if pool[t//2] not in compact:compact.append(pool[t//2])
        parts=[(compact.index(pool[t//2])*2,p,x,y)for t,p,x,y in parts];pool=compact
        candidates=[(sum(v not in g for v in pool),i) for i,g in enumerate(groups)
                    if len(g)+sum(v not in g for v in pool)<=32]
        if candidates:index=min(candidates)[1]
        else:index=len(groups);groups.append([])
        for value in pool:
            if value not in groups[index]:groups[index].append(value)
        parts=[(groups[index].index(pool[t//2])*2,p,x,y) for t,p,x,y in parts]
        packing.raw(lines,'SsBass'+name,parts)
        entries.append((name,index))
    logical=list(range(244,256))+list(range(0x72,0x78))+list(range(0x7a,0x80))
    assert len(groups)<=len(logical),('Bass special pose logical CHR budget',len(groups))
    for suffix,fmt in [('LeftLo','<SsBass{}Left'),('LeftHi','>SsBass{}Left'),
                       ('RightLo','<SsBass{}Right'),('RightHi','>SsBass{}Right')]:
        lines += ['SsBass'+suffix+':',' .byte '+','.join(fmt.format(n) for n,_ in entries)]
    lines += ['SsBassBanks:',' .byte '+','.join(str(logical[i]) for _,i in entries),'.popseg']
    (ROOT/'src/bass_special_poses.inc').write_text('\n'.join(lines)+'\n')
    (ROOT/'src/bass_special_pose_ids.inc').write_text('\n'.join('SS_BASS_'+n+'='+str(i) for i,(n,_) in enumerate(entries))+'\n')
    (ROOT/'chr/characters/special-bass-body.chr').write_bytes(b''.join(b''.join(g)+bytes(1024-32*len(g)) for g in groups))
    print('Bass separate arm / Pharaoh body art:',len(entries),'poses,',len(groups),'CHR banks')


if __name__=='__main__':main()
