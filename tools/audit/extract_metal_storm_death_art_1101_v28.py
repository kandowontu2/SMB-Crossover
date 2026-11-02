"""Recover explosion packets using the original death state and renderer."""
import hashlib,json
from PIL import Image,ImageDraw
import metal_storm_cpu_1101_v2 as M
O=M.ROOT/'build/metal-storm-death-art-1101-v28'

def main():
 O.mkdir(exist_ok=True);c=M.boot()
 for t in range(600):M.frame(c,16 if t in [120,121,300,301,480,481] else 0)
 m=c.memory;resume=c.pc
 for a,v in {0x60:4,0x61:0,0x604:3,0x52c:0,0x5d0:0,0x648:0,0x660:0,0x630:0}.items():m[a]=v
 M.call(c,0xe5a2,x=4);c.pc=resume
 seen=set();packets=[];patterns=[];lookup={};images=[]
 pal=(M.ROOT/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes()
 for tick in range(100):
  pose=(m[0x4e0],m[0x4f8])
  if m[0x528]==2 and pose not in seen:
   seen.add(pose);r=M.machine();b=r.memory;b[:2048]=bytes(m[:2048]);b.regs[6:8]=[12,13];b.map()
   palette=bytes(m.ppuread(0x3f10+i) for i in range(16))
   table=b[0x800e]+256*b[0x800f];b[0x24]=table&255;b[0x25]=table>>8
   b[0x480]=112;b[0x498]=0;b[0x4b0]=96;b[0x4c8]=0;b[0x710]=0;b[0x711]=0;b[0x50]=0;b[0x42]=252
   b[0x200:0x300]=bytes([240,0,0,0])*64
   M.call(r,0xf282,x=0,y=0);b.regs[:6]=b[0x756:0x75c]
   assert r.y%4==0 and 0<r.y<=128,(pose,r.y)
   cells=[];im=Image.new('RGB',(96,96),'#18243a')
   for slot in range(r.y//4):
    y,t,a,x=b[0x200+slot*4:0x204+slot*4];at=(t&1)*4096+(t&254)*16
    raw=bytes(b.ppuread(at+i) for i in range(32))
    if raw not in lookup:lookup[raw]=len(patterns);patterns.append(raw)
    dx=x-112;dy=y+1-96
    cells.append(dict(dx=dx,dy=dy,pattern=lookup[raw],attributes=a,source_tile=t,source_chr_bank=b.ca(at)//1024))
    for yy in range(16):
     py=15-yy if a&128 else yy
     for xx in range(8):
      px=7-xx if a&64 else xx
      v=((raw[(py//8)*16+py%8]>>(7-px))&1)|(((raw[(py//8)*16+py%8+8]>>(7-px))&1)<<1)
      if v:
       col=palette[(a&3)*4+v]&63;rx=dx+xx+16;ry=dy+yy+16
       assert 0<=rx<96 and 0<=ry<96,(pose,dx,dy,rx,ry)
       im.putpixel((rx,ry),tuple(pal[col*3:col*3+3]))
   images.append(im);packets.append(dict(tick=tick,pose=list(pose),cells=cells,palette=list(palette),chr_registers=list(b.regs[:6])))
  M.frame(c,0)
 assert len(packets)==16,len(packets)
 sheet=Image.new('RGB',(4*192,4*212),'#18243a');draw=ImageDraw.Draw(sheet)
 for i,(p,im) in enumerate(zip(packets,images)):
  x=i%4*192;y=i//4*212;sheet.paste(im.resize((192,192),Image.Resampling.NEAREST),(x,y+20));draw.text((x+4,y+3),f"{p['pose'][0]}:{p['pose'][1]}  t={p['tick']}",fill='white')
 sheet.save(O/'explosion-preview.png');blob=b''.join(patterns);(O/'explosion.chr').write_bytes(blob)
 q=dict(passed=True,donor_sha256=M.EXPECTED,source_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest(),renderer='Original F282 with original live death pose and CHR requests',unique_patterns=len(patterns),CHR_bytes=len(blob),CHR_sha256=hashlib.sha256(blob).hexdigest(),maximum_cells=max(len(p['cells']) for p in packets),packets=packets,host_wired=False,scope='Controlled donor lethal contact and original renderer extraction; untimed CPU, not native raster or host gameplay proof. Patterns have no host allocation yet.')
 (O/'art.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='packets'}))
if __name__=='__main__':main()
