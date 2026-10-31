"""Export five authentic current-cart standing sprites as transparent PNGs."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_quick_transport_controls_v4 as T
N=R/'build/functional-roster-ready54-v1/joint';O=R/'build/quick-roster-extra-portraits-1030-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(m,**kw):
 for n,v in kw.items():
  if n in m.lab:m.set(n,v)
def call(m,n,**kw):return T.S.execute(m,n,**kw)
def physical(m):
 out=[];raw=m.bundle['raw'];tab=m.lab['ChrPhysicalMap'];bank=m.bank('ChrPhysicalMap')
 for i in range(8):
  value=m.ram[m.lab['CurrentCHRBank']+i];mode=m.ram[m.lab['X5ChrMode']+i]
  if mode&128 and m.get('X5WideChrActive'):
   page=512+((value+168)&255)if i==0 and mode==132 else(mode&3)*256+value
  else:page=m.ROM_banks[bank][(tab&8191)+value]
  out.append(page)
 return out
def palette(m):
 # Real producers queue their exact NES color indices; universal color is
 # transparent in this standalone body export.
 colors=[0]*32;a=m.lab['VRAM_Buffer1'];data=list(m.ram[a:a+m.get('VRAM_Buffer1_Offset')+1]);i=0
 while i<len(data)and data[i]:
  address=data[i]*256+data[i+1];length=data[i+2]&63
  for j,v in enumerate(data[i+3:i+3+length]):
   at=address+j
   if 0x3f00<=at<0x3f20:colors[at-0x3f00]=v&63
  i+=3+length
 return colors
def render(m,parts,colors):
 pages=physical(m);rom=m.bundle['raw'];pal=(R/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes();assert len(pal)>=192
 im=Image.new('RGBA',(256,256),(0,0,0,0))
 for y,tile,attr,x in reversed(parts):
  at=(tile&1)*4096+(tile&254)*16;page=pages[at//1024]
  data=rom[16+128*8192+page*1024+at%1024:16+128*8192+page*1024+at%1024+32]
  assert len(data)==32
  for dy in range(16):
   yy=15-dy if attr&128 else dy
   for dx in range(8):
    xx=7-dx if attr&64 else dx
    v=((data[yy//8*16+yy%8]>>(7-xx))&1)|(((data[yy//8*16+yy%8+8]>>(7-xx))&1)<<1)
    if v and 0<=x+dx<256 and 0<=y+dy<256:
     index=colors[16+4*(attr&3)+v];rgb=tuple(pal[index*3:index*3+3]);im.putpixel((x+dx,y+dy),(*rgb,255))
 box=im.getbbox();assert box
 return im.crop(box),pages
def main():
 assert not O.exists();O.mkdir();rows=[]
 for slug,name,slot,select in [('kamikaze-v1-mario','Kamikaze V1 Mario',0,3),('celeste-mario','Celeste Mario',0,4),('gb-pit','GB Pit',6,1),('doc-louis','Doc Louis',14,1),('mike-tyson','Mike Tyson',14,2)]:
  m=T.bus(N);base=T.C.H.U.setup(m.bundle,slot);m.ram[:0x8000]=bytes(base.m[:0x8000]);m.set('CurrentBank',m.tags[1]);m.set('CurrentBankC',m.tags[2])
  put(m,CrossoverMenuState=2,CrossoverMenuIndex=slot,SelectedCharacter=0,OperMode=0,FamilyMainCommit=1,VRAM_Buffer1_Offset=0,FmAlts=0,FmGroups=0,MarioVariant=0,MacVariant=0,PlayerFacingDir=1)
  call(m,'MenuResolveCharacter');call(m,'QueueSelection')
  for _ in range(select):
   put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);call(m,'CrossoverMenuInput')
  call(m,'DrawSelectionPreview');source='actual MenuResolveCharacter/QueueSelection/Select/DrawSelectionPreview OAM'
  count=m.get('CurrentOAMOffset');parts=[list(m.ram[512+i:516+i])for i in range(0,count,4)]
  if slot==14:
   # The menu deliberately uses enlarged head portraits. For the requested
   # standing body, select the genuine current boxing idle frame X=0.
   call(m,'MacRosterSetPose',X=0);call(m,'MacRosterPublish')
   ptr=m.get('SmPosePtr')+256*m.ram[m.lab['SmPosePtr']+1];bank=m.bank('MacRosterArtBegin');data=m.ROM_banks[bank];at=ptr&8191;size=data[at];assert size%4==0
   record=list(data[at:at+size+1]);parts=[]
   for j in range(1,size+1,4):
    tile,attr,y,x=record[j:j+4];parts.append([96+(y if y<128 else y-256),tile,attr,96+(x if x<128 else x-256)])
   source='actual MacRosterSetPose(X=0 standing idle), immutable ROM pose record, MacRosterPublish'
  colors=palette(m);im,pages=render(m,parts,colors);path=O/(slug+'.png');im.save(path)
  rows.append(dict(name=name,id=slug,path=str(path.resolve()),sha256=sha(path),size=list(im.size),mode='RGBA',transparent=True,source=source,source_ROM=str((N/'candidate.nes').resolve()),source_ROM_sha256=sha(N/'candidate.nes'),menu_index=slot,Select_count=select,actual_sprite_parts=parts,physical_sprite_CHR_pages=pages,NES_sprite_palette=colors[16:],notes='Current source-authenticated Mario skin'if slot==0 and select==3 else'Current source-adapted Doc boxing body'if slug=='doc-louis'else'Current authentic source sprite'))
 (O/'mapping.json').write_text(json.dumps(dict(source_ROM_sha256=sha(N/'candidate.nes'),native=False,ROM_modified=False,RGB_palette=str((R/'tools/Windows/NEXXT 3.0/defaults/nes.pal').resolve()),images=rows),indent=2)+'\n',newline='\n')
 print(json.dumps(dict(mapping=str(O/'mapping.json'),images=[{k:v for k,v in q.items()if k in['name','path','size','sha256']}for q in rows])))
if __name__=='__main__':main()
