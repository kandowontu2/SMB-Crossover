"""Identify the hosted roster music against native APU drivers in the build."""
from pathlib import Path
import re,json,subprocess,concurrent.futures
import numpy as np
from compare_crossover_music import feature
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/roster-audio';OUT.mkdir(parents=True,exist_ok=True)
rom=(ROOT/'build/smb-crossover-mmc3.nes').read_bytes();labels={m[2]:int(m[1],16) for m in re.finditer(r'^al ([A-Fa-f0-9]+) \.([\w]+)$',(ROOT/'build/smb-crossover-mmc3.lbl').read_text(),re.M)}
def word(a):return list(a.to_bytes(2,'little'))
def nsf(name,bank,size,init,play):
 h=bytearray(128);h[:8]=b'NESM\x1a\x01\x01\x01';h[8:14]=bytes([0,0xa0,0,0xe0,*word(play)]);h[110:112]=(16639).to_bytes(2,'little')
 data=bytearray(rom[16+bank*8192:16+(bank+2)*8192]);data[0x3c00:]=bytes(1024)
 p=OUT/(name+'.nsf');p.write_bytes(h+data+bytes([0xa9,15,0x8d,0x15,0x40,*init,0x60]));return p
items=[]
for code in (0x26,0x2a,0x2e,0x32,0x36,0x3a,0x3e,0x42,0x46,0x4a,0x4e):
 name=f'Bill-{code:02x}';init=[0x20,*word(labels['init_pulse_and_noise_channels']),0xa9,code,0x20,*word(labels['init_sound_code_vars'])]
 items.append((name,nsf(name,0x17,0x4000,init,labels['handle_sound_slots'])))
for code in (1,2,4,8,0x10,0x20,0x40,0x80):
 name=f'Link-{code:02x}';init=[0xa9,code,0x8d,*word(labels['RgAudioRam']+0x100)]
 items.append((name,nsf(name,0x19,0x2000,init,labels['process_audio'])))
for code in range(0x27,0x52,3):
 name=f'Simon-{code:02x}';init=[0xa9,code,0x20,*word(labels['Cv8187'])]
 items.append((name,nsf(name,0x1b,0x4000,init,labels['Cv838a'])))
refs=[]
for role in ('Bill','Link','Simon'):refs+=list((ROOT/'reference/crossover/assets/sounds').glob('*'+role+'*.mp3'))
items +=[(p.stem,p) for p in refs]
def render(item):
 name,path=item;subprocess.run(['ffmpeg','-v','error','-y','-i',str(path),'-t','8','-ar','16000','-ac','1','-f','f32le',str(OUT/(name+'.raw'))],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(render,items))
tracks={name:feature(OUT/(name+'.raw')) for name,p in items if name.startswith(('Bill-','Link-','Simon-'))}
result={}
for p in refs:
 ref=feature(OUT/(p.stem+'.raw'));rank=[]
 for name,ft in tracks.items():
  if name.split('-')[0] not in p.stem:continue
  score=0
  for shift in range(-50,51):
   a=ref[max(0,shift):];b=ft[max(0,-shift):];n=min(len(a),len(b))
   if n>20:score=max(score,np.sum(a[:n]*b[:n],axis=1).mean())
  rank.append((float(score),name))
 rank.sort(reverse=True);result[p.name]=rank[:3];print(p.stem,rank[:3])
(OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
