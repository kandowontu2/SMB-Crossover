"""Compare actual captured HUD masks to frozen CHR/labels/attributes/palette."""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,hashlib,json
from PIL import Image,ImageDraw
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.packet/'preparation.json').read_text());run=Path(z['script']).parent;cfg=json.loads((run/'config.json').read_text());raw=(run/'candidate.nes').read_bytes();frames=[json.loads(s)for s in(run/'hud-frames.jsonl').read_text().splitlines()];rows=[];mapping=defaultdict(Counter);sheets=[];first=None
 canvas=Image.new('RGB',(8*256,26*56),'#202020');draw=ImageDraw.Draw(canvas)
 for fi,frame in enumerate(frames):
  n=frame['finished']['frame'];s=frame['start'];f=run/frame['capture'];im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');box=(fi%8*256,fi//8*56);canvas.paste(im.crop((0,0,256,40)),(box[0],box[1]+16));draw.text(box,f'{n} A{s["ram"]["InvHudActive"]} U{s["ram"]["X5HudChrUpper"]:02x}',fill='white')
  row=dict(frame=n,raw=str(f),raw_sha256=sha(f),active=s['ram']['InvHudActive'],upper=s['ram']['X5HudChrUpper'],font=s['chr'][8])
  if cfg['variant']and row['active']:
   assert row['active']==2*cfg['variant']+1 and row['font']==395+cfg['variant'];assert s['labels']==cfg['hud_labels'][str(cfg['variant'])];first=first or n;bad=[];bg=im.getpixel((0,8));assert bg==im.getpixel((255,8)),'Uncontested HUD margin backdrop'
   for tile,t in enumerate(s['labels']):
    x0=(tile+2)*8;physical=s['chr'][8+t//64];at=1048592+physical*1024+(t%64)*16;data=raw[at:at+16];pal=(s['attrs'][(tile+2)//4]>>(((tile+2)&2)))&3
    for y in range(8):
     for x in range(8):
      px=(data[y]>>(7-x)&1)|((data[y+8]>>(7-x)&1)<<1);color=s['palette'][0 if px==0 else pal*4+px]&63;actual=im.getpixel((x0+x,8+y));mapping[color][actual]+=1
      # Palette index0 is the universal backdrop. If another palette entry
      # has that same NES color it is visually backdrop too.
      expected=color!=(s['palette'][0]&63);visible=actual!=bg
      if expected!=visible:bad.append([x0+x,8+y,color,list(actual),list(bg)])
   row.update(mask_pixels=28*64,mask_mismatches=len(bad),first_mismatches=bad[:8]);assert not bad,('Source CHR/attrs/palette HUD visible mask',n,bad[:8])
  rows.append(row)
 canvas.save(a.output/'all-HUD-frames.png')
 if first:
  chosen=sorted(set([first-3,first-2,first-1,first,first+1,first+2,first+3,first+4]));sheet=Image.new('RGB',(4*256,2*260),'#202020');d=ImageDraw.Draw(sheet)
  for i,n in enumerate(chosen):
   f=run/f'frame-{n:06}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');x=i%4*256;y=i//4*260;sheet.paste(im,(x,y+20));d.text((x,y),f'Actual PPU {n}',fill='white')
  sheet.save(a.output/'first-publication-full-PPU.png')
 # Color classes are observed, not an assumed emulator RGB palette. A
 # single source NES color must consistently produce one actual RGB value.
 color_rows={str(k):[dict(RGB=list(rgb),pixels=n)for rgb,n in values.items()]for k,values in mapping.items()};assert all(len(v)==1 for v in color_rows.values()),color_rows
 (a.output/'frames.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');q=dict(source_mask_passed=True,human_visual_review=False,native_run=False,ROM_sha256=sha(run/'candidate.nes'),mode=z['mode'],variant=z['variant'],frames=len(rows),published_label_frames=sum('mask_pixels'in r for r in rows),first_published_frame=first,mask_mismatches=sum(r.get('mask_mismatches',0)for r in rows),observed_source_NES_color_to_RGB=color_rows,preparation_sha256=sha(a.packet/'preparation.json'),hud_frames_sha256=sha(run/'hud-frames.jsonl'),frames_sha256=sha(a.output/'frames.json'),tool_sha256=sha(Path(__file__)),output_bindings={f.name:sha(f)for f in a.output.iterdir()if f.is_file()},limits='Source glyph visible masks decoded from exact unchanged CHR and actual displayed labels/attributes/palette, compared to actual RGB HUD row8..15. RGB color classes are observed consistency, not a separate absolute palette calibration. Captured first-publication/fullscreen and everyHUD frame still require honest visual review. No body/crowding/campaign or unrecorded-frame verdict.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
