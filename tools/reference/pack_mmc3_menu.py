"""Pack exact current MMC5 menu poses for resident MMC3 menu-only CHR RAM.

The source captures are controller-only native PPU/OAM observations. Every
identity receives one 1 KiB page per outline setting. Gameplay family graphics
are restored on confirmation; no gameplay art or source pixels are redrawn.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
FIRST=756


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures',type=Path,default=ROOT/'build/verification/mmc3-menu-nj')
    args=parser.parse_args();root=args.captures
    records=[];pages=[];sources={}
    for setting in ('off','on'):
        folder=root/('source-sprite-'+setting)
        manifest=json.loads((folder/'manifest.json').read_text())
        assert manifest['exit']==0 and len(manifest['identities'])==33
        sources[setting]=manifest
        folder=folder/'build/verification'
        for index,case in enumerate(manifest['identities']):
            name=case[0];key=f'{index+1:02d}-{setting}-{name.lower().replace(" ","-")}'
            chr_data=(folder/(key+'-chr.bin')).read_bytes()
            oam=(folder/(key+'-oam.bin')).read_bytes()
            palette=(folder/(key+'-palette.bin')).read_bytes()[16:]
            pool=[];parts=[]
            for slot in range(64):
                y,tile,attr,x=oam[slot*4:slot*4+4]
                if y>=240:continue
                address=(tile&1)*4096+(tile&254)*16
                pair=chr_data[address:address+32]
                assert len(pair)==32
                if pair not in pool:pool.append(pair)
                parts.append([y,pool.index(pair)*2+1,attr&0xe3,x])
            assert 0<len(parts)<=32 and len(pool)<=32,(name,setting,len(parts),len(pool))
            pages.append(b''.join(pool).ljust(1024,b'\0'))
            records.append(dict(name=name,outline=setting,identity=index,
                                chr_ram_page=52+len(pages)-1,parts=parts,palette=list(palette),
                                source_files={suffix:hashlib.sha256((folder/(key+suffix)).read_bytes()).hexdigest()
                                              for suffix in ('-chr.bin','-oam.bin','-palette.bin')}))
    assert len(pages)==66 and FIRST+len(pages)<=1024
    assert sources['off']['ROM_sha256']==sources['on']['ROM_sha256']
    packed=b''.join(pages)
    target=ROOT/'chr/characters/mmc3-menu-previews.chr';target.write_bytes(packed)
    lines=['; Generated exact resident menu poses. Do not use in gameplay.',
           '.pushseg','.segment "M3_MENU"']
    for field in ('Lo','Hi'):
        lines.append('M3MenuRecord'+field+':')
        for start in range(0,len(records),11):
            lines.append(' .byte '+','.join(('<'if field=='Lo'else'>')+'M3MenuRecord'+str(i)
                                          for i in range(start,min(start+11,len(records)))))
    for index,record in enumerate(records):
        lines.append('M3MenuRecord'+str(index)+': .byte '+str(len(record['parts'])))
        for part in record['parts']:lines.append(' .byte '+','.join(str(value)for value in part))
        lines.append(' .byte '+','.join(str(value)for value in record['palette']))
    lines.append('.popseg')
    (ROOT/'ports/mmc3-oversized/menu_art.inc').write_text('\n'.join(lines)+'\n')
    report=dict(source=sources,source_first=FIRST,source_pages=len(pages),
                extraction='Observed MMC5 $5120..$5127 sprite bank registers plus $5130 upper bits, read from CHR ROM; PPU debug background view is not used.',
                chr_ram_first=52,chr_ram_pages=len(pages),gameplay_uses_these_pages=False,
                packed_sha256=hashlib.sha256(packed).hexdigest(),records=records,
                palette_policy='Only sprite color entries are queued. Universal background entries are never written.')
    (ROOT/'ports/mmc3-oversized/menu_art.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(identities=33,outline_settings=2,bytes=len(packed),source_first=FIRST)))


if __name__=='__main__':main()
