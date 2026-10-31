"""One individually pictured and named tile for every compiled menu identity."""
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[2]
OUT=R/'docs/images/SMB-Crossover-Full-Roster.png'
FONTS=Path('C:/Windows/Fonts')
def font(n,bold=False):return ImageFont.truetype(str(FONTS/('arialbd.ttf' if bold else 'arial.ttf')),n)

def cut(path,box):
    im=Image.open(path).convert('RGBA').crop(box)
    bg=im.getpixel((0,0))[:3]
    im.putdata([(0,0,0,0) if p[:3]==bg else p for p in im.getdata()])
    return im.crop(im.getbbox())

def main():
    rows=json.loads((R/'build/arthur-quick-functional-admission-v1/actual-menu-readiness.json').read_text())['rows']
    names=[]
    for row in rows:
        label=''.join(' ' if v==36 else str(v) if v<10 else chr(v+55) if v<36 else '*' for v in row['name_packets'][0]['data']).strip().lstrip('*')
        names.append((label,row['variant']>0))
    arts={}
    for rel in ['build/full-menu-known-art-v1/all-assets-manifest.json','build/full-menu-source-art-v1/menu-assets.json','build/full-menu-final-art-v1/manifest.json','build/contra-force-body-art-v6/manifest.json','build/full-menu-quickman-art-v1/manifest.json']:
        data=json.loads((R/rel).read_text())
        for row in data.get('entries',data.get('profiles',[])):
            arts[row.get('key',row.get('name'))]=Path(row.get('path',row.get('RGBA')))
    guide=R/'docs/player-guide/assets/edition'
    mapping={
        'MARIO':'mario','LUIGI':'luigi','MEGA MAN':'mega-man','PROTO MAN':'proto-man',
        'SAMUS ARAN':'samus','BILL RIZER':'bill','LANCE BEAN':'lance','LINK':'link',
        'ZELDA II LINK':'zelda-ii-link','SIMON BELMONT':'simon','GRANT':'grant','SYPHA':'sypha','ALUCARD':'alucard',
        'PIT':'pit','RYGAR':'rygar','SCROOGE MCDUCK':'scrooge','DARKWING DUCK':'darkwing',
        'BASS':'bass','ROLL':'roll','RYU HAYABUSA':'ryu','SOPHIA III':'sophia','KIRBY':'kirby',
        'META KNIGHT':'meta-knight','CHIP':'chip','DALE':'dale','LITTLE MAC':'little-mac',
        'MIKE JONES':'mike-jones','SMB3 MARIO':'smb3-mario','SMB3 LUIGI':'smb3-luigi',
        'VIC VIPER':'vic-viper','OCTOPUS':'octopus','TWINBEE':'twinbee','PENTAROU':'pentarou',
        'LEONARDO':'leonardo','RAPHAEL':'raphael','MICHELANGELO':'michelangelo','DONATELLO':'donatello'}
    pics={name:Image.open(guide/f'hero-{key}.png').convert('RGBA') for name,key in mapping.items()}
    pics['META KNIGHT']=Image.open(R/'docs/player-guide/assets/astra/hero-meta-knight.png').convert('RGBA')
    for name,key in {
        'SUPERMAAA MARIO':'supermaaa','ROGUE DAWN':'rogue-dawn','KARNOV':'karnov','QUICK MAN':'quick-man',
        'SHINOBI':'shinobi','THOMAS':'thomas','METAL STORM':'metalstorm',
        'FF FIGHTER':'ff-fighter','FF WHITE MAGE':'ff-white-mage','FF BLACK MAGE':'ff-black-mage','FF THIEF':'ff-thief',
        'GOKU':'goku','SMB2 MARIO':'smb2-mario','SMB2 LUIGI':'smb2-luigi','SMB2 TOAD':'smb2-toad','SMB2 PEACH':'smb2-peach',
        'GIMMICK':'gimmick','SMB3 BOWSER':'bowser-smb3','SMB1 BOWSER':'bowser-smb1','DONKEY KONG':'donkey-kong',
        'EXCITEBIKE':'excitebike','PRINCE PERSIA':'persia','BURNS':'contra-force-burns','SMITH':'contra-force-smith',
        'IRON':'contra-force-iron','BEANS':'contra-force-beans','ARTHUR':'arthur'}.items():
        pics[name]=Image.open(arts[key]).convert('RGBA')
    for name,box in [('POPO',(14,14,49,66)),('NANA',(14,102,49,154))]:
        pics[name]=cut(R/'chr/characters/ice-climbers-preview.png',box)
    for name,file in [('ALEX','river-city-alex-source.png'),('RYAN','river-city-ryan-stand-source.png')]:
        p=R/'chr/characters'/file
        im=Image.open(p)
        pics[name]=cut(p,(0,0,19,34)) if name=='ALEX' else im.convert('RGBA')
    pics['SUNNY']=cut(R/'chr/characters/sunny-review.png',(20,65,85,130))
    wwf=json.loads((R/'build/wwf-menu-art-v1/menu-assets.json').read_text())
    for item in wwf['variants']:
        pics[item['name'].upper()]=Image.open(item['colored_idle_preview']).convert('RGBA')
    extra=R/'build/quick-roster-extra-portraits-1030-v1'
    for name,file in [('KAMIKAZE MARIO','kamikaze-v1-mario.png'),('CELESTE MARIO','celeste-mario-fresh.png'),('GB PIT','gb-pit.png'),('DOC LOUIS','doc-louis.png'),('MIKE TYSON','mike-tyson.png')]:
        pics[name]=Image.open(extra/file).convert('RGBA')
    for name,file in [('SMB2 MARIO','mario'),('SMB2 LUIGI','luigi'),('SMB2 TOAD','toad'),('SMB2 PEACH','peach')]:
        p=R/f'build/smb2-roster-normal-rgba-1030-v2/smb2-{file}-normal.png'
        pics[name]=Image.open(p).convert('RGBA')
    # These existing reference exports face opposite to the requested roster
    # presentation. Flip the complete sprite, keeping all original pixels.
    for name in ['CHIP','DALE','SMB3 BOWSER','GIMMICK','THOMAS','GOKU']:
        pics[name]=pics[name].transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    assert len(names)==80 and len(set(n for n,_ in names))==80
    assert set(n for n,_ in names)<=set(pics),set(n for n,_ in names)-set(pics)
    W,H=1936,2168
    im=Image.new('RGB',(W,H),'#101725');d=ImageDraw.Draw(im)
    d.text((42,28),'SMB CROSSOVER · THE FULL ROSTER',font=font(48,True),fill='white')
    d.text((44,91),'80 characters · Every SELECT alternate shown individually',font=font(25),fill='#ffcb59')
    cw,ch,gap=220,178,16
    for i,(name,alt) in enumerate(names):
        x=32+(i%8)*(cw+gap);y=150+(i//8)*(ch+gap)
        d.rounded_rectangle((x,y,x+cw,y+ch),radius=8,fill='#1b273b',outline='#35465d',width=2)
        sprite=pics[name];bbox=sprite.getbbox();assert bbox,name;sprite=sprite.crop(bbox)
        scale=min(152/sprite.width,111/sprite.height,4)
        if scale>=1:scale=math.floor(scale)
        sprite=sprite.resize((max(1,round(sprite.width*scale)),max(1,round(sprite.height*scale))),Image.Resampling.NEAREST)
        im.paste(sprite,(x+(cw-sprite.width)//2,y+12+(112-sprite.height)//2),sprite)
        f=font(20,True)
        while d.textlength(name,font=f)>cw-14:f=font(f.size-1,True)
        d.text((x+(cw-d.textlength(name,font=f))/2,y+132),name,font=f,fill='#f4f7fc')
        if alt:d.text((x+cw-57,y+160),'SELECT',font=font(11,True),fill='#ffcb59')
    d.text((40,2110),'Expanded roster overview · Includes characters still in development.',font=font(24),fill='#aebed4')
    OUT.parent.mkdir(parents=True,exist_ok=True);im.save(OUT)
    target=Path('C:/Users/kando/Downloads/SMB-Crossover-Full-Roster.png');target.write_bytes(OUT.read_bytes())
    print(json.dumps(dict(path=str(OUT),downloads=str(target),individual_sprites=80,bytes=OUT.stat().st_size)))

if __name__=='__main__':main()
