from pathlib import Path
import json, subprocess
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[2]
O=R/'build/verification/root49-sophia-block-shift-hn'
times=json.loads((O/'video-frames.json').read_text())['frames']
p=subprocess.Popen(['ffmpeg','-v','error','-i','C:/Users/kando/Downloads/a.mp4','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
selected=[]
for n,f in enumerate(times):
    data=p.stdout.read(256*240*3)
    assert len(data)==256*240*3,n
    t=float(f['best_effort_timestamp_time'])
    if 8<=t<=12: selected.append((n,t,data))
assert p.wait()==0
for start in range(0,len(selected),48):
    group=selected[start:start+48]
    sheet=Image.new('RGB',(8*256,((len(group)+7)//8)*264),'#262626')
    d=ImageDraw.Draw(sheet)
    for k,(n,t,data) in enumerate(group):
        x,y=k%8*256,k//8*264
        sheet.paste(Image.frombytes('RGB',(256,240),data),(x,y+24))
        d.text((x+3,y+3),f'frame {n} / {t:.3f}s',fill='white')
    out=O/f'detail-{start//48}.png';sheet.save(out);print(out)
