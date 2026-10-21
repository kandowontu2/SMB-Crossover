"""Freeze 2.02 NSF attack effects as channel-owned APU register streams."""
from pathlib import Path
import csv,json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/reference-remaining-sfx'
NAMES=['LinkShootArrow','LinkSetBomb','LinkBombExplode','SimonThrowDagger','SimonCross','SimonHolyWaterExplode','SimonStopWatch','RyuArtOfFireWheel','RyuFireDrgonBall','RyuJumpSlash','RyuThrowSmallStar','RyuThrowBigStar','SamusShootMissile','SamusScrewAttack','SophiaMissile','BillLaser','BillFlare','SophiaBulletExplode','SophiaHitEnemy','SophiaKillEnemy','LinkTakeDamage','SimonTakeDamage','RyuTakeDamage','RyuJump']
def main():
 lines=['; Exact NSF references from 2.02 MusicInfo; frame-quantized NES APU writes.','.pushseg','.segment "REMAINING_AUDIO"'];sizes={};fixtures={};samples={}
 for id,name in enumerate(NAMES,1):
  writes=[[]for _ in range(180)]
  for row in csv.DictReader((OUT/(name+'.csv')).open()):
   f,a,v=map(int,row.values())
   if f<180 and(a<16 or a==21):writes[f].append((a,v))
  image=[0]*16;enable=15;mask=0;active=[];images=[]
  for f,ws in enumerate(writes):
   for a,v in ws:
    if a==21:enable=v&15
    else:image[a]=v
   audible=0
   for c in range(4):
    period=image[c*4+2]+(image[c*4+3]&7)*256
    if enable&(1<<c) and image[c*4]&(127 if c==2 else 15) and(c==3 or period>=(2 if c==2 else 8)):audible|=1<<c
   if audible:active.append(f);mask|=audible
   images.append((image[:],enable))
  if name in ('LinkTakeDamage','SimonTakeDamage'):
   records=list(csv.DictReader((OUT/(name+'-dpcm.csv')).open()))
   assert len(records)==1 and not active,(name,'Source injury cue must be one pure DMC sample')
   sample=records[0];payload=bytes.fromhex(sample['hex'])
   assert int(sample['rate'])==15 and int(sample['dac'])==0 and len(payload)==int(sample['length']) and(len(payload)-1)%16==0
   samples[name]={'rate':15,'dac':0,'frame':int(sample['frame']),'source_address':int(sample['start']),'length':len(payload),'hex':payload.hex(),'sha256':hashlib.sha256(payload).hexdigest()}
   lines +=[f'AvSfx{name}:',' .byte 255',f'AV_SFX_{name.upper()}={id}'];sizes[name]=1
   fixtures[str(id)]={'name':name,'mask':0,'frames':[],'dpcm':samples[name]}
   continue
  assert active,name
  first,last=active[0],active[-1];raw=[];prev={};fs=[]
  for f in range(first,last+1):
   im,en=images[f];written={a for a,v in writes[f]};frame=[]
   for a,v in enumerate(im):
    if not mask&(1<<(a//4)):continue
    if a%4==0 and not en&(1<<(a//4)):v=0 if a//4==2 else v&240
    if f==first or prev.get(a)!=v or(a%4==3 and a in written):raw +=[a,v];frame.append([a,v])
    prev[a]=v
   raw.append(254);fs.append(frame)
  raw.append(255);lines +=[f'AvSfx{name}:',' .byte '+','.join(map(str,raw))];sizes[name]=len(raw);fixtures[str(id)]={'name':name,'mask':mask,'frames':fs}
  lines +=[f'AV_SFX_{name.upper()}={id}']
 lines+=['AvSfxMasks:',' .byte '+','.join(str(fixtures[str(i)]['mask'])for i in range(1,len(NAMES)+1))]
 for suffix,op in [('Lo','<'),('Hi','>')]:lines +=['AvSfx'+suffix+':',' .byte '+','.join(op+'AvSfx'+n for n in NAMES)]
 lines+=['.segment "BASS_DPCM"']
 for name,sample in samples.items():
  lines +=['.align $40',f'AvDmc{name}:',' .byte '+','.join(str(v)for v in bytes.fromhex(sample['hex'])),f'AvDmc{name}End:']
 lines+=['.popseg'];(ROOT/'audio/remaining-source-sfx.inc').write_text('\n'.join(lines)+'\n')
 (ROOT/'tests/fixtures/remaining-source-sfx.json').write_text(json.dumps(fixtures,separators=(',',':'))+'\n')
 lua=['return {']
 for k,v in fixtures.items():
  lua+=[' ['+k+']={mask='+str(v['mask'])+',frames={'];image=[0]*16
  for fs in v['frames']:
   for a,val in fs:image[a]=val
   lua+=['  {'+','.join(map(str,image))+'},']
  lua+=[' }},']
 lua+=['}'];(ROOT/'tests/fixtures/remaining-source-sfx.lua').write_text('\n'.join(lua)+'\n')
 dmc=['-- Read-only mapped source NSF bytes/initial registers, independent of NES sample addresses.','return {']
 for name,sample in samples.items():
  dmc +=[f' [{NAMES.index(name)+1}]={{rate={sample["rate"]},dac={sample["dac"]},length={sample["length"]},hex="{sample["hex"]}"}},']
 dmc+=['}'];(ROOT/'tests/fixtures/remaining-source-dpcm.lua').write_text('\n'.join(dmc)+'\n')

 (ROOT/'docs/reference/remaining-sfx.json').write_text(json.dumps({'effects':json.loads((OUT/'source.json').read_text()),'bytes':sizes,'dpcm':samples,'limitations':['frame-quantized APU writes','looping effects capped at captured 180 updates; source MP3-only beams retain native NES adaptations','DMC payload/rate/initialDAC exact; common mixer resets DAC0 when hardware playback finishes']},indent=2)+'\n');print(sum(sizes.values()),'stream bytes +',sum(s['length']for s in samples.values()),'fixed DMC bytes (plus64-byte alignment)')
if __name__=='__main__':
 main()
 import runpy
 runpy.run_path(str(ROOT/'tools/reference/build_sophia_land_sfx.py'),run_name='__main__')

