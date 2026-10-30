"""Decode original native Arthur metasprites; no screenshots are cropped."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/arthur-source-v1'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from arthur_source_map_v1 import load,ROM,EXPECTED
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CAP=OUT/'native/original-discovery-v1'
PAL=ROOT/'tools/Windows/NEXXT 3.0/defaults/nes.pal'

def main():
    rom=load();bank=rom[16+4*16384:16+5*16384]
    chrpath=CAP/'f1100.chr.bin';palettepath=CAP/'f1100.palette.bin'
    chrdata=chrpath.read_bytes()[:4096];palette=palettepath.read_bytes()
    assert chrdata[:0x700]==rom[16:16+0x700]
    rgbraw=PAL.read_bytes();rgb=[tuple(rgbraw[i:i+3])for i in range(0,192,3)]
    def word(at):return int.from_bytes(bank[at-0x8000:at-0x8000+2],'little')
    def data(at,n):return list(bank[at-0x8000:at-0x8000+n])
    def signed(a):return a if a<128 else a-256
    poses=sorted(set(range(64))|set(range(0x40,0x46))|{0x4f,0x56,0x66,0x76,0x77,0x86,0x87,0xa0,0xa1,0xa2,0xa9,0xaa,0xf8,0xf9})
    records=[];tiles=set()
    for pose in poses:
        at=word(0x81eb+pose*2);count,layout=data(at,2);raw=data(at,2+count*2)
        assert 0<count<=16 and 0x8000<=at<0xc000
        xyat=word(0x9491+layout*2);xy=data(xyat,count*2)
        parts=[]
        for i in range(count):
            tile,attr=raw[2+i*2:4+i*2];x,y=xy[i*2:i*2+2]
            if tile!=255:tiles.add(tile)
            parts.append(dict(tile=tile,attribute=attr,x=signed(x),y=signed(y)))
        keys={}
        for key in (0,1,2,3,8):
            pat=word(0x9ae7+key*2);keys[str(key)]=dict(address=pat,values=data(pat,count))
        records.append(dict(pose=pose,address=at,raw=raw,layout=layout,layout_address=xyat,coordinates=xy,parts=parts,attribute_rows=keys))
    tileproof=[]
    for tile in sorted(tiles):
        block=chrdata[tile*16:tile*16+16];matches=[];at=0
        while(at:=rom.find(block,at))>=0:
            if at>=16:matches.append(at)
            at+=1
        assert matches,(tile,'captured tile must occur in exact original PRG')
        tileproof.append(dict(tile=tile,sha256=hashlib.sha256(block).hexdigest(),original_ROM_offsets=matches))
    def render(pose,key):
        r=next(r for r in records if r['pose']==pose);im=Image.new('RGBA',(160,160))
        attrs=r['attribute_rows'][str(key)]['values']
        for i in reversed(range(len(r['parts']))):
            p=r['parts'][i];tile=p['tile']
            if tile==255:continue
            attr=p['attribute']|attrs[i]
            for yy in range(8):
                sy=7-yy if attr&128 else yy
                for xx in range(8):
                    sx=7-xx if attr&64 else xx;at=tile*16+sy
                    value=(chrdata[at]>>(7-sx)&1)|((chrdata[at+8]>>(7-sx)&1)<<1)
                    if value:im.putpixel((64+p['x']+xx,65+p['y']+yy),rgb[palette[16+(attr&3)*4+value]&63]+(255,))
        return im.crop(im.getbbox())
    examples=[('armor idle',0,8),('armor walk',1,8),('armor jump',0x12,8),('armor throw',8,8),('crouch',0x10,8),
      ('naked idle',0x20,2),('death',0x1a,1),('lance',0x40,0),('dagger',0x42,0),('torch',0x44,2),
      ('axe',0x36,1),('cross',0x4f,0),('flame',0xa1,0)]
    sheet=Image.new('RGBA',(7*88,2*124),(48,48,48,255));draw=ImageDraw.Draw(sheet);examplesproof=[]
    for i,(name,pose,key)in enumerate(examples):
        pic=render(pose,key);scale=min(3,76/pic.width,94/pic.height)
        view=pic.resize((round(pic.width*scale),round(pic.height*scale)),Image.Resampling.NEAREST)
        x=(i%7)*88+(88-view.width)//2;y=(i//7)*124+96-view.height
        sheet.alpha_composite(view,(x,y));draw.text(((i%7)*88+3,(i//7)*124+101),name,fill='white')
        examplesproof.append(dict(name=name,pose=pose,attribute_row=key,size=list(pic.size),RGBA_sha256=hashlib.sha256(pic.tobytes()).hexdigest()))
        if name=='armor idle':pic.save(OUT/'source-armor-idle.png')
    sheet.save(OUT/'source-art-contact-sheet.png')
    (OUT/'arthur-original-sprites.chr').write_bytes(chrdata)
    result=dict(status='AUTHENTIC_NATIVE_DESCRIPTOR_AND_STREAMED_CHR_EXPORT',original_ROM=str(ROM),original_ROM_sha256=EXPECTED,
      CHR=dict(path=str((OUT/'arthur-original-sprites.chr').resolve()),sha256=sha(OUT/'arthur-original-sprites.chr'),bytes=4096,
        common_initial_bytes=0x700,common_initial_exact_ROM_offset=16,native_capture_frame=1100),
      palette=dict(hardware_indices=list(palette),decoder=str(PAL.resolve()),decoder_sha256=sha(PAL)),
      descriptor_tables=dict(metasprite=0x81eb,layout=0x9491,attribute_row=0x9ae7,PRG_bank=4),
      records=records,tiles=tileproof,examples=examplesproof,
      bindings={str(p.resolve()):sha(p)for p in [ROM,chrpath,palettepath,CAP/'manifest.json',Path(__file__),PAL]},
      limits='Original 8x8 source records; no host8x16 conversion, shared palette quantization, CHR lease or native all-pose visibility claim.')
    p=OUT/'art-source.json';p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(poses=len(records),tiles=len(tiles),source_armor_RGBA_sha256=examplesproof[0]['RGBA_sha256'],art_proof_sha256=sha(p))))
if __name__=='__main__':main()
