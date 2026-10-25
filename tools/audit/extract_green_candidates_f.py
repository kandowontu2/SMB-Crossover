from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'build/verification/outdoor-green-review-e'
data=json.loads((O/'candidates.json').read_text())
roster={'Mario':(0,0),'Luigi':(8,0),'Bill':(3,0),'Lance':(3,1),'Mega Man':(1,0),'Bass':(9,0),'Samus':(2,0),'Link':(4,0),'Simon':(5,0),'Pit':(6,0),'Rygar':(7,0),'Ryu':(10,0),'Sophia':(11,0),'Scrooge':(12,0)}
for name,(ch,v)in roster.items():
 frames=sorted({d['frame']for d in data if d['name']==name})
 if not frames:continue
 p=R/'build/roster-through-2-2'/f'claude-final-video-{ch}-v{v}-mmc3/playthrough-lossless.mkv'
 expr='+'.join(f'eq(n\\,{f-1})'for f in frames)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf','select='+expr,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
 size=256*240*3;assert len(raw)==len(frames)*size
 for start in range(0,len(frames),24):
  out=Image.new('RGB',(1024,((min(24,len(frames)-start)+3)//4)*264),'#252525');d=ImageDraw.Draw(out)
  for k,f in enumerate(frames[start:start+24]):
   n=start+k;x,y=k%4*256,k//4*264
   out.paste(Image.frombytes('RGB',(256,240),raw[n*size:(n+1)*size]),(x,y+24))
   d.text((x+3,y+3),f'{name} f{f} {(f-1)/60.0988:.2f}s',fill='white')
  out.save(O/f'{name}-candidates-{start//24+1}.png')
 print(name,len(frames),flush=True)
