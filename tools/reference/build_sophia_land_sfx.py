"""Append captured source SophiaLand without shifting any old effect bytes."""
from pathlib import Path
import csv,json,hashlib,re
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=ROOT/'audio/sophia-land-source-apu.csv';assert hashlib.sha256(p.read_bytes()).hexdigest()=='cadf792f172ee365e3bd7d97f359932e80d722f8779b6062479525e333eeb56e'
 writes=[[]for _ in range(180)]
 for row in csv.DictReader(p.open()):
  f,a,v=map(int,row.values())
  if f<180 and(a<16 or a==21):writes[f].append((a,v))
 image=[0]*16;enable=15;active=[];images=[];mask=0
 for f,ws in enumerate(writes):
  for a,v in ws:
   if a==21:enable=v&15
   else:image[a]=v
  audible=0
  for c in range(4):
   period=image[c*4+2]+(image[c*4+3]&7)*256
   if enable&(1<<c)and image[c*4]&(127 if c==2 else 15)and(c==3 or period>=(2 if c==2 else 8)):audible|=1<<c
  if audible:active.append(f);mask|=audible
  images.append((image[:],enable))
 assert active==list(range(1,9))and mask==2
 raw=[];prev={};frames=[]
 for f in active:
  image,en=images[f];written={a for a,v in writes[f]};fr=[]
  for a,v in enumerate(image):
   if not mask&(1<<(a//4)):continue
   if a%4==0 and not en&(1<<(a//4)):v=0 if a//4==2 else v&240
   if f==active[0]or prev.get(a)!=v or(a%4==3 and a in written):raw.extend([a,v]);fr.append([a,v])
   prev[a]=v
  raw.append(254);frames.append(fr)
 raw.append(255);assert len(raw)==21
 old=(ROOT/'audio/remaining-source-sfx.inc').read_text();names=re.search(r'AvSfxLo:\s*\.byte ([^\n]+)',old)[1].split(',');assert len(names)==24;names=[n[1:]for n in names]+['AvSfxSophiaLand']
 masks=re.search(r'AvSfxMasks:\s*\.byte ([^\n]+)',old)[1]+',2'
 lines=['; Source BlasterMaster NSF SFX track46, captured frames1..8.','.pushseg','.segment "REMAINING_AUDIO"','AvSfxSophiaLand:',' .byte '+','.join(map(str,raw)),'AV_SFX_SOPHIALAND=25','SophiaAvSfxMasks:',' .byte '+masks]
 for suffix,op in [('Lo','<'),('Hi','>')]:lines.extend(['SophiaAvSfx'+suffix+':',' .byte '+','.join(op+n for n in names)])
 lines.append('.popseg');(ROOT/'audio/sophia-land-sfx.inc').write_text('\n'.join(lines)+'\n')
 (ROOT/'audio/sophia-land-frames.json').write_text(json.dumps(dict(id=25,mask=2,source_active_frames=active,frames=frames,stream=raw,old_effects=24,limitations=['One source update per NES audio update; frame-quantized register equivalence, not waveform/subframe phase identity.']),indent=2)+'\n')
if __name__=='__main__':main()
