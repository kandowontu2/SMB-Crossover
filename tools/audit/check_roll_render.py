"""Compare actual committed Roll sprite pixels with the supplied mobile art."""
from pathlib import Path
import argparse,csv,hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
COLORS={(8,8,8):15,(248,184,0):40,(248,56,0):22,(248,224,168):55,(0,168,0):26,(248,248,248):48,(168,16,0):23}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);a=p.parse_args();folder=a.folder.resolve()
 m=json.loads((ROOT/'reference/roll-mobile/art.json').read_text())
 source=Image.open(ROOT/'reference/new-roster-art/rollsheet_mobile1.png').convert('RGBA')
 records=list(csv.DictReader((folder/'roll-body.csv').open()));pages={};cases={};star_frames=0
 assert len(records)>100
 partial_frames=0;invisible_frames=0;worst_fraction=1.0;worst_frame=None
 for row in records:
  pose,outline,facing,x,y,yhigh,star=(int(row[k])for k in('pose','outline','facing','x','y','yHigh','star'))
  if x>=32768:x-=65536
  banks=[int(i)for i in row['banks'].split(':')]
  pool=m['pool_chr'][m['pool_for'][str(pose)]]
  assert banks[0]==pool and banks[6]==pool+2,('Body CHR bank differs from source pose',row['frame'],pose,banks,pool)
  oam=bytes.fromhex(row['oam']);palette=bytes.fromhex(row['palette']);actual={};visible={}
  line_masks=[0]*240;line_counts=[0]*240
  for i in range(64):
   top=oam[4*i]+1
   if top>240:continue
   for line in range(max(32,top),min(240,top+16)):
    if line_counts[line]<8:line_masks[line]|=1<<i
    line_counts[line]+=1
  for i in reversed(range(64)):
   yy,tile,attr,xx=oam[4*i:4*i+4]
   if yy>=240 or not ((tile&1==0 and tile<64)or(tile&1 and 0x81<=tile<=0xbf)):continue
   address=(tile&1)*4096+(tile&254)*16;physical=banks[address//1024]
   if physical not in pages:pages[physical]=(folder/f'roll-chr-{physical}.bin').read_bytes()
   data=pages[physical][address%1024:address%1024+32]
   for dy in range(16):
    sy=15-dy if attr&128 else dy;offset=(sy//8)*16+sy%8
    for dx in range(8):
     sx=dx if attr&64 else 7-dx
     color=((data[offset]>>sx)&1)|(((data[offset+8]>>sx)&1)<<1)
     if color and xx+dx<256 and 32<=yy+dy+1<240:
      at=(xx+dx,yy+dy+1);value=palette[16+(attr&3)*4+color]&63;actual[at]=value
      if line_masks[at[1]]&(1<<i):visible[at]=value
  expected={};_,box,anchor=m['frames'][pose]
  for sy in range(box[1],box[3]):
   for sx in range(box[0],box[2]):
    rgba=source.getpixel((sx,sy))
    if not rgba[3]:continue
    dx=sx-anchor[0]+8;dy=sy-anchor[1]+32
    xx=x+(dx if facing==1 else 15-dx);yy=(yhigh-1)*256+y+dy+1
    if 0<=xx<256 and 32<=yy<240:expected[(xx,yy)]=COLORS[rgba[:3]]
  if star:
   # Source geometry must survive intentional native star palette cycling.
   assert set(actual)<=set(expected),('Star adds unexpected body pixels',row['frame'])
   star_frames+=1
  else:
   assert all(expected.get(at)==color for at,color in actual.items()),('Wrong actual body pixels/colors',row['frame'],pose,len(actual),len(expected))
  missing=set(expected)-set(actual)
  assert not missing if outline else all(expected[at]==15 for at in missing),('Missing non-optional source pixels',row['frame'],pose,len(missing),list(missing)[:8])
  key=f'{pose}-{outline}-{facing}';cases[key]=cases.get(key,0)+1
  if actual:
   fraction=len(visible)/len(actual)
   if fraction<1:partial_frames+=1
   if fraction==0:invisible_frames+=1
   if fraction<worst_fraction:worst_fraction=fraction;worst_frame=int(row['frame'])
 proof=dict(passed=True,actual_rendered_body_frames=len(records),pose_cases=cases,star_palette_frames=star_frames,
            trace_sha256=hashlib.sha256((folder/'roll-body.csv').read_bytes()).hexdigest(),source_sha256=m['source_sha256'],
            scanline_eligible_body=dict(partial_frames=partial_frames,fully_hidden_frames=invisible_frames,worst_fraction=worst_fraction,worst_frame=worst_frame),
            scope='Committed OAM, actual hardware sprite CHR pages and palette; source pixels for observed poses, not unobserved animations or physical scanline visibility')
 (folder/'roll-render-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 print('PASS',len(records),'actual Roll body frames;',len(cases),'pose/facing/outline cases')

if __name__=='__main__':main()
