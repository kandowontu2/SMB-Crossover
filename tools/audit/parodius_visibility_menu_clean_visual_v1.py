"""Build exact actual-frame comparisons for offline agent review; no native run."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def im(p):return Image.frombytes('RGBA',(256,240),Path(p).read_bytes(),'raw','BGRA').convert('RGB')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old=D/'parodius-menu3cee-preparation-v2/menu/baseline-early';bad=D/'parodius-menub0-preparation-v3/menu/baseline-early';new=D/'parodius-menu-clean731-preparation-v1/menu/baseline-early';bg=D/'parodius-menu-clean731-background-v1'
 assert json.loads((bg/'proof.json').read_text())['passed']
 frames=[184,194,206,218,230,242,254,266];sheet=Image.new('RGB',(1024,1560),'#202020');draw=ImageDraw.Draw(sheet);bound=[]
 for block in range(2):
  for row,(label,folder)in enumerate([('3cee actual baseline',old),('b0 actual HELD',bad),('clean731 actual',new)]):
   for col,n in enumerate(frames[block*4:block*4+4]):
    f=folder/f'frame-{n:06d}.argb';x,y=col*256,(block*3+row)*260;sheet.paste(im(f),(x,y+20));draw.text((x,y),label+' '+str(n),fill='white');bound.append(dict(label=label,frame=n,path=str(f.resolve()),sha256=sha(f)))
 sheet.save(a.output/'eight-actual-menu-before-held-after.png');put(a.output/'eight-frame-bindings.json',bound)
 timing={n:[]for n in frames}
 for line in(new/'menu-early-timing.jsonl').open():
  q=json.loads(line)
  if q['kind']in['early-DMA-complete','early-render-enable']:
   stamp=q['DMA']['complete']if q['kind']=='early-DMA-complete'else q['ppu'];n=stamp['frame']
   if n in timing:timing[n].append(q)
 put(a.output/'actual-eight-frame-DMA-enable.json',timing)
 selected=[180,184,185,194,206,218,230,242,254,266,274,278,290,302,314,326,336,341,348,349,388,392,544,545,546,547,548,586,589,674,1554,1800]
 pages=[]
 for page,start in enumerate(range(0,len(selected),24),1):
  group=selected[start:start+24];out=Image.new('RGB',(1536,1040),'#202020');od=ImageDraw.Draw(out)
  for i,n in enumerate(group):
   f=new/f'frame-{n:06d}.argb';x,y=i%6*256,i//6*260;out.paste(im(f),(x,y+20));od.text((x,y),'clean731 '+str(n),fill='white');bound.append(dict(label='selected clean731',frame=n,path=str(f.resolve()),sha256=sha(f)))
  f=a.output/f'selected-actual-whole-PPU-{page:02d}.png';out.save(f);pages.append(dict(path=str(f.resolve()),sha256=sha(f),frames=group))
 put(a.output/'selected-actual-pages.json',pages);put(a.output/'all-selected-frame-bindings.json',bound)
 files=[p for p in a.output.iterdir()if p.is_file()]+[Path(__file__),bg/'proof.json',bg/'whole-menu-review-pages.json',new/'lifecycle-proof.json',new/'menu-early-timing.jsonl']
 put(a.output/'manifest.json',{str(f.resolve()):sha(f)for f in files})
 proof=dict(prepared=True,native_launched=False,actual_raw_frame_comparisons=True,all_eight_required_frame_values=frames,selected_actual_wholeframes=selected,all_original_negative_bytes_untouched=True,agent_visual_review=False,manifest_sha256=sha(a.output/'manifest.json'),limits='Actual captured frame sheets only. Static-subset exact pixel proof is separate; agent inspection must be recorded additively. No sprite visibility/all-pixel/adoption claim.')
 put(a.output/'proof.json',proof);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),sheet_sha256=sha(a.output/'eight-actual-menu-before-held-after.png')),indent=2))
if __name__=='__main__':main()
