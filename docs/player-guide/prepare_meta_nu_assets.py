"""Read-only extraction of the frozen Meta Knight guide portrait/action crops.

The portrait uses linked 8x16 bitplanes and the renderer's reverse-descriptor
priority. Capture crops preserve their RGB pixels. This does not author ROM art.
"""
from pathlib import Path
from PIL import Image
import argparse, csv, gzip, hashlib, json, re

H=Path(__file__).resolve().parent
R=H.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PALETTE={0x36:(254,204,197),0x14:(160,26,204),0x0f:(0,0,0),
         0x16:(181,49,32),0x30:(255,254,255),0x27:(234,158,34)}

def portrait(rom_path,pose=8):
    rom=rom_path.read_bytes()
    text=gzip.decompress(rom_path.with_suffix('.dbg.gz').read_bytes()).decode()
    segments={}; labels={}
    for line in text.splitlines():
        if line.startswith('seg\t') and 'ooffs=' in line:
            d=dict(x.split('=',1)for x in line[4:].split(','))
            segments[d['id']]=(int(d['start'],16),int(d['ooffs']))
        elif line.startswith('sym\t') and 'name="MkBodyLo"' in line:
            d=dict(x.split('=',1)for x in line[4:].split(',')if '=' in x)
            segment=d['seg']
    start,offset=segments[segment]
    for line in rom_path.with_suffix('.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\w+)',line)
        if m:labels[m[2]]=int(m[1],16)
    read=lambda at:rom[offset+at-start]
    signed=lambda v:v if v<128 else v-256
    page=read(labels['MkBodyChr']+pose)+256
    at=read(labels['MkBodyLo']+pose)+256*read(labels['MkBodyHi']+pose)
    assert read(at)%4==0
    pixels={}
    for i in reversed(range(read(at)//4)):
        tile,attr,dy,dx=[read(at+1+i*4+j)for j in range(4)]
        dx,dy=signed(dx),signed(dy)
        bits=rom[16+1048576+page*1024+tile*16:16+1048576+page*1024+tile*16+32]
        for y in range(16):
            yy=15-y if attr&128 else y
            for x in range(8):
                xx=7-x if attr&64 else x
                color=((bits[yy//8*16+yy%8]>>(7-xx))&1)|(((bits[yy//8*16+yy%8+8]>>(7-xx))&1)<<1)
                if color:pixels[(dx+x,dy+y)]=([0x36,0x14,0x0f]if attr&3==0 else[0x16,0x30,0x27])[color-1]
    x0=min(x for x,y in pixels);y0=min(y for x,y in pixels)
    im=Image.new('RGBA',(max(x for x,y in pixels)-x0+1,max(y for x,y in pixels)-y0+1))
    for (x,y),c in pixels.items():im.putpixel((x-x0,y-y0),PALETTE[c]+(255,))
    return im,dict(pose=pose,page=page,pixels=len(pixels),bounds=[x0,y0,im.width,im.height])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--rom-sha256',required=True)
    parser.add_argument('--capture-dir',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    a=parser.parse_args()
    assert sha(a.rom)==a.rom_sha256
    result=json.loads((a.capture_dir.parent.parent/'result.json').read_text())
    assert result['passed'] and result['rom_sha256']==a.rom_sha256
    out=H/'assets/astra';rows=[]
    im,details=portrait(a.rom)
    target=out/'hero-meta-knight.png';im.save(target)
    rows.append(dict(asset=target.name,source=str(a.rom),source_sha256=a.rom_sha256,
        sha256=sha(target),size=im.size,linked_pose=details,
        evidence=str(a.evidence),evidence_sha256=sha(a.evidence),
        detail='Linked pose 8, native bitplane alpha and reverse-descriptor renderer priority. Exact body palette36/14/0F; sword world hues30/27/16. Mesen RGB palette, no color-key removal or invented pixels.'))
    trace=list(csv.DictReader((a.capture_dir/'moves.csv').open()))
    for name,stage,age in [('slash',2,25),('triple',3,40),('charge',7,25),('lunge',4,25),('spin',5,25),('plunge',6,40)]:
        state=next(r for r in trace if int(r['stage'])==stage and int(r['age'])==age)
        cx=int(state['x'])+8;cy=int(state['y'])+16
        crop=(cx-32,cy-32,cx+32,cy+32)
        source=a.capture_dir/f'action-{stage}-{age}.png'
        im=Image.open(source).convert('RGB').crop(crop)
        target=out/f'meta-nu-{name}.png';im.save(target)
        rows.append(dict(asset=target.name,source=str(source),source_sha256=sha(source),
            rom_sha256=a.rom_sha256,sha256=sha(target),size=im.size,crop=crop,state=state,
            detail='Unaltered native game screenshot crop from a controlled practice arena. Real controller attack and enemy; seeded terrain/player. Not a campaign screenshot.'))
    provenance=H/'assets/astra-provenance.json'
    old=json.loads(provenance.read_text());names={r['asset']for r in rows}
    provenance.write_text(json.dumps([r for r in old if r['asset']not in names]+rows,indent=2)+'\n')
    a.receipt.write_text(json.dumps(rows,indent=2)+'\n')
    print('Prepared frozen native portrait and six unaltered action crops.')

if __name__=='__main__':main()
