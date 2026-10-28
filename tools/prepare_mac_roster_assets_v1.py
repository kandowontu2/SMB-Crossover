"""Build credited Mac/Doc/Tyson source-derived assets, without shared integration.

Doc is an expressly adapted boxing set, not an original NES boxing animation.
Only owned mac-roster* assets and src/mac_roster_data.inc are written.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
from PIL import Image, ImageOps, ImageDraw

R=Path(__file__).resolve().parents[1]
A=R/'chr/characters'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCES={
 'mac':dict(file='mac-roster-source-126765.png',sha256='61bfc5addb2dae7c9404d4ce0ed5d032eba75eb0741b83210176af62bb4f7b58',
  page='https://www.spriters-resource.com/custom_edited/punchoutcustoms/asset/126765/',credit='MisterMike, Little Mac (Zelda 2-Style), 2020'),
 'doc':dict(file='mac-roster-source-32930.png',sha256='ffd346d5011963d0f7aa65b529f3d2d90ffb05d6167b910ed7aa93bbd1c9b1de',
  page='https://www.spriters-resource.com/nes/punchout/asset/32930/',credit='Nintendo; rip Solink / Tox2564'),
 'tyson':dict(file='mac-roster-source-32931.png',sha256='0d6cd570db1c2ed707c593dab54656ead61bd04be73c28fcaf01295c6459ab0c',
  page='https://www.spriters-resource.com/nes/punchout/asset/32931/',credit='Nintendo; rip evildevil / Tox2564'),
}
# Exact authored sheet cells; green/magenta are sheet transparency, never ink.
MAC={
 'idle':(1,11,17,43),'walk0':(29,11,45,43),'walk1':(46,11,62,43),
 'walk2':(63,11,79,43),'duck':(84,11,100,43),'jump0':(117,11,133,43),
 'jump1':(134,11,150,43),'hurt':(155,11,171,43),'pickup':(188,11,204,43),
 'victory':(264,11,280,43),'windup':(1,73,25,105),'punch':(26,73,58,105),
 'duckpunch':(67,73,99,105),'downthrust':(127,73,143,105),
 'uppercut':(190,73,206,105),'guard':(1,118,17,150),
}
HEAD={n:(4,1,15,15) for n in MAC}
HEAD.update(duck=(3,10,14,25),jump0=(3,10,14,25),hurt=(1,1,13,15),
 windup=(7,1,19,15),punch=(8,1,20,15),duckpunch=(7,12,19,26),
 downthrust=(1,4,13,25),uppercut=(5,1,16,16),pickup=(3,0,15,14),victory=(3,0,15,14))
PALETTE_RGB={
 'mac':[(0,0,0,0),(252,188,176,255),(0,80,0,255),(76,220,72,255)],
 'doc':[(0,0,0,0),(146,52,4,255),(0,0,0,255),(255,255,255,255)],
 'tyson':[(0,0,0,0),(115,80,5,255),(0,0,0,255),(146,52,4,255)],
}
NES_PALETTES={'mac':[0x36,0x0a,0x2a],'doc':[0x17,0x0f,0x30],'tyson':[0x18,0x0f,0x16]}

def indexed(im,mapping,background=()):
    out=Image.new('L',im.size,0)
    for y in range(im.height):
        for x in range(im.width):
            p=im.getpixel((x,y))
            if len(p)==4 and p[3]==0 or p[:3] in background:continue
            assert p[:3] in mapping,('Unmapped source color',p,x,y)
            out.putpixel((x,y),mapping[p[:3]])
    return out

def mac_frames(im):
    mapping={(252,188,176):1,(0,80,0):2,(76,220,72):3}
    return {n:indexed(im.crop(box),mapping,[(0,128,0),(128,0,128)]) for n,box in MAC.items()}

def doc_frames(mac,source):
    # Native Doc's profile head/neck, mirrored to face the supplied rightward
    # Mac scaffold. No Mac face, bicycle/wheels or trainer torso is substituted.
    head=source.crop((39,260,56,279))
    head=indexed(head,{(0,0,0):2,(93,0,16):1,(146,52,4):1,(255,255,255):3},[(99,154,255)])
    head=ImageOps.mirror(head).resize((13,15),Image.Resampling.NEAREST)
    frames={}
    for name,im in mac.items():
        body=im.resize((round(im.width*1.25),im.height),Image.Resampling.NEAREST)
        x0,y0,x1,y1=HEAD[name]
        x0,x1=round(x0*1.25),round(x1*1.25)
        ImageDraw.Draw(body).rectangle((x0,y0,x1-1,y1-1),fill=0)
        # Native head gives Doc his larger jaw/moustache; stockier authored
        # torso and actual gesture scaffold supply all distinct boxing poses.
        hx=(x0+x1-head.width)//2
        body.paste(head,(hx,y0),head.point(lambda v:255 if v else 0))
        frames[name]=body
    return frames

def tyson_frames(im):
    boxes={n:(c*52,0,(c+1)*52,120)for n,c in
        [('idle',0),('walk0',1),('walk1',2),('walk2',3),('guard',6),('windup',7),('uppercut',12)]}
    boxes.update(duck=(451,129,501,257),hurt=(305,129,359,257),
        punch=(501,129,552,257),duckpunch=(451,129,501,257),
        jump0=(104,129,156,257),jump1=(156,129,208,257),
        pickup=(575,0,626,120),victory=(626,0,675,120),
        downthrust=(334,273,395,380),uppercut=(552,129,608,257))
    frames={};meta={}
    # Three NES sprite colors: retain skin/ink/gloves. Original dark-green
    # trunks become black and tiny eye/teeth highlights become skin. This is
    # an explicit palette reduction, not exact-original color fidelity.
    mapping={(0,0,0):2,(115,80,5):1,(146,52,4):3,(23,68,23):2,(255,255,255):1,
             (58,35,8):2}
    for name,box in boxes.items():
        crop=im.crop(box)
        # Sheet captions are white too; actual eye/teeth pixels border skin.
        # Reject detached caption pixels rather than include them as body art.
        for y in range(crop.height):
            for x in range(crop.width):
                if crop.getpixel((x,y))[:3]==(255,255,255):
                    near=any(crop.getpixel((xx,yy))[:3] in [(115,80,5),(146,52,4),(58,35,8)]
                        for yy in range(max(0,y-2),min(crop.height,y+3))
                        for xx in range(max(0,x-2),min(crop.width,x+3)))
                    if not near:crop.putpixel((x,y),(0,0,0,0))
        cell=indexed(crop,mapping,[(52,194,142),(138,126,255)])
        bounds=cell.getbbox();assert bounds
        cell=cell.crop(bounds)
        size=(max(1,round(cell.width*3/8)),max(1,round(cell.height*3/8)))
        frames[name]=cell.resize(size,Image.Resampling.NEAREST)
        meta[name]=dict(source_box=box,opaque_bbox=bounds,uniform_scale='3/8 nearest-neighbor',output_size=size)
    return frames,meta

def tile_bytes(im,x,y):
    out=bytearray()
    for half in (0,8):
        for plane in (0,1):
            for dy in range(8):
                out.append(sum(((im.getpixel((x+dx,y+half+dy))>>plane)&1)<<(7-dx) for dx in range(8)))
    return bytes(out)

def main():
    for q in SOURCES.values():assert sha(A/q['file'])==q['sha256']
    sources={n:Image.open(A/q['file']).convert('RGBA') for n,q in SOURCES.items()}
    mac=mac_frames(sources['mac']);doc=doc_frames(mac,sources['doc'])
    tyson,tyson_meta=tyson_frames(sources['tyson'])
    families={'mac':mac,'doc':doc,'tyson':tyson}
    CHR=bytearray(40*1024);records=[];pages=[];family_offsets={};family_frames={}
    # Source-only portraits: Mac's authored face, original native Doc portrait,
    # original Tyson mugshot. No web art from an uncredited source is mixed in.
    portraits={
      'mac':mac['idle'].crop((3,1,15,17)).resize((24,32),Image.Resampling.NEAREST),
      'doc':indexed(sources['doc'].crop((784,8,811,47)),
        {(0,0,0):2,(58,35,8):1,(115,80,5):1,(146,52,4):1,(255,255,255):3},[(90,205,78)]).resize((20,32),Image.Resampling.NEAREST),
      'tyson':indexed(sources['tyson'].crop((608,227,688,307)),
        {(0,0,0):2,(115,80,5):1,(58,35,8):1,(146,52,4):3,(255,255,255):1},[(138,126,255)]).resize((24,24),Image.Resampling.NEAREST),
    }
    def pack_frame(family,name,im,page,slots,forced=False):
        # Match native Player origin: feet at +32 and center at +8. Wide
        # authored punches keep their original right-reaching alignment.
        left=(16-im.width)//2 if family=='tyson' else(-2 if family=='doc' else 0)
        if name=='portrait':left=(16-im.width)//2
        top=32-im.height
        canvas=Image.new('L',((im.width+7)//8*8,(im.height+15)//16*16))
        canvas.paste(im,(0,0))
        cells=[]
        for y in range(0,canvas.height,16):
            for x in range(0,canvas.width,8):
                part=canvas.crop((x,y,x+8,y+16))
                if part.getbbox():cells.append((x,y,tile_bytes(canvas,x,y)))
        assert cells and len(cells)<=10,(family,name,'Native body reservation',len(cells))
        needed=len({b for x,y,b in cells if b not in slots})
        if len(slots)+needed>32:
            assert not forced;page=len(pages);pages.append({});slots=pages[page]
        data=[]
        for x,y,b in cells:
            if b not in slots:slots[b]=len(slots)
            slot=slots[b];CHR[page*1024+slot*32:page*1024+(slot+1)*32]=b
            data.append(dict(tile=slot*2,x=left+x,y=top+y))
        index=len(records)
        records.append(dict(id=index,family=family,name=name,page=668+page,parts=data,
            size=im.size,origin_offset=[left,top],max_parts=len(data),indexed_sha256=hashlib.sha256(im.tobytes()).hexdigest()))
        return page,slots,index
    for family,frames in families.items():
        family_offsets[family]=len(records);family_frames[family]={};page=len(pages);pages.append({});slots=pages[page]
        for name,im in frames.items():
            page,slots,index=pack_frame(family,name,im,page,slots)
            family_frames[family][name]=index
    assert len(pages)<=36
    # Keep the already-qualified original star pickup page704 byte-exact.
    original=(A/'little-mac.chr').read_bytes();assert len(original)==len(CHR)
    CHR[36*1024:37*1024]=original[36*1024:37*1024]
    portrait_ids=[]
    for i,(family,im)in enumerate(portraits.items()):
        _,_,idx=pack_frame(family,'portrait',im,37+i,{},forced=True);portrait_ids.append(idx)
    (A/'mac-roster.chr').write_bytes(CHR)
    lines=['; Generated by tools/prepare_mac_roster_assets_v1.py; credited source pixels.',
           '.pushseg','.segment "MAC_ROSTER_ART"','MacRosterArtBegin:']
    for row in records:
        for facing in ('R','L'):
            lines.extend([f'MacRosterFrame{row["id"]}{facing}:',f' .byte {4*len(row["parts"])}'])
            for c in row['parts']:
                x=c['x'] if facing=='R'else 8-c['x'];attr=0 if facing=='R'else 0x40
                lines.append(f' .byte MetaspriteVramOffset{{${c["tile"]:02x}}}, {{SPRITE_BANK_0}}, ${attr:02x}, {c["y"]}, {x}')
    for facing in ('R','L'):
        for suffix,sigil in [('Lo','<'),('Hi','>')]:
            lines.extend([f'MacRoster{facing}{suffix}:',' .byte '+','.join(f'{sigil}MacRosterFrame{q["id"]}{facing}'for q in records)])
    lines.extend(['MacRosterChrLow:',' .byte '+','.join(str(q['page']&255)for q in records),
                  'MacRosterPortraitFrames:',' .byte '+','.join(map(str,portrait_ids))])
    names=list(mac)
    for name in names:
        lines.extend(['MacRosterPose_'+name+':',' .byte '+','.join(str(family_frames[f][name])for f in families)])
    lines.extend(['MacRosterArtEnd:',
        '.assert MacRosterArtEnd-MacRosterArtBegin<=$1d40,error,"Reserved94 C2C0..DFFF"',
        '.popseg',''])
    (R/'src/mac_roster_data.inc').write_text('\n'.join(lines),newline='\n')
    # Independent byte->pixel round trip for every emitted cell, both facings.
    for row in records:
        im=portraits[row['family']]if row['name']=='portrait'else families[row['family']][row['name']]
        right={};left={}
        for c in row['parts']:
            off=(row['page']-668)*1024+c['tile']*16;b=CHR[off:off+32]
            ox=c['x']-row['origin_offset'][0];oy=c['y']-row['origin_offset'][1]
            for y in range(16):
                half=y//8;dy=y%8
                for x in range(8):
                    v=((b[half*16+dy]>>(7-x))&1)|(((b[half*16+8+dy]>>(7-x))&1)<<1)
                    expected=im.getpixel((ox+x,oy+y))if ox+x<im.width and oy+y<im.height else 0
                    assert v==expected
                    if v:
                        right[c['x']+x,c['y']+y]=v
                        left[8-c['x']+7-x,c['y']+y]=v
        assert left=={(15-x,y):v for (x,y),v in right.items()},'Independent left world-coordinate raster'
    # A single concrete frame/portrait review sheet; no frame-file trees.
    sheet=Image.new('RGBA',(8*112,7*116),(30,35,42,255));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(records):
        im=portraits[row['family']]if row['name']=='portrait'else families[row['family']][row['name']]
        rgba=Image.new('RGBA',im.size)
        for y in range(im.height):
            for x in range(im.width):rgba.putpixel((x,y),PALETTE_RGB[row['family']][im.getpixel((x,y))])
        x=(i%8)*112;y=(i//8)*116;image=rgba.resize((rgba.width*2,rgba.height*2),Image.Resampling.NEAREST)
        sheet.alpha_composite(image,(x+(112-image.width)//2,y+14))
        draw.text((x+2,y+2),f'{row["family"]}:{row["name"]}',fill='white')
    sheet.save(A/'mac-roster-review.png')
    manifest=dict(source_only=True,native_run=False,sources=SOURCES,variant_order=list(families),
        source_scope=dict(mac='Exact requested authored source cells, no new painted pixels.',
            doc='Explicit new adapted boxing set: original Doc profile head/neck, stockier125% width and requested Mac pose scaffold. Not original NES boxing frames, not a bicycle gameplay crop.',
            tyson='Original NES combat poses, uniform3/8 nearest sampling; source green trunks->black and eye/teeth highlights->skin for one3-color sprite palette. Not exact original size/colors.'),
        NES_palettes=NES_PALETTES,frames=records,family_frames=family_frames,
        body_pages=[668,668+len(pages)-1],body_page_count=len(pages),star_page=704,
        original_star_page_exact=CHR[36*1024:37*1024]==original[36*1024:37*1024],
        portrait_pages=[705,706,707],portrait_frames=portrait_ids,CHR_bytes=len(CHR),
        all_cells_roundtrip_exact=True,left_facing_raster_mirror_exact=True,
        maximum_body_parts=max(q['max_parts']for q in records),
        both_facings='Same CHR cells, source-exact Hflip and x=8-originalX about player center7.5.',
        tyson_source_frames=tyson_meta,
        files={str(p.relative_to(R)):sha(p)for p in [Path(__file__),A/'mac-roster.chr',A/'mac-roster-review.png',R/'src/mac_roster_data.inc']})
    (A/'mac-roster-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(CHR_bytes=len(CHR),body_pages=len(pages),frames=len(records),max_parts=manifest['maximum_body_parts'],manifest_sha256=sha(A/'mac-roster-manifest.json'))))

if __name__=='__main__':main()
