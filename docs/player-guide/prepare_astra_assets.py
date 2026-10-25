"""Read-only authentic-art extraction for the redesigned guide."""
from pathlib import Path
import sys,xml.etree.ElementTree as ET
import hashlib,json,zipfile,re
from PIL import Image,ImageDraw
from prepare_edition_assets import render,RGB,PALS
R=Path(__file__).resolve().parents[2]; H=Path(__file__).parent
O=H/'assets/astra'; O.mkdir(exist_ok=True)
Q=R/'build/verification/player-guide-astra-redesign'; Q.mkdir(parents=True,exist_ok=True)
Z=zipfile.ZipFile(R/'build/checkpoints/parodius-death-nr/source.zip')
assert hashlib.sha256((R/'build/checkpoints/parodius-death-nr/source.zip').read_bytes()).hexdigest()=='81a9912e7001a8c3da3a374ac39ef4b1a2f16812fb2364fa0960dff1b779d2cf'
MAN=[]
def save(im,name,source,detail):
    if im.mode=='RGBA': im=im.crop(im.getbbox())
    p=O/(name+'.png'); im.save(p)
    entry=dict(asset=p.name,source=source,detail=detail,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=im.size)
    origin=R/source.split(' / ')[0]
    if origin.is_file():entry['source_sha256']=hashlib.sha256(origin.read_bytes()).hexdigest()
    elif source.startswith('StarTropics'):
        entry['source_sha256']='f56cf47d4c12502039b04cd6b7248d55fbd1f1fc85411894f310512a7e359be8';entry['source_url']='https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAZE.pdf'
    elif source.startswith('NR '):entry['source_archive_sha256']='81a9912e7001a8c3da3a374ac39ef4b1a2f16812fb2364fa0960dff1b779d2cf'
    MAN.append(entry)
def recs(name):
    out={};label=None
    for line in Z.read(name).decode().splitlines():
        line=line.split(';')[0].strip();m=re.match(r'(\w+):\s*(.*)',line)
        if m:label=m[1];out[label]=[];line=m[2]
        if label and line.startswith('.byte'):
            try:out[label]+=[int(v.strip().replace('$','0x'),0)&255 for v in line[5:].split(',')]
            except ValueError:pass
    return out
raw=Z.read('chr/mmc5/sprites_enemies.chr')
data={2:raw[:1024],3:raw[1024:2048],4:raw[2048:3072]}
# Enemy-facing world art; slot 1 is green, slot 2 red, slot 3 area neutral.
# The old guide used Kirby's pink player slot 0 for three of these records.
enemy=recs('src/kirby_copy_icons.inc')
for i in range(14):
    rec=enemy['KbIcon'+str(i)].copy();pal={**PALS,3:[0x0f,0x36,0x17]}
    if i in (1,2):
        rec=[16,184,1 if i==1 else 2,0,0,146,1 if i==1 else 2,0,8,176,1 if i==1 else 2,16,0,178,1 if i==1 else 2,16,8]
    if i==3:rec=[8,128,3,0,0,130,3,0,8]
    if i in (6,8):
        for k in range(2,len(rec),4):rec[k]=(rec[k]&0xfc)|1
    if i==6:pal[1]=[0x10,0x30,0x27]
    if i==5:pal[3]=[0x0f,0x30,0x10]
    save(render(rec,data,pal),'enemy-'+str(i+1),'NR src/metasprite.s + src/sprite_render.s; chr/mmc5/sprites_enemies.chr','Full native enemy pose and correct world palette, not a Kirby HUD emblem. Grey Cheep/Bloober use underwater neutral palette.')
# Manual illustrations are source art, explicitly captioned as such in the book.
manual=R/'build/mike-kd-private/references'
crops={
 'mike-bat':(20,(212,240,362,373)), 'mike-fire':(20,(700,28,864,199)),
 'mike-sling':(20,(440,267,551,393)), 'mike-bola':(20,(329,440,457,520)),
 'mike-baseball':(20,(37,650,101,715)), 'mike-mirror':(21,(367,23,532,185)),
 'mike-spikes':(21,(68,188,176,318)), 'mike-asterisk':(21,(164,352,286,457)),
 'mike-yoyo':(19,(619,84,730,157)), 'mike-shooting':(19,(719,473,943,588)),
 'mike-star':(22,(851,33,934,111)), 'mike-heart':(22,(716,72,793,136)),
 'mike-bigheart':(22,(833,401,948,509)),
 'mike-batter':(20,(702,346,906,684)), 'mike-kick':(21,(626,180,955,614)),
}
for name,(page,box) in crops.items():
    im=Image.open(manual/f'page-{page}.png').convert('RGB').crop(box)
    save(im,name,f'StarTropics original Nintendo manual p.{page}; CLV-P-NAAZE.pdf',f'Unaltered isolated source illustration crop {box}; not a ROM pickup screenshot.')
sp=R/'reference/parodius-nes/manual-08.png';im=Image.open(sp).convert('RGB').crop((87,228,187,317))
save(im,'pn-white-source','reference/parodius-nes/manual-08.png / original manual p.14','Original clearly identified white Bell illustration. Replaces the old duplicated red/white capture; source illustration, not a cartridge screenshot.')
sp=R/'build/player-guide-agent/little-mac-private/original-boxing-plane/source-40.png';im=Image.open(sp).convert('RGB');glyph=Image.new('RGBA',(11,12))
for y in range(22,34):
    for x in range(16,27):
        if im.getpixel((x,y))==(255,254,255):glyph.putpixel((x-16,y-22),(255,254,255,255))
save(glyph,'mac-star',str(sp.relative_to(R))+' / complete HUD star x16..26 y22..33','Complete original source HUD glyph. Old ROM extraction used x<24 and clipped its right side; this is clearly labeled source art.')
# Distinct actual primary/projectile pixel art, retaining alpha from bitplanes.
jn=recs('src/mike_jones_art.inc');jraw=Z.read('chr/characters/mike-jones.chr')[2048:4096]
for i in [1,2,3,4,5,6,7,8,9,12,13]:
    save(render(jn[f'JnShot{i}_0'],jraw),'mike-shot-'+str(i),'NR src/mike_jones_art.inc / JnShot'+str(i)+'_0','Actual installed projectile sprite; illustrative attack diagrams add labeled paths separately.')
# The kind-3 capture list contains an unverified checkerboard tile. Metadata
# association alone does not identify a visible original-game projectile.
sp=manual/'electronic-08.png'
save(Image.open(sp).convert('RGB').crop((177,342,220,385)),'mike-nova-source',str(sp.relative_to(R))+' / Nintendo electronic manual p.8, Super Nova row','Unaltered explicitly identified Super Nova illustration crop (177,342,220,385); not an installed pickup screenshot. Original manual PDF: CLV-P-NAAZE_en.pdf, SHA256 6b17e8feb4c5c5141bfd7f1ad4ae045e2d46d21f346bae728d58d56eda4f8b15.')
# The original 2.02 colored pickup frames make clearer identification art than
# the host's restricted brown/red palette. Their identity comes from the same
# frame map used by the cartridge's original extraction tool.
sys.path.insert(0,str(R/'tools/reference'))
import build_remaining_art as rem
from prepare_crossover import frames
tags=list(ET.parse(R/'reference/crossover2/main.xml').getroot().iter('item'));symbols={}
for tag in tags:
    if tag.get('type')in('SymbolClassTag','ExportAssetsTag'):
        ids,names=tag.find('tags'),tag.find('names')
        if ids is not None and names is not None:symbols.update({n.text:i.text for i,n in zip(ids,names)})
sprites={i.get('spriteId'):i for i in tags if i.get('type')=='DefineSpriteTag'}
for role in ['Bill','Link','Simon','Ryu','Samus','Sophia']:
    sheetpath=next((R/'reference/crossover2/images').glob('*_'+role+'000.png'))
    sheet=Image.open(sheetpath).convert('RGBA');symbol=role+'Pickup'
    pictures=rem.extract(frames(sprites[symbols[symbol]]),rem.ROLES[role],sheet)
    for p in (H/'assets/edition').glob('av_art_'+role.lower()+'pickup*.png'):
        n=int(p.stem.split('pickup')[1]);im=pictures[n-1]
        save(im,p.stem,str(sheetpath.relative_to(R))+' / '+symbol+' frame '+str(n),'Original 2.02 source pickup art, before host palette quantization. Labelled as source art in guide.')
import build_special_art as spec
sp=R/'reference/crossover2/images/412_com.smbc.graphics.skins.BmdInfo_Bass000.png';sheet=Image.open(sp).convert('RGBA')
pics=spec.extract(frames(sprites[symbols['MegaManPickup']]),24,sheet)
for name,n in [('arm',3),('metal',4),('knuckle',5),('pharaoh',6),('kick',7),('flame',8),('water',13),('rush',10),('balance',1),('energy-large',14),('energy-small',16)]:
    save(pics[n-1],'mm-'+name,str(sp.relative_to(R))+' / MegaManPickup frame '+str(n),'Original 2.02 source pickup art; host palette colors can differ.')
# A clearly recognizable source Jump Slash pose supplements its plain scroll.
sp=R/'reference/crossover2/images/550_com.smbc.graphics.skins.BmdInfo_Ryu000.png';im=Image.open(sp).convert('RGBA').crop((1,97,42,137))
im.putdata([(0,0,0,0)if p[:3]==(111,49,152)else p for p in im.getdata()])
save(im,'ryu-jump-slash',str(sp.relative_to(R))+' / cell (0,2)','Source character attack pose; an ability illustration, not a new pickup.')
(H/'assets/astra-provenance.json').write_text(json.dumps(MAN,indent=2)+'\n')
# Full prior-art inventory for independent visual audit.
files=sorted((H/'assets/edition').glob('*.png'))
for chunk in range(0,len(files),60):
    im=Image.new('RGB',(1000,660),'#17202c');d=ImageDraw.Draw(im)
    for j,p in enumerate(files[chunk:chunk+60]):
        a=Image.open(p).convert('RGBA');s=min(3,86/max(a.size));a=a.resize((round(a.width*s),round(a.height*s)),Image.Resampling.NEAREST)
        x=j%10*100;y=j//10*110;im.paste(a,(x+(100-a.width)//2,y),a);d.text((x+2,y+89),p.stem[:20],fill='white')
    im.save(Q/f'audit-assets-{chunk//60+1}.png')
print('Prepared',len(MAN),'verified replacement assets')
