from pathlib import Path
import csv,json,subprocess
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'build/verification/postable-story-c';O.mkdir(exist_ok=False)
story={}
for name,ch in [('Bass',9),('Bill',3)]:
 P=R/'build/roster-through-2-2'/f'claude-final-video-{ch}-v0-mmc3'
 rows=list(csv.DictReader((P/'trace.csv').open()));last=None;changes=[]
 for z in rows:
  if int(z['engine'])==8 and(z['world'],z['level'],z['power'])!=last:
   last=(z['world'],z['level'],z['power']);changes.append({k:int(z[k])for k in ['frame','world','level','power','x','y']})
 story[name]=changes
(O/'power-story.json').write_text(json.dumps(story,indent=2),encoding='utf-8');print(json.dumps(story))
P=R/'build/roster-through-2-2/claude-final-video-9-v0-mmc3/playthrough-lossless.mkv'
for start,end,label in [(12098,12120,'bass-green-candidate'),(19154,19174,'bass-position-candidate')]:
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P),'-vf',f'select=between(n\\,{start-1}\\,{end-1})','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
 size=256*240*3;assert len(raw)==(end-start+1)*size
 sheet=Image.new('RGB',(4*256,((end-start+4)//4)*264),'#262626');d=ImageDraw.Draw(sheet)
 for k in range(end-start+1):
  x,y=k%4*256,k//4*264;sheet.paste(Image.frombytes('RGB',(256,240),raw[k*size:(k+1)*size]),(x,y+24));d.text((x+4,y+4),f'frame {start+k}',fill='white')
 sheet.save(O/(label+'.png'))
