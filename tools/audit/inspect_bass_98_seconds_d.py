from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'build/verification/bass-98-seconds-d';O.mkdir(exist_ok=False)
raw=subprocess.check_output(['ffmpeg','-v','error','-ss','96','-i',str(R/'Playthrough Videos/Bass.mp4'),'-t','5','-vf','fps=10','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
size=256*240*3;assert len(raw)%size==0
for start in range(0,len(raw)//size,24):
 group=min(24,len(raw)//size-start);sheet=Image.new('RGB',(4*256,((group+3)//4)*264),'#262626');d=ImageDraw.Draw(sheet)
 for k in range(group):
  n=start+k;x,y=k%4*256,k//4*264;sheet.paste(Image.frombytes('RGB',(256,240),raw[n*size:(n+1)*size]),(x,y+24));d.text((x+4,y+4),f'{96+n/10:.1f}s',fill='white')
 sheet.save(O/f'bass-{start//24}.png')
print(O)
