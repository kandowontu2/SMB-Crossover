"""Independently compare linked Meta poses with the original cartridge pixels.

Also check the retained original boss-room hardware OAM/CHR/palette captures.
Sword hue quantization is explicit; the body palette is exact.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[2]
SOURCE_SHA='a7a742f5288cd4ab220f530ee7c8d0e3714b8bf107e89c9bf03039217fec5829'
KIRBY_SHA='94936eb3b3a3bd090da9fba0770cc0d1013e798625b2560cb2b9c1edfe1879e6'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def signed(v):return v if v<128 else v-256


def pixels(data):
    assert len(data)==32
    return [[((data[(y//8)*16+y%8]>>(7-x))&1)|(((data[(y//8)*16+y%8+8]>>(7-x))&1)<<1)
             for x in range(8)]for y in range(16)]


def compose(parts,read,palette):
    result={}
    for dx,dy,tile,attr in reversed(parts):
        p=pixels(read(tile))
        for y in range(16):
            for x in range(8):
                q=p[15-y if attr&128 else y][7-x if attr&64 else x]
                if q:result[(dx+x,dy+y)]=palette[attr&3][q-1]
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path("C:/NES/Kirby's Adventure (USA) (Rev 1).nes"))
    p.add_argument('--native-captures',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();original=a.source.read_bytes();assert sha(a.source)==SOURCE_SHA
    source_prg=original[16:16+524288];source_chr=original[16+524288:]
    source_read=lambda addr:source_prg[0x31*8192+(addr&8191)]
    word=lambda addr:source_read(addr)+256*source_read(addr+1)
    def native_parts(pose):
        at=word(0x8000+pose*2);count=source_read(at)
        assert 0<count<12
        return [(signed(source_read(at+1+4*i)),signed(source_read(at+2+4*i)),source_read(at+3+4*i),source_read(at+4+4*i))for i in range(count)]
    native_chr=lambda tile:source_chr[0xa4*1024+(tile-128)*16:0xa4*1024+(tile-128)*16+32]
    rom=a.rom.read_bytes();assert rom[4]==64 and rom[5]==128
    text=(a.rom.with_suffix('.dbg').read_text()if a.rom.with_suffix('.dbg').exists()else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode())
    segments={};symbols={}
    for line in text.splitlines():
        if line.startswith('seg\t')and'ooffs='in line:
            d=dict(x.split('=',1)for x in line[4:].split(','))
            segments[d['id']]=(int(d['start'],16),int(d['ooffs']))
        elif line.startswith('sym\t')and'name="MkBodyLo"'in line:
            d=dict(x.split('=',1)for x in line[4:].split(',')if'='in x)
            segment=d['seg']
    start,offset=segments[segment]
    for line in a.rom.with_suffix('.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\w+)',line)
        if m:symbols[m[2]]=int(m[1],16)
    read=lambda addr:rom[offset+addr-start]
    base=16+1024*1024
    assert hashlib.sha256(rom[base+340*1024:base+356*1024]).hexdigest()==KIRBY_SHA
    colors={1:[0x30,0x37,0x17],3:[0x36,0x14,0x0f]}
    quantization={0x30:0x30,0x37:0x27,0x17:0x16}
    cases=[]
    for pose in range(90):
        page=read(symbols['MkBodyChr']+pose)+256
        assert page in(356,358,360)
        at=read(symbols['MkBodyLo']+pose)+256*read(symbols['MkBodyHi']+pose)
        size=read(at);assert size%4==0
        parts=[(signed(read(at+4+i*4)),signed(read(at+3+i*4)),read(at+1+i*4),read(at+2+i*4))for i in range(size//4)]
        assert all(t%2==0 and t<64 and attr&3 in(0,2)for _,_,t,attr in parts)
        expected=compose([(x+8,y+25,t,v)for x,y,t,v in native_parts(pose)],native_chr,colors)
        expected={xy:quantization.get(v,v)for xy,v in expected.items()}
        # Port MetaspriteRenderLoop descends through descriptors, whereas
        # the original hardware captures establish forward descriptor OAM.
        # Compose the actual emitted order, not symmetric source assumptions.
        actual=compose(list(reversed(parts)),lambda tile:rom[base+page*1024+tile*16:base+page*1024+tile*16+32],{0:colors[3],2:[0x16,0x30,0x27]})
        assert actual==expected,(pose,'Linked source pixels differ')
        for index in(11,12,13):
            assert rom[base+page*1024+index*32:base+page*1024+index*32+32]==rom[base+340*1024+index*32:base+340*1024+index*32+32]
        cases.append(dict(pose=pose,page=page,pixels=len(actual)))
    observed=[]
    for state_path in sorted(a.native_captures.glob('pose-*-state.json')):
        stem=state_path.name.removesuffix('-state.json')
        s=json.loads(state_path.read_text());oam=(a.native_captures/(stem+'-oam.bin')).read_bytes()
        palette=(a.native_captures/(stem+'-palette.bin')).read_bytes()
        physical=(a.native_captures/(stem+'-chr.bin')).read_bytes()
        assert s['chr']==0xa4 and physical==source_chr[0xa4*1024:0xa6*1024]
        assert list(palette[29:32])==colors[3]and list(palette[21:24])==colors[1]
        quads=[tuple(oam[i:i+4])for i in range(0,256,4)]
        visible=clipped=0;indices=[]
        for x,y,t,attr in native_parts(s['pose']):
            xx=s['x']-s['cameraX']+x;yy=s['y']-s['cameraY']+y
            if xx<0 or xx>255 or yy<0 or yy>=240:clipped+=1;continue
            assert(yy,t|1,attr,xx)in quads,(stem,(yy,t|1,attr,xx),'Original visible OAM part')
            indices.append(quads.index((yy,t|1,attr,xx)))
            visible+=1
        assert indices==sorted(indices),(stem,'Native forward descriptor priority')
        observed.append(dict(pose=s['pose'],frame=s['frame'],visible_parts=visible,natively_clipped_parts=clipped,oam_indices=indices))
    assert len(observed)>=30,'Original hardware pose coverage'
    report=dict(passed=True,rom_sha256=sha(a.rom),source_sha256=SOURCE_SHA,checker_sha256=sha(Path(__file__)),
                linked_poses=cases,linked_pixels=sum(c['pixels']for c in cases),body_colors_exact=colors[3],
                sword_hue_quantization=quantization,Kirby_base_16k_unchanged=True,
                native_hardware=observed,native_visible_parts=sum(c['visible_parts']for c in observed),
                original_order='forward descriptors',port_order='descending descriptors; actual emitted priority is composed',
                scope='Independent original and linked ROM decoders:90 poses, exact body colors, explicit sword hue map. Original boss-room actual OAM/CHR/palettes checked; offscreen native parts excluded. Not a gameplay route or live port-DMA proof.')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,poses=len(cases),pixels=report['linked_pixels'],native_hardware_poses=len(observed),native_visible_parts=report['native_visible_parts'])))


if __name__=='__main__':main()
