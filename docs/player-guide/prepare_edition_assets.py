"""Read-only extraction of authentic installed pixels for the player guide.

Does not generate/repack any game asset. All pictures retain nearest-neighbor
pixels; small catalogue images are decoded from installed metasprite records.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).parent
OUT=HERE/'assets/edition';OUT.mkdir(parents=True,exist_ok=True)
QA=ROOT/'build/verification/player-guide-nq-refresh-2026-10-24';QA.mkdir(parents=True,exist_ok=True)
PIN='c5f15fcd1bca72ca6a0787782f010342dbea99df8391c57a305be1addca8bf2e'
PIN_ZIP='7eb24307588d0935e1b63d961ccc4da154e3f92fa3d7eeec375286dba9e3e005'
MAN=[]
RGB=[(84,84,84),(0,30,116),(8,16,144),(48,0,136),(68,0,100),(92,0,48),(84,4,0),(60,24,0),(32,42,0),(8,58,0),(0,64,0),(0,60,0),(0,50,60),(0,0,0),(0,0,0),(0,0,0),(152,150,152),(8,76,196),(48,50,236),(92,30,228),(136,20,176),(160,20,100),(152,34,32),(120,60,0),(84,90,0),(40,114,0),(8,124,0),(0,118,40),(0,102,120),(0,0,0),(0,0,0),(0,0,0),(236,238,236),(76,154,236),(120,124,236),(176,98,236),(228,84,236),(236,88,180),(236,106,100),(212,136,32),(160,170,0),(116,196,0),(76,208,32),(56,204,108),(56,180,204),(60,60,60),(0,0,0),(0,0,0),(236,238,236),(168,204,236),(188,188,236),(212,178,236),(236,174,236),(236,174,212),(236,180,176),(228,196,144),(204,210,120),(180,222,120),(168,226,144),(152,226,180),(160,214,228),(160,162,160),(0,0,0),(0,0,0)]
PALS={0:[0x0f,0x30,0x17],1:[0x1a,0x30,0x27],2:[0x16,0x30,0x27],3:[0x0f,0x37,0x17]}
def save(im,key,source,details):
    bbox=im.getbbox();assert bbox,(key,'empty');im=im.crop(bbox)
    p=OUT/(key+'.png');im.save(p)
    sp=ROOT/source.split(' :: ')[0]
    MAN.append(dict(asset=p.name,source=source,source_sha256=hashlib.sha256(sp.read_bytes()).hexdigest() if sp.is_file() else None,details=details,width=im.width,height=im.height,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    return key
def number(x):
    x=x.strip();return int(x[1:],16) if x.startswith('$') else int(x)
def records(path):
    txt=path.read_text();out={};label=None
    for line in txt.splitlines():
        s=line.split(';')[0].strip()
        if not s:continue
        m=re.match(r'(\w+):\s*(.*)',s)
        if m:label=m[1];out[label]=[];s=m[2]
        if not s.startswith('.byte') or label is None:continue
        if any(c in s for c in '<>"'):continue
        s=s[5:].strip()
        s=re.sub(r'MetaspriteVramOffset\{(\$[0-9a-fA-F]+)\},\s*\{SPRITE_BANK_(\d)\}',lambda m:str((number(m[1])&63)|((int(m[2])%4)*64)|(int(m[2])//4)),s)
        try:out[label]+= [number(x)&255 for x in s.split(',')]
        except ValueError:pass
    return out
def table(path,label):
    t=path.read_text();part=t.split(label+':',1)[1].split('\n',2)
    line=next(v for v in part if '.byte' in v)
    return [number(v) for v in line.split('.byte')[1].split(',')]
def render(rec,chrdata,pals=None):
    pals=pals or PALS;assert rec and len(rec)>=rec[0]+1,(len(rec),rec[:10]);im=Image.new('RGBA',(128,128))
    for n in range(rec[0]-3,0,-4):
        tile,attr,dy,dx=rec[n:n+4];dx=dx-256 if dx>=128 else dx;dy=dy-256 if dy>=128 else dy
        # caller supplies the selected 1K/2K sprite window, normalized to0.
        start=(tile&62)*16
        selected=chrdata
        if isinstance(chrdata,dict):selected=chrdata[((tile&1)*4)+(tile>>6)]
        elif len(chrdata)>=2048:start=(tile&126)*16
        for y in range(16):
            yy=15-y if attr&128 else y;raw=selected[start+(yy//8)*16:start+(yy//8+1)*16]
            assert len(raw)==16,(tile,start,len(selected))
            for x in range(8):
                xx=x if attr&64 else 7-x;color=((raw[yy%8]>>xx)&1)|(((raw[yy%8+8]>>xx)&1)<<1)
                if color:im.putpixel((64+dx+x,64+dy+y),(*RGB[pals[attr&3][color-1]],255))
    return im
def extract(key,path,label,data,pals=None,detail='Installed NES pixels; a static animation phase. Shared icon shapes are identified in the legend.'):
    save(render(records(ROOT/path)[label],data,pals),key,path+' :: '+label,detail)
def main():
    archive=ROOT/'build/checkpoints/parodius-render-nq/source.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==PIN_ZIP
    with zipfile.ZipFile(archive) as z:
        # Refuse to mix current mutable artwork into the pinned preview edition.
        for n in z.namelist():
            if n.startswith('chr/characters/') and n.endswith('.chr') or n.startswith('src/') and (n.endswith('_art.inc') or n.endswith('_art_ids.inc') or n in ['src/metasprite.s','src/vic_hud.inc','src/kirby_copy_icons.inc']):
                assert (ROOT/n).read_bytes()==z.read(n),n
    for folder,key in [('entry-v3','rom_sha256'),('pickups-v3','ROM_sha256')]:
        p=ROOT/f'build/verification/parodius-render-nq/{folder}/results.json'
        assert json.loads(p.read_text())[key]==PIN
    MAN.append(dict(reference_checkpoint='build/checkpoints/parodius-render-nq',rom_sha256=PIN,source_zip_sha256=PIN_ZIP,scope='Current preview captures and matched source assets; older field screenshots retain their original source.'))
    entry=ROOT/'build/verification/parodius-render-nq/entry-v3'
    raise RuntimeError('Historical decoder: use prepare_assets.py; color-key portraits have been retired.')
    shutil.copy2(entry/'mario/build/verification/selection.png',OUT/'character-select.png')
    # Current completed-world example art; older screenshots are labeled as field views.
    for name in ['mario-first-pipes','mario-gap-course','mario-underground-lifts','bass-firebars','mario-water-coral']:
        shutil.copy2(HERE/'assets'/f'{name}.png',OUT/(name+'.png'))
    # Source-derived original6 / later-guest inventory icons.
    sp=ROOT/'src/special_art.inc';families=table(sp,'SsArtFamilies');raw=(ROOT/'chr/characters/special-weapons-mmc5.chr').read_bytes()
    ids={m[1]:int(m[2]) for m in re.finditer(r'(SS_ART_\w+)\s*=\s*(\d+)',(ROOT/'src/special_art_ids.inc').read_text())}
    for name,i in [('arm',3),('metal',4),('knuckle',5),('pharaoh',6),('kick',7),('flame',8),('water',13),('rush',10),('balance',1),('energy-large',14),('energy-small',16)]:
        ident=ids['SS_ART_PICKUP'+str(i)];f=families[ident];extract('mm-'+name,'src/special_art.inc',f'SsArt{ident}Right',raw[f*2048+1024:(f+1)*2048])
    av=ROOT/'src/remaining_art.inc';fam=table(av,'AvArtFamilies')
    aids={m[1]:int(m[2]) for m in re.finditer(r'(AV_ART_\w+)\s*=\s*(\d+)',(ROOT/'src/remaining_art_ids.inc').read_text())}
    ar=(ROOT/'chr/characters/samus-remaining-shared-mmc5.chr').read_bytes()+(ROOT/'chr/characters/special-remaining-shared-mmc5.chr').read_bytes()+(ROOT/'chr/characters/remaining-weapons-mmc5.chr').read_bytes()
    for label,ident in aids.items():
        if 'PICKUP' not in label:continue
        f=fam[ident];extract(label.lower(),'src/remaining_art.inc',f'AvArt{ident}Right',ar[f*2048+1024:(f+1)*2048])
    # SMB3 original forms; both palette layers are the installed world layers.
    data=(ROOT/'chr/characters/smb3-mario.chr').read_bytes()[20*1024:21*1024]
    for i in range(1,7):extract('smb3-'+str(i),'src/smb3_mario_world_art.inc','M3Item'+str(i),data)
    # Mike uses actual source item shapes; several share the original same icon.
    data=(ROOT/'chr/characters/mike-jones.chr').read_bytes()[2048:4096]
    for i in range(1,14):extract('mike-'+str(i),'src/mike_jones_art.inc','JnItem'+str(i),data)
    for name in ['Heart','Star','BigHeart']:extract('mike-'+name.lower(),'src/mike_jones_art.inc','Jn'+name,data)
    data=(ROOT/'chr/characters/little-mac.chr').read_bytes()[(704-668)*1024:(705-668)*1024]
    extract('mac-star','src/little_mac_art.inc','LmStar',data,{**PALS,0:[0x36,0x0f,0x25]})
    data=(ROOT/'chr/characters/zelda2-link-items.chr').read_bytes()
    zp={**PALS,1:[0x0f,0x16,0x30]}
    for name in ['MAGIC','SWORD','FAIRY','HEART','FIRE','GLOVE','BLUE','RED','BAG']:extract('z2-'+name.lower(),'src/zelda2_link_items.inc','Z2Item'+name,data,zp)
    # Darkwing private world-item window and actual native records.
    data=(ROOT/'chr/characters/darkwing.chr').read_bytes()[(302-276)*1024:(304-276)*1024]
    dp={**PALS,0:[0x13,0x30,0x27]}
    for i in [0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29]:extract('dw-'+f'{i:x}','src/darkwing_art.inc',f'DwW{i:02X}F0R',data,dp)
    # Kirby HUD copy emblems are installed game graphics, not new drawings.
    native=(ROOT/'chr/mmc5/sprites_enemies.chr').read_bytes();misc=(ROOT/'chr/mmc5/sprites_misc.chr').read_bytes()
    data={2:native[:1024],3:native[1024:2048],4:native[2048:3072]};kp={**PALS,0:[0x35,0x25,0x0f]}
    for i in range(14):extract('kirby-copy-'+str(i+1),'src/kirby_copy_icons.inc','KbIcon'+str(i),data,kp,detail='Actual installed copy HUD emblem. This is an ability emblem, not an item dropped by a block.')
    # Roll's health circles are the installed supplied-mobile shapes.
    md=json.loads((ROOT/'reference/roll-mobile/art.json').read_text());MAN.append({'reference_metadata':'reference/roll-mobile/art.json','sha256':hashlib.sha256((ROOT/'reference/roll-mobile/art.json').read_bytes()).hexdigest()})
    roll=(ROOT/'chr/characters/roll.chr').read_bytes()[3072:4096]
    rp={**PALS,0:[0x1a,0x28,0x24]}
    for key,i in [('health-small',1),('health-large',4),('energy-small',5),('energy-large',6)]:extract('roll-'+key,'src/roll_art.inc','RlShot'+str(i),roll,rp)
    # Source projectile illustrations for CV3 block rewards (the game uses these,
    # rather than inventing a distinct inventory icon for every spell).
    cv=(ROOT/'chr/characters/cv3.chr').read_bytes()
    for variant,labels in [(1,['27','23','40','07']),(2,['1F','23','27','07']),(3,['22','07'])]:
        dat=cv[(518-460+(variant-1)*2)*1024:(520-460+(variant-1)*2)*1024]
        cvpal={**PALS,0:[0x16,0x27,0x30]}
        for p in labels:extract(f'cv{variant}-{p.lower()}','src/cv3_art.inc',f'Cv3W{variant}P{p}R',dat,cvpal)
    # Actual uploaded Parodius pickup screenshots, cropped to the known isolated
    # actor. Screenshot provenance has exact candidate/CHR/OAM evidence nearby.
    pn=ROOT/'build/verification/parodius-render-nq/pickups-v3/1/build/verification'
    for key,frame in [('gold',241),('red',243),('blue',245),('white',247),('big',249)]:
        im=Image.open(pn/f'pose-{frame}.png').convert('RGBA').crop((168,90,212,135));bg=im.getpixel((0,0))
        im.putdata([(0,0,0,0) if px==bg else px for px in im.getdata()])
        save(im,'pn-'+key,str((pn/f'pose-{frame}.png').relative_to(ROOT)),'Actual isolated native pickup screenshot, complete bounds; uniform sky made transparent. No tile repaint.')
    combined=Image.new('RGBA',(24,28))
    for variant in [1,2,3]:
        src=ROOT/f'build/verification/parodius-render-nq/pickups-v3/{variant}/build/verification/pose-241.png'
        im=Image.open(src).convert('RGBA').crop((208,8,232,16));bg=im.getpixel((0,0));im.putdata([(0,0,0,0)if px==bg else px for px in im.getdata()]);combined.alpha_composite(im,(0,(variant-1)*10))
        if variant==1:
            reset=Image.open(src).convert('RGBA').crop((176,8,200,16));bg=reset.getpixel((0,0));reset.putdata([(0,0,0,0)if px==bg else px for px in reset.getdata()]);save(reset,'pn-bar-reset',str(src.relative_to(ROOT)),'Actual printed Parodius reset cell from the live HUD, not the blank Gradius frame.')
    save(combined,'pn-bar-defenses','build/verification/parodius-render-nq/pickups-v3/{1,2,3}/build/verification/pose-241.png','Actual OTR/FLD/BUB defense labels, stacked without repainting. Top Octopus, middle TwinBee, bottom Pentarou.')
    extract('vic-capsule','src/vic_art.inc','VvPose16',(ROOT/'chr/characters/vic-viper.chr').read_bytes()[:1024],{**PALS,0:[0x0c,0x26,0x2c]})
    data=(ROOT/'chr/characters/vic-viper.chr').read_bytes()[(394-380)*1024:(395-380)*1024]
    cells=records(ROOT/'src/vic_hud.inc')['VvHudCells']
    for n in range(7):
        im=Image.new('RGBA',(32,8))
        for j,tile in enumerate(cells[n*4:n*4+4]):
            raw=data[tile*16:tile*16+16]
            for y in range(8):
                for x in range(8):
                    v=((raw[y]>>(7-x))&1)|(((raw[y+8]>>(7-x))&1)<<1)
                    if v:im.putpixel((j*8+x,y),(255,255,255,255))
        save(im,'vic-bar-'+str(n+1),'src/vic_hud.inc :: VvHudCells / chr/characters/vic-viper.chr','Actual in-game power-bar label. Equipment is purchased from this cell, not collected as a separate dropped icon.')
    # Shared native mushroom, flower, star and1up from installed original source records.
    m3=records(ROOT/'src/smb3_mario_world_art.inc')
    misc=(ROOT/'chr/mmc5/sprites_misc.chr').read_bytes()
    for key,rec in [('mushroom',[8,60,2,0,0,62,2,0,8]),('1up',[8,60,1,0,0,62,1,0,8]),('star',[8,52,0,0,0,54,0,0,8]),('flower',[16,56,0,0,0,56,64,0,8,58,1,16,0,58,65,16,8])]:
        save(render(rec,misc),key,'src/metasprite.s :: POWERUP / chr/mmc5/sprites_misc.chr','Actual native SMB item tiles/attributes. Animated color phase shown; the effect depends on the selected character.')
    (HERE/'assets/edition-provenance.json').write_text(json.dumps(MAN,indent=2)+'\n')
    files=sorted(OUT.glob('*.png'));sheet=Image.new('RGB',(900,((len(files)+9)//10)*95),'#101e2b');dr=ImageDraw.Draw(sheet)
    for i,p in enumerate(files):
        im=Image.open(p).convert('RGBA');scale=min(3,64/max(im.size));im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.NEAREST)
        x=(i%10)*90;y=(i//10)*95;sheet.paste(im,(x+(90-im.width)//2,y),im);dr.text((x+2,y+65),p.stem[:18],fill='white')
    sheet.save(QA/'assets-contact.png');print('Assets',len(files),'provenance',len(MAN))
if __name__=='__main__':main()
