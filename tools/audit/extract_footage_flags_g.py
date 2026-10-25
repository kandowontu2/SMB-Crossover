"""Extract bounded exact frame evidence for manual inspection of existing flags."""
from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];B=R/'build/verification/postable-footage-audit-b';O=R/'build/verification/footage-flag-inspection-g'
assert not O.exists();O.mkdir()
index=json.loads((B/'index.json').read_text());out=[]
for item in index['movies']:
 review=json.loads((R/item['review']).read_text());wanted={}
 for group in ('motion_candidates','video_vertical_shift_candidates','video_background_flash_candidates'):
  for z in review[group]:
   f=z['frame']
   for k in range(f-1,f+2):wanted.setdefault(k,[]).append(group.replace('_candidates',''))
 if not wanted:continue
 frames=sorted(wanted);p=R/item['packet']/'playthrough-lossless.mkv'
 expr='+'.join(f'eq(n\\,{f-1})'for f in frames)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf','select='+expr,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
 size=256*240*3;assert len(raw)==len(frames)*size
 for start in range(0,len(frames),24):
  batch=frames[start:start+24];sheet=Image.new('RGB',(1024,((len(batch)+3)//4)*264),'#242424');d=ImageDraw.Draw(sheet)
  for k,f in enumerate(batch):
   n=start+k;x,y=k%4*256,k//4*264;pixels=Image.frombytes('RGB',(256,240),raw[n*size:(n+1)*size]);sheet.paste(pixels,(x,y+24));d.text((x+3,y+3),f"{item['name']} f{f} {(f-1)/60.0988:.2f}s",fill='white')
  sheet.save(O/f"{item['name']}-{start//24+1}.png")
 out.append(dict(name=item['name'],frames=frames,motion=review['motion_candidates'],vertical=review['video_vertical_shift_candidates']))
 print('EXTRACT_FLAGS',item['name'],len(frames),flush=True)
(O/'index.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
