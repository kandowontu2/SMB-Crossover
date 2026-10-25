"""Read every lossless frame, compare outdoor background cells across all routes.

Masks committed sprite rectangles. This is a candidate finder, not a claim that
all pixel changes are bugs. Original movies and packets are read only.
"""
from pathlib import Path
import csv, json, subprocess, hashlib, sys, time
import numpy as np
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/outdoor-green-review-e'
ROSTER=[('Mario',0,0),('Luigi',8,0),('Bill',3,0),('Lance',3,1),('Mega Man',1,0),('Bass',9,0),('Samus',2,0),('Link',4,0),('Simon',5,0),('Pit',6,0),('Rygar',7,0),('Ryu',10,0),('Sophia',11,0),('Scrooge',12,0)]

def rows(p):
 with p.open(newline='',encoding='utf-8')as f:return list(csv.DictReader(f))
def read(pipe,size):
 b=bytearray()
 while len(b)<size:
  part=pipe.read(size-len(b))
  if not part:break
  b.extend(part)
 return b
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def active(t):return t and all(int(t[k])==v for k,v in [('mode',1),('task',3),('engine',8),('areaType',1)])
def sheet(frames,path):
 out=Image.new('RGB',(4*256,((len(frames)+3)//4)*264),'#242424');d=ImageDraw.Draw(out)
 for n,(label,pixels)in enumerate(frames):
  x,y=n%4*256,n//4*264;out.paste(Image.fromarray(pixels),(x,y+24));d.text((x+3,y+3),label,fill='white')
 out.save(path)

def scan(name,ch,variant):
 p=R/'build/roster-through-2-2'/f'claude-final-video-{ch}-v{variant}-mmc3'
 trace={int(t['frame']):t for t in rows(p/'trace.csv')}
 dma={int(t['frame']):bytes.fromhex(t['oamHex'])for t in rows(p/'oam.csv')}
 scroll={}
 for t in rows(p/'scroll-writes.csv'):
  if int(t['address'])==0x2005 and int(t['dot'])>=257:scroll[int(t['frame'])]=int(t['value'])
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(p/'playthrough-lossless.mkv'),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 stats={};count=outdoor=0;old_oam=None;atlas=[];atlas_no=0;last_sample=-1000
 started=time.time()
 while True:
  raw=read(proc.stdout,256*240*3)
  if not raw:break
  assert len(raw)==256*240*3
  count+=1;pixels=np.frombuffer(raw,np.uint8).reshape(240,256,3);t=trace.get(count)
  # Writes are labelled with the preceding completed frame. Mask both owners
  # near a physical-frame boundary instead of mistaking a green sprite for BG.
  current=dma.get(count-1,dma.get(count,old_oam))
  if active(t):
   outdoor+=1
   cam=int(t['camera']);sx=scroll.get(count-1,scroll.get(count,cam%256))
   cam=sx+256*round((cam-sx)/256)
   # Only complete aligned world cells, keeping native screen Y (no Y scroll).
   left=(-cam)%16;width=(256-left)//16*16;col=(cam+left)//16
   crop=pixels[32:240,left:left+width]
   green=(crop[:,:,1]>100)&(crop[:,:,1].astype(np.int16)>crop[:,:,0].astype(np.int16)+22)&(crop[:,:,1].astype(np.int16)>crop[:,:,2].astype(np.int16)+35)
   valid=np.ones((208,width),np.uint8)
   for owner in (old_oam,current):
    if owner:
     a=np.frombuffer(owner,np.uint8).reshape(64,4)
     for yy,_,_,xx in a:
      y=int(yy)+1;x=int(xx)-left
      if y<240 and y+16>32 and x<width and x+8>0:valid[max(y-32,0):min(y-32+16,208),max(x,0):min(x+8,width)]=0
   shape=(13,16,width//16,16)
   den=valid.reshape(shape).sum(axis=(1,3));num=(green*valid).reshape(shape).sum(axis=(1,3))
   room=tuple(int(t[k])for k in ('world','level','area'))
   for ry,cx in np.argwhere(den>=128):
    key=room+(col+int(cx),int(ry)+2);n=int(num[ry,cx]);v=int(den[ry,cx]);fraction=n/v
    z=stats.get(key)
    if z is None:stats[key]=[n,v,fraction,count,cam,int(cx)*16+left,1]
    else:
     z[0]+=n;z[1]+=v;z[6]+=1
     if fraction>z[2]:z[2:6]=[fraction,count,cam,int(cx)*16+left]
   if count-last_sample>=120:
    last_sample=count;atlas.append((f'{name} {count/60.0988:.2f}s f{count}',pixels.copy()))
    if len(atlas)==48:
     atlas_no+=1;sheet(atlas,O/f'{name}-outdoor-{atlas_no}.png');atlas=[]
  old_oam=current
 err=proc.stderr.read().decode();assert proc.wait()==0,err
 if atlas:atlas_no+=1;sheet(atlas,O/f'{name}-outdoor-{atlas_no}.png')
 data=[dict(key=key,green=z[0],valid=z[1],maximum=z[2],frame=z[3],camera=z[4],screenX=z[5],observations=z[6])for key,z in stats.items()]
 result=dict(name=name,packet=str(p.relative_to(R)),decoded=count,outdoor=outdoor,cells=data,atlas_sheets=atlas_no,seconds=round(time.time()-started,2))
 (O/(name+'.json')).write_text(json.dumps(result,separators=(',',':')),encoding='utf-8')
 print('OUTDOOR_SCAN',name,count,outdoor,len(data),result['seconds'],flush=True)
 return result

def compare(results):
 bycell={}
 for result in results:
  for cell in result['cells']:bycell.setdefault(tuple(cell['key']),{})[result['name']]=cell
 candidates=[]
 for key,owners in bycell.items():
  for name,z in owners.items():
   refs=[(n,v)for n,v in owners.items()if n!=name and v['observations']>=3]
   if len(refs)<3 or z['maximum']<.20:continue
   no_green=[(n,v)for n,v in refs if v['green']/v['valid']<.025 and v['maximum']<.08]
   if len(no_green)<max(3,len(refs)*.65):continue
   candidates.append(dict(name=name,key=key,frame=z['frame'],maximum=z['maximum'],mean=z['green']/z['valid'],screenX=z['screenX'],reference_names=[n for n,v in no_green]))
 candidates.sort(key=lambda z:(-z['maximum'],-z['mean']))
 (O/'candidates.json').write_text(json.dumps(candidates,indent=2)+'\n',encoding='utf-8')
 print('GREEN_CANDIDATES',len(candidates),flush=True)

def main():
 assert not O.exists();O.mkdir()
 (O/'method.json').write_text(json.dumps(dict(tool_sha256=sha(Path(__file__)),scope='Every frame decoded; every active outdoor frame checked using aligned world cells, sprite masks and cross-character comparison. Candidate finder only; inspect actual images. Every two seconds of outdoors retained as contact sheets. Originals unchanged.',cap=500000000),indent=2)+'\n',encoding='utf-8')
 results=[]
 for name,ch,v in ROSTER:
  results.append(scan(name,ch,v));compare(results)
 (O/'index.json').write_text(json.dumps(dict(movies=[{k:v for k,v in r.items()if k!='cells'}for r in results],decoded=sum(r['decoded']for r in results),outdoor=sum(r['outdoor']for r in results),manual_review_complete=False),indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
