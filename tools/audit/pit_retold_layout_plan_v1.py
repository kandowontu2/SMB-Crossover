"""Measure exact737d Pit alternate storage without changing art/ROM/source."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit'),str(R/'tools/reference')]
from PIL import Image
import prepare_pit_retold_assets_v1 as A
import build_expanded_assets as G
from sunny_integrated_controls_v1 import *
P=R/'build/kamikaze-mario-host-v4/candidate.nes'
O=R/'build/pit_retold_layout_plan_v1.json'

def source(frame,folder):
 p=R/'build'/folder/f'pit-{frame}';data=p.with_suffix('.chr').read_bytes()
 oam=p.with_suffix('.oam').read_bytes();pal=p.with_suffix('.pal').read_bytes()
 parts=[oam[i*4:i*4+4]for i in range(8,14)if oam[i*4]<240]
 left=min(z[3]for z in parts);top=min(z[0]+1 for z in parts);pics=[]
 for alternate in[False,True]:
  pic=Image.new('RGBA',(24,40))
  for sy,t,a,sx in parts:
   tile=bytes(PATCH.get(16+t*16+j,dict(value=data[t*16+j]))['value']for j in range(16))if alternate else data[t*16:t*16+16]
   for y in range(8):
    yy=7-y if a&128 else y
    for x in range(8):
     xx=7-x if a&64 else x
     v=(tile[yy]>>(7-xx)&1)|((tile[yy+8]>>(7-xx)&1)<<1)
     if v:pic.putpixel((sx-left+x,sy+1-top+y),G.RGB[pal[16+(a&3)*4+v]]+(255,))
  pics.append(pic)
 return pics

def target(pose):
 if pose.startswith('FLAP'):return target(G.PIT_FLIGHT_BASE[pose])
 if pose=='WALKSTEP':return target('STAND')
 frames={'STAND':300,'JUMP':457,'CROUCH':330,'UP':512,'DIAGUP':512,'THROW':405,'CROUCHSHOOT':330,'JUMPSHOOT':462,'JUMPUP':512,'HURT':457,'DIE':330}
 if pose.startswith('WALK'):
  frame={'WALK1':405,'WALK2':415,'WALK3':425}[pose];folder='reference-native'
 else:
  frame=frames.get(pose,300);folder='reference-combat'
  if 'ATTACK'in pose:frame=330 if pose.startswith('CROUCH') else 457 if pose.startswith('JUMP') else 300
 old,new=source(frame,folder);bb=old.getbbox();width,height=bb[2]-bb[0],bb[3]-bb[1]
 # Keep the existing host's original-source embedding and original OAM grid.
 # Include every new pixel even if it lies outside the old opaque bounds.
 out=Image.new('RGBA',(96,80));origin=(40-width//2-bb[0],64-height-bb[1])
 if pose=='JUMPUP':
  crop=new.crop((bb[0],bb[1],bb[0]+width,bb[1]+height));crop.paste((0,0,0,0),(0,16,crop.width,crop.height))
  lo,ln=source(457,'reference-combat');lb=lo.getbbox();legs=ln.crop((lb[0],lb[1]+16,lb[0]+18,lb[1]+24))
  crop.alpha_composite(legs,(0,16));out.alpha_composite(crop,(40-width//2,64-height))
 else:out.alpha_composite(new,origin)
 if pose=='CROUCHSHOOT':
  ao,an=source(405,'reference-combat');ab=ao.getbbox();arm=an.crop((ab[0]+9,ab[1]+9,ab[0]+16,ab[1]+17))
  # Existing authored crouching-bow adaptation, not a native Retold timeline.
  oldcenter=(width+5)//2;out=Image.new('RGBA',(96,80))
  out.alpha_composite(new,(40-oldcenter-bb[0],64-height-bb[1]))
  out.alpha_composite(arm,(40-oldcenter+width-2,64-height+6))
 if 'ATTACK'in pose:
  phase=int(pose[-1])-1;hammer=G.weapons('PIT')[8].rotate((90,0,-90)[phase],expand=True)
  out.alpha_composite(hammer,(41+(0,8,9)[phase],64-height+(-7,3,11)[phase]))
 return out

def encode(values):
 return bytes(sum((values[y][x]>>plane&1)<<(7-x)for x in range(8))for block in range(2)for plane in range(2)for y in range(block*8,block*8+8))

def main():
 global PATCH
 assert not O.exists();PATCH,_=A.ips();b=scoped_load(P)
 assert sha(P)=='737d71af449b70a73b1d13f228efb6cfa819ea027219f605344861fb0e2b0624'
 G.ROLE='PIT';G.COLORS=G.targets('PIT')
 def data(n,count):return b['raw'][location(b,n):location(b,n)+count]
 banks=data('XgPITBanks',252);mapping=data('ChrPhysicalMap',256)
 constraints={};conflicts=[];coverage=[];old_exact=[];records=set();patterns=set()
 # All existing weapon-prefix pairs must remain available simultaneously.
 for logical in set(banks):
  page=mapping[logical]
  for t in range(0,22,2):constraints[(logical,t)]=b['raw'][1048592+page*1024+t*16:1048592+page*1024+t*16+32]
 for index in range(252):
  pose=G.POSES[index%84];new=G.layers(target(pose));old=G.layers(G.body('PIT',pose,index//84))
  ptr=data('XgPITRightLo',252)[index]+256*data('XgPITRightHi',252)[index]
  at=16+31*8192+ptr-0xc000;record=b['raw'][at:at+1+b['raw'][at]];records.add(ptr)
  actual={p:[[0]*96 for _ in range(80)]for p in[0,2,3]};covered=set();parts=[]
  for j in range(1,len(record),4):
   t,attr,yy,xx=record[j:j+4];xx=xx if xx<128 else xx-256;yy=yy if yy<128 else yy-256;p=attr&3
   assert p in actual,(pose,p)
   raw=b['raw'][1048592+mapping[banks[index]]*1024+t*16:1048592+mapping[banks[index]]*1024+t*16+32]
   desired=[[0]*8 for _ in range(16)]
   for y in range(16):
    for x in range(8):
     tx,ty=32+xx+x,32+yy+y;sx=7-x if attr&64 else x;sy=15-y if attr&128 else y
     v=(raw[(sy//8)*16+sy%8]>>(7-sx)&1)|((raw[(sy//8)*16+8+sy%8]>>(7-sx)&1)<<1)
     if 0<=tx<96 and 0<=ty<80:
      if v:actual[p][ty][tx]=v
      covered.add((p,tx,ty));desired[sy][sx]=new[p][ty][tx]
   pattern=encode(desired);key=(banks[index],t);patterns.add(pattern)
   if key in constraints and constraints[key]!=pattern:conflicts.append([index,pose,banks[index],t])
   else:constraints[key]=pattern
   parts.append((t,attr,yy,xx))
  if actual!=old:old_exact.append([index,pose])
  missed=[(p,x,y)for p in new for y in range(80)for x in range(96)if new[p][y][x]and(p,x,y)not in covered]
  if missed:coverage.append(dict(index=index,pose=pose,missing_pixels=len(missed),bbox=[min(v[1]for v in missed),min(v[2]for v in missed),max(v[1]for v in missed),max(v[2]for v in missed)]))
 out=dict(status='READ_ONLY_MEASUREMENT_NOT_ALLOCATION_OR_CANDIDATE',parent=sha(P),raw_character=6,
  used_logical_CHR=sorted(set(banks)),used_physical_CHR=sorted(set(mapping[x]for x in banks)),
  old_record_unique=len(records),old_generated_pixel_mismatches=old_exact,
  pure_CHR_replacement_constraint_conflicts=conflicts,pure_CHR_replacement_uncovered_new_pixels=coverage,
  unique_new_pair_patterns=len(patterns),unused_requested_region808_831_zero=b['raw'][1048592+808*1024:1048592+832*1024]==bytes(24*1024),
  free_C31_DDE6_DFFF=b['raw'][16+31*8192+0x1de6:16+32*8192]==bytes([255])*538,
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),Path(G.__file__),P,P.with_suffix('.dbg'),P.with_suffix('.lbl'),R/'build/pit-retold-assets-v1/handoff.json']})
 O.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in['bindings','pure_CHR_replacement_constraint_conflicts','pure_CHR_replacement_uncovered_new_pixels','old_generated_pixel_mismatches']}));print('conflicts',len(conflicts),'uncovered',len(coverage),'oldMismatch',len(old_exact))
if __name__=='__main__':main()
