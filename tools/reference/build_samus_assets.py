"""Convert the pinned Samus frames to native CHR and private pose tables."""
from pathlib import Path
import json
from PIL import Image
import build_megaman_assets as assets

ROOT=assets.ROOT
POSE_FRAMES=[2,3,4,5,6,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34]
POSE_NAMES=['STAND','SHOOT','WALK1','WALK2','WALK3','WALKSHOOT1','WALKSHOOT2','WALKSHOOT3',
 'UPSTAND','UPSHOOT','UPWALK1','UPWALK2','UPWALK3','UPWALKSHOOT1','UPWALKSHOOT2','UPWALKSHOOT3',
 'JUMP','JUMPSHOOT','UPJUMP','UPJUMPSHOOT','FLIP1','FLIP2','FLIP3','FLIP4','SLIDE','CLIMB1','CLIMB2','BALL1','BALL2','BALL3','BALL4']

def samus_layers(image,projectile=False):
    colors=[((0,0,0),(3,1)),((216,40,0),(0,1)),((0,148,0),(0,2)),((252,152,56),(0,3)),
      ((252,196,216),(0,3)),((228,0,88),(0,1)),((0,184,0),(0,2)),((252,196,252),(0,3)),
      ((255,48,31),(0,1)),((63,127,0),(0,2)),((255,144,95),(0,3))]
    result={p:[[0]*image.width for _ in range(image.height)] for p in (0,3)}
    for y in range(image.height):
        for x in range(image.width):
            v=image.getpixel((x,y))
            if v[3]<128:continue
            rgb,(p,c)=min(colors,key=lambda item:sum((v[i]-item[0][i])**2 for i in range(3)))
            result[p][y][x]=c
    return result

def canvas(meta,frame,foot=(48,96),size=(96,128)):
    im=Image.new('RGBA',size)
    im.alpha_composite(assets.sprite_image(meta,frame),(round(foot[0]-meta['origin'][0]),round(foot[1]-meta['origin'][1])))
    return im.resize((size[0]//2,size[1]//2),Image.Resampling.NEAREST)

def flip_tile(data,h,v):
    rows=[[0]*8 for _ in range(16)]
    for y in range(16):
        for x in range(8):
            rows[y][x]=sum(((data[(y//8)*16+p*8+y%8]>>(7-x))&1)<<p for p in range(2))
    return assets.encode_pair([[rows[15-y if v else y][7-x if h else x] for x in range(8)] for y in range(16)])

def parts(image,origin,pool):
    temporary=[];result=[]
    for tile,pal,x,y in assets.parts(image,origin,temporary):
        data=temporary[tile//2]
        data,flags=min((flip_tile(data,h,v),(0x40 if h else 0)|(0x80 if v else 0)) for h,v in ((0,0),(1,0),(0,1),(1,1)))
        if data not in pool:pool.append(data)
        result.append((pool.index(data)*2,pal|flags,x,y))
    return result

RAW_CACHE={}
def raw(lines,name,parts,mirror=True,axis=16,bank='SPRITE_BANK_0'):
    # Private pose tables avoid spending a global 8-bit metasprite ID per pose.
    for facing in (('Left','Right') if mirror else ('Right',)):
        encoded=[]
        for tile,pal,x,y in parts:
            if facing=='Left':x=axis-x-8;pal^=0x40
            encoded.append(f'  .byte MetaspriteVramOffset{{${tile:02x}}}, {{{bank}}}, ${pal:02x}, {y}, {x}')
        key=tuple(encoded)
        label=f'{name}{facing}'
        if key in RAW_CACHE:
            lines.append(f'{label} = {RAW_CACHE[key]}')
        else:
            RAW_CACHE[key]=label
            lines += [label+':',f'  .byte {len(parts)*4}',*encoded]

def main():
    assets.layers=samus_layers
    body=assets.read_meta('1195');beam=assets.read_meta('1239');bomb=assets.read_meta('1226');guts=assets.read_meta('1704')
    pool=[];weapon=[]
    for frame in range(1,7):
        im=canvas(beam,frame,(32,32),(64,64))
        for up in (False,True):
            pic=im.rotate(90) if up else im
            weapon.append((f'SAMUS_BEAM_{frame}'+('_UP' if up else ''),parts(pic,(16,16),pool)))
    for frame in range(1,7):
        weapon.append((f'SAMUS_BOMB_{frame}',parts(canvas(bomb,frame,(32,32),(64,64)),(16,16),pool)))
    if len(pool)>26:raise RuntimeError(f'Common Samus weapons require {len(pool)} pairs; leave room for body poses')
    lines=['; Generated from the pinned hosted Samus sprites; see docs/reference/samus.json.',
      '.pushseg','.segment "SAMUS_GFX"']
    binary=bytearray();names=[];maximum=0;unique=[];banks=[];jobs=[]
    for power in range(3):
        for frame,pose in zip(POSE_FRAMES,POSE_NAMES):
            name=f'SmP{power}_{pose}';names.append(name)
            im=canvas(body,frame+power*35)
            local=[];body_parts=parts(im,(16,16),local)
            maximum=max(maximum,len(body_parts))
            if len(local)>32:raise RuntimeError(f'{name} requires {len(local)} tile pairs')
            jobs.append((name,body_parts,local))
            out=ROOT/f'build/reference-frames/SAMUS-{power}-{pose}.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
    # The 2.02 non-classic controller adds crouching before Morph Ball.
    # Its default-skin frames have the same foot origin as the older body.
    # Keep the original 31-pose stride stable for lives/power-up tables.
    import xml.etree.ElementTree as ET
    from prepare_crossover import frames
    from build_remaining_art import extract
    items=list(ET.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item'))
    timeline=next(i for i in items if i.get('type')=='DefineSpriteTag' and i.get('spriteId')=='28')
    sheet=Image.open(next((ROOT/'reference/crossover2/images').glob('*_Samus000.png'))).convert('RGBA')
    crouch_frames=extract(frames(timeline),27,sheet)
    # Suitless is a separate source skin, not a recolored armored crouch.
    # It uses the same timeline/masks and foot origin as the default skin.
    suitless_sheet=Image.open(next((ROOT/'reference/crossover2/images').glob('*_Samus003.png'))).convert('RGBA')
    suitless_crouch=extract(frames(timeline),27,suitless_sheet)
    crouch_names=[]
    for power in range(3):
        for frame,pose in ((31,'CROUCH'),(32,'CROUCHSHOOT')):
            name=f'SmP{power}_{pose}';crouch_names.append(name)
            pictures=suitless_crouch if power==2 else crouch_frames
            im=Image.new('RGBA',(48,64));im.alpha_composite(pictures[frame-1],(-24,0))
            if power==2:
                # Match the established suitless body's green hair/gun role
                # in the legacy three-state NES palette (2.02 uses brown).
                im.putdata([(0,184,0,p[3]) if p[:3]==(200,76,12) else p for p in im.getdata()])
            local=[];body_parts=parts(im,(16,16),local)
            maximum=max(maximum,len(body_parts));jobs.append((name,body_parts,local))
            im.save(ROOT/f'build/reference-frames/SAMUS-{power}-{pose}.png')
    groups=[];records={}
    for name,body_parts,local in sorted(jobs,key=lambda j:-len(j[2])):
        choices=[(sum(v not in g for v in local),i) for i,g in enumerate(groups)
                 if len(g)+sum(v not in g for v in local)<=32]
        if choices:index=min(choices)[1]
        else:index=len(groups);groups.append([])
        for value in local:
            if value not in groups[index]:groups[index].append(value)
        records[name]=(index,[(groups[index].index(local[t//2])*2,p,x,y) for t,p,x,y in body_parts])
    unique=[b''.join(g)+bytes(1024-len(g)*32) for g in groups]
    # The suitless crouch needs one additional body bank. Use the otherwise
    # blank logical $80 slot rather than moving the established death banks
    # at $a3..$a6 into Scrooge's reserved $a7 slot.
    assert len(unique)<=19, 'Samus body exceeds its18 original +1 auxiliary banks'
    def body_bank(index):return 0x91+index if index<18 else 0x80
    for name,_,_ in jobs:
        index,body_parts=records[name]
        if name in names:banks.append(body_bank(index))
        raw(lines,name,body_parts)
    binary=bytearray(b''.join(unique[:18]))
    (ROOT/'chr/characters/samus-extra-body.chr').write_bytes(b''.join(unique[18:]))
    lines += ['SamusPoseBanks:','  .byte '+','.join(f'${n:02x}' for n in banks),
      # Pointer arrays are read by SamusGraphics in the SAMUS A000 bank.
      # Moving these 372 bytes frees room in the tight C000 graphics bank
      # for the two native crouch poses without adding any CHR banks.
      '.segment "SAMUS"',
      'SamusPoseLeftLo:','  .byte '+','.join('<'+n+'Left' for n in names),
      'SamusPoseLeftHi:','  .byte '+','.join('>'+n+'Left' for n in names),
      'SamusPoseRightLo:','  .byte '+','.join('<'+n+'Right' for n in names),
      'SamusPoseRightHi:','  .byte '+','.join('>'+n+'Right' for n in names),
      'SamusCrouchBanks:','  .byte '+','.join(f'${body_bank(records[n][0]):02x}' for n in crouch_names),
      'SamusCrouchLeftLo:','  .byte '+','.join('<'+n+'Left' for n in crouch_names),
      'SamusCrouchLeftHi:','  .byte '+','.join('>'+n+'Left' for n in crouch_names),
      'SamusCrouchRightLo:','  .byte '+','.join('<'+n+'Right' for n in crouch_names),
      'SamusCrouchRightHi:','  .byte '+','.join('>'+n+'Right' for n in crouch_names),
      '.segment "SAMUS_GFX"']
    lines += ['MetaspriteData "SAMUS_BODY", SmP0_STANDLeft, SmP0_STANDRight']
    free=[i for i in range(32) if i not in {2,3,4,5,6,7,8,9,10,11,12,16,17,18,19,20,22,23,24,26}]
    families=[];weapon_families=[]
    for name,weapon_parts in weapon:
        tiles=list(dict.fromkeys(pool[t//2] for t,_,_,_ in weapon_parts))
        choices=[(sum(v not in g for v in tiles),i) for i,g in enumerate(families)
                 if len(g)+sum(v not in g for v in tiles)<=len(free)]
        if choices:index=min(choices)[1]
        else:index=len(families);families.append([])
        for value in tiles:
            if value not in families[index]:families[index].append(value)
        weapon_families.append(index)
        weapon_parts=[(free[families[index].index(pool[t//2])]*2,p,x,y) for t,p,x,y in weapon_parts]
        lines += [f'MetaspriteData "{name}", Sm{name}Left, Sm{name}Right']
        raw(lines,'Sm'+name,weapon_parts,axis=0,bank='SPRITE_BANK_4')
    lines += ['SamusWeaponFamilies:',' .byte '+','.join(map(str,weapon_families))]
    for mapper in ('mmc3','mmc5'):
        bg=(ROOT/'chr/mmc5/bg_ground.chr').read_bytes()[2048:4096]
        if mapper=='mmc5':bg=bg[:1024]+(ROOT/'chr/mmc5/sprites_enemies.chr').read_bytes()[2048:3072]
        art=bytearray()
        for group in families:
            bank=bytearray(bg)
            for index,value in enumerate(group):bank[1024+free[index]*32:1024+(free[index]+1)*32]=value
            art+=bank
        (ROOT/f'chr/characters/samus-weapons-{mapper}.chr').write_bytes(art)
    gut_names=[]
    for phase in range(4):
        gut_pool=[]
        for part in range(6):
            name=f'SmGuts{phase}_{part}';gut_names.append(name)
            im=canvas(guts,1+part*4+phase,(16,16),(32,32))
            raw(lines,name,parts(im,(8,8),gut_pool),False,axis=0)
        assert len(gut_pool)<=32
        binary+=b''.join(gut_pool)+bytes(1024-len(gut_pool)*32)
    lines += ['SamusGutsLo:','  .byte '+','.join('<'+n+'Right' for n in gut_names),
      'SamusGutsHi:','  .byte '+','.join('>'+n+'Right' for n in gut_names),'.popseg',
      'SAMUS_CHR_FIRST = $91',f'SAMUS_CHR_DEATH = ${0x91+min(len(unique),18):02x}',
      f'SAMUS_CHR_END = ${0x91+min(len(unique),18)+4:02x}',
      f'SAMUS_POSE_COUNT = {len(POSE_NAMES)}',f'SAMUS_MAX_SPRITES = {maximum}']
    for i,name in enumerate(POSE_NAMES):lines.append(f'SM_POSE_{name} = {i}')
    lines += ['SM_POSE_CROUCH = 31','SM_POSE_CROUCHSHOOT = 32']
    (ROOT/'src/samus_metasprites.inc').write_text('\n'.join(lines)+'\n')
    (ROOT/'chr/characters/crossover-samus.chr').write_bytes(binary+bytes(65536-len(binary)))
    assert 0x91*1024+len(binary)<=256*1024
    print(f'Samus: {len(names)} poses, {len(pool)} common weapon pairs, max {maximum} sprites, {len(binary)} CHR bytes')

if __name__=='__main__':main()
