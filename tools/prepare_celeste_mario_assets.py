"""Copy authenticated native Celeste Mario patterns and compiled pose records."""
from pathlib import Path
import hashlib,json,re
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
UPSTREAM=Path('C:/Users/kando/Documents/ChatGPT/SNES Ports/upstream-nes')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rom=ROOT/'build/celeste-native-reference.nes';raw=rom.read_bytes()
    assert sha(rom)=='f1b6123f891c01a2cb0200c7e77c168991a5adca121c1f296e08839e0f70f08b'
    listing=(ROOT/'build/celeste-native-reference.lst').read_text(errors='replace')
    symbols={m[2]:int(m[1],16) for line in listing.splitlines() if(m:=re.match(r'^([0-9A-F]{5})\s+([A-Za-z_][\w]*):',line))}
    source=UPSTREAM/'IncBins/editor/mg.chr';assert raw[-131072:]==source.read_bytes()
    patterns=source.read_bytes()[:16384]
    def bank7(name,n):return raw[16+7*8192+symbols[name]-0xa000:16+7*8192+symbols[name]-0xa000+n]
    table=bank7('PlayerGraphicsTable',104);banks=bank7('PlayerGFXBankTable',26)
    asm=['; Authenticated compiled MG native pose table; code bank98 A maps as data C98 (+2000).',
         '.pushseg','.segment "CELESTE_MARIO_CORE"','CmArtStart:']
    metadata=[]
    for face in (1,2):
        for pose in range(26):
            parts=[]
            for i,tile in enumerate(table[pose*4:pose*4+4]):
                if tile==255:continue
                assert tile%2==0
                x=(i%2)*8
                parts.append([tile,0 if face==1 else 64,(i//2)*16,x if face==1 else 8-x])
            label=f'CmArt{pose}{"R" if face==1 else "L"}'
            asm += [label+':',' .byte '+str(len(parts)*4)]
            asm += [' .byte '+','.join(map(str,q))for q in parts]
            metadata.append(dict(pose=pose,face=face,bank=banks[pose],parts=parts))
        for half,op in [('Lo','<'),('Hi','>')]:
            asm += [f'CmArt{"R" if face==1 else "L"}{half}:',
               ' .byte '+','.join(f'{op}(CmArt{i}{"R" if face==1 else "L"}+$2000)'for i in range(26))]
    asm += ['CmArtBanks:',' .byte '+','.join(map(str,banks)),'.popseg']
    (ROOT/'src/celeste_mario_art.inc').write_text('\n'.join(asm)+'\n')
    (ROOT/'chr/characters/celeste-mario.chr').write_bytes(patterns)
    colors=[(100,100,100),(200,76,12),(248,168,72),(0,30,116)]
    sheet=Image.new('RGB',(13*64,2*104),(80,80,80));d=ImageDraw.Draw(sheet)
    for r in metadata[:26]:
        im=Image.new('RGB',(24,40),(100,100,100))
        for tt,aa,yy,xx in r['parts']:
            for y in range(16):
                at=r['bank']*1024+(tt+(y//8))*16+y%8
                for x in range(8):
                    v=((patterns[at]>>(7-x))&1)|(((patterns[at+8]>>(7-x))&1)<<1)
                    if v:im.putpixel((xx+x+4,yy+y+4),colors[v])
        x=(r['pose']%13)*64;y=(r['pose']//13)*104
        sheet.paste(im.resize((48,80)),(x,y));d.text((x,y+82),str(r['pose']),fill='white')
    sheet.save(ROOT/'chr/characters/celeste-mario-preview.png')
    out=dict(native_ROM_sha256=sha(rom),source_chr_sha256=sha(source),
      output_chr_sha256=hashlib.sha256(patterns).hexdigest(),bytes=len(patterns),
      source='Native MG compiled bank7 PlayerGraphicsTable/PlayerGFXBankTable; IRQ writes WriteCHRBank0 to CHRPort0 in1KB mode. Source first16KB retained; actual player tiles use selected1KB page0/1/2.',
      palettes={'zero_dashes':[33,39,1],'one_dash':[22,39,1]},records=metadata,
      limits=['Source art only, not actual NES visible epochs.','Native speed mirage is intentionally not added to the host OAM load.'])
    (ROOT/'chr/characters/celeste-mario-assets.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(records=len(metadata),CHR_bytes=len(patterns),CHR_sha256=out['output_chr_sha256'])))
if __name__=='__main__':main()
