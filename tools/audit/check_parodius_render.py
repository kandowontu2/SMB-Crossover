"""Measure actual committed body coverage under the NES first-eight rule.

This compares the actual immutable pose record with committed OAM/CHR/palette,
including earlier opaque projectile pixels and scanline priority. Background
occlusion and physical-console behavior are outside this read-only model.
"""
from pathlib import Path
import argparse, csv, hashlib, json


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);a=p.parse_args();folder=a.folder.resolve()
 source=folder/'parodius-body.csv';rows=list(csv.DictReader(source.open()));pages={};cases={}
 assert len(rows)>100
 partial=hidden=measured=0;worst=1.0;total_expected=total_visible=0;updates=draws=lag=0;worst_frame=None
 for row in rows:
  updates+=int(row['updates']);draws+=int(row['draws']);lag+=int(row['lagNmis'])
  x,y,yhigh,attr=(int(row[k])for k in('x','y','yHigh','attr'))
  if x>=32768:x-=65536
  if not(32<=x<=207 and 48<=y<=207 and yhigh==1):continue
  banks=[int(v)for v in row['banks'].split(':')];palette=bytes.fromhex(row['palette']);raw=bytes.fromhex(row['record']);oam=bytes.fromhex(row['oam'])
  assert raw[0]==len(raw)-1 and raw[0]%4==0
  def pixels(tile):
   at=(tile&1)*4096+(tile&254)*16;page=banks[at//1024]
   if page not in pages:pages[page]=(folder/f'parodius-chr-{page}.bin').read_bytes()
   data=pages[page][at%1024:at%1024+32];assert len(data)==32
   return [[((data[dy//8*16+dy%8]>>(7-dx))&1)|(((data[dy//8*16+dy%8+8]>>(7-dx))&1)<<1)for dx in range(8)]for dy in range(16)]
  def paint(parts,allow=None):
   output={}
   for slot,(yy,tile,attribute,xx)in reversed(list(enumerate(parts))):
    if yy>=240:continue
    px=pixels(tile)
    for dy in range(16):
     sy=yy+dy+1
     if not 32<=sy<240 or(allow is not None and slot not in allow[sy]):continue
     for dx in range(8):
      sx=xx+dx
      v=px[15-dy if attribute&128 else dy][7-dx if attribute&64 else dx]
      if v and sx<256:output[sx,sy]=palette[16+(attribute&3)*4+v]&63
   return output
  expected_parts=[]
  for at in range(1,len(raw),4):
   tile,attribute,dy,dx=raw[at:at+4];dx=dx if dx<128 else dx-256;dy=dy if dy<128 else dy-256
   assert 0<=x+dx<256 and 0<=y+dy<240,'Interior body includes a wrapped sprite'
   expected_parts.append((y+dy,tile,(attribute|attr)&0xf3,x+dx))
  actual_parts=[tuple(oam[at:at+4])for at in range(0,256,4)]
  # Every intended body part must reach actual DMA, even when its pixels lose
  # scanline priority. This is separate from the visibility measurement.
  assert set(expected_parts)<=set(actual_parts),('Missing committed body part',row['frame'],row['pose'])
  expected=paint(expected_parts)
  allow=[[]for _ in range(240)]
  for i,(yy,_,_,_)in enumerate(actual_parts):
   for sy in range(max(32,yy+1),min(240,yy+17)):
    if len(allow[sy])<8:allow[sy].append(i)
  screen=paint(actual_parts,allow)
  visible=sum(screen.get(point)==color for point,color in expected.items())
  assert expected
  fraction=visible/len(expected);measured+=1;total_expected+=len(expected);total_visible+=visible
  if fraction<1:partial+=1
  if fraction==0:hidden+=1
  if fraction<worst:worst,worst_frame=fraction,int(row['frame'])
  key=row['variant']+'-'+row['pose'];cases[key]=cases.get(key,0)+1
 assert measured>100
 report=dict(passed=True,trace_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),frames=len(rows),
  measured_interior_frames=measured,partial_frames=partial,fully_hidden_frames=hidden,worst_fraction=worst,worst_frame=worst_frame,
  pixel_weighted_fraction=total_visible/total_expected,pose_cases=cases,native_updates=updates,draws=draws,lag_nmis=lag,
  scope='Actual DMA pose completeness and first-eight-sprite pixel visibility including sprite occlusion; no background/physical-console/full-campaign/source-color claim.')
 (folder/'parodius-render-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
