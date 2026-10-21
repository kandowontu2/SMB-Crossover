"""Preserve existing hurt bodies and share exact source white FX in window0.

Only hurt-pose tile numbers/bank entries change. The seven shared effect pairs
occupy the same indices in both private1KiB body composites, so inventory and
enemy world windows remain independent. Re-running is intentionally idempotent.
"""
from pathlib import Path
import hashlib,json,re
from PIL import Image
import build_megaman_assets as assets
import build_samus_assets as packing

ROOT=Path(__file__).resolve().parents[2]
PAIR=re.compile(r'(MetaspriteVramOffset\{\$)([0-9a-fA-F]+)(\}, \{SPRITE_BANK_0\})')
BODY=ROOT/'chr/characters/crossover-hurt-body.chr'

def table(code,name):
    m=re.search(r'^'+name+r':\n(\s*\.byte[^\n]+)',code,re.M)
    assert m,name
    values=[int(v.strip().replace('$','0x'),0)for v in m[1].split('.byte')[1].split(',')]
    return m,values

def main():
    reference=ROOT/'tests/fixtures/megaman-bass-injury-source-art.json'
    ref=json.loads(reference.read_text())
    assert ref['effect_pixels']['megaman']==ref['effect_pixels']['bass']
    def white(im,projectile=False):
        return {2:[[2 if im.getpixel((x,y))[3]>=128 else 0 for x in range(im.width)]for y in range(im.height)]}
    oldlayers,oldpriority=assets.layers,assets.SCANLINE_PRIORITY
    assets.layers=white;assets.SCANLINE_PRIORITY=True
    pool=[];effects=[]
    for rec in ref['effect_pixels']['megaman']:
        im=Image.new('RGBA',(64,64))
        for yy,row in enumerate(rec['rows']):
            for xx,p in enumerate(row):
                if p!='.':im.putpixel((32+rec['x']+xx,32+rec['y']+yy),(252,252,252,255))
        effects.append(packing.parts(im,(32,32),pool))
    assets.layers=oldlayers;assets.SCANLINE_PRIORITY=oldpriority
    assert len(pool)==7
    fxpool=pool[:];previous=BODY.read_bytes()if BODY.exists()else None
    results=[];binary=bytearray()
    for role,path,tablename,newbank,indices,labels in (
        ('megaman','megaman_metasprites.inc','MegaManSpriteBanks',0x81,[15,31,47,63],
         [f'MmMM_{skin}_HURT{side}'for skin in('HAIR','HELMET','FIRE','WIND')for side in('Left','Right')]),
        ('bass','bass_metasprites.inc','XgBASSBanks',0x82,
         [int(re.search(r'XG_POSE_COUNT=(\d+)',(ROOT/'src/expanded_poses.inc').read_text())[1])*p+11 for p in range(3)],
         [f'XgBASS0_HURT{side}'for side in('Left','Right')])):
        file=ROOT/'src'/path;code=file.read_text();before=code
        m,banks=table(code,tablename);oldbank=banks[indices[0]]
        assert all(banks[i]==oldbank for i in indices)
        if oldbank==newbank:
            assert previous is not None and len(previous)==2048
            old=previous[(newbank-0x81)*1024:(newbank-0x81+1)*1024]
        elif role=='megaman':
            assert oldbank==0x49
            raw=(ROOT/'chr/characters/crossover-megaman-mmc3.chr').read_bytes()
            old=raw[(oldbank-0x40)*1024:(oldbank-0x40+1)*1024]
        else:
            first=0xd1+len((ROOT/'chr/characters/crossover-roster-high.chr').read_bytes())//1024
            raw=(ROOT/'chr/characters/crossover-expanded.chr').read_bytes()
            old=raw[(oldbank-first)*1024:(oldbank-first+1)*1024]
        assert len(old)==1024
        pool=fxpool[:];oldparts={};newparts={}
        def section(text,label):
            s=re.search(r'^'+label+r':\n(.*?)(?=^[A-Za-z_.]|\Z)',text,re.M|re.S)
            assert s,label
            return s
        for label in labels:
            s=section(code,label);oldparts[label]=s[1]
            def replace_tile(p):
                n=int(p[2],16)//2;data=old[n*32:(n+1)*32]
                assert len(data)==32
                if data not in pool:pool.append(data)
                assert pool[pool.index(data)]==data,'Exact existing body pixels remain'
                return p[1]+f'{pool.index(data)*2:02x}'+p[3]
            body=PAIR.sub(replace_tile,s[1]);newparts[label]=body
            # Nothing except a tile number may change in the body records.
            assert PAIR.sub(r'\1TILE\3',body)==PAIR.sub(r'\1TILE\3',s[1])
            code=code[:s.start(1)]+body+code[s.end(1):]
        assert len(pool)<=32,(role,len(pool))
        m,current=table(code,tablename)
        for i in indices:current[i]=newbank
        code=code[:m.start(1)]+'  .byte '+', '.join(f'${v:02x}'for v in current)+code[m.end(1):]
        # Compare untouched source after masking only the known changed fields.
        def scrub(text):
            for label in labels:
                s=section(text,label);text=text[:s.start(1)]+'BODY\n'+text[s.end(1):]
            s,_=table(text,tablename);return text[:s.start(1)]+'BANKS'+text[s.end(1):]
        assert scrub(before)==scrub(code),'Non-hurt body/weapon/pose records remain byte-identical'
        assert all(current[i]==banks[i]for i in range(len(banks))if i not in indices)
        file.write_text(code)
        data=b''.join(pool)+bytes(1024-len(pool)*32);binary+=data
        results.append(dict(character=role,logical_bank=newbank,normal_bank=current[0],unique_pairs=len(pool),body_records=len(labels),chr_sha256=hashlib.sha256(data).hexdigest()))
    BODY.write_bytes(binary)
    lines=['; Exact raw2.02 white injury pixels; source oracle is independent.','.pushseg','.segment "SAMUS_GFX"']
    for i,parts in enumerate(effects):
        lines +=[f'MmHurtFx{i}:',f' .byte {len(parts)*4}']
        for tile,attr,x,y in parts:
            lines.append(f' .byte MetaspriteVramOffset{{${tile:02x}}}, {{SPRITE_BANK_0}}, ${attr:02x}, {y}, {x}')
    lines +=['MmHurtFxLo:',' .byte '+','.join('<MmHurtFx'+str(i)for i in range(4)),
             'MmHurtFxHi:',' .byte '+','.join('>MmHurtFx'+str(i)for i in range(4)),'.popseg',
             'MM_HURT_BODY_BANK=$81','BASS_HURT_BODY_BANK=$82',
             'MM_HURT_NORMAL_BANK='+str(results[0]['normal_bank']),
             'BASS_HURT_NORMAL_BANK='+str(results[1]['normal_bank'])]
    (ROOT/'src/megaman_injury_art.inc').write_text('\n'.join(lines)+'\n')
    target=ROOT/'build/megaman-injury-art';target.mkdir(exist_ok=True)
    (target/'manifest.json').write_text(json.dumps(dict(source_oracle_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),shared_effect_pairs=7,bodies=results,non_hurt_records_unchanged=True),indent=2)+'\n')
    print('MM/Bass injury player-window composites:',results)

if __name__=='__main__':main()
