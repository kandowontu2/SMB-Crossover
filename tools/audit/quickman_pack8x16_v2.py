"""Pack authenticated CX poses into NES8x16 sprites with exact visible roles."""
from pathlib import Path
import hashlib,json,itertools
from PIL import Image,ImageDraw
import sys
R=Path(__file__).resolve().parents[2];I=R/'build/quickman-source-v1';O=R/'build/quickman-component-v2/art'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encode(rows):
    return bytes(sum(((rows[ty+y][x]>>plane)&1)<<(7-x)for x in range(8))for ty in [0,8]for plane in [0,1]for y in range(8))
def decode(raw):return [[((raw[(y//8)*16+y%8]>>(7-x))&1)|(((raw[(y//8)*16+y%8+8]>>(7-x))&1)<<1)for x in range(8)]for y in range(16)]
def flipped(rows,h,v):return [list(reversed(row))if h else list(row)for row in (list(reversed(rows))if v else rows)]
def canonical(rows):return min([(encode(flipped(rows,h,v)),(64 if h else 0)|(128 if v else 0))for h,v in [(False,False),(True,False),(False,True),(True,True)]],key=lambda q:q[0])
def source_pixels(frame,chr):
    pixels={};winner={}
    for order,(y,tile,a,x)in reversed(list(enumerate(frame['OAM']))):
        for yy in range(8):
            py=7-yy if a&128 else yy
            for xx in range(8):
                px=7-xx if a&64 else xx;at=tile*16;v=((chr[at+py]>>(7-px))&1)|(((chr[at+py+8]>>(7-px))&1)<<1)
                if v:pixels[x+xx,y+1+yy]=(a&0x23,v);winner[x+xx,y+1+yy]=order
    return pixels,winner
def candidates(pixels,role):
    pts={xy:v for xy,(r,v)in pixels.items()if r==role};values=[];seen=set()
    for phase_x in range(8):
        for phase_y in range(16):
            tiles={}
            for(x,y),v in pts.items():
                tx=(x-phase_x)//8*8+phase_x;ty=(y-phase_y)//16*16+phase_y
                tiles.setdefault((tx,ty),[[0]*8 for _ in range(16)])[y-ty][x-tx]=v
            signature=tuple(sorted(tiles));
            if signature in seen:continue
            seen.add(signature);hist=tuple(sum(ty<=y<ty+16 for tx,ty in tiles)for y in range(96,176))
            values.append(dict(role=role,tiles=tiles,hist=hist,count=len(tiles),patterns={canonical(rows)[0]for rows in tiles.values()}))
    return values
def main():
    O.mkdir(parents=True,exist_ok=True);p=json.loads((I/'poses/pose-manifest.json').read_text());chr=(I/'source/quick-man-native-CHR.bin').read_bytes();pairs=[];lookup={};frames=[];maxscan=0;total=0
    sys.path.insert(0,str(Path(__file__).parent));import quickman_source_v1 as source
    source_frames=list(p['frames']);rom=source.ROM.read_bytes()
    for i,frame in enumerate([0x5c,0x5d,0x5e,0x5f]):
        bus=source.Bus(rom);r=bus.ram
        for a,v in {0x2b:2,0x422:0xc0,0x402:14,0x462:128,0x4a2:128,0x6a2:i}.items():r[a]=v
        cpu=source.run(bus,0xce88);n=r[6]//4
        source_frames.append(dict(frame=frame,OAM=[list(r[0x200+j*4:0x204+j*4])for j in range(n)],kind='native_boomerang',source_entry='CE88',animation_index=i,CPU=cpu))
    original_contact=Image.new('RGB',(8*48,5*48),'#004444');packed_contact=original_contact.copy();draw=ImageDraw.Draw(packed_contact)
    for index,frame in enumerate(source_frames):
        pixels,winners=source_pixels(frame,chr);roles=sorted({q[0]for q in pixels.values()});options=[candidates(pixels,role)for role in roles];best=None
        for choice in itertools.product(*options):
            hist=[sum(q['hist'][y]for q in choice)for y in range(80)];new=set().union(*(q['patterns']for q in choice))-lookup.keys();cost=(max(hist),sum(q['count']for q in choice),len(new),sum(v*v for v in hist))
            if best is None or cost<best[0]:best=(cost,choice)
        cost,choice=best;assert cost[0]<=8,(frame['frame'],cost);maxscan=max(maxscan,cost[0]);cells=[]
        for layer in choice:
            for(x,y),rows in sorted(layer['tiles'].items(),key=lambda item:(min(winners.get((item[0][0]+xx,item[0][1]+yy),999)for yy in range(16)for xx in range(8)if item[1][yy][xx]),item[0])):
                pattern,flip=canonical(rows);pair=lookup.get(pattern)
                if pair is None:pair=len(pairs);lookup[pattern]=pair;pairs.append(pattern)
                cells.append(dict(x=x-128,y=y-1-128,pair=pair,attr=layer['role']|flip))
        # Exact NES first-opaque-cell priority, palette role, pattern value and
        # behind-background bit. Occluded native pixels remain occluded.
        rebuilt={}
        for c in reversed(cells):
            rows=flipped(decode(pairs[c['pair']]),bool(c['attr']&64),bool(c['attr']&128))
            for yy,row in enumerate(rows):
                for xx,v in enumerate(row):
                    if v:rebuilt[c['x']+128+xx,c['y']+129+yy]=(c['attr']&0x23,v)
        assert rebuilt==pixels,(frame['frame'],'visible role/priority mismatch')
        # The opposite facing is verified against the actual original renderer,
        # rather than assuming symmetry from the supplied rip.
        ob=source.Bus(rom);rr=ob.ram;slot=2 if frame.get('kind')=='native_boomerang'else 0
        for a,v in {0x2b:slot,0x420+slot:0x80,0x400+slot:14 if slot else int(frame['from_type'],16),0x460+slot:128,0x4a0+slot:128,0x6a0+slot:frame['animation_index']if slot else frame['index']}.items():rr[a]=v
        source.run(ob,0xce88 if slot else 0xcd92);ocells=[list(rr[0x200+j*4:0x204+j*4])for j in range(rr[6]//4)];other,_=source_pixels(dict(OAM=ocells),chr)
        mirrored={}
        for c in reversed(cells):
            attr=c['attr']^64;rows=flipped(decode(pairs[c['pair']]),bool(attr&64),bool(attr&128));mx=-(c['x']+8)
            for yy,row in enumerate(rows):
                for xx,v in enumerate(row):
                    if v:mirrored[mx+128+xx,c['y']+129+yy]=(attr&0x23,v)
        assert mirrored==other,(frame['frame'],'opposite native facing mismatch')
        for bg_mode in range(3):
            project=lambda d:{xy:q for xy,q in d.items()if not(q[0]&32 and(bg_mode==1 or(bg_mode==2 and sum(xy)%2)))}
            assert project(rebuilt)==project(pixels)
        total+=len(cells);frames.append(dict(frame=frame['frame'],kind=frame.get('kind','body'),source_OAM=frame['OAM'],opposite_source_OAM=ocells,cells=cells,source_pixels=len(pixels),logical_1KiB_pages=sorted({c['pair']//32 for c in cells}),max_sprites_per_scanline=cost[0],verification='Both facings match actual source renderer pattern value, palette role and BG-priority. Original internal first-opaque priority preserved; tested transparent/opaque/checker backgrounds.',origin=dict(x=128,y=128)))
        pal=[[(0,0,0),(0,0,0),(209,213,0),(255,0,160)],[(0,0,0),(0,0,0),(255,255,255),(236,238,78)]]
        canvas=Image.new('RGBA',(256,240))
        for(x,y),(role,v)in rebuilt.items():canvas.putpixel((x,y),pal[role&3][v]+(255,))
        body=canvas.crop(canvas.getbbox());pos=(index%8*48+(48-body.width)//2,index//8*48+46-body.height);packed_contact.paste(body,pos,body);draw.text((index%8*48+2,index//8*48+1),f'{frame["frame"]:02X}',fill='white')
    raw=b''.join(pairs);(O/'quick-man-8x16.chr').write_bytes(raw)
    # Metasprite leaves: count followed by signedY, pairLow, attrs, signedX.
    meta=bytearray();offsets=[]
    for f in frames:
        offsets.append(len(meta));meta.append(len(f['cells']))
        for c in f['cells']:meta.extend([c['y']&255,(c['pair']*2)&255,c['attr'],c['x']&255])
    assert len(pairs)<=128,'One4KB8x16 pattern bank exceeded; require bank paging proposal.'
    (O/'quick-man-8x16-metasprites.bin').write_bytes(meta);packed_contact.resize((768,480),Image.Resampling.NEAREST).save(O/'contact.png')
    asm=['.export QuickManPackedChr,QuickManPoseLo,QuickManPoseHi','.segment "QUICKMAN_ART"','QuickManPoseLo: .byte '+','.join('<(QuickManMeta+'+str(offsets[[f['frame']for f in frames].index(i)])+')'if i in[f['frame']for f in frames]else '<QuickManEmpty'for i in range(256)),'QuickManPoseHi: .byte '+','.join('>(QuickManMeta+'+str(offsets[[f['frame']for f in frames].index(i)])+')'if i in[f['frame']for f in frames]else '>QuickManEmpty'for i in range(256)),'QuickManEmpty: .byte0','QuickManMeta: .incbin "'+str(O/'quick-man-8x16-metasprites.bin').replace('\\','/')+'"','.segment "QUICKMAN_CHR"','QuickManPackedChr: .incbin "'+str(O/'quick-man-8x16.chr').replace('\\','/')+'"']
    (O/'art.s').write_text('\n'.join(asm).replace('.byte0','.byte 0')+'\n')
    report=dict(status='ALL30_BODY_AND4_BOOMERANG_SOURCE_POSES_PIXEL_PALETTE_AND_PRIORITY_EXACT_8X16',source_handoff=str(I/'handoff.json'),source_handoff_sha256=sha(I/'handoff.json'),source_CHR_sha256=sha(I/'source/quick-man-native-CHR.bin'),frames=frames,metasprite_offsets=offsets,frame_order=[f['frame']for f in frames],pattern_pairs=len(pairs),CHR_bytes=len(raw),metasprite_bytes=len(meta),total_OAM_cells=total,max_body_sprites_per_scanline=maxscan,sprite_palette_roles=2,pattern_bank_bit=0,host_allocations=False,scope='Source pixels and source palette-role/BG-priority semantics preserved. Per-pixel internal first-opaque winner retained by dropping hidden source pixels; cells can merge because their remaining visible pixels do not overlap. External actor OAM ordering remains host-owned. Both facings use host whole-body mirror; native source fixture facing is supplied. One boomerang contributes one8x16 sprite; body5 plus3 boomerangs can consume all8 sprites on a shared scanline before host actors.',bindings={str(q):sha(q)for q in sorted(O.iterdir())if q.is_file()and q.name!='packing.json'})
    (O/'packing.json').write_text(json.dumps(report,indent=2)+'\n');print('pairs',len(pairs),'CHR',len(raw),'meta',len(meta),'maxscan',maxscan,'cells',total)
if __name__=='__main__':main()
