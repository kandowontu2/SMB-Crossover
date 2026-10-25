"""Independent actual-DMA source equipment pixel/OAM/CHR/admission check."""
from pathlib import Path
import json,csv,hashlib,argparse,collections
P=argparse.ArgumentParser()
for name in ('rom','output','evidence','reference','old-chr','new-chr','art-proof'):
 P.add_argument('--'+name,type=Path,required=True)
P.add_argument('--prefix',required=True);P.add_argument('--sha',required=True)
A=P.parse_args();D=A.evidence;O=A.output;O.mkdir(exist_ok=False)
rom=A.rom.read_bytes();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=A.reference.read_bytes();proof=json.loads(A.art_proof.read_text())
original_chr=src[16+131072:];chr=rom[16+1048576:]
assert sha(A.rom)==A.sha
assert hashlib.sha256(src).hexdigest()==proof['original_ROM_sha256']
old=A.old_chr.read_bytes();assert len(old)==24576
assert chr[604*1024:628*1024]==old
assert chr[628*1024:629*1024]==A.new_chr.read_bytes()[-1024:]

def pixels(raw,attr):
 for y in range(16):
  sy=15-y if attr&128 else y;at=sy//8*16+sy%8
  for x in range(8):
   bit=x if attr&64 else 7-x;c=(raw[at]>>bit&1)|((raw[at+8]>>bit&1)<<1)
   if c:yield x,y,c

def original_parts(pose):
 # Decode original variable-length source descriptors independently of packer.
 prg=src[16:16+131072];b=lambda a:prg[2*16384+(a&16383)];addr=0x8001+pose*2;at=b(addr)|b(addr+1)<<8;n=b(at);at+=1;attr=0;out=[]
 for i in range(n):
  y,t=b(at),b(at+1);at+=2
  if y&1==0:attr=b(at);at+=1
  x=b(at);at+=1;out.append((x-256 if x&128 else x,(y-256 if y&128 else y)//2,t,attr))
 return out
reports={}
for folder in sorted(D.glob(A.prefix+'-*')):
 if not folder.is_dir():continue
 draws=list(csv.DictReader((folder/'world-draws.csv').open()));data=(folder/'world-oam.bin').read_bytes();pals=(folder/'world-palettes.bin').read_bytes();assert len(data)%256==0 and len(pals)==len(data)//8;assert(folder/'physical-628.bin').read_bytes()==chr[628*1024:629*1024]
 eligibility={};partAdmission={};visible=0;frames=set();poses=set();maxline=0;occluded=0
 for d in draws:
  j=int(d['row'])-1;oam=data[j*256:j*256+256];pal=pals[j*32:j*32+32];qs=[tuple(oam[i:i+4])for i in range(0,256,4)];pose=int(d['pose']);face=int(d['face']);ox=int(d['x']);oy=int(d['y']);atr=int(d['attribute']);off=int(d['offset']);rot=int(d['rotation']);expected=proof['records'][str(pose)];assert len(expected)==int(d['count']);frames.add(j);poses.add((pose,face));parts=[]
  assert list(pal[25:28])==[0x16,0x30,0x27],('shared P2 changed',folder,d,list(pal[25:28]))
  for i,(t,a,y,x)in enumerate(expected):
   dx=x-256 if x&128 else x;dy=y-256 if y&128 else y
   if face==2:dx=-dx-8;a^=64
   xx=(ox+dx)&65535;yy=oy+dy;slot=((off+rot+i*4)&255)//4
   if off+len(expected)*4>255:continue
   if xx>=256 or not(0<=yy<240):assert qs[slot][0]==248,(folder,d,i,slot,qs[slot]);continue
   want=(yy,t,(a|atr)&0xf3,xx);assert qs[slot]==want,('actual DMA record differs',folder,d,i,slot,qs[slot],want)
   parts.append((slot,i,want));visible+=1
  # Actual intrinsic composite in hardware order vs original source colored pixels.
  actual={};native={};slots={p[0]for p in parts};linecounts={};eligible={p[1]:False for p in parts};colored={p[1]:[0,0]for p in parts}
  for slot,(y,t,a,x)in enumerate(qs):
   if y>=240:continue
   admitted=set()
   for sy in range(y+1,min(240,y+17)):
    if linecounts.get(sy,0)<8:admitted.add(sy)
    linecounts[sy]=linecounts.get(sy,0)+1;maxline=max(maxline,linecounts[sy])
   if slot not in slots:continue
   index=next(p[1]for p in parts if p[0]==slot);raw=chr[628*1024+(t&254)*16:628*1024+(t&254)*16+32]
   for px,py,c in pixels(raw,a):
    actual.setdefault((x-ox+px,y-oy+py),pal[16+(a&3)*4+c])
    colored[index][1]+=1
    if y+1+py in admitted:eligible[index]=True;colored[index][0]+=1
  for i,v in eligible.items():
   eligibility[(pose,face,i)]=eligibility.get((pose,face,i),False)or v;occluded+=not v
   key=(pose,face,i,'HUD'if oy==23 else'world');q=partAdmission.setdefault(key,[0,0,0,0]);q[0]+=1;q[1]+=v;q[2]+=colored[i][0];q[3]+=colored[i][1]
  for dx,dy,t,a in original_parts(pose):
   if face==2:dx=-dx-8;a^=64
   raw=original_chr[(21 if t&1 else 0)*4096+(t&254)*16:(21 if t&1 else 0)*4096+(t&254)*16+32]
   for x,y,c in pixels(raw,a):
    if 0<=ox+dx+x<256 and 0<=oy+dy+y<240:native.setdefault((dx+x,dy+y),[pal[29],pal[25],pal[26]][c-1])
  assert actual==native,('source pixel composition mismatch',folder,d,len(actual),len(native),list((set(actual.items())^set(native.items())))[:10])
 report={'frames_with_world':len(frames),'world_draws':len(draws),'actual_DMA_parts':visible,'poses_and_facings':sorted(map(list,poses)),'max_sprites_on_scanline':maxline,'temporarily_unadmitted_parts':occluded,'all_observed_source_parts_ever_admitted':all(eligibility.values()),'never_admitted':[list(k)for k,v in eligibility.items()if not v],'per_part_admission':[{'pose':k[0],'facing':k[1],'part':k[2],'role':k[3],'observed_frames':v[0],'any_pixel_admitted_frames':v[1],'frame_ratio':v[1]/v[0],'admitted_colored_pixels':v[2],'observed_colored_pixels':v[3],'pixel_ratio':v[2]/v[3]}for k,v in sorted(partAdmission.items())],'source_pixels_and_geometry_exact':True,'physical_page628_exact':True,'shared_palette2_unchanged':True,'files':{n:sha(folder/n)for n in ['world-draws.csv','world-oam.bin','world-palettes.bin','physical-628.bin']}}
 reports[folder.name]=report
 assert report['all_observed_source_parts_ever_admitted'],report
assert len(reports)==8, ('Expected four turtles/both modes',len(reports))
out={'passed':True,'ROM_sha256':sha(A.rom),'original_ROM_sha256':hashlib.sha256(src).hexdigest(),'old_body_primary_prefix_bytes_unchanged':24576,'checker_sha256':sha(Path(__file__)),'runs':reports,'scope':'Read-only actual DMA on explicitly seeded native equipment components. Original source colored pixel masks and OAM geometry/flips exact; declared shared-palette hue adaptation; native scanline admission measured. No original audio/untouched campaign parity claim.'};(O/'proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':True,'ROM_sha256':out['ROM_sha256'],'runs':{k:{'draws':v['world_draws'],'parts':v['actual_DMA_parts'],'max_sprites_per_scanline':v['max_sprites_on_scanline'],'minimum_part_frame_ratio':min(x['frame_ratio']for x in v['per_part_admission']),'minimum_part_pixel_ratio':min(x['pixel_ratio']for x in v['per_part_admission'])}for k,v in reports.items()}},indent=2))
