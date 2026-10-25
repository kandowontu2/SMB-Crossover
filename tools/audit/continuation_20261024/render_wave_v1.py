from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent/'kirby-wave-diagnosis-v1';sheet=Image.new('RGB',(1040,6*188),(20,25,35));draw=ImageDraw.Draw(sheet)
for i,frame in enumerate(range(3820,3844)):
 p=D/f'frame-{frame}.rgba';a=np.frombuffer(p.read_bytes(),dtype='<u4').reshape(240,256);rgb=np.stack(((a>>16)&255,(a>>8)&255,a&255),axis=2).astype(np.uint8)
 Image.fromarray(rgb).save(p.with_suffix('.png'));x=i%4*260;y=i//4*188;draw.text((x+3,y+2),str(frame),fill='white');sheet.paste(Image.fromarray(rgb).crop((64,152,192,236)).resize((256,168),Image.Resampling.NEAREST),(x+2,y+18))
sheet.save(D/'contact.png')
