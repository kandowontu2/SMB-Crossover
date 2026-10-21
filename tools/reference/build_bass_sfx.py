"""Compile source NSF APU traces into small, independently checked effects."""
from pathlib import Path
from collections import defaultdict
import csv
import json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/reference-bass-sfx'
# Public request numbers preserve existing gameplay hooks. They are not the
# source NSF song numbers; those are recorded in the provenance manifest.
REQUESTS=[(19,'Land',6),(20,'GetNewLife',8),(21,'Shoot',5),
          (22,'TakeDamage',9),(23,'Die',10),(24,'HitEnemy',7),
          (25,'Deflect',7),(28,'GetEnergy',9),(60,'PharaohShotSmall',7),
          (61,'PharaohShotBig',7),(62,'GetEnergyLoop',9),(63,'MetalBlade',7),
          (64,'ChargeKick',7),(65,'WaterShieldExpand',7),(67,'Teleport',8)]


def read(name):
    writes=defaultdict(list)
    for row in csv.DictReader((OUT/(name+'.csv')).open()):
        f,a,v=map(int,row.values())
        if a<16 or a==21:writes[f].append((a,v))
    image=[0]*16;enable=0;images=[];active=[];mask=0
    for f in range(180):
        for a,v in writes[f]:
            if a==21:enable=v&15
            else:image[a]=v
        audible=0
        for c in range(4):
            if not enable&(1<<c):continue
            v=image[c*4]&(127 if c==2 else 15)
            period=image[c*4+2]+(image[c*4+3]&7)*256
            if v and (c==3 or period>=(2 if c==2 else 8)):audible|=1<<c
        if audible:active.append(f);mask|=audible
        images.append((image[:],enable))
    assert active and max(active)<178,(name,active[-5:])
    first,last=min(active),max(active)
    result=[];previous={}
    for f in range(first,last+1):
        image,enable=images[f]
        frame=[]
        addresses={a for a,_ in writes[f] if a<16}
        for a in range(16):
            if not mask&(1<<(a//4)):continue
            value=image[a]
            if a%4==0 and not enable&(1<<(a//4)):
                value=0 if a//4==2 else value&240
            # Preserve timer-high writes: equal values can retrigger notes.
            if first==f or previous.get(a)!=value or (a%4==3 and a in addresses):frame.append((a,value))
            previous[a]=value
        result.append(frame)
    return mask,result


def main():
    source=json.loads((OUT/'source.json').read_text())
    names=list(dict.fromkeys(n for _,n,_ in REQUESTS));assets={n:read(n) for n in names if n!='GetEnergyLoop'}
    mask,fs=assets['GetEnergy']
    assets['GetEnergyLoop']=(mask,fs[:7])
    source['GetEnergyLoop']={**source['GetEnergy'],'duration_ms':120,'loop_ms':30}
    lines=['; Generated from the exact NSF tracks named by 2.02 MusicInfo.',
           '.pushseg','.segment "MUSIC"']
    fixtures=['-- Frozen source NSF register images, independent of the ROM decoder.','return {']
    total=0
    for name,(mask,fs) in assets.items():
        binary=[]
        for frame in fs:
            for a,v in frame:binary.extend((a,v))
            binary.append(254)
        binary.append(255)
        # An independent expansion must recover every captured update.
        decoded=[];current=[];it=iter(binary)
        for op in it:
            if op==255:break
            if op==254:decoded.append(current);current=[]
            else:current.append((op,next(it)))
        assert decoded==fs,name
        total+=len(binary)
        lines.append('BassSfx'+name+':')
        if name=='GetEnergyLoop':
            for index,frame in enumerate(fs):
                if index==2:lines.append('BassSfxRefillLoopPoint:')
                values=[v for pair in frame for v in pair]+[254]
                lines.append(' .byte '+','.join(str(v) for v in values))
            lines.append(' .byte 252,<BassSfxRefillLoopPoint,>BassSfxRefillLoopPoint')
        else:
            for i in range(0,len(binary),24):lines.append(' .byte '+','.join(str(v) for v in binary[i:i+24]))
        fixtures.append(f' {name}={{mask={mask},frames={{')
        image=[0]*16
        for frame in fs:
            for a,v in frame:image[a]=v
            fixtures.append('  {'+','.join(str(v) for v in image)+'},')
        fixtures.append(' }},')
        source[name].update(mask=mask,frames=len(fs),bytes=len(binary))
    for label,values in [('BassSfxRequests',[str(n) for n,_,_ in REQUESTS]),
                         ('BassSfxMasks',[str(assets[n][0]) for _,n,_ in REQUESTS]),
                         ('BassSfxPriorities',[str(p) for _,_,p in REQUESTS]),
                         ('BassSfxLo',['<BassSfx'+n for _,n,_ in REQUESTS]),
                         ('BassSfxHi',['>BassSfx'+n for _,n,_ in REQUESTS])]:
        lines.extend([label+':',' .byte '+','.join(values)])
    lines.extend(['BASS_SFX_COUNT = '+str(len(REQUESTS)),'.popseg'])
    (ROOT/'audio/bass-source-sfx.inc').write_text('\n'.join(lines)+'\n')
    fixtures.append('}')
    (ROOT/'tests/fixtures/bass-source-sfx.lua').write_text('\n'.join(fixtures)+'\n')
    (ROOT/'docs/reference/bass-sfx.json').write_text(json.dumps(source,indent=2)+'\n')
    print('Bass source SFX:',len(names),'effects,',total,'bytes')


if __name__=='__main__':main()
