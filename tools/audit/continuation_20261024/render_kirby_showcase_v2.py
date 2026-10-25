from pathlib import Path
import csv,json,math,wave,subprocess,hashlib,collections,textwrap
import numpy as np
from PIL import Image,ImageDraw,ImageFont

D=Path(__file__).resolve().parent/'kirby-showcase-v1'
E=D/'edit-v2'
E.mkdir(exist_ok=False)
FPS=60.09881389744
OUTFPS=60
W,H=1280,720
fonts={}
def font(n,bold=False):
 k=(n,bold)
 if k not in fonts:fonts[k]=ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf'if bold else'segoeui.ttf'),n)
 return fonts[k]
def load(name,file):return list(csv.DictReader((D/name/file).open()))
base=load('base','base-trace.csv');copies=load('copies','copy-trace.csv')
result=json.loads((D/'copies/copy-result.json').read_text())['powers']
assert len(result)==14 and all(x['recovered']and x['expired']for x in result)
scenes=[]
def add(source,first,last,title,category,desc,control,sub='',power=0,speed=1,freeze=False,chapter=True):
 assert first<=last
 scenes.append(dict(source=source,first=first,last=last,title=title,category=category,desc=desc,control=control,sub=sub,power=power,speed=speed,freeze=freeze,chapter=chapter,frames=round((last-first+1)/FPS/speed*OUTFPS)))
add('base',300,449,'ALL OF KIRBY','SMB CROSSOVER',
 '14 enemy copies. One very hungry hero.','Movement, combat & recovery','Current MMC5 build',freeze=True)
basic=[
 ('WALK & RUN','Double-tap a direction to run.','D-PAD: Move / double-tap: Run'),
 ('VARIABLE JUMP','Tap for a short hop. Hold for a higher jump.','A: Jump'),
 ('FLOAT & AIR PUFF','Inflate, float over obstacles, then spit an air puff.','UP: Float  ·  B: Air puff'),
 ('CROUCH & SLIDE','Duck low, then slide along the ground.','DOWN: Crouch  ·  DOWN + A/B: Slide'),
 ('INHALE & SPIT','Hold an enemy, then spit it out as a star.','Hold B: Inhale  ·  B again: Spit'),
 ('SWIM & WATER GUN','Swim and aim the water shot up or down.','D-PAD: Swim  ·  B: Water gun'),
]
for i,(title,desc,control)in enumerate(basic,1):
 rows=[r for r in base if int(r['case'])==i]
 add('base',int(rows[0]['frame']),int(rows[-1]['frame']),title,'BASIC MOVES',desc,control)
lineups=[
 ('GROUND CHARGE','GOOMBA','Rush forward along the ground.','B: Charge'),
 ('BOUNCING SHELL','GREEN KOOPA','Send a shell bouncing forward.','B: Throw shell'),
 ('RETURNING SHELL','RED KOOPA','The thrown shell turns back toward Kirby.','B: Throw returning shell'),
 ('BEETLE GUARD','BUZZY BEETLE','Hold a low guard to withstand enemy contact.','Hold B: Guard'),
 ('HAMMER THROW','HAMMER BRO','Lob hammers in an upward arc.','B: Throw hammer'),
 ('UPWARD JET','BLOOPER','Fire a burst straight above Kirby.','B: Upward shot'),
 ('BUBBLE SHOT','GRAY CHEEP CHEEP','Launch a slower forward shot.','B: Bubble shot'),
 ('WAVE SHOT','RED CHEEP CHEEP','Send a shot along a rising and falling path.','B: Wave shot'),
 ('HIGH JUMP','PARATROOPA','Leap high and defeat enemies on contact.','B: High jump'),
 ('CLOUD HOVER','LAKITU','Hold your height in midair, then release to fall.','Hold B: Hover'),
 ('NEEDLE SPREAD','SPINY','Launch three needles in a spreading arc.','B: Needle spread'),
 ('PIRANHA BITE','PIRANHA PLANT','Bite an enemy at close range.','B: Bite'),
 ('FIRE BURST','PODOBOO','Fire short-range bursts in quick succession.','B: Fire'),
 ('BULLET DASH','BULLET BILL','Dash forward with an attacking body.','B: Dash'),
]
for power,(title,enemy,desc,control)in enumerate(lineups,1):
 rows=[r for r in copies if int(r['power'])==power]
 def phase(name):return[r for r in rows if r['phase']==name]
 acquisition=phase('inhale');swallow=phase('swallow');attack=phase('attack');flourish=phase('flourish')
 info=dict(title=title,category=f'COPY {power:02} / 14',desc=desc,control=control,sub='FROM '+enemy,power=power)
 add('copies',int(acquisition[0]['frame']),int(swallow[-1]['frame']),**info)
 add('copies',int(attack[0]['frame']),int(attack[-1]['frame']),**info,chapter=False)
 # Show each projectile traveling freely as well as the contact demonstration.
 last=int(flourish[-1]['frame']) if power==9 else int(flourish[119]['frame'])
 add('copies',int(flourish[0]['frame']),last,**info,chapter=False)
drop=[r for r in copies if int(r['power'])==2 and r['phase']in('drop','reclaim','reswallow')]
add('copies',int(drop[0]['frame'])-12,int(drop[-1]['frame'])+12,'DROP & RECOVER','COPY MANAGEMENT',
 'Drop the copied power, inhale its star, then swallow to recover it.','SELECT: Drop  ·  B: Inhale  ·  DOWN: Swallow',sub='HALF-SPEED REPLAY',speed=.5)
food=json.loads((D/'food/health-result.json').read_text())['items']
for index,title,desc,control in [
 (0,'MUSHROOM HEAL','A mushroom restores two health points.','Health: 2 / 6  â†’  4 / 6'),
 (1,'FLOWER HEAL','A flower restores health too. Kirby keeps his copy system.','Health: 4 / 6  â†’  6 / 6'),
 (3,'STAR POWER','Temporary invincibility defeats enemies on contact.','Collect a Super Star'),
 (4,'EXTRA LIFE','A 1-Up grants an extra life.','Collect a 1-Up Mushroom')]:
 item=food[index]
 add('food',max(200,item['reveal']-10),item['receipt']+65,title,'HEALTH & PICKUPS',desc,control)
add('base',300,479,'READY TO COPY?','KIRBY / COMPLETE TOOLKIT',
 'Inhale an enemy. Swallow with Down. Use its power with B.','14 copies + movement + water gun + healing',sub='SMB CROSSOVER â€¢ GAMEPLAY SHOWCASE',freeze=True)

for source in ['base','copies','food']:
 q=json.loads((D/source/'capture.json').read_text());assert q['passed']
 assert all(q['first_frame']<=s['first']<=s['last']<=q['last_frame']for s in scenes if s['source']==source)
total=sum(s['frames']for s in scenes)
for i,s in enumerate(scenes):
 s['start_frame']=sum(x['frames']for x in scenes[:i]);s['end_frame']=s['start_frame']+s['frames']
(E/'edit.json').write_text(json.dumps(dict(width=W,height=H,fps=OUTFPS,total_frames=total,duration=total/OUTFPS,scenes=scenes),indent=2))

colors=dict(bg='#101827',panel='#182337',white='#f7f2ee',gray='#afbbcc',pink='#ff8ec9',yellow='#ffdb75',line='#33425a',active='#ffdc75')
def wrap(draw,text,n,width,bold=False):
 words=text.split();lines=[];line=''
 for word in words:
  test=(line+' '+word).strip()
  if draw.textlength(test,font=font(n,bold))>width and line:lines.append(line);line=word
  else:line=test
 if line:lines.append(line)
 return lines
def write_lines(draw,text,xy,n,width,fill,bold=False,spacing=8):
 x,y=xy
 for line in wrap(draw,text,n,width,bold):
  draw.text((x,y),line,font=font(n,bold),fill=fill);y+=n+spacing
 return y
def panel(s):
 im=Image.new('RGB',(512,H),colors['bg']);d=ImageDraw.Draw(im)
 d.rectangle((0,0,5,H),fill=colors['pink']);d.rectangle((5,0,512,8),fill=colors['pink'])
 d.text((35,30),'SMB CROSSOVER',font=font(22,True),fill=colors['gray'])
 d.text((32,63),'KIRBY',font=font(57,True),fill=colors['white'])
 d.text((36,128),'ABILITY SHOWCASE',font=font(19),fill=colors['pink'])
 d.line((36,174,476,174),fill=colors['line'],width=2)
 d.text((36,194),s['category'],font=font(20,True),fill=colors['pink'])
 y=write_lines(d,s['title'],(34,233),35,444,colors['white'],True,spacing=4)
 if s['sub']:
  y+=14;y=write_lines(d,s['sub'],(36,y),20,438,colors['yellow'],True,spacing=4)
 y=max(354,y+22)
 y=write_lines(d,s['desc'],(36,y),25,432,colors['white'],spacing=7)
 assert y<510,(s['title'],y)
 d.rounded_rectangle((30,523,482,613),radius=10,fill=colors['panel'])
 write_lines(d,s['control'],(45,537),20,420,colors['yellow'],True,spacing=5)
 d.text((36,635),'STAGED NATIVE ROM GAMEPLAY',font=font(14),fill=colors['gray'])
 d.text((36,658),'MMC5  /  CURRENT DEVELOPMENT BUILD',font=font(14),fill=colors['gray'])
 return im

# Build the continuous edited PCM track from native WaveRecorder samples.
waves={}
for name in ['base','copies','food']:
 with wave.open(str(D/name/'native-audio.wav'))as w:
  assert w.getnchannels()==2 and w.getsampwidth()==2 and w.getframerate()==48000
  waves[name]=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)
audio=[]
for s in scenes:
 a=round((s['first']-2)/FPS*48000);b=round((s['last']-1)/FPS*48000)
 pcm=waves[s['source']][a:b].copy()
 if s['speed']!=1:
  p=subprocess.run(['ffmpeg','-v','error','-f','s16le','-ar','48000','-ac','2','-i','pipe:0','-af',f"atempo={s['speed']}",'-f','s16le','pipe:1'],input=pcm.tobytes(),capture_output=True,check=True)
  pcm=np.frombuffer(p.stdout,dtype='<i2').reshape(-1,2).copy()
 needed=s['frames']*800
 if len(pcm)<needed:pcm=np.pad(pcm,((0,needed-len(pcm)),(0,0)))
 pcm=pcm[:needed].copy()
 fade=min(240,len(pcm)//4)
 pcm[:fade]=(pcm[:fade].astype('float64')*np.linspace(0,1,fade)[:,None]).astype('<i2')
 pcm[-fade:]=(pcm[-fade:].astype('float64')*np.linspace(1,0,fade)[:,None]).astype('<i2')
 audio.append(pcm)
pcm=np.concatenate(audio);assert len(pcm)==total*800
with wave.open(str(E/'showcase-audio.wav'),'wb')as w:
 w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())

video=E/'Kirby - All Abilities.mp4'
cmd=['ffmpeg','-n','-hide_banner','-loglevel','warning','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','60','-i','pipe:0','-i',str(E/'showcase-audio.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','6','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','title=Kirby â€” All Abilities | SMB Crossover','-metadata','comment=Native ROM gameplay. Labeled staged demonstrations of all 14 copies, base moves, swimming and health pickups.','-shortest',str(video)]
(E/'encode-command.json').write_text(json.dumps(cmd,indent=2))
samples=[]
with(E/'encode.log').open('w')as log:
 process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
 try:
  for i,s in enumerate(scenes):
   background=Image.new('RGB',(W,H));background.paste(panel(s),(768,0))
   for f in range(s['frames']):
    native=s['first'] if s['freeze']else min(s['last'],s['first']+int(f/OUTFPS*FPS*s['speed']))
    frame=background.copy()
    with Image.open(D/s['source']/'frames'/f'{native:06d}.png')as shot:frame.paste(shot.resize((768,720),Image.Resampling.NEAREST),(0,0))
    draw=ImageDraw.Draw(frame)
    progress=(s['start_frame']+f+1)/total
    draw.rectangle((768,704,1279,719),fill=colors['line'])
    draw.rectangle((768,704,768+int(progress*512),719),fill=colors['pink'])
    if s['speed']!=1:draw.rounded_rectangle((20,111,303,148),radius=5,fill=colors['bg']);draw.text((32,115),'HALF-SPEED REPLAY',font=font(22,True),fill=colors['yellow'])
    process.stdin.write(frame.tobytes())
    if f==min(s['frames']//2,48):
     target=E/f'review-{i:02}.png';frame.save(target);samples.append(dict(scene=i,path=target.name,outputFrame=s['start_frame']+f,nativeFrame=native))
   print(json.dumps(dict(encoded=i+1,of=len(scenes),title=s['title'])),flush=True)
  process.stdin.close();code=process.wait();assert code==0
 except:
  process.stdin.close();process.wait();raise

# A concise chapter list also records which power is shown at each point.
lines=[]
for s in scenes:
 if s['chapter']:
  seconds=s['start_frame']//60;lines.append(f'{seconds//60:02}:{seconds%60:02}  {s["title"].title()}')
(E/'Chapters.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(E/'review-samples.json').write_text(json.dumps(samples,indent=2))
probe=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],capture_output=True,text=True,check=True)
(E/'video-probe.json').write_text(probe.stdout)
q=json.loads(probe.stdout);v=next(s for s in q['streams']if s['codec_type']=='video');a=next(s for s in q['streams']if s['codec_type']=='audio')
assert v['width']==W and v['height']==H and v['r_frame_rate']=='60/1' and int(v['nb_frames'])==total
assert a['sample_rate']=='48000'and a['channels']==2
assert abs(float(q['format']['duration'])-total/60)<.1
decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
(E/'decode-check.log').write_text(decode.stdout+decode.stderr);assert decode.returncode==0 and not decode.stderr.strip()
report=dict(passed=True,file=str(video),duration=total/60,frames=total,video_sha256=hashlib.sha256(video.read_bytes()).hexdigest(),copies=14,base_scenes=6,pickup_scenes=4,discard_recovery=True,native_audio=True,ROM_sha256=json.loads((D/'capture-manifest.json').read_text())['ROM_sha256'],no_ROM_source_edits=True,lossless_native_frames_and_audio_retained=True,scope='Edited gameplay showcase. Actor/map/health scenes are arranged. Copy acquisition and actions are native ROM behavior. One explicitly labeled half-speed replay, title/outro hold frames, otherwise real-time gameplay. Native PCM edited at cuts and encoded to AAC.')
(E/'video-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
