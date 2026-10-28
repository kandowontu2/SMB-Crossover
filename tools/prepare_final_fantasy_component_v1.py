"""Pack authenticated unused2.02 FF poses and authored spell cells, not new art.

Standalone leaf only. Never changes shared source, linker, ROM or runtime.
The frozen audit remains the source authority; Fire/Ice cell repairs are explicit.
"""
from pathlib import Path
from collections import Counter
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/final-fantasy-component-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def bind(p):p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=sha(b))
BODY=[[(248,56,0),(255,255,255),(240,208,176)],
      [(248,56,0),(255,255,255),(240,208,176)],
      [(248,184,0),(175,127,0),(63,191,255)],
      [(248,184,0),(175,127,0),(63,191,255)]]
PURPLE=(111,49,152)
def encode(vals):
    q=bytearray(32)
    for y in range(16):
        for x in range(8):
            v=vals[y*8+x];a=(y//8)*16+y%8
            q[a]|=(v&1)<<(7-x);q[a+8]|=(v>>1)<<(7-x)
    return bytes(q)
def main():
    OUT.mkdir(exist_ok=True)
    audit=ROOT/'chr/characters/final-fantasy-source-v1.json'
    assert sha(audit.read_bytes())=='9be2faf6855b82a24926818a5eaa9b923cdfbcbb3845ee6e3b749abbcbc37d45'
    atlas=Image.open(ROOT/'chr/characters/final-fantasy-prototype-poses.png').convert('RGBA')
    original=Image.open(ROOT/'reference/crossover2/images/39.png').convert('RGBA')
    ff=Path('C:/NES/Final Fantasy (USA).nes');rom=ff.read_bytes()
    assert sha(rom)=='2f5d5ff2e22fb31c64d92dc783af443f94340b365595cd6b8d77e8c9b3a54820'
    assert rom[0x3ebb5:0x3ebc5]==bytes.fromhex('0f2818210f1630360f3022120f301000')
    records=[];index=[];unique={};facts=[]
    def add(im,colors,origin,kind,source,black=False):
        # Black remains a separately switchable original pixel mask; no dilation.
        cyan=[(0,66,90),(0,140,140),(0,239,222)]
        layers=[('color',0)]+([('weapon',128),('black',32)]if black else [])
        parts=[];opaque=Counter()
        for layer,flag in layers:
            for y in range(0,im.height,16):
                for x in range(0,im.width,8):
                    vals=[]
                    for yy in range(16):
                        for xx in range(8):
                            rgba=im.getpixel((x+xx,y+yy))if x+xx<im.width and y+yy<im.height else (0,0,0,0)
                            rgb=rgba[:3];v=0
                            if rgba[3]and rgb!=PURPLE:
                                if layer=='black':v=int(rgb==(0,0,0))
                                elif layer=='weapon':v=cyan.index(rgb)+1 if rgb in cyan else 0
                                elif rgb!=(0,0,0)and rgb not in cyan:
                                    rgb=(63,191,255)if rgb==(60,188,252)else rgb
                                    rgb=(240,208,176)if rgb==(255,192,128)else rgb
                                    assert rgb in colors,(kind,rgb)
                                    v=colors.index(rgb)+1
                            vals.append(v)
                            if v:opaque[layer]+=1
                    if any(vals):parts.append((encode(vals),flag,x-origin[0],y-origin[1]))
        patterns={q[0]for q in parts};assert len(patterns)<=32,(kind,len(patterns))
        key=tuple(parts)
        if key not in unique:
            unique[key]=len(records);records.append(dict(parts=parts,kind=kind))
        i=unique[key];index.append(i)
        facts.append(dict(entry=len(index)-1,record=i,kind=kind,source=source,origin=origin,
                          dimensions=im.size,opaque=dict(opaque),parts=len(parts),unique_pairs=len(patterns),RGBA_sha256=sha(im.tobytes())))
    for row in range(8):
        for frame in range(18):
            im=atlas.crop((frame*48,row*48,frame*48+48,row*48+48))
            add(im,BODY[row//2],(24,44),'body',dict(variant=row//2,tier=row%2,source_frame=frame+1),True)
    # Actual authored bitmap grid; the original stale timeline points at y383.
    # Preserve three Fire frames / five Ice frames. Fourth authored Fire not used.
    fire=[(894,195,46,22),(894,219,46,22),(894,242,46,22)]
    ice=[(941,289,73,70),(1015,289,72,70),(1088,289,72,70),(1161,289,72,70),(1234,289,72,70)]
    bolt=[(941+61*i,7,60,282)for i in range(6)]
    for kind,rects,colors,role in [
        ('fire',fire,[(216,40,0),(252,116,96),(252,252,252)],64),
        ('ice',ice,[(0,90,255),(63,191,255),(255,255,255)],128),
        ('bolt',bolt,[(175,127,0),(248,184,0),(255,255,255)],128)]:
        for frame,r in enumerate(rects):
            x,y,w,h=r;im=original.crop((x,y,x+w,y+h))
            before=len(index);add(im,colors,(w//2,h//2),kind,dict(rect=r,frame=frame,authored_timeline_repair=kind!='bolt'))
            rec=records[index[before]]
            rec['parts']=[(p,f|role,dx,dy)for p,f,dx,dy in rec['parts']]
    # Best-fit union packing keeps each complete record in ONE 1KB window.
    pages=[]
    for rec in sorted(records,key=lambda r:len({q[0]for q in r['parts']}),reverse=True):
        patterns={q[0]for q in rec['parts']};best=None
        for p,page in enumerate(pages):
            n=len(patterns-set(page))
            if len(page)+n<=32 and(best is None or n<best[0]):best=(n,p)
        if best is None:pages.append([]);p=len(pages)-1
        else:p=best[1]
        page=pages[p]
        for pattern in sorted(patterns):
            if pattern not in page:page.append(pattern)
        rec['page']=p;rec['encoded']=[(page.index(q)*1|flag,dx,dy)for q,flag,dx,dy in rec['parts']]
    assert len(pages)<=32,('CHR reservation exceeded',len(pages))
    chrdata=b''.join(b''.join(page)+bytes((32-len(page))*32)for page in pages)
    chrdata+=bytes(32768-len(chrdata))
    (ROOT/'chr/characters/final-fantasy.chr').write_bytes(chrdata)
    lines=['; Authenticated2.02 source pixels. Generated by prepare_final_fantasy_component_v1.py.',
           '.pushseg','.segment "FINAL_FANTASY_ART"','FfArtStart:','FfEntryRecord:']
    def byte(seq):return ' .byte '+','.join(str(i)for i in seq)
    for at in range(0,len(index),24):lines.append(byte(index[at:at+24]))
    lines+=['FfRecordLo:',byte(['<FfRecord'+str(i)for i in range(len(records))]),
            'FfRecordHi:',byte(['>FfRecord'+str(i)for i in range(len(records))])]
    sizes=[]
    for i,rec in enumerate(records):
        # Rebase each chunk's signed Y so dy bytes remain0..127; max15parts
        # permits a complete61-byte descriptor in the dedicated64-byte buffer.
        chunks=[]
        body=rec['kind']=='body'
        groups=[rec['encoded']]
        if body:groups=[[q for q in rec['encoded']if not q[0]&32],[q for q in rec['encoded']if q[0]&32]]
        for group in groups:
          for band in sorted({dy//96 for _,_,dy in group}):
            bandparts=[q for q in group if q[2]//96==band]
            for start in range(0,len(bandparts),15):chunks.append((band*96,bandparts[start:start+15]))
        data=[rec['page']|(128 if body else 0),len(chunks)]
        for ybase,parts in chunks:
            data += [len(parts)]if body else [len(parts),ybase&255,(ybase>>8)&255]
            for pattern,dx,dy in parts:
                if body:
                    assert (dx+24)%8==0 and (dy+44)%16==0
                    data +=[pattern,(dx+24)//8|((dy+44)//16)<<3]
                else:data +=[pattern,dx&255,(dy-ybase)&255]
        lines+=['FfRecord'+str(i)+':',byte(data)];sizes.append(len(data));rec['chunks']=len(chunks)
    lines+=['FfArtEnd:','.assert FfArtEnd-FfArtStart <= $1000,error,"FF ART allocation"','.popseg']
    (ROOT/'src/final_fantasy_art.inc').write_text('\n'.join(lines)+'\n')
    proof=dict(status='standalone authenticated assets; no host integration/native',source_audit=bind(audit),
               original_FF1=bind(ff),original_FF1_palette_file_offset=0x3ebb5,palette_rows=[[15,22,48,54],[15,40,24,33]],
               class_palette_rows=[0,0,1,1],entry_count=len(index),unique_records=len(records),used_CHR_pages=len(pages),
               encoded_ART_bytes=len(index)+2*len(records)+sum(sizes),body_black='exact original mask, optional shadow layer only',
               fire_ice_adaptation='same authored atlas, repaired stale out-of-bitmap frame rectangles; no new pixels',
               source_cells=facts,records=[dict(id=i,page=r['page'],parts=len(r['parts']),chunks=r['chunks'],kind=r['kind'])for i,r in enumerate(records)],
               outputs=[bind(ROOT/'src/final_fantasy_art.inc'),bind(ROOT/'chr/characters/final-fantasy.chr')])
    assert proof['encoded_ART_bytes']<=4096,proof['encoded_ART_bytes']
    (OUT/'assets.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in ['entry_count','unique_records','used_CHR_pages','encoded_ART_bytes']}))
if __name__=='__main__':main()
