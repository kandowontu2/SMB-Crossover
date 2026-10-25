"""Pack completed expanded profiles into a 6/6/7 grid and explicit navigation.

The input manifest lists real portrait sources and slots that are playable.
Omitted entries stay absent and cannot be selected. This does not generate
character implementations or enable unfinished profiles.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]


def encode_tile(values):
    return bytes(sum(((values[y][x]>>p)&1)<<(7-x) for x in range(8))
                 for p in range(2) for y in range(8))


def slot_position(slot):
    assert 0<=slot<19
    if slot<12:
        return (slot//6,2+(slot%6)*5)
    return (2,2+(slot-12)*4)


def navigation(slots):
    """Each row wraps horizontally; vertical motion finds the nearest column."""
    positions={s:slot_position(s) for s in slots}
    rows={r:sorted(s for s in slots if positions[s][0]==r) for r in range(3)}
    live_rows=sorted(r for r,v in rows.items() if v)
    result={}
    for s in slots:
        row,col=positions[s]
        same=rows[row];i=same.index(s);ri=live_rows.index(row)
        result[s]={
            'left':same[(i-1)%len(same)],'right':same[(i+1)%len(same)]}
        for name,delta in (('up',-1),('down',1)):
            other=live_rows[(ri+delta)%len(live_rows)]
            result[s][name]=min(rows[other],key=lambda v:(abs(positions[v][1]-col),v))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--polished',action='store_true',help='High-contrast text, clean navigation and dedicated preview area')
    a=p.parse_args()
    spec=json.loads(a.manifest.read_text())
    records=spec['portraits'];slots=sorted(r['slot'] for r in records)
    assert len(slots)==len(set(slots)) and set(range(12))<=set(slots)
    assert len({r['character'] for r in records})==len(records)
    a.output.mkdir(parents=True,exist_ok=True)
    assert not (a.output/'manifest.json').exists(),'Use a fresh output to preserve prior evidence'
    chr_data=bytearray((ROOT/'chr/mmc5/bg_ground.chr').read_bytes())
    assert len(chr_data)==4096
    nt=bytearray([0x24]*960+[0]*64)
    def text(row,column,value):
        chars={' ':0x24,'-':0x28,'/':0x2d,'.':0x2c}
        for i,c in enumerate(value):nt[row*32+column+i]=chars[c] if c in chars else ord(c)-ord('A')+10
    if a.polished:
        text(1,8,'CHOOSE YOUR HERO')
        text(27,5,'A OR START PLAY  B BACK')
        text(28,10,'D PAD CHOOSE')
        # Portraits retain their grayscale palette. UI text is independently
        # white/gold, rather than brightening and washing out every portrait.
        nt[960:968]=bytes([0xa5]*8)
        nt[960+5*8:960+6*8]=bytes([0x55]*8)
        nt[960+6*8:960+7*8]=bytes([0x5a]*8)
        nt[960+7*8:1024]=bytes([0x55]*8)
        for col in range(2,30):nt[3*32+col]=0xfc
        # A blue card makes the genuine black sprite ink visible.
        for row in range(18,24):
            for col in range(12,20):nt[row*32+col]=0xfe
        for col in (3,4):
            nt[960+4*8+col]=0xf0
            nt[960+5*8+col]=0xff
    else:
        text(1,5,'SELECT YOUR CHARACTER')
        text(27,3,'D-PAD CHOOSE  A/START PLAY')
        text(28,12,'B - BACK')
    pool={bytes(16):0x24};next_tile=0x40
    page=Image.new('RGBA',(256,240),(0,0,0,255))
    source_hashes={}
    for r in records:
        path=Path(r['image'])
        if not path.is_absolute():path=ROOT/path
        source_hashes[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        picture=Image.open(path).convert('RGBA')
        picture=picture.crop(picture.getbbox())
        # Keep the whole genuine source portrait. Some tall33/34px source poses
        # need a tiny thumbnail reduction; the live colored preview stays full.
        ratio=min(1,24/picture.width,32/picture.height)
        if ratio<1:picture=picture.resize((max(1,round(picture.width*ratio)),max(1,round(picture.height*ratio))),Image.Resampling.NEAREST)
        canvas=Image.new('RGBA',(24,32))
        canvas.alpha_composite(picture,((24-picture.width)//2,32-picture.height))
        row,column=slot_position(r['slot']);top=4+row*5
        for ty in range(4):
            for tx in range(3):
                values=[]
                for y in range(8):
                    line=[]
                    for x in range(8):
                        rr,g,b,alpha=canvas.getpixel((tx*8+x,ty*8+y))
                        shade=1 if .299*rr+.587*g+.114*b<95 else 2 if .299*rr+.587*g+.114*b<200 else 3
                        line.append(shade if alpha>=128 else 0)
                    values.append(line)
                data=encode_tile(values)
                if data not in pool:
                    assert next_tile<256,'Expanded portrait tiles exceed a native4KB background'
                    pool[data]=next_tile;next_tile+=1
                tile=pool[data]
                chr_data[tile*16:(tile+1)*16]=data
                nt[(top+ty)*32+column+tx]=tile
                for y,line in enumerate(values):
                    for x,color in enumerate(line):
                        if color:page.putpixel(((column+tx)*8+x,(top+ty)*8+y),((0,100,176,252)[color],)*3+(255,))
    chr_data[0x3f*16:0x40*16]=encode_tile([[3 if 3-y<=x<=4+y and y<=3 else 0 for x in range(8)] for y in range(8)])
    if a.polished:
        # The shared first font page is deduplicated; custom UI tiles belong
        # in the dedicated menu page, outside the native font and portrait pool.
        assert next_tile<=0xfc,'Reserve FC/FD/FE for menu decoration'
        chr_data[0xfc*16:0xfd*16]=encode_tile([[1 if y==3 else 0 for x in range(8)] for y in range(8)])
        chr_data[0xfd*16:0xfe*16]=encode_tile([[3 if 1<=x<=5 and abs(y-3)<=5-x else 0 for x in range(8)] for y in range(8)])
        chr_data[0xfe*16:0xff*16]=encode_tile([[1]*8 for _ in range(8)])
    nav=navigation(slots)
    lines=['; Generated from completed profiles only. Absent slots are never linked by navigation.']
    for direction in ('left','right','up','down'):
        lines+=['X5Menu'+direction.title()+':', '  .byte '+','.join(str(nav[s][direction]) if s in nav else '0' for s in range(19))]
    for name,values in (
        ('Characters',[next((r['character'] for r in records if r['slot']==s),0) for s in range(19)]),
        ('Present',[int(s in nav) for s in range(19)]),
        ('CursorLo',[((4+slot_position(s)[0]*5+(1 if a.polished else 4))*32+slot_position(s)[1]+(-1 if a.polished else 1))&255 for s in range(19)]),
        ('CursorHi',[0x20+((4+slot_position(s)[0]*5+(1 if a.polished else 4))*32+slot_position(s)[1]+(-1 if a.polished else 1))//256 for s in range(19)])):
        lines+=['X5Menu'+name+':','  .byte '+','.join(map(str,values))]
    (a.output/'x5-menu-layout.inc').write_text('\n'.join(lines)+'\n')
    (a.output/'x5-menu.chr').write_bytes(chr_data)
    (a.output/'x5-menu.bin').write_bytes(nt)
    page.save(a.output/'portrait-layout.png')
    report=dict(playable_slots=slots,navigation=nav,unique_portrait_tiles=next_tile-0x40,
        chr_bytes=len(chr_data),source_hashes=source_hashes,
        scope='Portrait packing/navigation data only. Does not assert implemented gameplay.')
    (a.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(playable_slots=slots,unique_portrait_tiles=next_tile-0x40)))


if __name__=='__main__':main()
