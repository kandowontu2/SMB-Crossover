"""Pack the actual Kirby portrait with the twelve existing portraits for layout review only."""
from pathlib import Path
import json
import subprocess
import sys
from PIL import Image

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/third-row-lp/menu-kirby-layout'


def main():
    O.mkdir(parents=True,exist_ok=True)
    mario=Image.new('RGBA',(16,16))
    source=(R/'chr/mmc3/sprites_mario.chr').read_bytes()[2048:3072]
    colors=((0,0,0,0),(182,40,0,255),(248,184,120,255),(170,90,0,255))
    for half in range(2):
        for y in range(16):
            for x in range(8):
                base=half*32+(y//8)*16+y%8
                color=((source[base]>>(7-x))&1)|(((source[base+8]>>(7-x))&1)<<1)
                mario.putpixel((half*8+x,y),colors[color])
    mario.save(O/'mario.png')
    portraits=[dict(slot=0,character=0,image=str(O/'mario.png'))]
    names=['HAIR-STAND','SAMUS-0-STAND','BILL-0-STAND','LINK-0-STAND','SIMON-0-STAND']
    names += [r+'-0-STAND' for r in ('PIT','RYGAR','SCROOGE','BASS','RYU','SOPHIA')]
    for slot,(name,char) in enumerate(zip(names,(1,2,3,4,5,6,7,12,9,10,11)),1):
        portraits.append(dict(slot=slot,character=char,image=f'build/reference-frames/{name}.png'))
    portraits.append(dict(slot=12,character=13,image='build/kirby-kd-private/art/kirby-portrait.png'))
    manifest=O/'layout-input.json'
    manifest.write_text(json.dumps(dict(portraits=portraits,
        scope='ART/NAVIGATION COMPONENT ONLY. Does not enable Kirby in the main ROM.'),indent=2)+'\n')
    subprocess.run([sys.executable,str(R/'tools/reference/build_x5_menu.py'),
                    '--manifest',str(manifest),'--output',str(O/'packed')],check=True)


if __name__=='__main__':main()
