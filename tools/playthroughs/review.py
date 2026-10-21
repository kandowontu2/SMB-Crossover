"""Decode every recorded frame; audit coverage, split timing, world SFX and video.

This is automated per-frame review, with contact sheets for human inspection;
it does not claim a person manually watched every frame or waveform parity.
"""
from pathlib import Path
import argparse,csv,json,re,subprocess
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
NAMES=['Mario','Mega Man','Samus','Bill','Link','Simon','Pit','Rygar','Luigi','Bass','Ryu','Sophia']
def rows(path):return list(csv.DictReader(path.open()))
def read_exact(pipe,size):
 data=bytearray()
 while len(data)<size:
  chunk=pipe.read(size-len(data))
  if not chunk:break
  data.extend(chunk)
 return data
def review(directory):
 manifest=json.loads((directory/'manifest.json').read_text());settings=manifest['settings'];character=settings['character']
 trace={int(r['frame']):r for r in rows(directory/'trace.csv')}
 animation=rows(directory/'animation.csv') if (directory/'animation.csv').exists() else []
 animation_by_frame={int(r['frame']):r for r in animation}
 render=rows(directory/'render.csv');render_by_frame={int(r['frame']):r for r in render}
 events=rows(directory/'events.csv');objects=rows(directory/'objects.csv');splits=rows(directory/'scroll-writes.csv')
 labels={m[2]:int(m[1],16) for m in re.finditer(r'^al ([0-9a-fA-F]+) \.(\w+)$',(directory/f"smb-crossover-{settings['mapper']}.lbl").read_text(),re.M)}
 captures={};reveals=[];prior=False;wanted=set()
 for frame,t in trace.items():
  power=int(t['powerX'])>=0 and int(t['powerState'])>0 and int(t['level'])==0
  if power and not prior and frame>540:
   reveals.append((frame,int(t['powerX']),int(t['powerY'])))
  prior=power
 for frame,_,_ in reveals:
  wanted.update(range(max(1,frame-3),frame+22))
 milestones={int(e['frame']):e['event'] for e in events if e['event'].startswith('goal-')}
 deaths=[e for e in objects if e['event']=='defeat']
 for e in deaths[::max(1,len(deaths)//5)]:milestones[int(e['frame'])]='enemy defeated'
 previous_area=None
 for frame,t in trace.items():
  area=(t['level'],t['areaType'])
  if frame>540 and previous_area and area!=previous_area:milestones[frame]='area transition'
  previous_area=area
 milestones[max(trace)]='endpoint: 1-2 control'
 wanted.update(milestones)
 # The IRQ audit observes actual PPU register writes on every gameplay frame.
 by_split={}
 for r in splits:by_split.setdefault(int(r['frame']),[]).append(r)
 split_flags=[];split_count=0
 for frame,rr in by_split.items():
  t=trace.get(frame)
  if not t or int(t['engine'])!=8 or int(t['mode'])!=1 or int(t['task'])!=3 or int(t['level'])!=0:continue
  final=rr[-2:]
  split_count+=1
  if len(final)!=2 or any(int(v['scanline'])!=31 or not 257<=int(v['dot'])<=320 for v in final):split_flags.append(frame)
 # A queued common tone must acquire its voice on the next audio updates.
 missing_sfx=[];sfx_count=0;priority_suppressed=[]
 if character:
  for e in events:
   if e['event']!='sfx':continue
   address,value,frame=int(e['slot']),int(e['value']),int(e['frame'])
   # Bass filters these shared queues into his native MM3 effect engine.
   # Its masks describe physical channels and differ from SMB's cue voice.
   native_bits=0
   if character==9:
    if address==labels['Square1SoundQueue']:
     if value&32:native_bits=2
     elif value&8:native_bits=8
     elif value&16:native_bits=10
     elif value&(1|128):continue # Source jump is silent; landing has its own cue.
    elif address==labels['Square2SoundQueue'] and value&64:native_bits=2
   bits=0
   if address==labels['Square1SoundQueue'] and value&(255 if character>=6 else 66):bits=1
   if address==labels['Square2SoundQueue'] and value&(255 if character>=6 else 31):bits=2
   if address==labels['NoiseSoundQueue'] and value&1:bits=8
   if not bits:continue
   t=trace.get(frame)
   if not t or int(t['engine'])!=8:continue
   sfx_count+=1
   def owned(f):
    if native_bits:
     return int(render_by_frame.get(f,{}).get('nativeSfxMask',0))&native_bits
    if character==8:
     a=animation_by_frame.get(f,{})
     return int(a.get({1:'sfx1',2:'sfx2',8:'sfxNoise'}[bits],0))>0
    return int(render_by_frame.get(f,{}).get('worldSfx',0))&bits
   if not any(owned(f) for f in range(frame,frame+4)):
    cue={'frame':frame,'voice':bits,'queue':address,'value':value}
    # The native MM3 engine has one effect priority. Enemy-hit priority 9
    # suppresses buster priority 7 even though their channel masks differ.
    # Only the enemy-hit cue in BassAudioBegin owns noise alone (mask 8).
    if character==9 and value&32 and native_bits==2 and any(int(render_by_frame.get(f,{}).get('nativeSfxMask',0))==8 for f in range(frame,frame+4)):
     priority_suppressed.append(cue)
    else:missing_sfx.append(cue)
 animation_flags=[];palette_flags=[];bank_flags=[];motion_flags=[];emergence_flags=[];animation_samples={}
 prior_t=None
 for frame,t in trace.items():
  a=animation_by_frame.get(frame)
  if a and t['engine']=='8' and t['level']=='0' and t['mode']=='1' and t['task']=='3':
   pose,state,crouch,shoot,attack=map(int,(a['pose'],a['state'],a['crouch'],a['shoot'],a['attack']))
   key=(pose,int(a['power']),state,crouch,bool(shoot),bool(attack))
   animation_samples.setdefault(key,frame+1);wanted.add(animation_samples[key])
   if int(a['chr'])!=int(a['expectedChr']):
    bank_flags.append(frame);wanted.update((frame,frame+1))
   if tuple(int(a[k]) for k in ('mushroom1','mushroom2','mushroom3'))!=(22,48,39):palette_flags.append(frame)
   if not int(a['powerup']) and character in (6,7):
    if shoot and not attack:
     expected=21 if crouch else (23 if character==6 and pose==23 else 22) if state else (14 if pose==14 else 17 if character==6 else 7)
     if pose!=expected:animation_flags.append({'frame':frame,'pose':pose,'expected':expected,'state':state,'crouch':crouch})
  if prior_t and t['engine']==prior_t['engine']=='8' and t['areaType']==prior_t['areaType'] and t['level']==prior_t['level']=='0':
   dx=abs(int(t['x'])-int(prior_t['x']));dy=abs(int(t['y'])-int(prior_t['y']));dy=min(dy,256-dy)
   if dx>8 or dy>12:motion_flags.append({'frame':frame,'dx':dx,'dy':dy})
   if 0<int(t['powerState'])<128 and 0<int(prior_t['powerState'])<128:
    px=int(t['powerX'])-int(prior_t['powerX']);py=int(t['powerY'])-int(prior_t['powerY'])
    if px or py not in (-1,0):emergence_flags.append({'frame':frame,'dx':px,'dy':py})
  prior_t=t
 # Row color profiles are insensitive to ordinary horizontal scrolling. A
 # vertical whole-stage jump shifts the floor's profile relative to the last
 # frame. Compare all neighboring offsets and retain flagged frames visually.
 command=['ffmpeg','-v','error','-i',str(directory/'native.avi'),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
 process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 frame_count=0;previous=None;previous_t=None;pixel_flags=[];compared=0
 while True:
  raw=read_exact(process.stdout,256*240*3)
  if not raw:break
  if len(raw)!=256*240*3:raise RuntimeError('Partial decoded video frame')
  frame_count+=1;pixels=np.frombuffer(raw,np.uint8).reshape(240,256,3)
  t=trace.get(frame_count)
  profile=pixels[202:240,16:240].mean(axis=1)
  if previous is not None and t and previous_t and t['engine']=='8' and previous_t['engine']=='8' and t['areaType']==previous_t['areaType'] and t['level']=='0' and previous_t['level']=='0' and abs(int(t['camera'])-int(previous_t['camera']))<8:
   costs=[float(np.abs(profile[4+d:34+d]-previous[4:34]).mean()) for d in range(-3,4)]
   best=int(np.argmin(costs))-3;compared+=1
   if best and costs[3]>costs[best+3]*2+3:
    pixel_flags.append({'frame':frame_count,'vertical_offset':best,'error_without_shift':round(costs[3],3),'error_with_shift':round(costs[best+3],3)})
    wanted.add(frame_count)
  if frame_count in wanted:captures[frame_count]=Image.fromarray(pixels.copy())
  previous=profile;previous_t=t
 error=process.stderr.read().decode();process.wait()
 if process.returncode:raise RuntimeError(error)
 # All emergence frames are retained in local, pixel-scaled contact sheets.
 for i,(start,wx,wy) in enumerate(reveals,1):
  sheet=Image.new('RGB',(6*192,5*274),'#202020');draw=ImageDraw.Draw(sheet)
  for j,f in enumerate(range(max(1,start-3),start+22)):
   if f not in captures:continue
   t=trace.get(f,trace[start]);sx=wx-int(t['camera']);left=min(160,max(0,sx-40));top=min(112,max(32,wy-40))
   crop=captures[f].crop((left,top,left+96,top+128)).resize((192,256),Image.Resampling.NEAREST)
   x=(j%6)*192;y=(j//6)*274;sheet.paste(crop,(x,y));draw.text((x+3,y+257),f'frame {f}',fill='white')
  sheet.save(directory/f'reveal-{i}.png')
 entries=sorted(milestones.items())
 sheet=Image.new('RGB',(4*256,((len(entries)+3)//4)*260),'#202020');draw=ImageDraw.Draw(sheet)
 for j,(f,label) in enumerate(entries):
  if f not in captures:continue
  x=(j%4)*256;y=(j//4)*260;sheet.paste(captures[f],(x,y));draw.text((x+3,y+242),f'{f}: {label}',fill='white')
 sheet.save(directory/'review-contact-sheet.png')
 # A desired pose can advance while a lag frame retains the previous OAM/CHR.
 # Keep both adjacent native images for inspection instead of deleting flags.
 bank_frames=sorted({f+d for f in bank_flags for d in (0,1)})
 for start in range(0,len(bank_frames),48):
  batch=bank_frames[start:start+48];sheet=Image.new('RGB',(8*144,((len(batch)+7)//8)*170),'#202020');draw=ImageDraw.Draw(sheet)
  for j,f in enumerate(batch):
   if f not in captures:continue
   t=trace.get(f,trace.get(f-1));left=min(192,max(0,int(t['x'])-int(t['camera'])-24));top=min(160,max(32,int(t['y'])-16))
   crop=captures[f].crop((left,top,left+64,top+72)).resize((128,144),Image.Resampling.NEAREST)
   x=j%8*144;y=j//8*170;sheet.paste(crop,(x,y));draw.text((x+2,y+145),str(f),fill='white')
  sheet.save(directory/f'bank-review-{start//48+1}.png')
 samples=sorted((f,key) for key,f in animation_samples.items())
 for start in range(0,len(samples),48):
  batch=samples[start:start+48];sheet=Image.new('RGB',(8*144,((len(batch)+7)//8)*146),'#202020');draw=ImageDraw.Draw(sheet)
  for j,(f,key) in enumerate(batch):
   if f not in captures:continue
   t=trace.get(f,trace.get(f-1));left=min(192,max(0,int(t['x'])-int(t['camera'])-24));top=min(180,max(32,int(t['y'])-8))
   crop=captures[f].crop((left,top,left+64,top+60)).resize((128,120),Image.Resampling.NEAREST)
   x=j%8*144;y=j//8*146;sheet.paste(crop,(x,y));draw.text((x+2,y+121),f'{f} p{key[0]} pow{key[1]} s{key[2]}',fill='white')
  sheet.save(directory/f'animation-{start//48+1}.png')
 lag=sum((int(b['lag'])-int(a['lag']))%256 for a,b in zip(render,render[1:]))
 result={'character':NAMES[character],'route':settings['route'],'mapper':settings['mapper'],'verified_full_coverage':manifest.get('verified_full_coverage',False),'decoded_video_frames':frame_count,'video_matches_emulated_frames':frame_count in (manifest['result']['frames'],manifest['result']['frames']-1),'terminal_callback_frame_not_recorded':frame_count==manifest['result']['frames']-1,'floor_frames_compared':compared,'pixel_vertical_shift_flags':pixel_flags,'hud_split_frames_checked':split_count,'hud_split_flags':split_flags,'common_sfx_cues_checked':sfx_count,'missing_common_sfx_flags':missing_sfx,'lag_frames':lag,'sprite_overload_frames':sum(int(r['oamMax'])>8 for r in render),'powerup_emergence_sequences':len(reveals),'coverage':manifest.get('audit'),'rom_sha256':manifest['rom_sha256'],'input_sha256':manifest.get('inputs_sha256')}
 result.update(animation_frames_checked=len(animation),animation_pose_flags=animation_flags,animation_chr_flags=bank_flags,powerup_palette_flags=palette_flags,motion_flags=motion_flags,powerup_emergence_motion_flags=emergence_flags,unique_animation_contexts=len(animation_samples),source_priority_suppressed_sfx=priority_suppressed)
 result['background_font_check_captured']=bool(render and 'backgroundFontTiles' in render[0])
 result['background_font_flags']=[{'frame':int(r['frame']),'tiles':int(r['backgroundFontTiles'])} for r in render if int(r.get('backgroundFontTiles',0))]
 audio=subprocess.run(['ffmpeg','-v','error','-i',str(directory/'native.avi'),'-vn','-ac','1','-ar','48000','-f','s16le','pipe:1'],capture_output=True,check=True)
 pcm=np.frombuffer(audio.stdout,dtype='<i2').astype(np.float64)
 result['audio']={'sample_rate':48000,'samples':len(pcm),'duration_seconds':len(pcm)/48000,'rms':round(float(np.sqrt(np.mean(pcm*pcm))),3),'non_silent':bool(np.any(pcm))}
 (directory/'review.json').write_text(json.dumps(result,indent=2)+'\n')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(directory/'native.avi'),'-vf','setsar=5/4','-c:v','libx264','-crf','12','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(directory/'playthrough.mp4')],check=True)
 print(json.dumps({k:v for k,v in result.items() if k not in ('coverage','rom_sha256','input_sha256')}),flush=True)
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('directories',nargs='+',type=Path);a=p.parse_args()
 for directory in a.directories:review(directory)
if __name__=='__main__':main()
